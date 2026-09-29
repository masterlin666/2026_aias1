#include <torch/script.h>
#include <torch/torch.h>
#include <iostream>
#include <iomanip>
#include <vector>
#include <algorithm>

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

void analyze_activations(const std::string& model_path) {
    std::cout << "=== Activation Memory: " << model_path << " (batch_size=1) ===" << std::endl;
    
    torch::jit::Module module;
    try {
        module = torch::jit::load(model_path);
    } catch (const c10::Error& e) {
        std::cerr << "Error loading model: " << e.what() << std::endl;
        return;
    }

    at::Tensor current_tensor = torch::randn({1, 3, 224, 224});

    std::cout << std::left 
              << "| " << std::setw(3) << "#" 
              << " | " << std::setw(18) << "Operator" 
              << " | " << std::setw(18) << "Output Shape" 
              << " | " << std::setw(12) << "Elements" 
              << " | " << std::setw(18) << "Activation (bytes)" << " |" << std::endl;
    std::cout << "|-----|--------------------|--------------------|--------------|--------------------|" << std::endl;

    int op_count = 1;
    int64_t total_activation_bytes = 0;
    int64_t peak_activation_bytes = 0;

    auto process_layer = [&](const std::string& name, torch::jit::Module& sub_module) {
        current_tensor = sub_module.forward({current_tensor}).toTensor();
        int64_t numel = current_tensor.numel();
        int64_t bytes = numel * 4; // FP32: 4 bytes
        
        total_activation_bytes += bytes;
        peak_activation_bytes = std::max(peak_activation_bytes, bytes);

        std::cout << "| " << std::left << std::setw(3) << op_count++ 
                  << " | " << std::setw(18) << name
                  << " | " << std::setw(18) << get_shape_str(current_tensor)
                  << " | " << std::setw(12) << numel
                  << " | " << std::setw(18) << bytes << " |" << std::endl;
    };

    // 1. Features
    auto features = module.attr("features").toModule();
    for (const auto& child : features.named_children()) {
        auto mutable_child = child.value; // 取得拷貝或賦值給非 const 變數
        process_layer(child.value.type()->name()->name(), mutable_child);
    }

    // 2. AvgPool
    if (module.hasattr("avgpool")) {
        auto avgpool_mod = module.attr("avgpool").toModule();
        process_layer("AdaptiveAvgPool2d", avgpool_mod);
    }

    // 3. Flatten (保持不變)
    if (current_tensor.dim() > 2) {
        current_tensor = current_tensor.view({current_tensor.size(0), -1});
    }

    // 4. Classifier
    auto classifier = module.attr("classifier").toModule();
    for (const auto& child : classifier.named_children()) {
        auto mutable_child = child.value;
        process_layer(child.value.type()->name()->name(), mutable_child);
    }

    std::cout << std::string(80, '-') << std::endl;
    std::cout << "Total activation memory:      " << total_activation_bytes << " bytes" << std::endl;
    std::cout << "Peak single-layer activation: " << peak_activation_bytes << " bytes" << std::endl << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    for (int i = 1; i < argc; ++i) analyze_activations(argv[i]);
    return 0;
}