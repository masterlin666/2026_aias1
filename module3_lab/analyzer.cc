#include <torch/script.h>
#include <torch/torch.h>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <functional>
#include <iomanip>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: analyzer <path-to-model.pt>" << std::endl;
        return 1;
    }

    std::string model_path = argv[1];

    // =============================================================
    // Part A: Load the TorchScript model
    // =============================================================
    std::cout << "=== Loading Model ===" << std::endl;
    torch::jit::Module module;
    try {
        module = torch::jit::load(model_path);
    } catch (const c10::Error& e) {
        std::cerr << "Error loading model: " << e.what() << std::endl;
        return 1;
    }
    module.eval();
    std::cout << "Model loaded successfully from: " << model_path << std::endl;

    // =============================================================
    // Part B: Create input and run forward pass
    // =============================================================
    std::cout << "\n=== Running Forward Pass ===" << std::endl;
    auto input = torch::randn({1, 3, 224, 224});
    std::cout << "Input shape: " << input.sizes() << std::endl;

    std::vector<torch::jit::IValue> inputs;
    inputs.push_back(input);

    at::Tensor output;
    try {
        output = module.forward(inputs).toTensor();
    } catch (const c10::Error& e) {
        std::cerr << "Error during forward pass: " << e.what() << std::endl;
        return 1;
    }
    std::cout << "Output shape: " << output.sizes() << std::endl;

    // Print top-5 predictions
    auto topk = torch::topk(output, 5, /*dim=*/1);
    std::cout << "Top-5 class indices: ";
    auto indices = std::get<1>(topk);
    for (int i = 0; i < 5; i++) {
        std::cout << indices[0][i].item<int>();
        if (i < 4) std::cout << ", ";
    }
    std::cout << std::endl;

    // =============================================================
    // Part C: Dump model structure
    // =============================================================
    std::cout << "\n=== Model Structure (dump) ===" << std::endl;
    std::cout << module.dump_to_str(true, false, false) << std::endl;

    return 0;
}