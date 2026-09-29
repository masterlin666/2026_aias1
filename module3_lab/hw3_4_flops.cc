#include <torch/script.h>
#include <torch/torch.h>
#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <functional>
// 格式化 Shape
std::string get_shape_str(const at::Tensor& t) {
    std::ostringstream ss;
    ss << "[";
    for (int i = 0; i < t.dim(); ++i) {
        ss << t.size(i) << (i == t.dim() - 1 ? "" : ", ");
    }
    ss << "]";
    return ss.str();
}

void analyze_flops(const std::string& model_path) {
    std::cout << "=== FLOPs: " << model_path << " ===" << std::endl;
    
    torch::jit::Module module;
    try {
        module = torch::jit::load(model_path);
    } catch (const c10::Error& e) {
        std::cerr << "Error loading model." << std::endl;
        return;
    }

    at::Tensor current_tensor = torch::randn({1, 3, 224, 224});
    
    std::cout << std::left 
              << "| " << std::setw(3) << "#" 
              << " | " << std::setw(22) << "Layer (Type)" 
              << " | " << std::setw(18) << "Output Shape" 
              << " | " << std::setw(15) << "FLOPs" << " |" << std::endl;
    std::cout << "|-----|------------------------|--------------------|-----------------|" << std::endl;

    int layer_idx = 1;
    int64_t total_flops = 0;

// 定義一個遞歸 lambda 來處理嵌套模組
    std::function<void(const std::string&, torch::jit::Module&)> process_recursive;
    
    process_recursive = [&](const std::string& prefix, torch::jit::Module& m) {
        at::Tensor original_input = current_tensor;
        at::Tensor combined_output; 
        
        // 判斷是否為並聯容器：
        // 如果模組類型名稱包含 "Split" 或我們自定義的並聯類別
        std::string mod_type = m.type()->name()->name();
        bool is_parallel = (mod_type.find("Split") != std::string::npos);

        for (const auto& child : m.named_children()) {
            std::string type_name = child.value.type()->name()->name();
            auto mutable_child = child.value;

            // 如果是並聯，每一層都用進入容器前的原始輸入
            if (is_parallel) {
                current_tensor = original_input;
            }

            // 1. 葉子節點 (具有權重的運算層)
            if (mutable_child.hasattr("weight") && mutable_child.named_children().size() == 0) {
                at::Tensor layer_input = current_tensor;
                current_tensor = mutable_child.forward({current_tensor}).toTensor();
                
                // --- FLOPs 計算邏輯 (保持不變) ---
                int64_t flops = 0;
                auto weight = mutable_child.attr("weight").toTensor();
                if (weight.dim() == 4) {
                    int64_t OC = weight.size(0), KH = weight.size(2), KW = weight.size(3);
                    int64_t IC = layer_input.size(1), OH = current_tensor.size(2), OW = current_tensor.size(3);
                    int64_t groups = IC / weight.size(1);
                    flops = 2 * OH * OW * OC * (IC / groups) * KH * KW;
                    if (mutable_child.hasattr("bias") && mutable_child.attr("bias").isTensor()) flops += (OH * OW * OC);
                } else if (weight.dim() == 2) {
                    flops = 2 * weight.size(0) * weight.size(1);
                    if (mutable_child.hasattr("bias") && mutable_child.attr("bias").isTensor()) flops += weight.size(0);
                }

                if (flops > 0) {
                    total_flops += flops;
                    std::cout << "| " << std::left << std::setw(3) << layer_idx++ 
                              << " | " << std::setw(22) << (prefix + "." + child.name + " (" + type_name + ")")
                              << " | " << std::setw(18) << get_shape_str(current_tensor)
                              << " | " << std::setw(15) << flops << " |" << std::endl;
                }
            }
            // 2. 嵌套模組 (繼續遞歸)
            else if (mutable_child.named_children().size() > 0) {
                process_recursive(prefix + "." + child.name, mutable_child);
            }
            // 3. 無權重層 (ReLU, MaxPool...)
            else {
                current_tensor = mutable_child.forward({current_tensor}).toTensor();
            }

            // 如果是並聯，收集輸出準備 Concat
            if (is_parallel) {
                if (!combined_output.defined()) combined_output = current_tensor;
                else combined_output = at::cat({combined_output, current_tensor}, 1);
            }
        }
        
        // 並聯結束，合併結果供下一層使用
        if (is_parallel && combined_output.defined()) {
            current_tensor = combined_output;
        }
    };

    // 1. Features
    auto features = module.attr("features").toModule();
    process_recursive("features", features);

    // 2. AvgPool (此時 Tensor 應該還是 4D, 例如 [1, 256, 13, 13])
    if (module.hasattr("avgpool")) {
        auto avgpool = module.attr("avgpool").toModule();
        current_tensor = avgpool.forward({current_tensor}).toTensor();
    }

    // 3. 關鍵修正：進入 Classifier 之前進行 Flatten
    // 將 [1, 256, 6, 6] 轉換為 [1, 9216]
    if (current_tensor.dim() > 2) {
        current_tensor = current_tensor.view({current_tensor.size(0), -1});
    }

    // 4. Classifier
    auto classifier = module.attr("classifier").toModule();
    process_recursive("classifier", classifier);

    std::cout << "|-----|------------------------|--------------------|-----------------|" << std::endl;
    std::cout << "Total FLOPs: " << total_flops << std::endl << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    for (int i = 1; i < argc; ++i) analyze_flops(argv[i]);
    return 0;
}