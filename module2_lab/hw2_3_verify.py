import numpy as np
import onnxruntime as ort

sess_orig = ort.InferenceSession("alexnet.onnx")
sess_tiled = ort.InferenceSession("alexnet_tiled.onnx")

num_tests = 100
max_error = 0.0
all_pass = True

for i in range(num_tests):
    x = np.random.randn(1, 3, 224, 224).astype(np.float32)
    out_orig = sess_orig.run(None, {'input': x})[0]
    out_tiled = sess_tiled.run(None, {'input': x})[0]
    error = np.max(np.abs(out_orig - out_tiled))
    max_error = max(max_error, error)
    if not np.allclose(out_orig, out_tiled, atol=1e-4):
        all_pass = False
        print(f"Test {i}: FAILED (max error = {error:.2e})")

print(f"\nResults: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
print(f"Maximum absolute error across all tests: {max_error:.2e}")