import torch
import torchvision.models as models

# 1. 載入預訓練的 AlexNet
model = models.alexnet(weights=models.AlexNet_Weights.DEFAULT)
model.eval()

# 2. 準備 Dummy Input (Batch size=1, Channels=3, H=224, W=224)
dummy_input = torch.randn(1, 3, 224, 224)

# 3. 匯出為 ONNX
torch.onnx.export(
    model, 
    dummy_input, 
    "alexnet.onnx", 
    export_params=True, 
    opset_version=13, 
    do_constant_folding=True, 
    input_names=['input'], 
    output_names=['output']
)

print("alexnet.onnx has been exported successfully.")