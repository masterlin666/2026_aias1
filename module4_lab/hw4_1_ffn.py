import pandas as pd

def calculate_hw4_1_2():
    # LLaMA-7B Hyperparameters
    d_model = 4096
    d_ff = 11008
    n_layers = 32
    bpe = 2 # FP16
    ridge_point = 295 # H100
    
    # Pre-calculated Attention totals from HW 4-1-1
    # Prefill (S=512): Q, K, V, O projections + QK^T + SV
    attn_prefill_flops = (2*512*d_model*d_model*2) + (2*512*d_model*d_model*2) + (2*32*512*512*128*2)
    # Decode (S=1, C=512): Q, K, V, O projections + QK^T + SV (S_kv = 513)
    attn_decode_flops = (2*1*d_model*d_model*2) + (2*1*d_model*d_model*2) + (2*32*1*513*128*2)

    def get_row(name, flops, w_mem, act_mem):
        total_mem = w_mem + act_mem
        oi = flops / total_mem if total_mem > 0 else 0
        bound = "COMPUTE" if oi >= ridge_point else "MEMORY"
        return {
            "Operation": name,
            "FLOPs": int(flops),
            "Weight Mem (B)": int(w_mem),
            "Total Mem (B)": int(total_mem),
            "OI (F/B)": round(oi, 2),
            "Bound": bound
        }

    def analyze_mlp(B, S, phase_name):
        rows = []
        # gate_proj & up_proj: (B, S, d) @ (d, d_ff)
        rows.append(get_row("gate_proj", 2*B*S*d_model*d_ff, d_model*d_ff*bpe, (B*S*d_model + B*S*d_ff)*bpe))
        rows.append(get_row("up_proj",   2*B*S*d_model*d_ff, d_model*d_ff*bpe, (B*S*d_model + B*S*d_ff)*bpe))
        # down_proj: (B, S, d_ff) @ (d_ff, d)
        rows.append(get_row("down_proj", 2*B*S*d_ff*d_model, d_ff*d_model*bpe, (B*S*d_ff + B*S*d_model)*bpe))
        
        df = pd.DataFrame(rows)
        print(f"\n**{phase_name} Phase (B={B}, S={S})**\n")
        # Format for Markdown
        print(df.to_markdown(index=False, tablefmt="github"))
        
        mlp_total_flops = df["FLOPs"].sum()
        mlp_total_weight = df["Weight Mem (B)"].sum()
        print(f"\n| **MLP Total** | {mlp_total_flops:,} | {mlp_total_weight:,} | | |")
        return mlp_total_flops, mlp_total_weight

    # Run MLP Analysis
    pf_mlp_flops, pf_mlp_weight = analyze_mlp(1, 512, "Prefill")
    dc_mlp_flops, dc_mlp_weight = analyze_mlp(1, 1, "Decode")

    # Full Layer Metrics
    pf_layer_total = attn_prefill_flops + pf_mlp_flops
    dc_layer_total = attn_decode_flops + dc_mlp_flops
    
    # Full Model Weight (Approx including Embeddings: Vocab 32000 * d_model * bpe)
    total_model_weight = (pf_mlp_weight + (4 * d_model * d_model * bpe)) * n_layers + (32000 * d_model * bpe)

    print(f"\n### Full Layer and Model Totals:\n")
    totals_data = [
        ["Attention FLOPs (per layer)", f"{attn_prefill_flops:,}", f"{attn_decode_flops:,}"],
        ["MLP FLOPs (per layer)", f"{pf_mlp_flops:,}", f"{dc_mlp_flops:,}"],
        ["Layer total FLOPs", f"{pf_layer_total:,}", f"{dc_layer_total:,}"],
        ["Attention / MLP ratio", f"{attn_prefill_flops/pf_mlp_flops:.4f}", f"{attn_decode_flops/dc_mlp_flops:.4f}"],
        ["Full model FLOPs (32 layers)", f"{pf_layer_total * n_layers:,}", f"{dc_layer_total * n_layers:,}"],
        ["Full model weight memory", f"{total_model_weight / 1e9:.2f} GB", f"{total_model_weight / 1e9:.2f} GB"]
    ]
    totals_df = pd.DataFrame(totals_data, columns=["Metric", "Prefill (S=512)", "Decode (S=1)"])
    print(totals_df.to_markdown(index=False, tablefmt="github"))

    
if __name__ == "__main__":
    calculate_hw4_1_2()
    print("The MLP dominates the FLOPs because it performs dense matrix multiplications on every token regardless of context length.For LLaMA-7B, d_ff (11008) is nearly 2.7x larger than d_model (4096), and SwiGLU adds a 3rd projection matrix.In contrast, Attention FLOPs only grow significantly when sequence length S is very large (O(S^2)).")