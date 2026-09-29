"""
Lab 1-3, Part A: Export LeNet-5 to ONNX for Netron visualization.
"""

import torch
import torch.nn as nn
import onnx

class LeNet5(nn.Module):
    """Classic LeNet-5 architecture for MNIST digit classification."""
    def __init__(self):
        super(LeNet5, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5, padding=2)   # 28x28 -> 28x28
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)             # 14x14 -> 10x10
        self.fc1   = nn.Linear(16 * 5 * 5, 120)
        self.fc2   = nn.Linear(120, 84)
        self.fc3   = nn.Linear(84, 10)
        self.relu  = nn.ReLU()
        self.pool  = nn.MaxPool2d(2, 2)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))  # -> 6 x 14 x 14
        x = self.pool(self.relu(self.conv2(x)))  # -> 16 x 5 x 5
        x = x.view(-1, 16 * 5 * 5)              # Flatten
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Export
model = LeNet5()
model.eval()
dummy_input = torch.randn(1, 1, 28, 28)
torch.onnx.export(
    model, dummy_input, "lenet5.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
)

# Quick analysis
onnx_model = onnx.load("lenet5.onnx")
onnx.checker.check_model(onnx_model)
print(f"[OK] LeNet-5 exported: {len(onnx_model.graph.node)} nodes")

params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {params:,}")
