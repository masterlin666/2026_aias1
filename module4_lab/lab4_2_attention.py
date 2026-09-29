"""
Module 4 - Lab 4-2
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

import torch
import torch.nn.functional as F
import time

def scaled_dot_product_attention_manual(Q, K, V, mask=None):
    """
    Implement scaled dot-product attention from scratch.

    Args:
        Q: Query tensor of shape (B, n_heads, S_q, d_k)
        K: Key tensor of shape (B, n_heads, S_k, d_k)
        V: Value tensor of shape (B, n_heads, S_k, d_k)
        mask: Optional causal mask of shape (S_q, S_k)

    Returns:
        output: Attention output of shape (B, n_heads, S_q, d_k)
        attn_weights: Attention weights of shape (B, n_heads, S_q, S_k)
    """
    d_k = Q.shape[-1]

    # Step 1: Compute attention scores: QK^T / sqrt(d_k)
    # Q: (B, h, S_q, d_k), K^T: (B, h, d_k, S_k) -> scores: (B, h, S_q, S_k)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)

    # Step 2: Apply causal mask (set future positions to -inf)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # Step 3: Apply softmax along the key dimension
    attn_weights = F.softmax(scores, dim=-1)

    # Step 4: Weighted sum of values
    output = torch.matmul(attn_weights, V)

    return output, attn_weights


# Test with small dimensions
B, n_heads, S, d_k = 1, 4, 8, 64
Q = torch.randn(B, n_heads, S, d_k)
K = torch.randn(B, n_heads, S, d_k)
V = torch.randn(B, n_heads, S, d_k)

# Create causal mask
causal_mask = torch.tril(torch.ones(S, S)).unsqueeze(0).unsqueeze(0)

output_manual, weights_manual = scaled_dot_product_attention_manual(Q, K, V, causal_mask)

print("Scaled Dot-Product Attention (Manual Implementation)")
print(f"  Q shape:      {list(Q.shape)}")
print(f"  K shape:      {list(K.shape)}")
print(f"  V shape:      {list(V.shape)}")
print(f"  Output shape: {list(output_manual.shape)}")
print(f"  Weights shape:{list(weights_manual.shape)}")

# Verify: attention weights should sum to 1 along key dimension
row_sums = weights_manual.sum(dim=-1)
print(f"\n  Weight row sums (should be ~1.0): min={row_sums.min():.6f}, max={row_sums.max():.6f}")

# Verify: causal mask is working (no attention to future tokens)
print(f"  Weights[0,0] (lower triangular pattern):")
print(weights_manual[0, 0, :4, :4].detach().numpy().round(3))

# ============================================================
# Part B
# ============================================================

print("\n" + "=" * 60)
print("Comparison: Manual vs PyTorch SDPA")
print("=" * 60)

# PyTorch's scaled_dot_product_attention (uses FlashAttention when available)
output_pytorch = F.scaled_dot_product_attention(Q, K, V, is_causal=True)

# Compare outputs
diff = (output_manual - output_pytorch).abs().max().item()
print(f"\nMax absolute difference: {diff:.2e}")
print(f"Outputs match: {'YES' if diff < 1e-5 else 'NO (check implementation)'}")

# Larger test for timing comparison
B, n_heads, S, d_k = 1, 32, 2048, 128
Q = torch.randn(B, n_heads, S, d_k)
K = torch.randn(B, n_heads, S, d_k)
V = torch.randn(B, n_heads, S, d_k)
causal_mask = torch.tril(torch.ones(S, S)).unsqueeze(0).unsqueeze(0)

# Time manual implementation
start = time.perf_counter()
for _ in range(5):
    out_m, _ = scaled_dot_product_attention_manual(Q, K, V, causal_mask)
manual_time = (time.perf_counter() - start) / 5

# Time PyTorch implementation
start = time.perf_counter()
for _ in range(5):
    out_p = F.scaled_dot_product_attention(Q, K, V, is_causal=True)
pytorch_time = (time.perf_counter() - start) / 5

print(f"\nTiming (B=1, h=32, S=2048, d_k=128):")
print(f"  Manual:  {manual_time * 1000:.1f} ms")
print(f"  PyTorch: {pytorch_time * 1000:.1f} ms")
print(f"  Speedup: {manual_time / pytorch_time:.1f}x")

# ============================================================
# Part C
# ============================================================

import numpy as np
import matplotlib.pyplot as plt

print("\n" + "=" * 60)
print("Attention Memory Scaling Analysis")
print("=" * 60)

B = 1
n_heads = 32  # LLaMA 3 8B
d_k = 128

seq_lengths = [128, 256, 512, 1024, 2048, 4096, 8192, 16384]
attn_matrix_sizes_mb = []
qkv_sizes_mb = []
total_sizes_mb = []

bytes_per_elem = 2  # FP16

print(f"\n{'S':>8} {'Attn Matrix':>15} {'Q+K+V':>12} {'Total':>12} {'Scaling':>10}")
print("-" * 60)

for S in seq_lengths:
    # Attention score matrix: (B, n_heads, S, S) in FP16
    attn_bytes = B * n_heads * S * S * bytes_per_elem
    attn_mb = attn_bytes / (1024 ** 2)

    # Q, K, V tensors: each (B, n_heads, S, d_k)
    qkv_bytes = 3 * B * n_heads * S * d_k * bytes_per_elem
    qkv_mb = qkv_bytes / (1024 ** 2)

    total_mb = attn_mb + qkv_mb

    attn_matrix_sizes_mb.append(attn_mb)
    qkv_sizes_mb.append(qkv_mb)
    total_sizes_mb.append(total_mb)

    scaling = f"{S}x{S}" if S <= 1024 else f"{S/1024:.0f}Kx{S/1024:.0f}K"
    print(f"{S:>8} {attn_mb:>12.1f} MB {qkv_mb:>9.1f} MB {total_mb:>9.1f} MB {scaling:>10}")

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Memory breakdown
ax1.plot(seq_lengths, attn_matrix_sizes_mb, 'ro-', label='Attention matrix (O(S^2))', linewidth=2)
ax1.plot(seq_lengths, qkv_sizes_mb, 'bs-', label='Q+K+V tensors (O(S))', linewidth=2)
ax1.plot(seq_lengths, total_sizes_mb, 'g^-', label='Total', linewidth=2)
ax1.set_xlabel('Sequence Length')
ax1.set_ylabel('Memory (MB)')
ax1.set_title('Attention Memory vs Sequence Length\n(B=1, h=32, d_k=128)')
ax1.set_xscale('log', base=2)
ax1.set_yscale('log')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Right: Attention matrix as fraction of total
fractions = [a / t * 100 for a, t in zip(attn_matrix_sizes_mb, total_sizes_mb)]
ax2.bar([str(s) for s in seq_lengths], fractions, color='coral')
ax2.set_xlabel('Sequence Length')
ax2.set_ylabel('Attention Matrix as % of Total')
ax2.set_title('Attention Matrix Dominance')
ax2.set_ylim(0, 100)
ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5)
for i, (s, f) in enumerate(zip(seq_lengths, fractions)):
    ax2.text(i, f + 2, f'{f:.0f}%', ha='center', fontsize=8)
ax2.grid(True, axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('attention_memory_scaling.png', dpi=150)
plt.show()
print("\nPlot saved to attention_memory_scaling.png")
