#python3  hw2_3_transform.py
import onnx
from onnx import helper, numpy_helper, TensorProto
import numpy as np
import math

def get_initializer_data(graph, name):
    for init in graph.initializer:
        if init.name == name:
            return numpy_helper.to_array(init)
    return None

def create_tiled_nodes(input_name, output_name, W_data, b_data, tile_size=64):
    in_features, out_features = W_data.shape
    num_m = math.ceil(in_features / tile_size)
    num_n = math.ceil(out_features / tile_size)
    
    nodes = []
    inits = []
    
    # 1. Slice Input X
    x_slices = []
    for i in range(num_m):
        raw_slice = f"{output_name}_x_s{i}_raw"
        s_name = f"{output_name}_x_s{i}_pad"
        start, end = i * tile_size, min((i + 1) * tile_size, in_features)
        
        c_start = helper.make_tensor(f"{output_name}_s_start_{i}", TensorProto.INT64, [1], [start])
        c_end = helper.make_tensor(f"{output_name}_s_end_{i}", TensorProto.INT64, [1], [end])
        c_axis = helper.make_tensor(f"{output_name}_s_axis_{i}", TensorProto.INT64, [1], [1])
        inits.extend([c_start, c_end, c_axis])
        
        nodes.append(helper.make_node(
            'Slice', [input_name, c_start.name, c_end.name, c_axis.name], [raw_slice],
            name=f"Node_{output_name}_Slice_{i}"
        ))
        
        if (end - start) < tile_size:
            p_val = helper.make_tensor(f"{output_name}_p_val_{i}", TensorProto.INT64, [4], [0, 0, 0, tile_size - (end - start)])
            inits.append(p_val)
            nodes.append(helper.make_node('Pad', [raw_slice, p_val.name], [s_name], name=f"Node_{output_name}_Pad_{i}"))
        else:
            s_name = raw_slice
        x_slices.append(s_name)

    # 2. MatMul tiles & Summing (已修正重複節點問題)
    W_padded = np.zeros((num_m * tile_size, num_n * tile_size), dtype=np.float32)
    W_padded[:in_features, :out_features] = W_data
    
    y_tiles = []
    for j in range(num_n):
        partial_sums = []
        for i in range(num_m):
            w_tile_data = W_padded[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size]
            w_name = f"{output_name}_W_t{i}_{j}"
            inits.append(helper.make_tensor(w_name, TensorProto.FLOAT, [tile_size, tile_size], w_tile_data.flatten()))
            
            mm_out = f"{output_name}_mm_{i}_{j}"
            nodes.append(helper.make_node(
                'MatMul', [x_slices[i], w_name], [mm_out],
                name=f"Node_{output_name}_MatMul_{i}_{j}"
            ))
            partial_sums.append(mm_out)
        
        y_tile_j = f"{output_name}_y_t{j}"
        # 修正：加上 Sum 節點來加總 Partial Sums
        nodes.append(helper.make_node(
            'Sum', partial_sums, [y_tile_j],
            name=f"Node_{output_name}_Sum_{j}"
        ))
        y_tiles.append(y_tile_j)

    # 3. Concat & Final Crop & Bias
    concat_out = f"{output_name}_concat"
    nodes.append(helper.make_node('Concat', y_tiles, [concat_out], axis=1, name=f"Node_{output_name}_Concat"))
    
    sliced_out = f"{output_name}_sliced"
    c_f_start = helper.make_tensor(f"{output_name}_f_s", TensorProto.INT64, [1], [0])
    c_f_end = helper.make_tensor(f"{output_name}_f_e", TensorProto.INT64, [1], [out_features])
    c_f_axis = helper.make_tensor(f"{output_name}_f_a", TensorProto.INT64, [1], [1])
    inits.extend([c_f_start, c_f_end, c_f_axis])
    nodes.append(helper.make_node('Slice', [concat_out, c_f_start.name, c_f_end.name, c_f_axis.name], [sliced_out], name=f"Node_{output_name}_FinalSlice"))

    b_name = f"{output_name}_bias"
    inits.append(helper.make_tensor(b_name, TensorProto.FLOAT, [1, out_features], b_data.flatten()))
    nodes.append(helper.make_node('Add', [sliced_out, b_name], [output_name], name=f"Node_{output_name}_BiasAdd"))
    
    return nodes, inits

def transform_alexnet(input_path, output_path):
    model = onnx.load(input_path)
    graph = model.graph
    
    target_layers = ['classifier.1', 'classifier.4', 'classifier.6']
    new_nodes = []
    new_inits = list(graph.initializer)
    
    # 建立一個輸出名稱到節點的映射，方便尋找
    nodes_to_remove = []
    
    for node in graph.node:
        if node.op_type == 'Gemm' and any(target in node.name for target in target_layers):
            print(f"Tiling layer: {node.name}")
            
            # 取得輸入名稱 (X), 權重名稱 (W), 偏置名稱 (B)
            x_in = node.input[0]
            w_name = node.input[1]
            b_name = node.input[2]
            y_out = node.output[0]
            
            w_data = get_initializer_data(graph, w_name)
            b_data = get_initializer_data(graph, b_name)
            
            # 注意：ONNX Gemm 的 W 通常是 [Out, In]，但矩陣乘法需要 [In, Out]
            # 如果 transB=1 (預設 PyTorch 導出)，則需要轉置
            w_data = w_data.T 
            
            t_nodes, t_inits = create_tiled_nodes(x_in, y_out, w_data, b_data)
            new_nodes.extend(t_nodes)
            new_inits.extend(t_inits)
            nodes_to_remove.append(node)
        else:
            new_nodes.append(node)
            
    # 移除舊節點
    final_nodes = [n for n in new_nodes if n not in nodes_to_remove]
    
    # 建立新圖
    new_graph = helper.make_graph(final_nodes, graph.name, graph.input, graph.output, initializer=new_inits)
    new_model = helper.make_model(new_graph, opset_imports=model.opset_import)
    
    onnx.checker.check_model(new_model)
    onnx.save(new_model, output_path)
    print(f"Successfully transformed AlexNet to {output_path}")

if __name__ == "__main__":
    transform_alexnet("alexnet.onnx", "alexnet_tiled.onnx")