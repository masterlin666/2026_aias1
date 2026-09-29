"""
HW 1-1 Part 1: ResNet-50 ONNX Conversion

Export a pre-trained ResNet-50 model from PyTorch to ONNX format.

Requirements:
  - Opset version >= 17
  - Input name: "input", Output name: "output"
  - Dynamic batch size via dynamic_axes
  - export_params=True, do_constant_folding=True
  - Save as resnet50.onnx
  - Verify with onnx.checker.check_model()
  - Print IR version, opset version, and total graph nodes
"""

import torch
import torchvision.models as models
import onnx
import os

# TODO: Load pre-trained ResNet-50
# model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
# TODO: Set model to eval mode
model.eval()
# TODO: Create dummy input tensor (batch=1, channels=3, height=224, width=224)
dummy_input = torch.randn(1, 3, 224, 224)
# TODO: Export to ONNX with the settings described above
onnx_filename = "resnet50.onnx"
torch.onnx.export(
    model,
    dummy_input,
    onnx_filename,
    export_params=True,        # 儲存訓練後的權重
    opset_version=17,          # 要求版本 >= 17
    do_constant_folding=True,  # 執行常數折疊優化
    input_names=['input'],     # 指定輸入名稱
    output_names=['output'],   # 指定輸出名稱
    dynamic_axes={             # 設定動態批次大小
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

print(f"Successfully exported {onnx_filename}")
# TODO: Load and verify the exported ONNX model
onnx_model = onnx.load(onnx_filename)
onnx.checker.check_model(onnx_model)

# TODO: Print model info (IR version, opset version, total nodes)
print("-" * 30)
print(f"IR Version: {onnx_model.ir_version}")
print(f"Opset Version: {onnx_model.opset_import[0].version}")
print(f"Total Graph Nodes: {len(onnx_model.graph.node)}")
print("-" * 30)
