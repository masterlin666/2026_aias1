import torch
import torchvision.models as models

# Load pretrained ResNet-18 (PyTorch 2.x weights API)
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.eval()

# Create example input: batch=1, channels=3, height=224, width=224
example_input = torch.randn(1, 3, 224, 224)

# Trace the model
traced_model = torch.jit.trace(model, example_input)

# Save the traced model
traced_model.save("resnet18_traced.pt")
print("Model saved to resnet18_traced.pt")

# Verification: reload and run
loaded = torch.jit.load("resnet18_traced.pt")
output = loaded(example_input)
print(f"Output shape: {output.shape}")
print(f"Top-5 class indices: {torch.topk(output, 5).indices[0].tolist()}")

# Print model architecture summary
print(f"\nModel parameters: {sum(p.numel() for p in model.parameters()):,}")
print(f"Model size on disk: {__import__('os').path.getsize('resnet18_traced.pt') / 1e6:.1f} MB")
