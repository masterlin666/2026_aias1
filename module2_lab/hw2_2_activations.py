# python3 hw2_2_activations.py
import onnx
from onnx import helper, shape_inference

model = onnx.load("mobilenetv2.onnx")
inferred_model = shape_inference.infer_shapes(model)

total_act_bytes = 0
max_act = {"name": "", "size_kb": 0, "shape": []}

# 遍歷圖中的所有加值輸出
for value_info in inferred_model.graph.value_info:
    shape = [d.dim_value for d in value_info.type.tensor_type.shape.dim]
    num_elements = 1
    for d in shape:
        # 處理動態 Batch Size (如為 0 或未定義則設為 1)
        num_elements *= (d if d > 0 else 1)
    
    size_kb = (num_elements * 4) / 1024
    total_act_bytes += num_elements * 4
    
    if size_kb > max_act["size_kb"]:
        max_act = {"name": value_info.name, "size_kb": size_kb, "shape": shape}

print(f"Total Activation Memory (sum of all): {total_act_bytes/(1024**2):.2f} MB")
print(f"Largest Tensor: {max_act['name']} | Shape: {max_act['shape']} | Size: {max_act['size_kb']:.2f} KB")