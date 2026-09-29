"""
Lab 32-1: Operator Profiling with PyTorch Hooks on GPT-2
Measures per-operator time breakdown in a transformer forward pass.
"""

import torch
import torch.nn as nn
import time
import matplotlib.pyplot as plt
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from collections import defaultdict

# Load GPT-2
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Storage for timing results
timing_results = defaultdict(list)

def classify_module(module):
    """
    Classify a PyTorch module into an operator category.

    Returns one of: 'GEMM', 'LayerNorm', 'Softmax', 'Activation', 'Other'
    """
    if isinstance(module, nn.Linear):
        return "GEMM"
    elif isinstance(module, nn.LayerNorm):
        return "LayerNorm"
    elif isinstance(module, nn.Softmax):
        return "Softmax"
    elif isinstance(module, (nn.GELU, nn.ReLU, nn.SiLU)):
        return "Activation"
    else:
        return "Other"

def make_timing_hook(name, category):
    """Create a forward hook that measures execution time."""
    def hook_fn(module, input, output):
        if device.type == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter()

        # We measure the time of a redundant forward pass to estimate cost.
        # NOTE: This is an approximation. For production profiling, use
        # torch.profiler or NVIDIA Nsight.
        with torch.no_grad():
            if isinstance(input, tuple):
                _ = module(input[0])
            else:
                _ = module(input)

        if device.type == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        timing_results[category].append(elapsed)

    return hook_fn

# Register hooks on all relevant modules
hooks = []
for name, module in model.named_modules():
    category = classify_module(module)
    if category != "Other":
        hooks.append(
            module.register_forward_hook(make_timing_hook(name, category))
        )

print(f"Registered {len(hooks)} profiling hooks")
