import torch
import torchvision.models as models
from torch.profiler import profile, record_function, ProfilerActivity

# Load ResNet-18
model = models.resnet18(weights=None)
model.eval()

input_data = torch.randn(1, 3, 224, 224)

# Warm-up
with torch.no_grad():
    _ = model(input_data)

# Profile with memory tracking
with profile(
    activities=[ProfilerActivity.CPU],
    profile_memory=True,
    record_shapes=True,
    with_stack=True
) as prof:
    with torch.no_grad():
        with record_function("resnet18_inference"):
            output = model(input_data)

# Time profile
print("=" * 80)
print("ResNet-18: Top-15 Operators by CPU Time")
print("=" * 80)
print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=15))

# Memory profile
print("\n" + "=" * 80)
print("ResNet-18: Top-10 Operators by Memory Usage")
print("=" * 80)
print(prof.key_averages().table(
    sort_by="self_cpu_memory_usage", row_limit=10
))

# Export TensorBoard trace
with profile(
    activities=[ProfilerActivity.CPU],
    schedule=torch.profiler.schedule(wait=1, warmup=1, active=3),
    on_trace_ready=torch.profiler.tensorboard_trace_handler('./log/resnet18'),
    record_shapes=True
) as prof:
    for step in range(6):
        with torch.no_grad():
            model(input_data)
        prof.step()

print("\nTensorBoard traces saved to ./log/resnet18/")
print("View with: tensorboard --logdir=./log/resnet18")
