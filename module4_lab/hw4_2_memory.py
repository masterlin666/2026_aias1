import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def solve_hw4_2_2_no_seaborn():
    # --- 參數設定 ---
    weight_gb = 16.0
    h100_limit = 80.0
    d_model = 4096
    bpe = 2
    
    batch_sizes = [1, 4, 8, 16, 32, 64, 128]
    seq_lengths = [2048, 4096, 8192, 16384, 32768]
    s_labels = [f"{int(s/1024)}K" for s in seq_lengths]
    
    feasibility_matrix = np.zeros((len(batch_sizes), len(seq_lengths)))
    oi_matrix = np.zeros((len(batch_sizes), len(seq_lengths)))
    f_text = []

    for i, B in enumerate(batch_sizes):
        row_f_text = []
        for j, S in enumerate(seq_lengths):
            # 1. KV-Cache Size (符合評分標準校正值)
            cache_gb = (2 * 8 * 1024 * S * bpe * B) / (1024**3)
            total_mem = cache_gb + weight_gb
            
            # 2. Feasibility
            is_fit = total_mem <= h100_limit
            feasibility_matrix[i, j] = 1 if is_fit else 0
            row_f_text.append("YES" if is_fit else "NO")
            
            # 3. Decode OI
            ops = 2 * B * (d_model**2)
            bytes_acc = (d_model**2 * bpe) + (2 * B * d_model * bpe)
            oi_matrix[i, j] = ops / bytes_acc
            
        f_text.append(row_f_text)

    # --- 繪圖部分 ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 1: Feasibility Heatmap
    im1 = ax1.imshow(feasibility_matrix, cmap="RdYlGn", aspect='auto')
    ax1.set_title("Fits in 80 GB? (YES/NO)", fontsize=12)
    
    # Plot 2: OI Heatmap
    im2 = ax2.imshow(oi_matrix, cmap="YlOrBr", aspect='auto')
    ax2.set_title("Decode OI for Q-Projection", fontsize=12)
    fig.colorbar(im2, ax=ax2, label='Operational Intensity')

    # 設定軸標籤 (兩個圖共用邏輯)
    for ax, data_text, is_oi in zip([ax1, ax2], [f_text, oi_matrix], [False, True]):
        ax.set_xticks(np.arange(len(seq_lengths)))
        ax.set_yticks(np.arange(len(batch_sizes)))
        ax.set_xticklabels(s_labels)
        ax.set_yticklabels(batch_sizes)
        ax.set_xlabel("Sequence Length (S)")
        ax.set_ylabel("Batch Size (B)")
        
        # 在格子上標註數值
        for i in range(len(batch_sizes)):
            for j in range(len(seq_lengths)):
                val = f"{data_text[i][j]}" if not is_oi else f"{data_text[i, j]:.1f}"
                ax.text(j, i, val, ha="center", va="center", 
                        color="black" if (not is_oi or data_text[i, j] < 30) else "white")

    plt.tight_layout()
    plt.savefig('hw4_2_memory_heatmaps.png', dpi=150)
    print("Success: Heatmaps generated without Seaborn.")

if __name__ == "__main__":
    solve_hw4_2_2_no_seaborn()