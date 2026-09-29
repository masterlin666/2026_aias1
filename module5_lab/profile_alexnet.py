import torch
import torchvision.models as models
from torch.profiler import profile, record_function, ProfilerActivity

# Load AlexNet
model = models.alexnet(weights=None)
model.eval()

# Create input: batch=1, 3 channels, 224x224
input_data = torch.randn(1, 3, 224, 224)

# Warm-up
with torch.no_grad():
    _ = model(input_data)

# Profile CPU time
print("=" * 80)
print("AlexNet Profiling: CPU Time")
print("=" * 80)

with profile(
    activities=[ProfilerActivity.CPU],
    record_shapes=True,
    with_stack=True
) as prof:
    with torch.no_grad():
        with record_function("alexnet_inference"):
            output = model(input_data)

print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=15))

# Export Chrome trace
prof.export_chrome_trace("alexnet_trace.json")
print("\nExported trace to alexnet_trace.json")
print("View in chrome://tracing or TensorBoard")
