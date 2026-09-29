"""
Lab 1-4: Vision Transformer (ViT-B/16) deep analysis.
Exports to ONNX, analyzes operators, and compares with AlexNet.
"""

import torch
import torchvision.models as models
import onnx
import os

# ═══════════════════════════════════════════════════════════════
# Step 1: Load and inspect ViT-B/16
# ═══════════════════════════════════════════════════════════════
vit = models.vit_b_16(weights=models.ViT_B_16_Weights.DEFAULT)
vit.eval()

print("=" * 70)
print("  Vision Transformer (ViT-B/16) Architecture")
print("=" * 70)

# Patch embedding
print(f"\n  Patch Embedding: {vit.conv_proj}")
print(f"    → Converts 16x16 patches into {vit.hidden_dim}-dim embeddings")
print(f"    → Image 224x224 / patch 16x16 = {224//16}x{224//16} = {(224//16)**2} patches")

# Class token
print(f"\n  [CLS] Token shape: {vit.class_token.shape}")
print(f"    → Total sequence length: {(224//16)**2} patches + 1 CLS = {(224//16)**2 + 1}")

# Encoder
num_blocks = len(vit.encoder.layers)
print(f"\n  Transformer Encoder: {num_blocks} blocks")

# Examine one encoder block
block = vit.encoder.layers[0]
print(f"\n  Encoder Block 0:")
print(f"    Layer Norm 1:     {block.ln_1}")
print(f"    Self-Attention:   {block.self_attention}")
print(f"    Layer Norm 2:     {block.ln_2}")
print(f"    MLP:              {block.mlp}")

# Classification head
print(f"\n  Classification Head: {vit.heads}")

# ═══════════════════════════════════════════════════════════════
# Step 2: Parameter distribution
# ═══════════════════════════════════════════════════════════════
total_params    = sum(p.numel() for p in vit.parameters())
embed_params    = sum(p.numel() for p in vit.conv_proj.parameters())
pos_embed_params = vit.encoder.pos_embedding.numel()
cls_params      = vit.class_token.numel()
encoder_params  = sum(p.numel() for p in vit.encoder.parameters())
head_params     = sum(p.numel() for p in vit.heads.parameters())

print(f"\n{'=' * 70}")
print(f"  Parameter Distribution")
print(f"{'=' * 70}")
print(f"  {'Component':<30} {'Count':>12} {'Percent':>8}")
print(f"  {'-' * 50}")
print(f"  {'Patch embedding (Conv2d)':<30} {embed_params:>12,} {100*embed_params/total_params:>7.1f}%")
print(f"  {'Positional embedding':<30} {pos_embed_params:>12,} {100*pos_embed_params/total_params:>7.1f}%")
print(f"  {'[CLS] token':<30} {cls_params:>12,} {100*cls_params/total_params:>7.1f}%")
print(f"  {'Transformer encoder':<30} {encoder_params:>12,} {100*encoder_params/total_params:>7.1f}%")
print(f"  {'Classification head':<30} {head_params:>12,} {100*head_params/total_params:>7.1f}%")
print(f"  {'-' * 50}")
print(f"  {'TOTAL':<30} {total_params:>12,} {'100.0%':>8}")

# ═══════════════════════════════════════════════════════════════
# Step 3: Export to ONNX
# ═══════════════════════════════════════════════════════════════
print(f"\n  Exporting ViT-B/16 to ONNX...")
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    vit, dummy_input, "vit_b_16.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input":  {0: "batch_size"},
        "output": {0: "batch_size"},
    },
)

onnx_model = onnx.load("vit_b_16.onnx")
onnx.checker.check_model(onnx_model)
print(f"  [OK] ViT-B/16 exported and verified")

# ═══════════════════════════════════════════════════════════════
# Step 4: ONNX operator analysis
# ═══════════════════════════════════════════════════════════════
op_counts = {}
for node in onnx_model.graph.node:
    op_counts[node.op_type] = op_counts.get(node.op_type, 0) + 1

print(f"\n{'=' * 70}")
print(f"  ONNX Operator Distribution")
print(f"{'=' * 70}")
for op, count in sorted(op_counts.items(), key=lambda x: -x[1]):
    bar = "#" * min(count, 40)
    print(f"  {op:<25} {count:>5}  {bar}")
print(f"  {'─' * 50}")
print(f"  {'TOTAL':<25} {sum(op_counts.values()):>5}")

# ═══════════════════════════════════════════════════════════════
# Step 5: Compare with AlexNet
# ═══════════════════════════════════════════════════════════════
alexnet = models.alexnet(weights=models.AlexNet_Weights.DEFAULT)
alexnet.eval()
torch.onnx.export(
    alexnet, dummy_input, "alexnet.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input":  {0: "batch_size"},
        "output": {0: "batch_size"},
    },
)

alexnet_onnx = onnx.load("alexnet.onnx")
alexnet_ops = {}
for node in alexnet_onnx.graph.node:
    alexnet_ops[node.op_type] = alexnet_ops.get(node.op_type, 0) + 1

alexnet_params = sum(p.numel() for p in alexnet.parameters())
vit_params = total_params

print(f"\n{'=' * 70}")
print(f"  AlexNet vs. ViT-B/16 Comparison")
print(f"{'=' * 70}")
print(f"  {'Metric':<30} {'AlexNet':>15} {'ViT-B/16':>15}")
print(f"  {'-' * 60}")
print(f"  {'Total parameters':<30} {alexnet_params:>15,} {vit_params:>15,}")
print(f"  {'Parameter ratio':<30} {'1.0x':>15} {f'{vit_params/alexnet_params:.1f}x':>15}")
print(f"  {'ONNX nodes':<30} {len(alexnet_onnx.graph.node):>15} {len(onnx_model.graph.node):>15}")
print(f"  {'Unique op types':<30} {len(alexnet_ops):>15} {len(op_counts):>15}")
print(f"  {'File size (MB)':<30} {os.path.getsize('alexnet.onnx')/1024/1024:>15.1f} {os.path.getsize('vit_b_16.onnx')/1024/1024:>15.1f}")
print(f"  {'Primary operation':<30} {'Convolution':>15} {'Self-Attention':>15}")
print(f"  {'Architecture pattern':<30} {'Sequential':>15} {'Repeated blocks':>15}")
print(f"  {'Input processing':<30} {'Pixel grid':>15} {'Patch sequence':>15}")
