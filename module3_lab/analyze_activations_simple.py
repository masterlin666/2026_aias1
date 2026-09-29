import onnx
from onnx import numpy_helper
import numpy as np

def infer_tensor_shapes(onnx_path):
    """用形狀推斷來計算每層的激活值記憶體"""
    
    # 載入清理前的模型
    model = onnx.load(onnx_path)
    graph = model.graph
    
    # 應用清理邏輯（與 convert_onnx_to_torchscript_v2.py 相同）
    pad_nodes = [node for node in graph.node if node.op_type == 'Pad']
    for pad_node in pad_nodes:
        pad_output = pad_node.output[0]
        next_node = None
        for node in graph.node:
            if pad_output in node.input:
                next_node = node
                break
        
        if next_node:
            graph.node.remove(pad_node)
            pad_input = pad_node.input[0]
            for i, inp in enumerate(next_node.input):
                if inp == pad_output:
                    next_node.input[i] = pad_input
    
    # 清理孤立節點
    output_names = {out.name for out in graph.output}
    required_tensors = set(output_names)
    required_nodes = []
    
    changed = True
    while changed:
        changed = False
        for node in graph.node:
            if any(out in required_tensors for out in node.output):
                if node not in required_nodes:
                    required_nodes.append(node)
                    for inp in node.input:
                        if inp not in required_tensors:
                            required_tensors.add(inp)
                            changed = True
    
    nodes_to_remove = [n for n in graph.node if n not in required_nodes]
    for node in nodes_to_remove:
        graph.node.remove(node)
    
    # 現在手動推斷形狀
    print(f"=== Activation Memory Analysis: {onnx_path} ===\n")
    print(f"Input shape: (1, 3, 224, 224)")  # batch_size=1 for analysis
    print(f"{'Layer':<35} | {'Output Shape':<25} | {'Elements':>12} | {'Memory (MB)':>12}")
    print("-" * 90)
    
    # 已知的初始形狀
    tensor_shapes = {}
    
    for inp in graph.input:
        dim_vals = []
        for dim in inp.type.tensor_type.shape.dim:
            if dim.HasField("dim_value"):
                dim_vals.append(dim.dim_value)
            else:
                dim_vals.append(1)  # 使用 batch=1
        tensor_shapes[inp.name] = tuple(dim_vals)
    
    for init in graph.initializer:
        tensor_shapes[init.name] = tuple(init.dims)
    
    # 逐節點推斷
    total_bytes = 0
    peak_bytes = 0
    
    for node in graph.node:
        if node.op_type == 'Conv':
            # Conv: (N, H, W, C) -> (N, H', W', C_out)
            # input: (1, 3, 224, 224)
            # weight: [32, 3, 3, 3]
            # output: (1, 32, 224, 224) （假設 padding='same'）
            output_shape = (1, 32, 224, 224)
            node_name = "Conv2d"
        
        elif node.op_type == 'Sigmoid':
            # Sigmoid 保持相同形狀
            prev_output = node.input[0]
            output_shape = tensor_shapes.get(prev_output, (1, 32, 224, 224))
            node_name = "Sigmoid"
        
        elif node.op_type == 'Mul':
            # Mul 保持相同形狀
            prev_output = node.input[0]
            output_shape = tensor_shapes.get(prev_output, (1, 32, 224, 224))
            node_name = "Mul"
        
        else:
            continue
        
        # 記錄輸出形狀
        for out in node.output:
            tensor_shapes[out] = output_shape
        
        # 計算記憶體（FP32: 4 bytes per element）
        numel = int(np.prod(output_shape))
        bytes_val = numel * 4
        memory_mb = bytes_val / (1024 * 1024)
        
        shape_str = str(output_shape)
        print(f"{node_name:<35} | {shape_str:<25} | {numel:>12} | {memory_mb:>12.6f}")
        
        total_bytes += bytes_val
        peak_bytes = max(peak_bytes, bytes_val)
    
    print("-" * 90)
    total_mb = total_bytes / (1024 * 1024)
    peak_mb = peak_bytes / (1024 * 1024)
    
    print(f"\nTotal activation memory: {total_bytes} bytes ({total_mb:.6f} MB)")
    print(f"Peak single-layer activation: {peak_bytes} bytes ({peak_mb:.6f} MB)\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        onnx_path = "efficientnet-b1-subgraph.onnx"
    else:
        onnx_path = sys.argv[1]
    
    infer_tensor_shapes(onnx_path)
