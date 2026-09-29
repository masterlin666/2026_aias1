# Module 2 Lab

Starter files for Module 2 lab exercises.

## Prerequisites

> **Lab 2-4 requires `lenet.onnx`.** Run the setup script first to generate it:
> ```bash
> python3 setup_models.py
> ```

## Setup

```bash
# Clone this repo
git clone https://course.playlab.tw/git/<your-username>/module2_lab.git
cd module2_lab

# Install required packages (inside the course Docker container)
pip install onnx onnxruntime torch torch_tb_profiler torchinfo torchsummary torchvision

# Generate prerequisite models
python3 setup_models.py
```

## Lab Files

- `setup_models.py` — generates `lenet.onnx` (run this first)
- `lab2_1_inspection.py`
- `lab2_2_memory.py`
- `lab2_3_macs.py`
- `lab2_4_parse_model.py`
- `lab2_5_hooks.py`
- `lab2_6_profiler.py`

## Homework

Place your homework deliverables in the `homework/` directory.

## Submission

1. Complete the lab exercises and homework
2. Commit and push your work
3. Submit via the course website submission panel
