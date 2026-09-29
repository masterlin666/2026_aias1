import onnx
from onnx import numpy_helper

model = onnx.load('efficientnet-b1-subgraph.onnx')
pad_node = next(node for node in model.graph.node if node.op_type == 'Pad')
print('Pad node inputs', list(pad_node.input))
for idx, inp in enumerate(pad_node.input):
    print('input', idx, inp)
    found = False
    for node in model.graph.node:
        if inp in node.output:
            found = True
            print('  produced by', node.op_type, node.name, 'output idx', node.output.index(inp))
            if node.op_type == 'Constant':
                const_val = numpy_helper.to_array(next(attr for attr in node.attribute if attr.name == 'value').t)
                print('   constant value', const_val, const_val.shape)
            elif node.op_type == 'Cast':
                print('   cast to', [a.t for a in node.attribute if a.name == 'to'])
    for init in model.graph.initializer:
        if init.name == inp:
            arr = numpy_helper.to_array(init)
            print('  initializer', arr, arr.shape)
    if not found:
        print('  no producer node found; may be graph input or initializer')
