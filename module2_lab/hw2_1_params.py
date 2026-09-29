# hw2_1_params.py
#python3 hw2_1_params.py
import torch
import torchvision.models as models

model = models.googlenet(weights=models.GoogLeNet_Weights.DEFAULT)
model.eval()

# HW 2-1-1: 計算總參數量
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
non_trainable_params = total_params - trainable_params

print(f"--- HW 2-1-1: Parameter Count ---")
print(f"Total Parameters: {total_params:,}")
print(f"Trainable Parameters: {trainable_params:,}")
print(f"Non-trainable Parameters: {non_trainable_params:,}\n")

# HW 2-1-2: 計算權重記憶體
print(f"--- HW 2-1-2: Weight Memory Usage ---")
precisions = {
    "FP32": 4,
    "FP16/BF16": 2,
    "INT8": 1,
    "INT4": 0.5
}

for name, byte_size in precisions.items():
    mem_bytes = total_params * byte_size
    mem_mb = mem_bytes / (1024**2)
    print(f"{name:<10}: {mem_bytes:>12,.0f} bytes ({mem_mb:>6.2f} MB)")
    
from torchinfo import summary

# 執行摘要
model_stats = summary(model, input_size=(1, 3, 224, 224),
        col_names=("input_size", "output_size", "num_params",
                   "kernel_size", "mult_adds"),
        depth=3) # 設定 depth=3 可以清楚看到 Inception 內部的卷積層
print(model_stats)   