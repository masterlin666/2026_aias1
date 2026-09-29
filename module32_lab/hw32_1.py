import torch
import torch.nn as nn
import time
import pandas as pd
import matplotlib.pyplot as plt
from transformers import GPT2Model, GPT2Config
from transformers.pytorch_utils import Conv1D

# 1. 環境設定
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PRECISION_BYTES = 4 
PEAK_TFLOPS = 8.1   
MEM_BW_GBs = 300    
RIDGE_POINT = (PEAK_TFLOPS * 1e12) / (MEM_BW_GBs * 1e9)

print(f"Using device: {DEVICE}")

# 2. 修正後的 Profiling Hook (不再觸發遞迴)
def profile_op(module, input, output, name):
    in_tensor = input[0]
    # 取得維度
    B, L, D = in_tensor.shape
    H = output.shape[-1]
    
    # 計算 FLOPs 與 Bytes
    flops = 2 * B * L * D * H
    # Read (X, W) + Write (Y)
    total_bytes = (B*L*D + D*H + B*L*H) * PRECISION_BYTES
    ai = flops / total_bytes
    
    # 由於我們無法在 hook 內精確測量單個 Op 的 Latency 
    # (因為會包含重複計算或同步開銷)，這裡我們專注於計算 AI 與分類
    results.append({
        "Operator": name,
        "AI": ai,
        "FLOPs": flops,
        "Bytes": total_bytes,
        "Bound": "Compute" if ai > RIDGE_POINT else "Memory"
    })

# 3. 初始化模型
model = GPT2Model.from_pretrained("gpt2").to(DEVICE).eval()
results = []

# 註冊 Hook
for name, module in model.named_modules():
    if isinstance(module, (nn.Linear, Conv1D)):
        module.register_forward_hook(lambda m, i, o, n=name: profile_op(m, i, o, n))

# 4. 執行實驗
batch_sizes = [1, 4, 16, 64]
summary_list = []

for b in batch_sizes:
    results = [] # 重置當前 batch 的結果
    dummy_input = torch.randint(0, 100, (b, 128)).to(DEVICE)
    
    with torch.no_grad():
        model(dummy_input)
    
    df = pd.DataFrame(results)
    avg_ai = df['AI'].mean()
    summary_list.append({"BatchSize": b, "Avg_AI": avg_ai})
    print(f"Batch Size {b} finished. Avg AI: {avg_ai:.2f}")

# 5. 繪製圖表與輸出
summary_df = pd.DataFrame(summary_list)
plt.figure(figsize=(8, 5))
plt.plot(summary_df['BatchSize'], summary_df['Avg_AI'], marker='o', label='GPT-2 Average AI')
plt.axhline(y=RIDGE_POINT, color='r', linestyle='--', label=f'Ridge Point ({RIDGE_POINT:.1f})')
plt.xscale('log', base=2)
plt.xlabel('Batch Size')
plt.ylabel('Arithmetic Intensity (FLOP/Byte)')
plt.title('Batch Size Sensitivity Analysis')
plt.legend()
plt.grid(True)
plt.savefig('batch_sensitivity.png')

print("\n--- HW 32-1-1 Operator Analysis (BatchSize=1) ---")
# 重新執行一次 B=1 取得詳細列表
results = []
with torch.no_grad():
    model(torch.randint(0, 100, (1, 128)).to(DEVICE))
print(pd.DataFrame(results).head(10).to_markdown())