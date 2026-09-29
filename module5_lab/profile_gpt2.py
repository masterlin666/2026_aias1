import torch
from torch.profiler import profile, record_function, ProfilerActivity
from transformers import GPT2LMHeadModel, GPT2Config

# GPT-2 Small configuration
config = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_embd=768,
    n_layer=12,
    n_head=12,
)

model = GPT2LMHeadModel(config)
model.eval()

# Create input: batch=1, sequence_length=128
input_ids = torch.randint(0, config.vocab_size, (1, 128))
attention_mask = torch.ones_like(input_ids)

# Warm-up
with torch.no_grad():
    _ = model(input_ids, attention_mask=attention_mask)

# ============================================================
# Phase 1: Operator-Level Profiling
# ============================================================
print("=" * 80)
print("GPT-2 Small: Operator-Level Profile (seq_len=128)")
print("=" * 80)

with profile(
    activities=[ProfilerActivity.CPU],
    profile_memory=True,
    record_shapes=True,
    with_stack=True
) as prof:
    with torch.no_grad():
        with record_function("gpt2_forward"):
            output = model(input_ids, attention_mask=attention_mask)

# Top operators by time
print("\n--- Top-20 Operators by CPU Time ---")
print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=20))

# Top operators by memory
print("\n--- Top-10 Operators by Memory ---")
print(prof.key_averages().table(
    sort_by="self_cpu_memory_usage", row_limit=10
))

# Group by input shapes to distinguish different GEMM sizes
print("\n--- Operators Grouped by Input Shape ---")
print(prof.key_averages(group_by_input_shape=True).table(
    sort_by="cpu_time_total", row_limit=20
))

prof.export_chrome_trace("gpt2_trace.json")
print("\nTrace exported to gpt2_trace.json")

# ============================================================
# Phase 2: Sequence Length Scaling
# ============================================================
print("\n" + "=" * 80)
print("GPT-2 Small: Sequence Length Scaling")
print("=" * 80)

seq_lengths = [32, 64, 128, 256, 512]
results = []

for seq_len in seq_lengths:
    input_ids = torch.randint(0, config.vocab_size, (1, seq_len))
    attn_mask = torch.ones_like(input_ids)

    # Warm-up
    with torch.no_grad():
        _ = model(input_ids, attention_mask=attn_mask)

    with profile(activities=[ProfilerActivity.CPU]) as prof:
        with torch.no_grad():
            _ = model(input_ids, attention_mask=attn_mask)

    gemm_time = sum(
        item.cpu_time_total for item in prof.key_averages()
        if item.key == "aten::linear" or item.key == "aten::matmul"
    )
    overall_time = sum(
        item.self_cpu_time_total for item in prof.key_averages()
    )

    results.append((seq_len, overall_time / 1000, gemm_time / 1000))
    print(f"seq_len={seq_len:4d}  total={overall_time/1000:.2f} ms  "
          f"linear+matmul={gemm_time/1000:.2f} ms")

print("\n--- Summary Table ---")
print(f"{'Seq Len':>8} {'Total (ms)':>12} {'Linear+MatMul (ms)':>20} {'GEMM %':>8}")
for seq_len, total, gemm in results:
    pct = gemm / total * 100 if total > 0 else 0
    print(f"{seq_len:>8d} {total:>12.2f} {gemm:>20.2f} {pct:>7.1f}%")
