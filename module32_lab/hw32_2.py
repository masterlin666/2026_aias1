import torch
import torch.nn.functional as F
import time
import pandas as pd

# 自動偵測設備
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Running on: {DEVICE}")

def unfused_bias_gelu(x, bias):
    x_biased = x + bias
    return F.gelu(x_biased)

def fused_bias_gelu(x, bias):
    # 在 CPU 上，這依然能減少中間 Tensor 的分配與讀寫
    return F.gelu(x + bias)

def benchmark(size, iterations=1000):
    # 使用正確的裝置
    x = torch.randn(size, device=DEVICE, dtype=torch.float32)
    bias = torch.randn(size[-1], device=DEVICE, dtype=torch.float32)
    
    # Warmup
    for _ in range(10):
        unfused_bias_gelu(x, bias)
        fused_bias_gelu(x, bias)
    
    if DEVICE == 'cuda': torch.cuda.synchronize()
    
    # Timing Unfused
    start = time.perf_counter()
    for _ in range(iterations):
        _ = unfused_bias_gelu(x, bias)
    if DEVICE == 'cuda': torch.cuda.synchronize()
    t_unfused = (time.perf_counter() - start) / iterations
    
    # Timing Fused
    start = time.perf_counter()
    for _ in range(iterations):
        _ = fused_bias_gelu(x, bias)
    if DEVICE == 'cuda': torch.cuda.synchronize()
    t_fused = (time.perf_counter() - start) / iterations
    
    # Numerical Check
    out_unfused = unfused_bias_gelu(x, bias)
    out_fused = fused_bias_gelu(x, bias)
    max_diff = torch.max(torch.abs(out_unfused - out_fused)).item()
    
    return t_unfused, t_fused, max_diff

# 執行實驗
sizes = [(1, 4096), (32, 4096), (512, 4096), (2048, 4096)]
for s in sizes:
    u, f, diff = benchmark(s)
    speedup = u / f
    print(f"Size {s}: Speedup = {speedup:.2f}x, Max Diff = {diff:.2e}")