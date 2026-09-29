import pandas as pd

def calculate_hw4_1_1():
    # LLaMA-7B Config
    B = 1
    S_prefill = 512
    C_decode = 512
    d_model = 4096
    n_h = 32
    d_k = 128
    d_kv = n_h * d_k # MHA: 4096
    bpe = 2
    ridge_point = 295

    def get_row(name, flops, w_mem, act_mem):
        total_mem = w_mem + act_mem
        oi = flops / total_mem if total_mem > 0 else 0
        bound = "COMPUTE" if oi >= ridge_point else "MEMORY"
        return {
            "Operation": name,
            "FLOPs": int(flops),
            "Weight Mem (B)": int(w_mem),
            "Act Mem (B)": int(act_mem),
            "Total Mem (B)": int(total_mem),
            "OI (F/B)": round(oi, 2),
            "Bound": bound
        }

    def analyze_phase(S, S_kv, phase_name):
        rows = []
        
        # Q/K/V Projections (Linear layers)
        # FLOPs = 2 * B * S * d_in * d_out
        # Weight = d_in * d_out * bpe
        # Act = (B*S*d_in + B*S*d_out) * bpe
        rows.append(get_row("Q projection", 2*B*S*d_model*d_model, d_model*d_model*bpe, (B*S*d_model + B*S*d_model)*bpe))
        rows.append(get_row("K projection", 2*B*S*d_model*d_kv, d_model*d_kv*bpe, (B*S*d_model + B*S*d_kv)*bpe))
        rows.append(get_row("V projection", 2*B*S*d_model*d_kv, d_model*d_kv*bpe, (B*S*d_model + B*S*d_kv)*bpe))

        # QK^T: (B, h, S, d_k) @ (B, h, d_k, S_kv) -> (B, h, S, S_kv)
        # FLOPs = 2 * B * h * S * S_kv * d_k
        # Act = (Q_act + K_cache_act + Score_matrix_act) * bpe
        qkt_flops = 2 * B * n_h * S * S_kv * d_k
        qkt_act = (B*n_h*S*d_k + B*n_h*S_kv*d_k + B*n_h*S*S_kv) * bpe
        rows.append(get_row("QK^T (all heads)", qkt_flops, 0, qkt_act))

        # SV: (B, h, S, S_kv) @ (B, h, S_kv, d_k) -> (B, h, S, d_k)
        # FLOPs = 2 * B * h * S * S_kv * d_k
        # Act = (Score_matrix_act + V_cache_act + Out_act) * bpe
        sv_flops = 2 * B * n_h * S * S_kv * d_k
        sv_act = (B*n_h*S*S_kv + B*n_h*S_kv*d_k + B*n_h*S*d_k) * bpe
        rows.append(get_row("SV (all heads)", sv_flops, 0, sv_act))

        # Output projection: (B,S,d) x (d,d)
        rows.append(get_row("O projection", 2*B*S*d_model*d_model, d_model*d_model*bpe, (B*S*d_model + B*S*d_model)*bpe))

        df = pd.DataFrame(rows)
        total_flops = df["FLOPs"].sum()
        total_weight = df["Weight Mem (B)"].sum()
        
        print(f"\n--- {phase_name} Phase (B={B}, S={S}, S_kv={S_kv}) ---")
        print(df.to_string(index=False))
        print(f"Attention Total FLOPs: {total_flops:,}")
        print(f"Attention Total Weight Mem: {total_weight:,} B")
        return df

    analyze_phase(S_prefill, S_prefill, "Prefill")
    analyze_phase(1, C_decode + 1, "Decode") # C+1 because we add the new token to cache

if __name__ == "__main__":
    calculate_hw4_1_1()