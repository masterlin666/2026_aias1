"""
Module 4 - Lab 4-3
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

import torch
import numpy as np
import matplotlib.pyplot as plt

class KVCache:
    """
    Simple KV-Cache implementation for a single decoder layer.
    Stores K and V tensors and grows as new tokens are generated.
    """

    def __init__(self, n_kv_heads, d_k, max_seq_len=4096, dtype=torch.float16):
        self.n_kv_heads = n_kv_heads
        self.d_k = d_k
        self.max_seq_len = max_seq_len
        self.dtype = dtype
        self.current_len = 0

        # Pre-allocate cache: (max_seq_len, n_kv_heads, d_k)
        self.k_cache = torch.zeros(max_seq_len, n_kv_heads, d_k, dtype=dtype)
        self.v_cache = torch.zeros(max_seq_len, n_kv_heads, d_k, dtype=dtype)

    def update(self, new_k, new_v):
        """
        Append new K, V entries to the cache.

        Args:
            new_k: (n_tokens, n_kv_heads, d_k) - new key vectors
            new_v: (n_tokens, n_kv_heads, d_k) - new value vectors
        """
        n_new = new_k.shape[0]
        assert self.current_len + n_new <= self.max_seq_len, "Cache overflow!"

        self.k_cache[self.current_len:self.current_len + n_new] = new_k
        self.v_cache[self.current_len:self.current_len + n_new] = new_v
        self.current_len += n_new

    def get(self):
        """Return current cached K, V tensors."""
        return (self.k_cache[:self.current_len],
                self.v_cache[:self.current_len])

    def memory_bytes(self):
        """Return actual memory used by the cache (not pre-allocated)."""
        elem_size = 2 if self.dtype == torch.float16 else 4
        return 2 * self.current_len * self.n_kv_heads * self.d_k * elem_size

    def reset(self):
        self.current_len = 0


# --- Demonstrate KV-Cache usage ---
print("=" * 60)
print("KV-Cache Demonstration")
print("=" * 60)

# LLaMA 3 8B-like config (one layer)
n_kv_heads = 8   # GQA with 8 KV heads
d_k = 128

cache = KVCache(n_kv_heads=n_kv_heads, d_k=d_k, max_seq_len=4096)

# Simulate prefill: add 100 tokens at once
prefill_k = torch.randn(100, n_kv_heads, d_k, dtype=torch.float16)
prefill_v = torch.randn(100, n_kv_heads, d_k, dtype=torch.float16)
cache.update(prefill_k, prefill_v)
print(f"\nAfter prefill (100 tokens):")
print(f"  Cache length:  {cache.current_len}")
print(f"  Cache memory:  {cache.memory_bytes():,} bytes ({cache.memory_bytes() / 1024:.1f} KB)")

# Simulate decode: add tokens one at a time
for i in range(20):
    new_k = torch.randn(1, n_kv_heads, d_k, dtype=torch.float16)
    new_v = torch.randn(1, n_kv_heads, d_k, dtype=torch.float16)
    cache.update(new_k, new_v)

print(f"\nAfter 20 decode steps:")
print(f"  Cache length:  {cache.current_len}")
print(f"  Cache memory:  {cache.memory_bytes():,} bytes ({cache.memory_bytes() / 1024:.1f} KB)")

# Verify we can retrieve the full cache
k_all, v_all = cache.get()
print(f"  Retrieved K shape: {list(k_all.shape)}")
print(f"  Retrieved V shape: {list(v_all.shape)}")

# ============================================================
# Part B
# ============================================================

print("\n" + "=" * 60)
print("KV-Cache Growth: MHA vs GQA vs MQA")
print("=" * 60)

# Model configurations to compare
configs = {
    "MHA (n_kv=32)": {"n_kv_heads": 32, "d_k": 128, "n_layers": 32},   # Full MHA
    "GQA (n_kv=8)":  {"n_kv_heads": 8,  "d_k": 128, "n_layers": 32},   # LLaMA 3 8B
    "MQA (n_kv=1)":  {"n_kv_heads": 1,  "d_k": 128, "n_layers": 32},   # Single KV head
}

seq_lengths = [256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]
bytes_per_elem = 2  # FP16

print(f"\n{'Seq Len':>10}", end="")
for name in configs:
    print(f" {name:>18}", end="")
print()
print("-" * 70)

results = {name: [] for name in configs}

for S in seq_lengths:
    print(f"{S:>10}", end="")
    for name, cfg in configs.items():
        # KV-cache = 2 * n_kv_heads * d_k * n_layers * S * bytes_per_elem
        cache_bytes = 2 * cfg["n_kv_heads"] * cfg["d_k"] * cfg["n_layers"] * S * bytes_per_elem
        cache_gb = cache_bytes / (1024 ** 3)
        results[name].append(cache_gb)
        print(f" {cache_gb:>15.2f} GB", end="")
    print()

# Plot
fig, ax = plt.subplots(figsize=(10, 6))

colors = {'MHA (n_kv=32)': 'red', 'GQA (n_kv=8)': 'blue', 'MQA (n_kv=1)': 'green'}
for name, sizes in results.items():
    ax.plot(seq_lengths, sizes, 'o-', color=colors[name], label=name, linewidth=2)

# Add hardware memory reference lines
ax.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='H100 HBM3 (80 GB)')
ax.axhline(y=16, color='purple', linestyle='--', alpha=0.7, label='LLaMA 3 8B weights (16 GB)')

ax.set_xlabel('Sequence Length', fontsize=12)
ax.set_ylabel('KV-Cache Size (GB)', fontsize=12)
ax.set_title('KV-Cache Memory Growth: MHA vs GQA vs MQA\n(LLaMA 3 8B scale, 32 layers, FP16)', fontsize=13)
ax.set_xscale('log', base=2)
ax.set_yscale('log')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('kv_cache_growth.png', dpi=150)
plt.show()
print("\nPlot saved to kv_cache_growth.png")

# ============================================================
# Part C
# ============================================================

print("\n" + "=" * 60)
print("Full Decode Session Simulation")
print("=" * 60)

# Simulate generating 500 tokens after a 100-token prompt
# Track memory usage at each step

n_kv_heads = 8
d_k = 128
n_layers = 32
prompt_len = 100
gen_len = 500
bytes_per_elem = 2

steps = list(range(prompt_len, prompt_len + gen_len + 1))
cache_sizes_mb = []

for S in steps:
    total_cache = 2 * n_kv_heads * d_k * n_layers * S * bytes_per_elem
    cache_sizes_mb.append(total_cache / (1024 ** 2))

model_weights_mb = 16 * 1024  # 16 GB in MB

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(steps, cache_sizes_mb, 'b-', linewidth=2, label='KV-Cache')
ax.axhline(y=model_weights_mb, color='red', linestyle='--', alpha=0.7,
           label=f'Model weights ({model_weights_mb / 1024:.0f} GB)')
ax.fill_between(steps, cache_sizes_mb, alpha=0.2)

ax.set_xlabel('Tokens Generated (prompt + output)', fontsize=12)
ax.set_ylabel('Memory (MB)', fontsize=12)
ax.set_title('KV-Cache Growth During Decode\n(GQA n_kv=8, d_k=128, 32 layers, FP16)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('kv_cache_decode_session.png', dpi=150)
plt.show()
print("Plot saved to kv_cache_decode_session.png")

# Print summary
print(f"\nDecode session summary:")
print(f"  Prompt length:     {prompt_len} tokens")
print(f"  Generated tokens:  {gen_len}")
print(f"  Final cache size:  {cache_sizes_mb[-1]:.1f} MB ({cache_sizes_mb[-1] / 1024:.2f} GB)")
print(f"  Cache growth rate: {(cache_sizes_mb[-1] - cache_sizes_mb[0]) / gen_len:.2f} MB/token")
