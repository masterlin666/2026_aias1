import onnx
import numpy as np

def analyze_flops(onnx_path):
    """計算 ONNX 模型的 FLOPs"""
    
    # 載入並清理模型
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
    
    # 獲取初始化器（權重）
    initializers = {init.name: init for init in graph.initializer}
    
    print(f"=== FLOPs Analysis: {onnx_path} ===\n")
    print(f"Input shape: (1, 3, 224, 224)")
    print(f"{'Layer':<35} | {'Operation Details':<45} | {'FLOPs':>15}")
    print("-" * 100)
    
    total_flops = 0
    
    for node in graph.node:
        flops = 0
        details = ""
        
        if node.op_type == 'Conv':
            # Conv FLOPs = 2 * H_out * W_out * C_out * (C_in / groups) * K_h * K_w
            # input: (1, 3, 224, 224)
            # weight: [C_out, C_in/groups, K_h, K_w]
            
            # 從權重推斷參數
            weight_init = initializers.get(node.input[1])
            if weight_init:
                weight_shape = list(weight_init.dims)
                C_out, C_in_group, K_h, K_w = weight_shape
                
                # 假設 padding='same'，所以 H_out = H_in, W_out = W_in
                H_out = 224
                W_out = 224
                
                # 基本 FLOPs（不考慮分組卷積）
                flops = 2 * H_out * W_out * C_out * C_in_group * K_h * K_w
                
                # 檢查是否有偏置
                has_bias = len(node.input) > 2
                if has_bias:
                    flops += H_out * W_out * C_out
                
                details = f"H_out={H_out}, W_out={W_out}, C_out={C_out}, K=({K_h}x{K_w})"
        
        elif node.op_type == 'Sigmoid':
            # Sigmoid FLOPs = 輸入元素數
            flops = 1 * 32 * 224 * 224
            details = "Element-wise sigmoid"
        
        elif node.op_type == 'Mul':
            # Mul FLOPs = 輸入元素數
            flops = 1 * 32 * 224 * 224
            details = "Element-wise multiplication"
        
        if flops > 0:
            node_name = node.op_type
            flops_str = f"{flops:,}"
            print(f"{node_name:<35} | {details:<45} | {flops_str:>15}")
            total_flops += flops
    
    print("-" * 100)
    print(f"{'Total':<35} | {'':<45} | {total_flops:>15,}")
    print(f"\nTotal FLOPs: {total_flops:,} ({total_flops/1e9:.3f}G)\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        onnx_path = "efficientnet-b1-subgraph.onnx"
    else:
        onnx_path = sys.argv[1]
    
    analyze_flops(onnx_path)
