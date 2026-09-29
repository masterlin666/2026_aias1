#include <torch/script.h>
#include <torch/torch.h>
#include <iostream>
#include <iomanip>
#include <vector>

// 輔助函式：格式化 Tensor Shape
std::string get_shape_str(const at::Tensor& t) {
    std::ostringstream ss;
    ss << "[";
    for (int i = 0; i < t.dim(); ++i) {
        ss << t.size(i) << (i == t.dim() - 1 ? "" : ", ");
    }
    ss << "]";
    return ss.str();
}

void analyze_operators(const std::string& model_path) {
    std::cout << "=== Operator List: " << model_path << " ===" << std::endl;
    
    torch::jit::Module module;
    try {
        module = torch::jit::load(model_path);
    } catch (const c10::Error& e) {
        std::cerr << "Error loading model: " << e.what() << std::endl;
        return;
    }

    // 初始化輸入：[1, 3, 224, 224]
    at::Tensor current_tensor = torch::randn({1, 3, 224, 224});

    std::cout << std::left 
              << "| " << std::setw(3) << "#" 
              << " | " << std::setw(18) << "Operator" 
              << " | " << std::setw(18) << "Input Shape" 
              << " | " << std::setw(18) << "Output Shape" << " |" << std::endl;
    std::cout << "|-----|--------------------|--------------------|--------------------|" << std::endl;

    int op_count = 1;

    // 1. 遍歷 features 區塊
    auto features = module.attr("features").toModule();
    for (const auto& child : features.named_children()) {
    at::Tensor input_tensor = current_tensor;
    
    // 使用 const_cast 移除 const 以呼叫 forward
    auto& mutable_child = const_cast<torch::jit::Module&>(child.value);
    current_tensor = mutable_child.forward({current_tensor}).toTensor();
    
    std::cout << "| " << std::left << std::setw(3) << op_count++ 
              << " | " << std::setw(18) << child.value.type()->name()->name()
              << " | " << std::setw(18) << get_shape_str(input_tensor)
              << " | " << std::setw(18) << get_shape_str(current_tensor) << " |" << std::endl;
    }

// 2. 修正：檢查是否存在 avgpool 子模組
    if (module.hasattr("avgpool")) {
        auto avgpool = module.attr("avgpool").toModule();
        at::Tensor pre_avg = current_tensor;
        current_tensor = avgpool.forward({current_tensor}).toTensor();
        std::cout << "| " << std::left << std::setw(3) << op_count++ 
                  << " | " << std::setw(18) << "AdaptiveAvgPool2d"
                  << " | " << std::setw(18) << get_shape_str(pre_avg)
                  << " | " << std::setw(18) << get_shape_str(current_tensor) << " |" << std::endl;
    } else {
        std::cout << "--- No 'avgpool' module found, skipping... ---" << std::endl;
    }

    // 3. 關鍵步驟：Flatten (從 [1, 256, 6, 6] 轉為 [1, 9216])
    // 確保 current_tensor 是二維的，以適應 classifier 的輸入
    if (current_tensor.dim() > 2) {
        current_tensor = current_tensor.view({current_tensor.size(0), -1});
    }
    // 4. 遍歷 classifier 區塊
    auto classifier = module.attr("classifier").toModule();
    for (const auto& child : classifier.named_children()) {
    at::Tensor input_tensor = current_tensor;
    
    // 使用 const_cast 移除 const 以呼叫 forward
    auto& mutable_child = const_cast<torch::jit::Module&>(child.value);
    current_tensor = mutable_child.forward({current_tensor}).toTensor();
    
    std::cout << "| " << std::left << std::setw(3) << op_count++ 
              << " | " << std::setw(18) << child.value.type()->name()->name()
              << " | " << std::setw(18) << get_shape_str(input_tensor)
              << " | " << std::setw(18) << get_shape_str(current_tensor) << " |" << std::endl;
    }
    std::cout << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    for (int i = 1; i < argc; ++i) analyze_operators(argv[i]);
    return 0;
}