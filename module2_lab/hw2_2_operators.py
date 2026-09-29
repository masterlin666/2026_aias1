# python3 hw2_2_operators.py
import onnx
from collections import Counter

model = onnx.load("mobilenetv2.onnx")
graph = model.graph

op_counts = Counter()
conv_stats = {
    "Standard (group=1)": 0,
    "Depthwise (group>1)": 0,
    "1x1 Kernel": 0,
    "3x3 Kernel": 0
}

for node in graph.node:
    op_counts[node.op_type] += 1
    
    if node.op_type == "Conv":
        # 提取屬性
        attrs = {attr.name: attr for attr in node.attribute}
        group = attrs['group'].i if 'group' in attrs else 1
        kernel = list(attrs['kernel_shape'].ints) if 'kernel_shape' in attrs else []
        
        # 統計卷積類型
        if group == 1:
            conv_stats["Standard (group=1)"] += 1
        else:
            conv_stats["Depthwise (group>1)"] += 1
            
        if kernel == [1, 1]:
            conv_stats["1x1 Kernel"] += 1
        elif kernel == [3, 3]:
            conv_stats["3x3 Kernel"] += 1

print("--- Operator Counts ---")
for op, count in op_counts.most_common():
    print(f"{op:<15}: {count}")

print("\n--- Convolution Summary ---")
for key, val in conv_stats.items():
    print(f"{key:<20}: {val}")