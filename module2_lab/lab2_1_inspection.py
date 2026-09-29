import torch
import torchvision.models as models

# Load pretrained AlexNet
model = models.alexnet(weights=models.AlexNet_Weights.DEFAULT)
model.eval()

print("=" * 70)
print("Level 1: print(model)")
print("=" * 70)
print(model)
