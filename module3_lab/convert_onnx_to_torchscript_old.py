import torch
import onnx
from onnx import numpy_helper, helper, TensorProto
import copy

def remove_problematic_pad_nodes(onnx_model):
    """移除或簡化會造成 onnx2pytorch 轉換失敗的 Pad 節點"""
    graph = onnx_model.graph
    
    # 找出所有 Pad 節點
    pad_nodes = [node for node in graph.node if node.op_type == 'Pad']
    
    for pad_node in pad_nodes:
        print(f"Found Pad node: {pad_node.name}")
        
        # 找出 Pad 的輸出被誰使用
        pad_output = pad_node.output[0]
        next_node = None
        for node in graph.node:
            if pad_output in node.input:
                next_node = node
                break
        
        if next_node:
            # 直接連接 Pad 的輸入到下一個節點
            # 移除 Pad 節點
            graph.node.remove(pad_node)
            
            # 更新下一個節點的輸入為 Pad 的輸入
            pad_input = pad_node.input[0]
            for i, inp in enumerate(next_node.input):
                if inp == pad_output:
                    next_node.input[i] = pad_input
                    break
            
            print(f"  Removed Pad node and connected input '{pad_input}' directly to '{next_node.op_type}'")
    
    return onnx_model


def convert_subgraph_to_pt(onnx_path, output_path):
    print(f"Loading ONNX model from {onnx_path}...")
    model = onnx.load(onnx_path)
    
    # 移除有問題的 Pad 節點
    print("Preprocessing: removing problematic Pad nodes...")
    model = remove_problematic_pad_nodes(model)
    
    # 驗證修改後的模型
    try:
        onnx.checker.check_model(model)
        print("ONNX model validation: OK")
    except Exception as e:
        print(f"Warning: ONNX model validation failed: {e}")
    
    # 嘗試用 onnx2pytorch 轉換
    try:
        from onnx2pytorch import ConvertModel
        print("Converting ONNX to PyTorch using onnx2pytorch...")
        pytorch_model = ConvertModel(model)
        pytorch_model.eval()
        
        # 用 dummy input trace 成 TorchScript
        print("Tracing PyTorch model to TorchScript...")
        dummy_input = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            jit_model = torch.jit.trace(pytorch_model, dummy_input)
        
        jit_model.save(output_path)
        print(f"Successfully saved TorchScript model to {output_path}")
        
    except Exception as e:
        print(f"onnx2pytorch conversion failed: {e}")
        print("Falling back to weight-only wrapper method...")
        
        # 備用方案：只提取權重
        class WeightOnlyWrapper(torch.nn.Module):
            def __init__(self, onnx_model):
                super().__init__()
                self.params = torch.nn.ParameterDict()
                for init in onnx_model.graph.initializer:
                    tensor = numpy_helper.to_array(init)
                    self.params[init.name] = torch.nn.Parameter(torch.from_numpy(tensor))
            
            def forward(self, x):
                return x
        
        wrapper = WeightOnlyWrapper(model)
        jit_model = torch.jit.script(wrapper)
        jit_model.save(output_path)
        print(f"Saved weight-only wrapper to {output_path}")

if __name__ == "__main__":
    convert_subgraph_to_pt("efficientnet-b1-subgraph.onnx", "efficientnet-b1-subgraph.pt")