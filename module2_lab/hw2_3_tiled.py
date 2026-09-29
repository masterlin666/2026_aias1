# hw2_3_tiled.py
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper
import onnxruntime as ort
import math

def create_tiled_linear_model(in_features, out_features, tile_size=64, model_path="tiled_linear.onnx"):
    # 1. 準備原始數據 (與 HW 2-3-1 相同，確保可對比性)
    np.random.seed(42)
    W_data = np.random.randn(in_features, out_features).astype(np.float32)
    b_data = np.random.randn(out_features).astype(np.float32)

    # 計算 Padding 尺寸
    num_tiles_m = math.ceil(in_features / tile_size)
    num_tiles_n = math.ceil(out_features / tile_size)
    m_pad = num_tiles_m * tile_size
    n_pad = num_tiles_n * tile_size

    # 定義輸入與輸出
    X = helper.make_tensor_value_info('X', TensorProto.FLOAT, [1, in_features])
    Y = helper.make_tensor_value_info('Y', TensorProto.FLOAT, [1, out_features])

    nodes = []
    initializers = []

    # 2. 建立輸入 Slice (將 X 切成多個 1x64)
    x_slices = []
    for i in range(num_tiles_m):
        slice_name = f"x_slice_{i}"
        start = i * tile_size
        # 注意：如果最後一塊不足 64，硬體上通常補零，ONNX 則需小心處理邊界
        # 這裡為了符合 64x64 計算，我們先對輸入做 Padding 或精確 Slice
        end = min((i + 1) * tile_size, in_features)
        
        # 由於是 1xM，我們沿 axis 1 切割
        s_node = helper.make_node(
            'Slice',
            inputs=['X', 
                    helper.make_tensor(f"s_start_{i}", TensorProto.INT64, [1], [start]).name,
                    helper.make_tensor(f"s_end_{i}", TensorProto.INT64, [1], [end]).name,
                    helper.make_tensor(f"s_axes_{i}", TensorProto.INT64, [1], [1]).name],
            outputs=[f"x_raw_slice_{i}"]
        )
        nodes.append(s_node)
        initializers.extend([
            helper.make_tensor(f"s_start_{i}", TensorProto.INT64, [1], [start]),
            helper.make_tensor(f"s_end_{i}", TensorProto.INT64, [1], [end]),
            helper.make_tensor(f"s_axes_{i}", TensorProto.INT64, [1], [1])
        ])

        # 如果切出來不足 64，補零到 64 (為了模擬 64x64 MatMul)
        if (end - start) < tile_size:
            pad_node = helper.make_node(
                'Pad',
                inputs=[f"x_raw_slice_{i}", 
                        helper.make_tensor(f"p_val_{i}", TensorProto.INT64, [4], [0, 0, 0, tile_size - (end-start)]).name],
                outputs=[slice_name]
            )
            nodes.append(pad_node)
            initializers.append(helper.make_tensor(f"p_val_{i}", TensorProto.INT64, [4], [0, 0, 0, tile_size - (end-start)]))
        else:
            slice_name = f"x_raw_slice_{i}"
        
        x_slices.append(slice_name)

    # 3. 建立 Tiled MatMul 與 Partial Sums
    y_tiles = []
    W_padded = np.zeros((m_pad, n_pad), dtype=np.float32)
    W_padded[:in_features, :out_features] = W_data

    for j in range(num_tiles_n):
        partial_results = []
        for i in range(num_tiles_m):
            w_block = W_padded[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size]
            w_name = f"W_tile_{i}_{j}"
            initializers.append(helper.make_tensor(w_name, TensorProto.FLOAT, [tile_size, tile_size], w_block.flatten()))
            
            mm_out = f"mm_{i}_{j}"
            nodes.append(helper.make_node('MatMul', [x_slices[i], w_name], [mm_out]))
            partial_results.append(mm_out)
        
        # 累加 Partial Sums
        y_tile_j = f"y_tile_{j}"
        nodes.append(helper.make_node('Sum', partial_results, [y_tile_j]))
        y_tiles.append(y_tile_j)

    # 4. 合併輸出並加上 Bias
    concat_out = "y_concat"
    nodes.append(helper.make_node('Concat', y_tiles, [concat_out], axis=1))

    bias_init = helper.make_tensor('B', TensorProto.FLOAT, [1, out_features], b_data.flatten())
    initializers.append(bias_init)

    # 如果有 Padding N，需要先加 Bias (需要擴展 Bias) 或先 Slice
    # 這裡選擇先 Slice 回原始寬度 N，再加 Bias
    final_slice_out = "y_sliced"
    nodes.append(helper.make_node(
        'Slice',
        inputs=[concat_out,
                helper.make_tensor("f_start", TensorProto.INT64, [1], [0]).name,
                helper.make_tensor("f_end", TensorProto.INT64, [1], [out_features]).name,
                helper.make_tensor("f_axes", TensorProto.INT64, [1], [1]).name],
        outputs=[final_slice_out]
    ))
    initializers.extend([
        helper.make_tensor("f_start", TensorProto.INT64, [1], [0]),
        helper.make_tensor("f_end", TensorProto.INT64, [1], [out_features]),
        helper.make_tensor("f_axes", TensorProto.INT64, [1], [1])
    ])

    nodes.append(helper.make_node('Add', [final_slice_out, 'B'], ['Y']))

    # 5. 組裝模型
    graph = helper.make_graph(nodes, 'tiled_linear_graph', [X], [Y], initializer=initializers)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
    onnx.checker.check_model(model)
    onnx.save(model, model_path)
    print(f"Tiled model saved to {model_path}")
    return W_data, b_data

# 驗證邏輯
W_ref, b_ref = create_tiled_linear_model(256, 128)
sess = ort.InferenceSession("tiled_linear.onnx")
x_test = np.random.randn(1, 256).astype(np.float32)
res = sess.run(None, {'X': x_test})[0]
expected = x_test @ W_ref + b_ref
print(f"Verification Error: {np.max(np.abs(res - expected)):.2e}")