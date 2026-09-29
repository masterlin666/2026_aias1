"""
Module 6 - Lab 6-2
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

from transformers import BertForSequenceClassification
from peft import LoraConfig, get_peft_model

# Load base model
base_model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)

# Configure LoRA
lora_config = LoraConfig(
    r=16,                          # Rank
    lora_alpha=16,                 # Scaling factor
    target_modules=["query", "value"],  # Apply to Q and V projections
    lora_dropout=0.1,
    bias="none",
    task_type="SEQ_CLS",
)

# Apply LoRA
lora_model = get_peft_model(base_model, lora_config)

# Print parameter summary
lora_model.print_trainable_parameters()

# ============================================================
# Part B
# ============================================================

# Manual parameter count verification
d_model = 768
r = 16
n_layers = 12
n_target_modules = 2  # query and value

# LoRA parameters per projection: A (r x d) + B (d x r)
params_per_projection = r * d_model + d_model * r
print(f"Parameters per projection: {params_per_projection:,}")

# Per layer (Q + V)
params_per_layer = n_target_modules * params_per_projection
print(f"Parameters per layer:      {params_per_layer:,}")

# All layers
total_lora_params = n_layers * params_per_layer
print(f"Total LoRA parameters:     {total_lora_params:,}")

# Classification head
cls_head_params = d_model * 2 + 2  # weights + bias for 2-class output
print(f"Classification head:       {cls_head_params:,}")

# Total trainable
total_trainable = total_lora_params + cls_head_params
print(f"Total trainable:           {total_trainable:,}")

# Original model parameters
original_params = sum(p.numel() for p in base_model.parameters())
print(f"\nOriginal model params:     {original_params:,}")
print(f"LoRA trainable fraction:   {total_trainable / original_params:.4%}")

# ============================================================
# Part C
# ============================================================

# Show which modules have LoRA adapters
for name, module in lora_model.named_modules():
    if "lora" in name.lower():
        if hasattr(module, "weight"):
            print(f"{name}: shape={tuple(module.weight.shape)}")
        else:
            print(f"{name}: {type(module).__name__}")
