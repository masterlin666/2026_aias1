import numpy as np
import onnx
from onnx import helper, TensorProto
import onnxruntime as ort

def create_linear_model(in_features, out_features, model_path):
    """Create an ONNX model with a single Gemm (Linear) node."""
    # Input and output
    X = helper.make_tensor_value_info('X', TensorProto.FLOAT, [1, in_features])
    Y = helper.make_tensor_value_info('Y', TensorProto.FLOAT, [1, out_features])

    # Weights and bias (random initialization)
    np.random.seed(42)
    W_data = np.random.randn(in_features, out_features).astype(np.float32)
    b_data = np.random.randn(out_features).astype(np.float32)

    W = helper.make_tensor('W', TensorProto.FLOAT,
                           [in_features, out_features], W_data.flatten())
    b = helper.make_tensor('b', TensorProto.FLOAT,
                           [out_features], b_data.flatten())

    # Gemm node: Y = X @ W + b
    gemm_node = helper.make_node('Gemm', inputs=['X', 'W', 'b'], outputs=['Y'],
                                  alpha=1.0, beta=1.0, transA=0, transB=0)

    graph = helper.make_graph([gemm_node], 'linear_graph', [X], [Y],
                              initializer=[W, b])
    model = helper.make_model(graph,
                              opset_imports=[helper.make_opsetid('', 13)])
    model.ir_version = 8

    onnx.checker.check_model(model)
    onnx.save(model, model_path)
    return model, W_data, b_data

# Create and verify
model, W_data, b_data = create_linear_model(256, 128, "linear_256x128.onnx")

sess = ort.InferenceSession("linear_256x128.onnx")
x_input = np.random.randn(1, 256).astype(np.float32)
result = sess.run(None, {'X': x_input})[0]
expected = x_input @ W_data + b_data
print(f"Max error: {np.max(np.abs(result - expected)):.2e}")
assert np.allclose(result, expected, atol=1e-5), "Verification failed!"
print("Single Linear model verified successfully.")