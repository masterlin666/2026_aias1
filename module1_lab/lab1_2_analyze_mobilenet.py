"""
Lab 1-2: Analyze converted MobileNet V2 ONNX model.
"""

import onnx
import os

model = onnx.load("mobilenet_v2.onnx")
onnx.checker.check_model(model)
print("[OK] MobileNet V2 ONNX verification passed!")

# Collect operator statistics
op_counts = {}
for node in model.graph.node:
    op_counts[node.op_type] = op_counts.get(node.op_type, 0) + 1

file_size_mb = os.path.getsize("mobilenet_v2.onnx") / (1024 * 1024)
print(f"\nFile size: {file_size_mb:.1f} MB")
print(f"Total nodes: {len(model.graph.node)}")
print(f"Unique operator types: {len(op_counts)}")
print(f"\nOperator Distribution:")
for op, count in sorted(op_counts.items(), key=lambda x: -x[1]):
    print(f"  {op:<30} {count:>4}")

# Identify depthwise vs standard convolutions
print(f"\n--- Convolution Analysis ---")
conv_nodes = [n for n in model.graph.node if n.op_type == "Conv"]
print(f"Total Conv nodes: {len(conv_nodes)}")

# Check for group attribute (depthwise conv has group == input_channels)
for i, node in enumerate(conv_nodes[:5]):  # Show first 5
    group = 1
    for attr in node.attribute:
        if attr.name == "group":
            group = attr.i
    conv_type = "depthwise" if group > 1 else "standard"
    print(f"  Conv #{i}: group={group} ({conv_type})")
