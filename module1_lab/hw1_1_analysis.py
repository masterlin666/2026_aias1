"""
HW 1-1 Part 3: ResNet-50 Operator Analysis

Load resnet50.onnx and report operator statistics:
  - Count of each operator type (Conv, Gemm, BatchNormalization, Relu, Add, etc.)
  - Total number of unique operator types
  - Complete sorted operator list with counts

Print a clean, formatted table. Example output format:

    ResNet-50 ONNX Operator Analysis
    ================================
      Conv                     53
      BatchNormalization       53
      Relu                     49
      Add                      16
      ...
"""

import onnx
import os

# TODO: Load resnet50.onnx
# (Run hw1_1_convert.py first to generate the file)

# TODO: Verify the model passes onnx.checker.check_model()

# TODO: Iterate over onnx_model.graph.node and count each op_type

# TODO: Print formatted operator table with counts

# TODO: Print total nodes and unique operator type count
import onnx
from collections import Counter

def analyze_onnx(model_path):
    model = onnx.load(model_path)
    nodes = model.graph.node
    
    # 統計運算子
    op_counts = Counter(node.op_type for node in nodes)
    
    print("\nResNet-50 ONNX Operator Analysis")
    print("=" * 40)
    
    # 指定要求的特定算子
    target_ops = ['Conv', 'Gemm', 'BatchNormalization', 'Relu', 'Add', 'GlobalAveragePool']
    
    for op in target_ops:
        print(f"  {op:<25} {op_counts.get(op, 0)}")
    
    print("-" * 40)
    
    # 其他不重複算子與排序列表
    all_ops_sorted = sorted(op_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"  TOTAL NODES               {len(nodes)}")
    print(f"  UNIQUE OP TYPES           {len(op_counts)}")
    print("\nFull Operator List (Sorted):")
    for op, count in all_ops_sorted:
        print(f"  - {op}: {count}")

if __name__ == "__main__":
    analyze_onnx("resnet50.onnx")
