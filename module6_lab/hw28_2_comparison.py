import pandas as pd

# 1. 填入你實驗中觀察到的數值 (根據你提供的 BERT-base 數據)
data = {
    "Metric": [
        "Trainable parameters",
        "Training time (seconds)",
        "Peak GPU memory (MB)",
        "Final accuracy",
        "Model checkpoint size (MB)"
    ],
    "Full Finetuning": [
        109483778,  # 全參數數量
        33.81,      # Full FT 耗時
        2537.36,    # Full FT 顯存
        0.80,       # Full FT 準確度
        418.0       # BERT 權重大小
    ],
    "LoRA (r=16)": [
        591362,     # LoRA (r=16) 參數數量
        25.00,      # LoRA 耗時
        2150.00,    # LoRA 顯存
        0.58,       # LoRA 準確度
        2.3         # Adapter 大小
    ]
}

# 2. 建立 DataFrame
df = pd.DataFrame(data)

# 3. 計算比率 (Ratio) - 這裡以 Full/LoRA 為基準
# 為了易讀性，我們將數值格式化
def calculate_ratio(row):
    full = row["Full Finetuning"]
    lora = row["LoRA (r=16)"]
    if lora == 0: return "N/A"
    return f"{full / lora:.2f}x"

df["Ratio (Full/LoRA)"] = df.apply(calculate_ratio, axis=1)

# 4. 輸出美化後的表格
print("="*60)
print("HW 6-2: Full Finetuning vs LoRA Comparison Table")
print("="*60)
print(df.to_string(index=False))
print("="*60)

# 額外計算：顯存節省百分比
mem_saved = (1 - (data["LoRA (r=16)"][2] / data["Full Finetuning"][2])) * 100
print(f"Memory Savings: {mem_saved:.2f}%")

# 額外計算：參數壓縮率
param_compression = data["Full Finetuning"][0] / data["LoRA (r=16)"][0]
print(f"Parameter Reduction: {param_compression:.1f}x smaller")