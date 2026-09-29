import onnx
import numpy as np
import onnxruntime as rt
from onnx import numpy_helper, TensorProto

def analyze_activations_onnx(onnx_path, batch_size=1, input_shape=(1, 3, 224, 224)):
    """用 ONNX 模型分析激活值記憶體"""
    
    # 載入模型
    model = onnx.load(onnx_path)
    graph = model.graph
    
    print(f"=== Activation Memory Analysis: {onnx_path} ===\n")
    print(f"Input shape: {input_shape}")
    print(f"{'Tensor':<40} | {'Shape':<25} | {'Elements':>12} | {'Memory (MB)':>12}")
    print("-" * 95)
    
    # 建立 ONNX Runtime 會話並啟用所有中間張量輸出
    # 先修改模型，使其輸出所有中間張量
    model_copy = onnx.load(onnx_path)
    graph = model_copy.graph
    
    # 記錄原始輸出
    original_outputs = [out.name for out in graph.output]
    
    # 添加所有中間張量作為輸出
    all_tensors = set()
    for node in graph.node:
        for out in node.output:
            all_tensors.add(out)
    for inp in graph.input:
        all_tensors.add(inp.name)
    for init in graph.initializer:
        all_tensors.add(init.name)
    
    # 清除原始輸出，添加所有張量作為輸出
    del graph.output[:]
    for tensor_name in all_tensors:
        output = graph.output.add()
        output.name = tensor_name
        # 嘗試推斷類型
        output.type.tensor_type.elem_type = TensorProto.FLOAT
    
    # 建立會話
    sess = rt.InferenceSession(model_copy.SerializeToString())
    
    # 準備輸入
    input_data = np.random.randn(*input_shape).astype(np.float32)
    
    # 執行推論
    input_name = graph.input[0].name
    outputs = sess.run(None, {input_name: input_data})
    
    # 分析結果
    tensor_memory = {}
    total_bytes = 0
    peak_bytes = 0
    
    for i, output_name in enumerate(all_tensors):
        if i < len(outputs) and outputs[i] is not None:
            arr = outputs[i]
            if isinstance(arr, np.ndarray):
                numel = arr.size
                bytes_val = numel * 4  # FP32
                shape_str = str(arr.shape)
                
                # 只列出合理大小的張量（不列出權重）
                if numel > 0 and numel < 100_000_000:  # 小於 100M 元素
                    memory_mb = bytes_val / (1024 * 1024)
                    print(f"{output_name:<40} | {shape_str:<25} | {numel:>12} | {memory_mb:>12.6f}")
                    
                    total_bytes += bytes_val
                    peak_bytes = max(peak_bytes, bytes_val)
    
    print("-" * 95)
    total_mb = total_bytes / (1024 * 1024)
    peak_mb = peak_bytes / (1024 * 1024)
    
    print(f"\nTotal activation memory: {total_bytes} bytes ({total_mb:.6f} MB)")
    print(f"Peak single-layer activation: {peak_bytes} bytes ({peak_mb:.6f} MB)\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        onnx_path = "efficientnet-b1-subgraph.onnx"
    else:
        onnx_path = sys.argv[1]
    
    analyze_activations_onnx(onnx_path)
