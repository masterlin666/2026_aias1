import onnx
from onnx import numpy_helper

def analyze_cleaned_graph():
    """分析清理後的 ONNX 圖"""
    model = onnx.load('efficientnet-b1-subgraph.onnx')
    graph = model.graph
    
    # 移除 Pad 節點
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
    
    # 現在分析清理後的圖
    print("=== 清理後的 ONNX 圖 ===\n")
    
    print("圖輸入：")
    for inp in graph.input:
        print(f"  {inp.name} - shape: {[d.dim_value for d in inp.type.tensor_type.shape.dim]}")
    
    print("\n圖輸出：")
    for out in graph.output:
        print(f"  {out.name}")
    
    print("\n剩餘節點：")
    for node in graph.node:
        print(f"\n  {node.op_type} ({node.name})")
        print(f"    輸入: {list(node.input)}")
        print(f"    輸出: {list(node.output)}")
    
    print("\n權重/初始化器：")
    for init in graph.initializer:
        shape = list(init.dims)
        print(f"  {init.name} - shape: {shape}")
    
    # 檢查所有張量的來源
    print("\n=== 張量來源追蹤 ===")
    tensor_sources = {}
    for inp in graph.input:
        tensor_sources[inp.name] = "INPUT"
    for init in graph.initializer:
        tensor_sources[init.name] = "INITIALIZER"
    
    for node in graph.node:
        for out in node.output:
            tensor_sources[out] = f"{node.op_type}({node.name})"
    
    for node in graph.node:
        print(f"\n{node.op_type} ({node.name}):")
        for inp in node.input:
            source = tensor_sources.get(inp, "UNKNOWN")
            print(f"  輸入: {inp} <- {source}")

if __name__ == "__main__":
    analyze_cleaned_graph()
