cmake_minimum_required(VERSION 3.18 FATAL_ERROR)
project(model_analyzer)

# Find the LibTorch package
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

#hw3_1
add_executable(hw3_1 hw3_1_weight_memory.cc)
target_link_libraries(hw3_1 "${TORCH_LIBRARIES}")

# 新增 hw3_2
add_executable(hw3_2 hw3_2_operators.cc)
target_link_libraries(hw3_2 "${TORCH_LIBRARIES}")

#hw3_3
add_executable(hw3_3 hw3_3_activations.cc)
target_link_libraries(hw3_3 "${TORCH_LIBRARIES}")

#hw3_4
add_executable(hw3_4 hw3_4_flops.cc)
target_link_libraries(hw3_4 "${TORCH_LIBRARIES}")
set_property(TARGET hw3_1 hw3_2 hw3_3 hw3_4 PROPERTY CXX_STANDARD 17)