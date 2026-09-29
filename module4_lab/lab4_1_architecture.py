"""
Module 4 - Lab 4-1
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

import torch
from transformers import GPT2LMHeadModel, GPT2Config
from types import SimpleNamespace

# Load GPT-2 (124M parameters)
model = GPT2LMHeadModel.from_pretrained("gpt2")
config = model.config

print("=" * 60)
print("GPT-2 Architecture Inspection")
print("=" * 60)

# Print key hyperparameters
print(f"\nModel hyperparameters:")
print(f"  Hidden dimension (d_model):  {config.n_embd}")
print(f"  Number of attention heads:   {config.n_head}")
print(f"  Head dimension (d_k):        {config.n_embd // config.n_head}")
print(f"  MLP intermediate dim (d_ff): {config.n_inner or 4 * config.n_embd}")
print(f"  Number of layers:            {config.n_layer}")
print(f"  Vocabulary size:             {config.vocab_size}")
print(f"  Max sequence length:         {config.n_positions}")
print(f"  Attention type:              MHA (Multi-Head Attention)")

# ============================================================
# Part B
# ============================================================

print("\n" + "=" * 60)
print("Parameter Count by Component")
print("=" * 60)

# Count parameters in each component
def count_params(module):
    return sum(p.numel() for p in module.parameters())

# Embedding layers
embed_params = model.transformer.wte.weight.numel()
pos_embed_params = model.transformer.wpe.weight.numel()
print(f"\nToken embedding:     {embed_params:>12,} params  ({embed_params * 2 / 1e6:.1f} MB FP16)")
print(f"Position embedding:  {pos_embed_params:>12,} params  ({pos_embed_params * 2 / 1e6:.1f} MB FP16)")

# Analyze one decoder layer
layer0 = model.transformer.h[0]

# Attention block
attn = layer0.attn
attn_params = count_params(attn)

# The c_attn weight contains Q, K, V concatenated: [d_model, 3 * d_model]
qkv_weight = attn.c_attn.weight
qkv_bias = attn.c_attn.bias
print(f"\nAttention block (per layer):")
print(f"  QKV weight shape:  {list(qkv_weight.shape)}  (Q, K, V concatenated)")
print(f"  QKV params:        {qkv_weight.numel() + qkv_bias.numel():>12,}")
print(f"  Output proj shape: {list(attn.c_proj.weight.shape)}")
print(f"  Output proj params:{attn.c_proj.weight.numel() + attn.c_proj.bias.numel():>12,}")
print(f"  Total attention:   {attn_params:>12,}")

# MLP block
mlp = layer0.mlp
mlp_params = count_params(mlp)
print(f"\nMLP block (per layer):")
print(f"  FC1 (up) shape:    {list(mlp.c_fc.weight.shape)}  ({config.n_embd} -> {4 * config.n_embd})")
print(f"  FC2 (down) shape:  {list(mlp.c_proj.weight.shape)}  ({4 * config.n_embd} -> {config.n_embd})")
print(f"  Total MLP:         {mlp_params:>12,}")

# LayerNorm
ln_params = count_params(layer0.ln_1) + count_params(layer0.ln_2)
print(f"\nLayerNorm (per layer): {ln_params:>10,}")

# Per-layer and full model
per_layer = attn_params + mlp_params + ln_params
print(f"\n--- Per decoder layer total: {per_layer:>12,}")
print(f"--- All {config.n_layer} layers total: {per_layer * config.n_layer:>15,}")

# LM head (often shares weights with embedding)
total = count_params(model)
print(f"\n--- FULL MODEL TOTAL: {total:>15,} ({total / 1e6:.1f}M)")
print(f"    Weight memory (FP16): {total * 2 / 1e9:.2f} GB")
print(f"    Weight memory (INT4): {total * 0.5 / 1e9:.2f} GB")

# ============================================================
# Part C
# ============================================================

# LLaMA 3.1 8B architecture config (hardcoded to avoid HuggingFace gated access requirement)
llama_config = SimpleNamespace(
    hidden_size=4096,
    num_attention_heads=32,
    num_key_value_heads=8,
    intermediate_size=14336,
    num_hidden_layers=32,
    vocab_size=128256,
)

print("\n" + "=" * 60)
print("Architecture Comparison: GPT-2 vs LLaMA 3 8B")
print("=" * 60)

comparison = {
    "Parameter": ["d_model", "n_heads", "n_kv_heads", "d_k", "d_ff",
                   "n_layers", "vocab_size", "attention_type", "MLP_type",
                   "normalization", "positional_encoding"],
    "GPT-2": [768, 12, 12, 64, 3072, 12, 50257, "MHA", "Standard",
              "LayerNorm", "Learned absolute"],
    "LLaMA 3 8B": [
        llama_config.hidden_size,
        llama_config.num_attention_heads,
        llama_config.num_key_value_heads,
        llama_config.hidden_size // llama_config.num_attention_heads,
        llama_config.intermediate_size,
        llama_config.num_hidden_layers,
        llama_config.vocab_size,
        f"GQA (g={llama_config.num_attention_heads // llama_config.num_key_value_heads})",
        "SwiGLU",
        "RMSNorm",
        "RoPE"
    ]
}

print(f"\n{'Parameter':<22} {'GPT-2':>18} {'LLaMA 3 8B':>18}")
print("-" * 60)
for i, param in enumerate(comparison["Parameter"]):
    print(f"{param:<22} {str(comparison['GPT-2'][i]):>18} {str(comparison['LLaMA 3 8B'][i]):>18}")

# Compute parameter counts for LLaMA
d = llama_config.hidden_size
d_kv = llama_config.num_key_value_heads * (d // llama_config.num_attention_heads)
d_ff = llama_config.intermediate_size
n_layers = llama_config.num_hidden_layers
vocab = llama_config.vocab_size

attn_params_llama = d * d + 2 * d * d_kv + d * d  # Q, K, V, O projections
mlp_params_llama = 3 * d * d_ff  # gate, up, down
layer_params = attn_params_llama + mlp_params_llama
total_params = n_layers * layer_params + vocab * d  # + embedding

print(f"\nLLaMA 3 8B estimated parameter count:")
print(f"  Attention per layer: {attn_params_llama:>15,}")
print(f"  MLP per layer:       {mlp_params_llama:>15,}")
print(f"  Per layer total:     {layer_params:>15,}")
print(f"  All layers:          {n_layers * layer_params:>15,}")
print(f"  + Embedding:         {vocab * d:>15,}")
print(f"  TOTAL:               {total_params:>15,} ({total_params / 1e9:.2f}B)")
