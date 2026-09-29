import onnx
from onnx import numpy_helper, helper, TensorProto
import torch
import numpy as np

def clean_unused_nodes(onnx_model):
    """移除所有未被使用的節點（孤立節點）和未使用的輸入"""
    graph = onnx_model.graph
    
    # 找出所有有效的輸出節點
    output_names = {out.name for out in graph.output}
    
    # 反向追蹤：從輸出開始，找出所有必要的節點
    required_tensors = set(output_names)
    required_nodes = []
    
    # 重複掃描直到找不到新的所需節點
    changed = True
    while changed:
        changed = False
        for node in graph.node:
            if any(out in required_tensors for out in node.output):
                if node not in required_nodes:
                    required_nodes.append(node)
                    # 將此節點的輸入加入必要張量集
                    for inp in node.input:
                        if inp not in required_tensors:
                            required_tensors.add(inp)
                            changed = True
    
    # 移除所有不必要的節點
    nodes_to_remove = [n for n in graph.node if n not in required_nodes]
    for node in nodes_to_remove:
        graph.node.remove(node)
        print(f"  Removed unused node: {node.op_type} ({node.name})")
    
    # 移除未被使用的圖輸入
    inputs_to_remove = []
    for inp in graph.input:
        if inp.name not in required_tensors:
            inputs_to_remove.append(inp)
    
    for inp in inputs_to_remove:
        graph.input.remove(inp)
        print(f"  Removed unused input: {inp.name}")
    
    return onnx_model


def remove_problematic_constructs(onnx_model):
    """
    1. 移除 Pad 節點
    2. 清理孤立的常數構造節點
    """
    graph = onnx_model.graph
    
    # 第1步：移除 Pad 節點
    print("Step 1: Removing Pad nodes...")
    pad_nodes = [node for node in graph.node if node.op_type == 'Pad']
    
    for pad_node in pad_nodes:
        print(f"  Found Pad node: {pad_node.name}")
        
        # 找出 Pad 的輸出被誰使用
        pad_output = pad_node.output[0]
        next_node = None
        for node in graph.node:
            if pad_output in node.input:
                next_node = node
                break
        
        if next_node:
            # 直接連接 Pad 的輸入到下一個節點
            graph.node.remove(pad_node)
            
            # 更新下一個節點的輸入
            pad_input = pad_node.input[0]
            for i, inp in enumerate(next_node.input):
                if inp == pad_output:
                    next_node.input[i] = pad_input
                    break
            
            print(f"  Removed Pad and connected input '{pad_input}' to '{next_node.op_type}'")
    
    # 第2步：清理孤立節點
    print("Step 2: Removing unused nodes...")
    clean_unused_nodes(onnx_model)
    
    return onnx_model


def convert_subgraph_to_pt(onnx_path, output_path):
    print(f"Loading ONNX model from {onnx_path}...")
    model = onnx.load(onnx_path)
    
    print("\nPreprocessing ONNX model...")
    model = remove_problematic_constructs(model)
    
    # 驗證修改後的模型
    try:
        onnx.checker.check_model(model)
        print("✓ ONNX model validation: OK\n")
    except Exception as e:
        print(f"⚠ Warning: ONNX model validation failed: {e}\n")
    
    # 嘗試用 onnx2pytorch 轉換
    try:
        from onnx2pytorch import ConvertModel
        print("Converting ONNX to PyTorch using onnx2pytorch...")
        pytorch_model = ConvertModel(model)
        pytorch_model.eval()
        
        # 用 dummy input trace 成 TorchScript
        print("Tracing PyTorch model to TorchScript...")
        dummy_input = torch.randn(10, 3, 224, 224)  # batch=10 like in subgraph
        with torch.no_grad():
            jit_model = torch.jit.trace(pytorch_model, dummy_input)
        
        jit_model.save(output_path)
        print(f"✓ Successfully saved TorchScript model to {output_path}\n")
        return True
        
    except Exception as e:
        print(f"✗ onnx2pytorch conversion failed: {e}\n")
        print("Falling back to weight-only wrapper method...")
        
        # 備用方案：只提取權重
        class WeightOnlyWrapper(torch.nn.Module):
            def __init__(self, onnx_model):
                super().__init__()
                self.params = torch.nn.ParameterDict()
                for init in onnx_model.graph.initializer:
                    tensor = numpy_helper.to_array(init)
                    # 確保張量是可寫的
                    if not tensor.flags.writeable:
                        tensor = np.array(tensor)
                    self.params[init.name] = torch.nn.Parameter(
                        torch.from_numpy(tensor).float()
                    )
            
            def forward(self, x):
                # 未來可以實現實際的前向傳播
                return x
        
        wrapper = WeightOnlyWrapper(model)
        jit_model = torch.jit.script(wrapper)
        jit_model.save(output_path)
        print(f"✓ Saved weight-only wrapper to {output_path}\n")
        return False


if __name__ == "__main__":
    success = convert_subgraph_to_pt(
        "efficientnet-b1-subgraph.onnx", 
        "efficientnet-b1-subgraph.pt"
    )
    
    if success:
        print("✓ Full conversion successful!")
    else:
        print("⚠ Converted with weight-only fallback")
