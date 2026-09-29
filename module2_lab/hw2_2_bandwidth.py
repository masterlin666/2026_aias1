# python3 hw2_2_bandwidth.py
import onnx

model = onnx.load("mobilenetv2.onnx")
total_params = 0

for init in model.graph.initializer:
    num_elements = 1
    for d in init.dims:
        num_elements *= d
    total_params += num_elements

weight_mb = (total_params * 4) / (1024**2)
print(f"Total Weights: {total_params:,} parameters")
print(f"Total Weight Data (FP32): {weight_mb:.2f} MB\n")

# 頻寬計算 (GB/s = 1000 MB/s for simplicity in hardware estimates)
bandwidths = {
    "DDR4 (Edge)": 25.6,
    "LPDDR5 (Mobile)": 51.2,
    "HBM2e (Data Center)": 460.0
}

print(f"{'Memory Tech':<20} | {'Loading Time (ms)':>20}")
print("-" * 45)
for tech, bw in bandwidths.items():
    time_ms = (weight_mb / (bw * 1024)) * 1000
    print(f"{tech:<20} | {time_ms:>20.4f} ms")