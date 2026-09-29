import pandas as pd

def calculate_hardware_specs():
    # --- 模型架構參數 (LLaMA 3 8B 真實規格) ---
    L = 32
    d_model = 4096
    n_kv = 8
    d_head = 128
    d_ff = 14336
    vocab_size = 128256  # 包含 Embedding 層以精確對齊 16GB
    
    # --- 工作負載參數 ---
    num_users = 100
    p_len = 512
    max_ctx = 768
    target_tp_per_user = 50 
    target_ttft_s = 0.5
    
    # --- 1. 精確參數計算 (Total Parameters) ---
    attn_params = (d_model**2) + 2*(d_model * n_kv * d_head) + (d_model**2)
    mlp_params = 3 * (d_model * d_ff)
    core_params = (attn_params + mlp_params) * L
    ext_params = 2 * (vocab_size * d_model) # Embedding + LM Head
    total_params = core_params + ext_params
    
    # 單位轉換：10^9 (Standard GB)
    gb_unit = 1e9 
    w_fp16 = (total_params * 2) / gb_unit
    w_int8 = w_fp16 / 2
    w_int4 = w_fp16 / 4
    
    # --- 2. Decode 頻寬 ---
    bw_fp16 = w_fp16 * target_tp_per_user
    bw_int8 = w_int8 * target_tp_per_user
    bw_int4 = w_int4 * target_tp_per_user
    
    # --- 3. Compute (TFLOPS) ---
    flops_per_token = 2 * total_params
    decode_tflops = (flops_per_token * (num_users * target_tp_per_user)) / 1e12
    
    # --- 4. Prefill ---
    prefill_flops = flops_per_token * p_len * L / L # 每層都算，這裡是 512 tokens 的總量
    # 注意：作業要求 512 tokens, 32 layers 的總 FLOPs
    total_prefill_flops = flops_per_token * p_len 
    required_prefill_tflops = (total_prefill_flops * num_users / target_ttft_s) / 1e12
    # 最小頻寬 (避免 Prefill 變成 Memory-bound): Weight / TTFT_limit
    min_prefill_bw = w_fp16 / target_ttft_s

    # --- 5. KV-Cache ---
    kv_bytes_per_token = L * 2 * n_kv * d_head * 2
    kv_per_user_gb = (kv_bytes_per_token * max_ctx) / 1e9
    total_kv_gb = kv_per_user_gb * num_users
    total_mem_fp16 = w_fp16 + total_kv_gb

    # --- 輸出格式化表格 ---
    print("\n" + "="*50)
    print("HW 4-3-1: Hardware Requirements Report")
    print("="*50)
    
    print("\n[Decode Requirements]")
    decode_df = pd.DataFrame({
        "Metric": ["Model weight size", "BW for 50 tok/s (B=1)", "BW for 5000 tok/s (B=100)"],
        "FP16": [f"{w_fp16:.1f} GB", f"{bw_fp16:.0f} GB/s", f"{bw_fp16:.0f} GB/s"],
        "INT8": [f"{w_int8:.1f} GB", f"{bw_int8:.0f} GB/s", f"{bw_int8:.0f} GB/s"],
        "INT4": [f"{w_int4:.1f} GB", f"{bw_int4:.0f} GB/s", f"{bw_int4:.0f} GB/s"]
    })
    print(decode_df.to_markdown(index=False))
    print(f"Decode FLOPs/token (B=100): {flops_per_token/1e9:.2f} GFLOPS")
    print(f"Required compute: {decode_tflops:.1f} TFLOPS")

    print("\n[Prefill Requirements]")
    prefill_data = [
        ["Prefill FLOPs (512 tokens, 32 layers)", f"{total_prefill_flops/1e12:.3f} TFLOPs"],
        ["Required compute for TTFT < 500 ms", f"{required_prefill_tflops:.1f} TFLOPS"],
        ["Minimum bandwidth (to avoid memory-bound)", f"{min_prefill_bw:.1f} GB/s"]
    ]
    print(pd.DataFrame(prefill_data, columns=["Metric", "Value"]).to_markdown(index=False))

    print("\n[KV-Cache Requirements]")
    kv_data = [
        ["KV-cache per user (768 tokens)", f"{kv_per_user_gb:.4f} GB"],
        ["Total KV-cache (100 users)", f"{total_kv_gb:.2f} GB"],
        ["Total memory (weights + cache, FP16)", f"{total_mem_fp16:.2f} GB"]
    ]
    print(pd.DataFrame(kv_data, columns=["Metric", "Value"]).to_markdown(index=False))

if __name__ == "__main__":
    calculate_hardware_specs()