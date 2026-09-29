import torch
import torchvision.models as models
from torch.profiler import profile, record_function, ProfilerActivity

model = models.resnet50(weights=None).eval()
input_data = torch.randn(1, 3, 224, 224)

# Warm-up
with torch.no_grad():
    _ = model(input_data)

with profile(
    activities=[ProfilerActivity.CPU],
    profile_memory=True,
    record_shapes=True,
    with_stack=True
) as prof:
    with torch.no_grad():
        with record_function("resnet50_inference"):
            model(input_data)

print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))
print(prof.key_averages().table(sort_by="self_cpu_memory_usage", row_limit=5))