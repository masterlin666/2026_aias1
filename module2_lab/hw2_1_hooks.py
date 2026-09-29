# python3 hw2_1_hooks.py
import torch
import torch.nn as nn
import torchvision.models as models

model = models.googlenet(weights=models.GoogLeNet_Weights.DEFAULT)
model.eval()

activation_records = []

def act_hook(name):
    def hook(module, input, output):
        # 計算輸出 Tensor 的元素數量
        num_elements = output.numel()
        # 假設 FP32 (4 bytes)
        mem_kb = (num_elements * 4) / 1024
        activation_records.append({
            "name": name,
            "shape": tuple(output.shape),
            "mem_kb": mem_kb
        })
    return hook

hooks = [m.register_forward_hook(act_hook(n)) 
         for n, m in model.named_modules() if isinstance(m, nn.Conv2d)]

with torch.no_grad():
    model(torch.randn(1, 3, 224, 224))

for h in hooks: h.remove()

# 統計分析
max_act = max(activation_records, key=lambda x: x['mem_kb'])
total_mem_kb = sum(x['mem_kb'] for x in activation_records)

print(f"{'Layer Name':<40} {'Output Shape':<20} {'Mem (KB)':>10}")
print("-" * 75)
for rec in activation_records:
    print(f"{rec['name']:<40} {str(rec['shape']):<20} {rec['mem_kb']:>10.2f}")

print("\n--- Summary ---")
print(f"Largest Activation Layer: {max_act['name']} ({max_act['mem_kb']:.2f} KB)")
print(f"Total Conv2d Activation Memory: {total_mem_kb / 1024:.2f} MB")