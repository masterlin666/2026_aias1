"""
Module 4 - Lab 4-4
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

import numpy as np
import matplotlib.pyplot as plt

class LLMAnalyticalModel:
    """
    Analytical performance model for decoder-only LLM inference.
    Computes FLOPs, memory access, and arithmetic intensity for
    each operation in a single decoder layer.
    """

    def __init__(self, d_model, n_heads, n_kv_heads, d_ff, n_layers,
                 vocab_size, bytes_per_param=2):
        self.d = d_model
        self.n_h = n_heads
        self.n_kv = n_kv_heads
        self.d_k = d_model // n_heads
        self.d_kv = n_kv_heads * (d_model // n_heads)  # total KV dim
        self.d_ff = d_ff
        self.n_layers = n_layers
        self.vocab = vocab_size
        self.bpe = bytes_per_param  # bytes per element

    def analyze_prefill(self, batch_size, seq_len):
        """Analyze prefill phase: process seq_len tokens in parallel."""
        B, S = batch_size, seq_len
        d, d_kv, d_ff = self.d, self.d_kv, self.d_ff
        bpe = self.bpe
        results = {}

        # Q projection: (B*S, d) x (d, d) -> (B*S, d)
        results["Q_proj"] = {
            "flops": 2 * B * S * d * d,
            "weight_bytes": d * d * bpe,
            "act_in_bytes": B * S * d * bpe,
            "act_out_bytes": B * S * d * bpe,
        }

        # K projection: (B*S, d) x (d, d_kv) -> (B*S, d_kv)
        results["K_proj"] = {
            "flops": 2 * B * S * d * d_kv,
            "weight_bytes": d * d_kv * bpe,
            "act_in_bytes": B * S * d * bpe,
            "act_out_bytes": B * S * d_kv * bpe,
        }

        # V projection: same as K
        results["V_proj"] = {
            "flops": 2 * B * S * d * d_kv,
            "weight_bytes": d * d_kv * bpe,
            "act_in_bytes": B * S * d * bpe,
            "act_out_bytes": B * S * d_kv * bpe,
        }

        # QK^T: per head (B, S, d_k) x (B, d_k, S) -> (B, S, S), all heads
        results["QKT"] = {
            "flops": 2 * B * self.n_h * S * S * self.d_k,
            "weight_bytes": 0,
            "act_in_bytes": (B * self.n_h * S * self.d_k + B * self.n_kv * S * self.d_k) * bpe,
            "act_out_bytes": B * self.n_h * S * S * bpe,
        }

        # Softmax: ~5 ops per element
        results["Softmax"] = {
            "flops": 5 * B * self.n_h * S * S,
            "weight_bytes": 0,
            "act_in_bytes": B * self.n_h * S * S * bpe,
            "act_out_bytes": B * self.n_h * S * S * bpe,
        }

        # SV: (B, h, S, S) x (B, h, S, d_k) -> (B, h, S, d_k)
        results["SV"] = {
            "flops": 2 * B * self.n_h * S * S * self.d_k,
            "weight_bytes": 0,
            "act_in_bytes": (B * self.n_h * S * S + B * self.n_kv * S * self.d_k) * bpe,
            "act_out_bytes": B * self.n_h * S * self.d_k * bpe,
        }

        # Output projection: (B*S, d) x (d, d) -> (B*S, d)
        results["O_proj"] = {
            "flops": 2 * B * S * d * d,
            "weight_bytes": d * d * bpe,
            "act_in_bytes": B * S * d * bpe,
            "act_out_bytes": B * S * d * bpe,
        }

        # SwiGLU MLP: gate_proj, up_proj, down_proj
        results["Gate_proj"] = {
            "flops": 2 * B * S * d * d_ff,
            "weight_bytes": d * d_ff * bpe,
            "act_in_bytes": B * S * d * bpe,
            "act_out_bytes": B * S * d_ff * bpe,
        }
        results["Up_proj"] = {
            "flops": 2 * B * S * d * d_ff,
            "weight_bytes": d * d_ff * bpe,
            "act_in_bytes": B * S * d * bpe,
            "act_out_bytes": B * S * d_ff * bpe,
        }
        results["Down_proj"] = {
            "flops": 2 * B * S * d_ff * d,
            "weight_bytes": d_ff * d * bpe,
            "act_in_bytes": B * S * d_ff * bpe,
            "act_out_bytes": B * S * d * bpe,
        }

        # Compute OI for each operation
        for name, r in results.items():
            r["total_bytes"] = r["weight_bytes"] + r["act_in_bytes"] + r["act_out_bytes"]
            r["oi"] = r["flops"] / r["total_bytes"] if r["total_bytes"] > 0 else 0

        return results

    def analyze_decode(self, batch_size, context_len):
        """Analyze decode phase: generate 1 token with context_len cached tokens."""
        B, C = batch_size, context_len
        S = 1  # processing 1 new token
        d, d_kv, d_ff = self.d, self.d_kv, self.d_ff
        bpe = self.bpe
        results = {}

        # Q projection: (B, 1, d) x (d, d) -> (B, 1, d)
        results["Q_proj"] = {
            "flops": 2 * B * d * d,
            "weight_bytes": d * d * bpe,
            "act_in_bytes": B * d * bpe,
            "act_out_bytes": B * d * bpe,
        }

        # K projection: (B, 1, d) x (d, d_kv) -> (B, 1, d_kv)
        results["K_proj"] = {
            "flops": 2 * B * d * d_kv,
            "weight_bytes": d * d_kv * bpe,
            "act_in_bytes": B * d * bpe,
            "act_out_bytes": B * d_kv * bpe,
        }

        # V projection
        results["V_proj"] = {
            "flops": 2 * B * d * d_kv,
            "weight_bytes": d * d_kv * bpe,
            "act_in_bytes": B * d * bpe,
            "act_out_bytes": B * d_kv * bpe,
        }

        # QK^T: (B, h, 1, d_k) x (B, h, d_k, C+1) -> (B, h, 1, C+1)
        # Must read entire KV-cache
        results["QKT"] = {
            "flops": 2 * B * self.n_h * (C + 1) * self.d_k,
            "weight_bytes": 0,
            "act_in_bytes": (B * self.n_h * self.d_k + B * self.n_kv * (C + 1) * self.d_k) * bpe,
            "act_out_bytes": B * self.n_h * (C + 1) * bpe,
        }

        # Softmax
        results["Softmax"] = {
            "flops": 5 * B * self.n_h * (C + 1),
            "weight_bytes": 0,
            "act_in_bytes": B * self.n_h * (C + 1) * bpe,
            "act_out_bytes": B * self.n_h * (C + 1) * bpe,
        }

        # SV: (B, h, 1, C+1) x (B, h, C+1, d_k) -> (B, h, 1, d_k)
        results["SV"] = {
            "flops": 2 * B * self.n_h * (C + 1) * self.d_k,
            "weight_bytes": 0,
            "act_in_bytes": (B * self.n_h * (C + 1) + B * self.n_kv * (C + 1) * self.d_k) * bpe,
            "act_out_bytes": B * self.n_h * self.d_k * bpe,
        }

        # Output projection
        results["O_proj"] = {
            "flops": 2 * B * d * d,
            "weight_bytes": d * d * bpe,
            "act_in_bytes": B * d * bpe,
            "act_out_bytes": B * d * bpe,
        }

        # SwiGLU MLP
        results["Gate_proj"] = {
            "flops": 2 * B * d * d_ff,
            "weight_bytes": d * d_ff * bpe,
            "act_in_bytes": B * d * bpe,
            "act_out_bytes": B * d_ff * bpe,
        }
        results["Up_proj"] = {
            "flops": 2 * B * d * d_ff,
            "weight_bytes": d * d_ff * bpe,
            "act_in_bytes": B * d * bpe,
            "act_out_bytes": B * d_ff * bpe,
        }
        results["Down_proj"] = {
            "flops": 2 * B * d_ff * d,
            "weight_bytes": d_ff * d * bpe,
            "act_in_bytes": B * d_ff * bpe,
            "act_out_bytes": B * d * bpe,
        }

        for name, r in results.items():
            r["total_bytes"] = r["weight_bytes"] + r["act_in_bytes"] + r["act_out_bytes"]
            r["oi"] = r["flops"] / r["total_bytes"] if r["total_bytes"] > 0 else 0

        return results

    def print_analysis(self, results, title=""):
        """Print formatted analysis table."""
        print(f"\n{'=' * 90}")
        print(f"  {title}")
        print(f"{'=' * 90}")
        print(f"{'Operation':<14} {'FLOPs':>14} {'Weights(B)':>12} {'TotalMem(B)':>13} {'OI(F/B)':>10} {'Bound':>10}")
        print("-" * 90)

        total_flops = 0
        total_bytes = 0

        for name, r in results.items():
            bound = "COMPUTE" if r["oi"] >= 100 else ("MEMORY" if r["oi"] < 10 else "MIXED")
            print(f"{name:<14} {r['flops']:>14,} {r['weight_bytes']:>12,} {r['total_bytes']:>13,} {r['oi']:>10.1f} {bound:>10}")
            total_flops += r["flops"]
            total_bytes += r["total_bytes"]

        print("-" * 90)
        print(f"{'LAYER TOTAL':<14} {total_flops:>14,} {'':>12} {total_bytes:>13,}")
        print(f"\n  Full model ({self.n_layers} layers):")
        print(f"    Total FLOPs:  {total_flops * self.n_layers:,.0f} ({total_flops * self.n_layers / 1e9:.2f} GFLOPS)")

        return total_flops, total_bytes


# --- Run the analysis for LLaMA-7B ---
llama7b = LLMAnalyticalModel(
    d_model=4096,
    n_heads=32,
    n_kv_heads=32,     # LLaMA-7B uses MHA (n_kv = n_h)
    d_ff=11008,
    n_layers=32,
    vocab_size=32000,
    bytes_per_param=2   # FP16
)

# Prefill analysis
prefill = llama7b.analyze_prefill(batch_size=1, seq_len=512)
pf_flops, pf_bytes = llama7b.print_analysis(prefill, "LLaMA-7B Prefill (B=1, S=512)")

# Decode analysis
decode = llama7b.analyze_decode(batch_size=1, context_len=512)
dc_flops, dc_bytes = llama7b.print_analysis(decode, "LLaMA-7B Decode (B=1, C=512)")

print(f"\n{'=' * 60}")
print(f"PREFILL vs DECODE Comparison:")
print(f"  Prefill FLOPs/token: {pf_flops / 512:,.0f}")
print(f"  Decode FLOPs/token:  {dc_flops:,.0f}")
print(f"  Ratio: Prefill has {pf_flops / 512 / dc_flops:.1f}x more FLOPs per token")
print(f"  But decode is {'memory' if True else 'compute'}-bound (OI ~ 1)")

# ============================================================
# Part B
# ============================================================

print("\n" + "=" * 60)
print("Batch Size and Sequence Length Sweep")
print("=" * 60)

batch_sizes = [1, 4, 16, 64, 256]
seq_lengths = [128, 512, 2048, 8192]

# Compute average OI for linear projections during decode
print(f"\n{'B':>6} {'C':>8} {'Q_proj OI':>12} {'Gate OI':>12} {'QKT OI':>12} {'Avg OI':>12}")
print("-" * 65)

oi_data = []

for B in batch_sizes:
    for C in seq_lengths:
        decode = llama7b.analyze_decode(batch_size=B, context_len=C)
        q_oi = decode["Q_proj"]["oi"]
        gate_oi = decode["Gate_proj"]["oi"]
        qkt_oi = decode["QKT"]["oi"]

        # Weighted average OI (by FLOPs)
        total_flops = sum(r["flops"] for r in decode.values())
        weighted_oi = sum(r["flops"] * r["oi"] for r in decode.values()) / total_flops

        oi_data.append((B, C, q_oi, gate_oi, qkt_oi, weighted_oi))
        print(f"{B:>6} {C:>8} {q_oi:>12.2f} {gate_oi:>12.2f} {qkt_oi:>12.2f} {weighted_oi:>12.2f}")

# Plot: Decode OI vs Batch Size for Q_proj (representative linear layer)
fig, ax = plt.subplots(figsize=(10, 6))

for C in seq_lengths:
    bs_list = []
    oi_list = []
    for B, c, q_oi, _, _, _ in oi_data:
        if c == C:
            bs_list.append(B)
            oi_list.append(q_oi)
    ax.plot(bs_list, oi_list, 'o-', label=f'C={C}', linewidth=2)

# Hardware ridge points
ax.axhline(y=295, color='red', linestyle='--', alpha=0.5, label='H100 ridge (295 F/B)')
ax.axhline(y=156, color='orange', linestyle='--', alpha=0.5, label='A100 ridge (156 F/B)')

ax.set_xlabel('Batch Size', fontsize=12)
ax.set_ylabel('Operational Intensity (FLOP/Byte)', fontsize=12)
ax.set_title('Decode OI vs Batch Size (Q Projection)\nLLaMA-7B, FP16', fontsize=13)
ax.set_xscale('log', base=2)
ax.set_yscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('decode_oi_vs_batch.png', dpi=150)
plt.show()
print("\nPlot saved to decode_oi_vs_batch.png")
