"""
Lab 32-2: Arithmetic Intensity Calculator & Roofline Diagram
Computes arithmetic intensity for each transformer operator type.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- Hardware specs ---
class HardwareSpec:
    """Hardware specification for roofline analysis."""
    def __init__(self, name, peak_flops, mem_bandwidth):
        self.name = name
        self.peak_flops = peak_flops        # FLOP/s
        self.mem_bandwidth = mem_bandwidth    # bytes/s
        self.ridge_point = peak_flops / mem_bandwidth  # FLOP/byte

    def __repr__(self):
        return (f"{self.name}: {self.peak_flops/1e12:.0f} TFLOP/s, "
                f"{self.mem_bandwidth/1e9:.0f} GB/s, "
                f"ridge={self.ridge_point:.1f} FLOP/byte")

# Define hardware targets
a100 = HardwareSpec("A100 (FP16 Tensor Core)", 312e12, 2039e9)
hypothetical_asic = HardwareSpec("Hypothetical ASIC", 500e12, 4000e9)

print(a100)
print(hypothetical_asic)


# --- Arithmetic Intensity Functions ---

def gemm_arithmetic_intensity(M, N, K, dtype_bytes=2):
    """
    Compute arithmetic intensity for GEMM: C[M,N] = A[M,K] * B[K,N].

    FLOPs: 2 * M * N * K  (multiply + accumulate)
    Bytes: (A + B + C) * dtype_bytes = (M*K + K*N + M*N) * dtype_bytes

    Args:
        M, N, K: Matrix dimensions
        dtype_bytes: Bytes per element (2 for FP16, 4 for FP32)

    Returns:
        Arithmetic intensity in FLOP/byte
    """
    flops = 2 * M * N * K
    bytes_accessed = (M * K + K * N + M * N) * dtype_bytes
    return flops / bytes_accessed


def softmax_arithmetic_intensity(seq_len, num_heads, dtype_bytes=2):
    """
    Compute arithmetic intensity for softmax over attention scores.

    For each head: input is [seq_len, seq_len] (or [1, seq_len] in decode).
    FLOPs per element: ~5 (exp, sum, divide, subtract max, compare)
    Bytes: read input + write output = 2 * elements * dtype_bytes

    Args:
        seq_len: Sequence length (rows of attention matrix)
        num_heads: Number of attention heads
        dtype_bytes: Bytes per element

    Returns:
        Arithmetic intensity in FLOP/byte
    """
    elements = num_heads * seq_len * seq_len
    flops = 5 * elements  # exp, sub, div, max, sum (approximate)
    bytes_accessed = 2 * elements * dtype_bytes  # read + write
    return flops / bytes_accessed


def layernorm_arithmetic_intensity(seq_len, hidden_dim, dtype_bytes=2):
    """
    Compute arithmetic intensity for LayerNorm.

    Per token: compute mean (H adds), variance (H adds + H muls),
               normalize (H muls + H adds), affine (H muls + H adds).
    FLOPs: ~5 * seq_len * hidden_dim
    Bytes: read input + read gamma/beta + write output

    Args:
        seq_len: Number of tokens
        hidden_dim: Hidden dimension
        dtype_bytes: Bytes per element

    Returns:
        Arithmetic intensity in FLOP/byte
    """
    flops = 5 * seq_len * hidden_dim
    # Read input, write output, read gamma + beta (shared across tokens)
    bytes_accessed = (2 * seq_len * hidden_dim + 2 * hidden_dim) * dtype_bytes
    return flops / bytes_accessed


def elementwise_arithmetic_intensity(num_elements, ops_per_element=1,
                                      dtype_bytes=2):
    """
    Compute arithmetic intensity for element-wise ops (GELU, residual add).

    Args:
        num_elements: Total elements processed
        ops_per_element: FLOPs per element (1 for add, ~10 for GELU approx)
        dtype_bytes: Bytes per element

    Returns:
        Arithmetic intensity in FLOP/byte
    """
    flops = ops_per_element * num_elements
    bytes_accessed = 2 * num_elements * dtype_bytes  # read + write
    return flops / bytes_accessed
