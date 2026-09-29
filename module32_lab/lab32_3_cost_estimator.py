"""
Lab 32-3: End-to-End LLM Inference Cost Estimator
Analytical model for prefill vs. decode latency in LLaMA-7B.
"""

import numpy as np
import matplotlib.pyplot as plt

class LLaMAConfig:
    """LLaMA-7B architecture parameters."""
    def __init__(self):
        self.num_layers = 32
        self.hidden_dim = 4096
        self.num_heads = 32
        self.head_dim = 128
        self.intermediate_dim = 11008
        self.vocab_size = 32000
        self.dtype_bytes = 2  # FP16

    def total_params(self):
        """Approximate total parameter count."""
        per_layer = (
            4 * self.hidden_dim * self.hidden_dim +  # Q, K, V, O projections
            3 * self.hidden_dim * self.intermediate_dim +  # gate, up, down (SwiGLU)
            2 * self.hidden_dim  # two LayerNorms (weight + bias approx)
        )
        embedding = self.vocab_size * self.hidden_dim
        return self.num_layers * per_layer + 2 * embedding  # embed + lm_head

    def total_weight_bytes(self):
        return self.total_params() * self.dtype_bytes


class HardwareConfig:
    """Hardware specification."""
    def __init__(self, name, peak_flops, mem_bandwidth):
        self.name = name
        self.peak_flops = peak_flops        # FLOP/s
        self.mem_bandwidth = mem_bandwidth    # bytes/s


def estimate_prefill_latency(config, hw, prompt_len):
    """
    Estimate prefill latency for a given prompt length.

    In prefill, all tokens are processed in parallel. The dominant cost
    is the GEMM operations across all layers.

    For each layer, the main GEMMs are:
    - QKV projection: [prompt_len, hidden] x [hidden, 3*hidden]  (fused)
    - Attention: [prompt_len, head_dim] x [head_dim, prompt_len] per head
    - Output projection: [prompt_len, hidden] x [hidden, hidden]
    - FFN gate+up: [prompt_len, hidden] x [hidden, 2*intermediate]  (fused)
    - FFN down: [prompt_len, intermediate] x [intermediate, hidden]

    Returns:
        Estimated prefill latency in seconds
    """
    h = config.hidden_dim
    inter = config.intermediate_dim
    n_heads = config.num_heads
    head_d = config.head_dim
    L = config.num_layers
    S = prompt_len

    # FLOPs per layer
    flops_qkv = 2 * S * h * 3 * h         # QKV projection
    flops_attn_score = 2 * n_heads * S * S * head_d  # QK^T
    flops_attn_value = 2 * n_heads * S * S * head_d  # Attn * V
    flops_out_proj = 2 * S * h * h         # Output projection
    flops_ffn_up = 2 * S * h * 2 * inter   # Gate + Up (SwiGLU)
    flops_ffn_down = 2 * S * inter * h     # Down projection

    flops_per_layer = (flops_qkv + flops_attn_score + flops_attn_value +
                       flops_out_proj + flops_ffn_up + flops_ffn_down)

    total_flops = L * flops_per_layer

    # Prefill is compute-bound for reasonable sequence lengths
    # Latency = max(compute_time, memory_time)
    compute_time = total_flops / hw.peak_flops

    # Memory: need to load all weights once
    weight_bytes = config.total_weight_bytes()
    memory_time = weight_bytes / hw.mem_bandwidth

    # Prefill latency is the larger of compute time and memory load time
    latency = max(compute_time, memory_time)

    return latency, total_flops, compute_time, memory_time


def estimate_decode_latency_per_token(config, hw, context_len):
    """
    Estimate per-token decode latency.

    In decode, we process one token at a time. All GEMMs become
    matrix-vector multiplications (M=1), making them memory-bound.

    The dominant cost is loading model weights from memory for each token.

    Returns:
        Estimated per-token decode latency in seconds
    """
    h = config.hidden_dim
    inter = config.intermediate_dim
    n_heads = config.num_heads
    head_d = config.head_dim
    L = config.num_layers

    # FLOPs per layer (M=1 for all linear layers)
    flops_qkv = 2 * 1 * h * 3 * h
    flops_attn_score = 2 * n_heads * 1 * context_len * head_d  # Against full KV cache
    flops_attn_value = 2 * n_heads * 1 * context_len * head_d
    flops_out_proj = 2 * 1 * h * h
    flops_ffn_up = 2 * 1 * h * 2 * inter
    flops_ffn_down = 2 * 1 * inter * h

    flops_per_layer = (flops_qkv + flops_attn_score + flops_attn_value +
                       flops_out_proj + flops_ffn_up + flops_ffn_down)

    total_flops = L * flops_per_layer

    compute_time = total_flops / hw.peak_flops

    # Memory: must reload all weights for each token
    weight_bytes = config.total_weight_bytes()
    # Also read KV cache: 2 * num_layers * context_len * hidden_dim * dtype_bytes
    kv_cache_bytes = 2 * L * context_len * h * config.dtype_bytes
    total_memory = weight_bytes + kv_cache_bytes
    memory_time = total_memory / hw.mem_bandwidth

    # Decode is memory-bound: memory_time >> compute_time
    latency = max(compute_time, memory_time)

    return latency, total_flops, compute_time, memory_time


# --- Instantiate ---
llama = LLaMAConfig()
print(f"LLaMA-7B parameters: {llama.total_params() / 1e9:.2f} B")
print(f"Weight size (FP16):  {llama.total_weight_bytes() / 1e9:.2f} GB")
