import torch
from transformers import BertConfig, BertModel
from torch.profiler import profile, record_function, ProfilerActivity

config = BertConfig() # Default BERT-base
model = BertModel(config).eval()
# Sequence length = 512, Batch size = 1
input_ids = torch.randint(0, 1000, (1, 512))

# Warm-up
with torch.no_grad():
    _ = model(input_ids)

with profile(
    activities=[ProfilerActivity.CPU],
    profile_memory=True,
    record_shapes=True,
    with_stack=True
) as prof:
    with torch.no_grad():
        with record_function("bert_inference"):
            model(input_ids)

print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))
print(prof.key_averages().table(sort_by="self_cpu_memory_usage", row_limit=5))