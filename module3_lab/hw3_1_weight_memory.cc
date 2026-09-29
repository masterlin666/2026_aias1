#include <torch/script.h>
#include <torch/torch.h>
#include <iostream>
#include <iomanip>
#include <string>
#include <vector>

void analyze_weight_memory(const std::string& model_path) {
    std::cout << "=== Weight Memory: " << model_path << " ===" << std::endl;
    
    torch::jit::Module module;
    try {
        module = torch::jit::load(model_path);
    } catch (const c10::Error& e) {
        std::cerr << "Error loading model: " << e.what() << std::endl;
        return;
    }

    // 表頭列印
    std::cout << std::left 
              << std::setw(25) << "Layer" << " | "
              << std::setw(20) << "Shape" << " | "
              << std::setw(10) << "Params" << " | "
              << "Memory (bytes)" << std::endl;
    std::cout << std::string(80, '-') << std::endl;

    int64_t total_params = 0;
    int64_t total_bytes = 0;

    // 迭代所有具名參數
    for (const auto& param : module.named_parameters()) {
        std::string name = param.name;
        at::Tensor tensor = param.value;
        
        int64_t numel = tensor.numel();
        int64_t bytes = numel * tensor.element_size();
        
        total_params += numel;
        total_bytes += bytes;

        // 格式化 Shape 字串 (例如 [64, 3, 11, 11])
        std::ostringstream shape_ss;
        shape_ss << tensor.sizes();

        std::cout << std::left 
                  << std::setw(25) << name << " | "
                  << std::setw(20) << shape_ss.str() << " | "
                  << std::setw(10) << numel << " | "
                  << bytes << std::endl;
    }

    std::cout << std::string(80, '-') << std::endl;
    double total_mb = static_cast<double>(total_bytes) / (1024.0 * 1024.0);
    
    std::cout << "Total parameters: " << total_params << std::endl;
    std::cout << "Total memory: " << total_bytes << " bytes (" 
              << std::fixed << std::setprecision(2) << total_mb << " MB)" << std::endl << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: ./hw3_1 <model1.pt> [model2.pt ...]" << std::endl;
        return 1;
    }

    for (int i = 1; i < argc; ++i) {
        analyze_weight_memory(argv[i]);
    }

    return 0;
}