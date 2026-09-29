# Module 1 Lab: AI Model Fundamentals & Formats

Starter files for Module 1 lab exercises and homework.

## Setup

```bash
# Clone your personal repo (after clicking "Create Lab Repo" on the course website)
git clone https://course.playlab.tw/git/<your-username>/module1_lab.git
cd module1_lab

# Install required packages (inside the course Docker container)
pip install torch torchvision onnx onnxruntime netron tf2onnx tensorflow transformers timm
```

## Repository Structure

```
module1_lab/
├── lab1_1_pytorch_to_onnx.py      # Lab 1-1: PyTorch to ONNX conversion
├── lab1_2_analyze_mobilenet.py     # Lab 1-2: TF/JAX to ONNX
├── lab1_3_lenet_export.py          # Lab 1-3 Part A: LeNet CNN export
├── lab1_3_bert_export.py           # Lab 1-3 Part B: BERT Transformer export
├── lab1_4_vit_exploration.py       # Lab 1-4: ViT deep analysis
├── hw1_1_convert.py                # HW 1-1 Part 1: ResNet-50 ONNX conversion (TODO)
├── hw1_1_analysis.py               # HW 1-1 Part 3: Operator analysis (TODO)
├── hw1_2_export.py                 # HW 1-2 Part 1: AlexNet + ViT export (TODO)
├── submission_template.md          # Fill this in and push with your submission
└── .gitignore                      # Excludes large model files (*.onnx, *.pth, etc.)
```

## Workflow

1. **Complete the labs** (`lab1_*.py`) — these are for practice and not graded for points
2. **Complete the homework** — write `hw1_1_convert.py`, `hw1_1_analysis.py`, `hw1_2_export.py`
3. **Take Netron screenshots** — save as `.png` files in this directory (see submission template for exact filenames)
4. **Fill in `submission_template.md`** — paste your results, observations, and written analysis
5. **Push and submit**:
   ```bash
   git add .
   git commit -m "Complete Module 1 homework"
   git push origin main
   ```
6. Submit via the course website submission panel

## Important Notes

- **Do NOT commit `.onnx` files** — they are excluded by `.gitignore`. TAs will regenerate them by running your `.py` scripts.
- **DO commit `.png` screenshots** — Netron screenshots are small and should be included.
- **Written analysis goes in `submission_template.md`** — the Part 3 written analysis (400+ words) should be written directly in the submission template.
