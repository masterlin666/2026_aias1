"""
Lab 1-1: PyTorch to ONNX Conversion
Exports AlexNet and ResNet-18 to ONNX, verifies them, and compares operator distributions.
"""

import torch
import torchvision.models as models
import onnx
import os

def export_model_to_onnx(model, model_name, input_shape=(1, 3, 224, 224), opset=17):
    """Export a PyTorch model to ONNX format with standard settings."""
    model.eval()
    dummy_input = torch.randn(*input_shape)
    onnx_path = f"{model_name}.onnx"

    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,          # Store weights in the ONNX file
        opset_version=opset,         # ONNX opset version
        do_constant_folding=True,    # Fold constants at export time
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={               # Allow variable batch size
            "input":  {0: "batch_size"},
            "output": {0: "batch_size"},
        },
    )
    print(f"[OK] {model_name} exported to {onnx_path}")
    return onnx_path


def verify_and_analyze(onnx_path, model_name):
    """Load, verify, and analyze an ONNX model."""
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    print(f"[OK] {model_name} verification passed")

    # Collect operator statistics
    op_counts = {}
    for node in onnx_model.graph.node:
        op_counts[node.op_type] = op_counts.get(node.op_type, 0) + 1

    # Print summary
    file_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    print(f"\n{'=' * 50}")
    print(f"  {model_name} ONNX Analysis")
    print(f"{'=' * 50}")
    print(f"  File size:        {file_size_mb:.1f} MB")
    print(f"  IR version:       {onnx_model.ir_version}")
    print(f"  Opset version:    {onnx_model.opset_import[0].version}")
    print(f"  Total nodes:      {len(onnx_model.graph.node)}")
    print(f"  Unique op types:  {len(op_counts)}")
    print(f"\n  Operator Distribution:")
    for op, count in sorted(op_counts.items(), key=lambda x: -x[1]):
        print(f"    {op:<25} {count:>4}")
    print(f"{'=' * 50}\n")

    return op_counts


# ── Part A: Export AlexNet ──────────────────────────────────────────────
print("\n>>> Part A: AlexNet")
alexnet = models.alexnet(weights=models.AlexNet_Weights.DEFAULT)
print(f"AlexNet architecture:\n{alexnet}\n")

alexnet_path = export_model_to_onnx(alexnet, "alexnet")
alexnet_ops = verify_and_analyze(alexnet_path, "AlexNet")

# ── Part B: Export ResNet-18 ────────────────────────────────────────────
print("\n>>> Part B: ResNet-18")
resnet18 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
resnet18_path = export_model_to_onnx(resnet18, "resnet18")
resnet18_ops = verify_and_analyze(resnet18_path, "ResNet-18")

# ── Part C: Compare ────────────────────────────────────────────────────
print("\n>>> Comparison")
all_ops = sorted(set(list(alexnet_ops.keys()) + list(resnet18_ops.keys())))
print(f"{'Operator':<25} {'AlexNet':>10} {'ResNet-18':>10}")
print(f"{'-' * 45}")
for op in all_ops:
    a = alexnet_ops.get(op, 0)
    r = resnet18_ops.get(op, 0)
    print(f"{op:<25} {a:>10} {r:>10}")

# Parameter counts
alexnet_params = sum(p.numel() for p in alexnet.parameters())
resnet_params = sum(p.numel() for p in resnet18.parameters())
print(f"\n{'Total parameters':<25} {alexnet_params:>10,} {resnet_params:>10,}")
