import torch
import torch.nn as nn
from collections import OrderedDict

def analyze_activations_pytorch(model_path, batch_size=1, input_shape=(1, 3, 224, 224)):
    """用 PyTorch 分析激活值記憶體"""
    
    model = torch.jit.load(model_path)
    model.eval()
    
    print(f"=== Activation Memory Analysis: {model_path} ===\n")
    print(f"Input shape: {input_shape}")
    print(f"{'Layer':<30} | {'Output Shape':<20} | {'Elements':>12} | {'Memory (MB)':>12}")
    print("-" * 80)
    
    # 用 hook 來捕捉每層的輸出
    activations = []
    hooks = []
    
    def hook_fn(module, input, output):
        if isinstance(output, torch.Tensor):
            activations.append({
                'name': module.__class__.__name__,
                'shape': tuple(output.shape),
                'numel': output.numel(),
                'bytes': output.numel() * 4  # FP32
            })
    
    # 註冊 hooks
    def register_hooks(model, hooks):
        for name, module in model.named_modules():
            if isinstance(module, (nn.Conv2d, nn.Linear, nn.ReLU, nn.Sigmoid, 
                                  nn.BatchNorm2d, nn.AdaptiveAvgPool2d)):
                hook = module.register_forward_hook(hook_fn)
                hooks.append(hook)
    
    register_hooks(model, hooks)
    
    # 前向傳播
    try:
        dummy_input = torch.randn(*input_shape)
        with torch.no_grad():
            _ = model(dummy_input)
    except Exception as e:
        print(f"Error during forward pass: {e}")
        print("Falling back to simple forward...")
        return
    finally:
        # 移除 hooks
        for hook in hooks:
            hook.remove()
    
    # 列印結果
    total_bytes = 0
    peak_bytes = 0
    
    for i, act in enumerate(activations):
        shape_str = str(act['shape'])
        memory_mb = act['bytes'] / (1024 * 1024)
        total_bytes += act['bytes']
        peak_bytes = max(peak_bytes, act['bytes'])
        
        print(f"{act['name']:<30} | {shape_str:<20} | {act['numel']:>12} | {memory_mb:>12.6f}")
    
    print("-" * 80)
    total_mb = total_bytes / (1024 * 1024)
    peak_mb = peak_bytes / (1024 * 1024)
    
    print(f"\nTotal activation memory: {total_bytes} bytes ({total_mb:.6f} MB)")
    print(f"Peak single-layer activation: {peak_bytes} bytes ({peak_mb:.6f} MB)\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_activations.py <model.pt>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    analyze_activations_pytorch(model_path)
