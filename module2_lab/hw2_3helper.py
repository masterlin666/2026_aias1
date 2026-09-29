import onnx
import os

def get_model_stats(model_path):
    model = onnx.load(model_path)
    graph = model.graph
    
    # 統計節點數量
    total_nodes = len(graph.node)
    matmul_nodes = sum(1 for n in graph.node if n.op_type == 'MatMul')
    gemm_nodes = sum(1 for n in graph.node if n.op_type == 'Gemm')
    
    # 檔案大小
    file_size = os.path.getsize(model_path)
    
    # ONNX Checker
    try:
        onnx.checker.check_model(model)
        checker_status = "Pass"
    except Exception:
        checker_status = "Fail"
        
    return {
        "nodes": total_nodes,
        "matmul": matmul_nodes,
        "gemm": gemm_nodes,
        "size": file_size,
        "checker": checker_status
    }

orig = get_model_stats("alexnet.onnx")
tiled = get_model_stats("alexnet_tiled.onnx")

print(f"{'Metric':<25} | {'Original':<15} | {'Tiled':<15}")
print("-" * 60)
print(f"{'Number of nodes':<25} | {orig['nodes']:<15} | {tiled['nodes']:<15}")
print(f"{'Number of MatMul nodes':<25} | {orig['matmul']:<15} | {tiled['matmul']:<15}")
print(f"{'Number of Gemm nodes':<25} | {orig['gemm']:<15} | {tiled['gemm']:<15}")
print(f"{'File size (bytes)':<25} | {orig['size']:<15} | {tiled['size']:<15}")
print(f"{'ONNX checker':<25} | {orig['checker']:<15} | {tiled['checker']:<15}")