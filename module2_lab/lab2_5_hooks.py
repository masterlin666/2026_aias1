#!/usr/bin/env python3
"""Lab 2-5: Forward Hooks for Activation Extraction"""

import torch
import torchvision.models as models

model = models.alexnet(weights=models.AlexNet_Weights.DEFAULT)
model.eval()

# ============================================================
# Part 1: Hook Linear layers only
# ============================================================
activations = {}

def hook_fn(name):
    """Return a hook that records the output tensor for a given layer name."""
    def hook(module, input, output):
        activations[name] = output.detach()
    return hook

# Register hooks on all Linear layers in the classifier
hooks = []
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        h = module.register_forward_hook(hook_fn(name))
        hooks.append(h)

# Run inference with a dummy input
dummy_input = torch.randn(1, 3, 224, 224)
with torch.no_grad():
    output = model(dummy_input)

print("=" * 60)
print("AlexNet Linear Layer Activations")
print("=" * 60)
for name, act in activations.items():
    print(f"{name}: shape={list(act.shape)}, numel={act.numel()}, "
          f"memory={act.numel() * act.element_size():,} bytes")

# Clean up hooks
for h in hooks:
    h.remove()
print(f"\nHooks removed: {len(hooks)}")

# ============================================================
# Part 2: Hook ALL leaf layers to find the largest activation
# ============================================================
print("\n" + "=" * 60)
print("All Layer Activations (finding the largest)")
print("=" * 60)

all_activations = {}

def hook_all(name):
    def hook(module, input, output):
        if isinstance(output, torch.Tensor):
            all_activations[name] = output.detach()
    return hook

hooks2 = []
for name, module in model.named_modules():
    if len(list(module.children())) == 0:  # Leaf modules only
        hooks2.append(module.register_forward_hook(hook_all(name)))

with torch.no_grad():
    output = model(dummy_input)

# Sort by activation size (descending)
sorted_acts = sorted(all_activations.items(),
                     key=lambda x: x[1].numel(), reverse=True)

print(f"\n{'Layer':<40} {'Shape':<25} {'Elements':>10} {'Memory (KB)':>12}")
print("-" * 90)
total_activation_mem = 0
for name, act in sorted_acts:
    mem_kb = act.numel() * act.element_size() / 1024
    total_activation_mem += act.numel() * act.element_size()
    print(f"{name:<40} {str(list(act.shape)):<25} {act.numel():>10,} {mem_kb:>12.1f}")

print("-" * 90)
print(f"{'TOTAL':<40} {'':>25} {'':>10} {total_activation_mem / 1024:>12.1f}")
print(f"\nLargest activation: {sorted_acts[0][0]}")
print(f"  Shape: {list(sorted_acts[0][1].shape)}")
print(f"  Memory: {sorted_acts[0][1].numel() * sorted_acts[0][1].element_size() / 1024:.1f} KB")

# Clean up
for h in hooks2:
    h.remove()
print(f"\nHooks removed: {len(hooks2)}")
