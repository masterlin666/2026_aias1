"""
HW 1-2 Part 1: AlexNet & ViT-B/16 Export and Comparison

Export both AlexNet and ViT-B/16 to ONNX and print a comparison summary:
  - Opset version: 17
  - Dynamic batch size
  - Named inputs/outputs
  - Verify both models pass onnx.checker.check_model()
  - Print comparison table (file size, ONNX nodes, parameters, verification)
"""
import torch
import torchvision.models as models
import onnx
import os

def get_model_info(model_path, model):
    # 計算檔案大小 (MB)
    file_size = os.path.getsize(model_path) / (1024 * 1024)
    
    # 載入 ONNX 模型計算節點數
    onnx_model = onnx.load(model_path)
    nodes_count = len(onnx_model.graph.node)
    
    # 計算參數量 (Millions)
    params_count = sum(p.numel() for p in model.parameters())
    
    # 驗證模型
    try:
        onnx.checker.check_model(onnx_model)
        verified = "Pass"
    except Exception:
        verified = "Fail"
        
    return file_size, nodes_count, params_count, verified

# 1. Load pre-trained models
# AlexNet: 典型的卷積神經網路
alexnet = models.alexnet(weights=models.AlexNet_Weights.IMAGENET1K_V1).eval()
# ViT-B/16: 典型的 Vision Transformer
vit = models.vit_b_16(weights=models.ViT_B_16_Weights.IMAGENET1K_V1).eval()

# 準備虛擬輸入 (Dummy Input)
dummy_input = torch.randn(1, 3, 224, 224)
input_names = ["input"]
output_names = ["output"]
dynamic_axes = {"input": {0: "batch_size"}, "output": {0: "batch_size"}}

# 2. Export AlexNet
alexnet_path = "alexnet.onnx"
torch.onnx.export(
    alexnet, dummy_input, alexnet_path,
    export_params=True, opset_version=17,
    do_constant_folding=True,
    input_names=input_names, output_names=output_names,
    dynamic_axes=dynamic_axes
)

# 3. Export ViT-B/16
vit_path = "vit_b_16.onnx"
torch.onnx.export(
    vit, dummy_input, vit_path,
    export_params=True, opset_version=17,
    do_constant_folding=True,
    input_names=input_names, output_names=output_names,
    dynamic_axes=dynamic_axes
)

# 4. Get stats and Print Table
alex_stats = get_model_info(alexnet_path, alexnet)
vit_stats = get_model_info(vit_path, vit)

print(f"{'Model':<12} | {'File Size':<10} | {'ONNX Nodes':<10} | {'Parameters':<12} | {'Verified'}")
print("─" * 62)
print(f"{'AlexNet':<12} | {alex_stats[0]:>6.2f} MB | {alex_stats[1]:>10} | {alex_stats[2]:>12,} | {alex_stats[3]}")
print(f"{'ViT-B/16':<12} | {vit_stats[0]:>6.2f} MB | {vit_stats[1]:>10} | {vit_stats[2]:>12,} | {vit_stats[3]}")