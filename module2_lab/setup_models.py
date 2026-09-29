#!/usr/bin/env python3
"""Generate prerequisite ONNX models for Module 2 labs.

Run this script before starting Lab 2-4:
    python3 setup_models.py
"""

import torch
import torch.nn as nn

# ============================================================
# LeNet-5 for Lab 2-4 (ONNX model parsing)
# ============================================================
class LeNet5(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, 5, padding=2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = x.flatten(1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = LeNet5()
model.eval()
dummy = torch.randn(1, 1, 28, 28)
torch.onnx.export(
    model, dummy, "lenet.onnx",
    opset_version=13,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}}
)
print("Created lenet.onnx (LeNet-5, MNIST 28x28 input)")
