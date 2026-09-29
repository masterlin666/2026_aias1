import onnx
model = onnx.load("efficientnet-b1-subgraph.onnx")
for node in model.graph.node:
    print(f"{node.op_type} : {node.name}")