import onnx

model = onnx.load('efficientnet-b1-subgraph.onnx')
initializers = model.graph.initializer
print(f"總權重參數數：{len(initializers)}")
for i, init in enumerate(initializers):
    print(f"  {init.name} - shape: {list(init.dims)}")
