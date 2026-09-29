import torch
import torchvision
import onnx
import onnxruntime

print(f"PyTorch version:      {torch.__version__}")
print(f"torchvision version:  {torchvision.__version__}")
print(f"ONNX version:         {onnx.__version__}")
print(f"ONNX Runtime version: {onnxruntime.__version__}")
print(f"CUDA available:       {torch.cuda.is_available()}")