#!/usr/bin/env python3
"""Lab 2-4: ONNX Model Parsing"""

import onnx
from onnx import shape_inference
from collections import Counter

# ============================================================
# Step 1: Load the ONNX model
# ============================================================
model = onnx.load("lenet.onnx")
graph = model.graph

print("=" * 60)
print("ONNX Model Overview")
print("=" * 60)
print(f"Model IR version:               {model.ir_version}")
print(f"Opset version:                  {model.opset_import[0].version}")
print(f"Number of nodes (operators):    {len(graph.node)}")
print(f"Number of initializers (weights): {len(graph.initializer)}")

# ============================================================
# Step 2: List unique operators with counts
# ============================================================
print("\n" + "=" * 60)
print("Operator Counts")
print("=" * 60)

op_counts = Counter(node.op_type for node in graph.node)
for op_type, count in sorted(op_counts.items(), key=lambda x: -x[1]):
    print(f"  {op_type:<25} {count:>3}")
print(f"  {'TOTAL':<25} {sum(op_counts.values()):>3}")

# ============================================================
# Step 3: Extract Conv operator details
# ============================================================
print("\n" + "=" * 60)
print("Conv Operator Details")
print("=" * 60)

for node in graph.node:
    if node.op_type == "Conv":
        print(f"\nConv node: {node.name}")
        print(f"  Inputs:  {list(node.input)}")
        print(f"  Outputs: {list(node.output)}")
        for attr in node.attribute:
            if attr.name == "kernel_shape":
                print(f"  kernel_shape: {list(attr.ints)}")
            elif attr.name == "strides":
                print(f"  strides: {list(attr.ints)}")
            elif attr.name == "pads":
                print(f"  pads: {list(attr.ints)}")
            elif attr.name == "dilations":
                print(f"  dilations: {list(attr.ints)}")
            elif attr.name == "group":
                print(f"  group: {attr.i}")

# ============================================================
# Step 4: Shape inference
# ============================================================
print("\n" + "=" * 60)
print("Shape Inference Results")
print("=" * 60)

inferred_model = shape_inference.infer_shapes(model)

def get_shape(type_proto):
    """Extract shape from a TypeProto."""
    shape = []
    for d in type_proto.tensor_type.shape.dim:
        if d.dim_param:
            shape.append(d.dim_param)
        else:
            shape.append(d.dim_value)
    return shape

print("\nGraph inputs:")
for inp in inferred_model.graph.input:
    print(f"  {inp.name}: {get_shape(inp.type)}")

print("\nIntermediate tensors:")
for vi in inferred_model.graph.value_info:
    print(f"  {vi.name}: {get_shape(vi.type)}")

print("\nGraph outputs:")
for out in inferred_model.graph.output:
    print(f"  {out.name}: {get_shape(out.type)}")

# ============================================================
# Step 5: Extract weight tensor dimensions
# ============================================================
print("\n" + "=" * 60)
print("Weight Tensors (Initializers)")
print("=" * 60)

total_weight_bytes = 0
print(f"\n{'Name':<40} {'Shape':<20} {'Elements':>10} {'Size (bytes)':>12}")
print("-" * 85)
for init in graph.initializer:
    dims = list(init.dims)
    num_elements = 1
    for d in dims:
        num_elements *= d
    size_bytes = num_elements * 4  # Assuming FP32
    total_weight_bytes += size_bytes
    print(f"  {init.name:<38} {str(dims):<20} {num_elements:>10,} {size_bytes:>12,}")

print("-" * 85)
print(f"  {'TOTAL':<38} {'':>20} {'':>10} {total_weight_bytes:>12,}")
print(f"  Total weight data: {total_weight_bytes / 1024:.1f} KB ({total_weight_bytes / 1024**2:.3f} MB)")
