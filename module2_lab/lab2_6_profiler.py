#!/usr/bin/env python3
"""Lab 2-6: PyTorch Profiler and TensorBoard"""

import torch
import torchvision.models as models
from torch.profiler import profile, ProfilerActivity, record_function

# ============================================================
# Part A: Basic CPU profiling (inference)
# ============================================================
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.eval()

inputs = torch.randn(1, 3, 224, 224)

print("=" * 60)
print("Part A: CPU Time Profiling (ResNet-18 Inference)")
print("=" * 60)

with profile(activities=[ProfilerActivity.CPU], record_shapes=True) as prof:
    with record_function("model_inference"):
        model(inputs)

print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=15))
