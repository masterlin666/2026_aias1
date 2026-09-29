import pandas as pd

def estimate_llm_performance(config, workload, model_params=7e9):
    """
    簡單的 LLM 效能估算模型 (以 7B 模型為例)
    model_params: 參數數量 (預設 70 億)
    """
    TFLOPS = config['TFLOPS'] * 1e12
    BW = config['BW'] * 1e9
    prompt_len = workload['prompt']
    gen_len = workload['gen']
    
    # 1. Prefill 階段 (通常是 Compute-bound)
    # 運算量估算: 2 * params * prompt_len
    prefill_flops = 2 * model_params * prompt_len
    t_prefill_compute = prefill_flops / TFLOPS
    t_prefill_mem = (model_params * 2) / BW  # 假設 FP16 權重讀取一次
    t_prefill = max(t_prefill_compute, t_prefill_mem)
    
    # 2. Decode 階段 (通常是 Memory-bound)
    # 每一顆 Token 都需要讀取一次完整的 Model Weights
    # Decode Throughput (tokens/s) = BW / (2 * model_params)
    decode_throughput = BW / (model_params * 2) 
    t_decode = gen_len / decode_throughput
    
    return {
        "TTFT (s)": round(t_prefill, 4),
        "Decode TPS": round(decode_throughput, 2),
        "Total Latency (s)": round(t_prefill + t_decode, 2),
        "Bottleneck": "Compute" if t_prefill_compute > t_prefill_mem else "Memory"
    }

# 硬體配置 (來自 32-3-1)
configs = {
    "A (Max Compute)": {"TFLOPS": 800, "BW": 1200},
    "B (Max BW)":      {"TFLOPS": 200, "BW": 4800},
    "E (Optimized)":   {"TFLOPS": 500, "BW": 1600}
}

# 測試 Workload
workloads = {
    "Chatbot": {"prompt": 128, "gen": 512},
    "Summarization": {"prompt": 4096, "gen": 128}
}

# 執行評估
for cw_name, workload in workloads.items():
    print(f"--- Workload: {cw_name} ---")
    for cfg_name, cfg in configs.items():
        res = estimate_llm_performance(cfg, workload)
        print(f"{cfg_name}: {res}")