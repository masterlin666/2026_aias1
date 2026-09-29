"""
Lab 1-3, Part B: Export BERT-tiny to ONNX for Netron visualization.
"""

import torch
from transformers import BertModel, BertTokenizer

# Load BERT-tiny (2 layers, 128 hidden, 2 attention heads)
model_name = "prajjwal1/bert-tiny"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)
model.eval()

print(f"Model: {model_name}")
params = sum(p.numel() for p in model.parameters())
print(f"Parameters: {params:,}")
print(f"Hidden size: {model.config.hidden_size}")
print(f"Num layers: {model.config.num_hidden_layers}")
print(f"Num attention heads: {model.config.num_attention_heads}")

# Create dummy input
text = "Hello, this is a test sentence for visualization."
inputs = tokenizer(text, return_tensors="pt", padding="max_length",
                   max_length=32, truncation=True)

# Export to ONNX
torch.onnx.export(
    model,
    (inputs["input_ids"], inputs["attention_mask"]),
    "bert_tiny.onnx",
    opset_version=17,
    input_names=["input_ids", "attention_mask"],
    output_names=["last_hidden_state", "pooler_output"],
    dynamic_axes={
        "input_ids":          {0: "batch", 1: "seq_len"},
        "attention_mask":     {0: "batch", 1: "seq_len"},
        "last_hidden_state":  {0: "batch", 1: "seq_len"},
        "pooler_output":      {0: "batch"},
    },
)

# Verify and analyze
import onnx
onnx_model = onnx.load("bert_tiny.onnx")
onnx.checker.check_model(onnx_model)

op_counts = {}
for node in onnx_model.graph.node:
    op_counts[node.op_type] = op_counts.get(node.op_type, 0) + 1

print(f"\n[OK] BERT-tiny exported: {len(onnx_model.graph.node)} nodes")
print(f"Operator distribution:")
for op, count in sorted(op_counts.items(), key=lambda x: -x[1]):
    print(f"  {op:<25} {count:>4}")
