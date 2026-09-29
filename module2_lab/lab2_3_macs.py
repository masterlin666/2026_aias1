import torch
import torch.nn as nn

# ============================================================
# Part A: SimpleLinearModel
# ============================================================

class SimpleLinearModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 20)   # MACs = 10 * 20 = 200
        self.fc2 = nn.Linear(20, 15)   # MACs = 20 * 15 = 300
        self.fc3 = nn.Linear(15, 1)    # MACs = 15 * 1  = 15

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x

model = SimpleLinearModel()
print("=" * 60)
print("Part A: SimpleLinearModel MACs")
print("=" * 60)

total_macs = 0
for name, module in model.named_modules():
    if isinstance(module, nn.Linear):
        macs = module.in_features * module.out_features
        total_macs += macs
        print(f"{name}: in={module.in_features}, out={module.out_features}, MACs={macs:,}")

print(f"\nTotal MACs: {total_macs:,}")
print(f"Total FLOPs: {total_macs * 2:,}")
