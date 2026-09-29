import onnx

model = onnx.load('efficientnet-b1-subgraph.onnx')

print(f"=== 模型基本信息 ===")
print(f"輸入：{[inp.name for inp in model.graph.input]}")
print(f"輸出：{[out.name for out in model.graph.output]}")
print(f"節點數：{len(model.graph.node)}")
print(f"權重數：{len(model.graph.initializer)}")

print(f"\n=== 節點操作 ===")
op_count = {}
for node in model.graph.node:
    op_type = node.op_type
    op_count[op_type] = op_count.get(op_type, 0) + 1
    
for op_type, count in sorted(op_count.items()):
    print(f"  {op_type}: {count}")

print(f"\n=== 權重詳情 ===")
for init in model.graph.initializer:
    print(f"  {init.name} - shape: {list(init.dims)}")
