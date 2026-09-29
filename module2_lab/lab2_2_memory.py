import torch
import torchvision.models as models

model = models.alexnet(weights=models.AlexNet_Weights.DEFAULT)
model.eval()

# ============================================================
# Step 1: Count total parameters
# ============================================================
total_params = sum(p.numel() for p in model.parameters())
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
non_trainable = sum(p.numel() for p in model.parameters() if not p.requires_grad)

print("=" * 70)
print("Parameter Counting")
print("=" * 70)
print(f"Total parameters:         {total_params:>15,}")
print(f"Trainable parameters:     {trainable:>15,}")
print(f"Non-trainable parameters: {non_trainable:>15,}")

# ============================================================
# Step 2: Memory estimation across precisions
# ============================================================
print("\n" + "=" * 70)
print("Memory Estimation by Precision")
print("=" * 70)

param_size_fp32 = sum(p.numel() * p.element_size() for p in model.parameters())
precisions = {
    "FP32": (4, param_size_fp32),
    "FP16 / BF16": (2, total_params * 2),
    "INT8": (1, total_params * 1),
    "INT4": (0.5, int(total_params * 0.5)),
}

print(f"\n{'Precision':<15} {'Bytes/Elem':>10} {'Total Bytes':>18} {'MB':>10}")
print("-" * 55)
for name, (bpe, total_bytes) in precisions.items():
    print(f"{name:<15} {bpe:>10} {total_bytes:>18,} {total_bytes / 1024**2:>10.2f}")

# ============================================================
# Step 3: Buffer memory (non-parameter tensors)
# ============================================================
buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
print(f"\nBuffer memory (BatchNorm running stats, etc.): {buffer_size:,} bytes")
print(f"Total model memory (params + buffers, FP32): {(param_size_fp32 + buffer_size):,} bytes")

# ============================================================
# Step 4: Per-layer breakdown
# ============================================================
print("\n" + "=" * 70)
print("Per-Layer Parameter Breakdown")
print("=" * 70)
print(f"\n{'Layer':<45} {'Params':>12} {'Memory (KB)':>12} {'% Total':>8}")
print("-" * 80)
for name, param in model.named_parameters():
    mem = param.numel() * param.element_size()
    pct = param.numel() / total_params * 100
    print(f"{name:<45} {param.numel():>12,} {mem / 1024:>12.1f} {pct:>7.2f}%")

# ============================================================
# Step 5: DRAM loading time calculation
# ============================================================
print("\n" + "=" * 70)
print("DRAM Loading Time (all weights, FP16)")
print("=" * 70)

weight_bytes_fp16 = total_params * 2
bandwidths = {
    "DDR5 (51.2 GB/s)": 51.2e9,
    "HBM2e (460 GB/s)": 460e9,
    "HBM3e (1.2 TB/s)": 1.2e12,
}

print(f"\nWeight data (FP16): {weight_bytes_fp16:,} bytes ({weight_bytes_fp16 / 1024**2:.2f} MB)")
for name, bw in bandwidths.items():
    time_ms = weight_bytes_fp16 / bw * 1000
    print(f"  {name:<25} Loading time: {time_ms:.4f} ms")
