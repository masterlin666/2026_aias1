import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# FILL IN YOUR HARDWARE PARAMETERS
# ============================================================
peak_perf_gflops = 200.0    # Your peak CPU performance
peak_bw_gbs = 51.2          # Your peak memory bandwidth

# ============================================================
# FILL IN YOUR MEASURED KERNEL DATA
# Each entry: (name, actual_oi, achieved_gflops)
# ============================================================
kernels = [
    # From Lab 5-1 / 5-3 measurements
    ("Naive GEMM",      0.027,   1.84),    # FILL IN
    ("Tiled T=16",      0.15,    3.50),    # FILL IN
    ("Tiled T=64",      0.82,    2.32),    # FILL IN
    ("Tiled T=128",     0.45,    2.10),    # FILL IN
]

# Ideal operating point
total_ops = 2 * 512 * 768 * 3072
total_data = (512 * 768 + 768 * 3072) * 4  # bytes
ideal_oi = total_ops / total_data

# ============================================================
# PLOT THE ROOFLINE
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Roofline curve
oi_range = np.logspace(-3, 4, 1000)
ridge = peak_perf_gflops / peak_bw_gbs
roofline = np.minimum(peak_perf_gflops, peak_bw_gbs * oi_range)
ax.loglog(oi_range, roofline, 'b-', linewidth=2.5, label='Roofline')

# Ridge point marker
ax.axvline(x=ridge, color='gray', linestyle=':', alpha=0.5,
           label=f'Ridge Point (OI={ridge:.1f})')

# Ideal point
ideal_perf = min(peak_perf_gflops, peak_bw_gbs * ideal_oi)
ax.plot(ideal_oi, ideal_perf, 'g^', markersize=15, zorder=5,
        label=f'Ideal (OI={ideal_oi:.1f})')

# Measured kernels
colors = ['red', 'orange', 'purple', 'brown', 'cyan']
markers = ['v', 's', 'D', 'o', 'p']
for i, (name, oi, perf) in enumerate(kernels):
    ax.plot(oi, perf, marker=markers[i % len(markers)],
            color=colors[i % len(colors)], markersize=12,
            zorder=5, label=f'{name} (OI={oi:.3f}, {perf:.2f} GF)')

# Labels and formatting
ax.set_xlabel('Operational Intensity (FLOP/Byte)', fontsize=13)
ax.set_ylabel('Performance (GFLOPS)', fontsize=13)
ax.set_title('Roofline Model: Measured GEMM Kernels', fontsize=15)
ax.legend(fontsize=10, loc='lower right')
ax.grid(True, alpha=0.3, which='both')
ax.set_xlim(1e-3, 1e4)
ax.set_ylim(1e-1, peak_perf_gflops * 2)

plt.tight_layout()
plt.savefig('roofline_lab5_4.png', dpi=150, bbox_inches='tight')
print("Saved roofline_lab5_4.png")
plt.show()
