# python3 hw2_1_macs.py
import torch
import torch.nn as nn
import torchvision.models as models

model = models.googlenet(weights=models.GoogLeNet_Weights.DEFAULT)
model.eval()

mac_records = []

def mac_hook(name):
    def hook(module, input, output):
        if isinstance(module, nn.Conv2d):
            _, _, oh, ow = output.shape
            # 計算卷積層 MACs
            macs = oh * ow * module.kernel_size[0] * module.kernel_size[1] * \
                   module.in_channels * module.out_channels
            mac_records.append((name, "Conv2d", macs))
        elif isinstance(module, nn.Linear):
            # 計算全連接層 MACs (Input_features * Output_features)
            macs = module.in_features * module.out_features
            mac_records.append((name, "Linear", macs))
    return hook

# 註冊 Hooks
hooks = []
for name, module in model.named_modules():
    if isinstance(module, (nn.Conv2d, nn.Linear)):
        hooks.append(module.register_forward_hook(mac_hook(name)))

# 前向傳播
dummy_input = torch.randn(1, 3, 224, 224)
with torch.no_grad():
    _ = model(dummy_input)

# 移除 Hooks
for h in hooks:
    h.remove()

# 輸出結果
total_macs = sum(m[2] for m in mac_records)
for name, l_type, macs in mac_records:
    print(f"{name:<50} {l_type:<10} {macs:>15,}")

print(f"\nTotal MACs: {total_macs:,}")
print(f"Total FLOPs (MACs * 2): {total_macs * 2:,}")