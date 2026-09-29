# Module 6 Lab

Starter files for Module 6 lab exercises.

## Prerequisites

> **Labs 6-3 and 6-4 require a GPU.** Use the provided Colab notebook:
>
> 1. Open `lab6_gpu_labs.ipynb` in Google Colab (upload or use GitHub import)
> 2. Set runtime to **T4 GPU**: `Runtime > Change runtime type > T4 GPU`
> 3. Run cells in order
>
> Labs 6-1 and 6-2 run on CPU and can be done locally.

## Setup

```bash
# Clone this repo
git clone https://course.playlab.tw/git/<your-username>/module6_lab.git
cd module6_lab

# Install required packages for labs 6-1 and 6-2 (CPU)
pip install datasets evaluate peft torch transformers
```

## Lab Files

- `lab6_1_bert_sst2.py` — BERT fine-tuning basics (CPU)
- `lab6_2_lora_params.py` — LoRA parameter analysis (CPU)
- `lab6_3_llama_lora.py` — LLaMA LoRA fine-tuning (GPU required)
- `lab6_4_rank_sweep.py` — LoRA rank sweep experiment (GPU required)
- `lab6_gpu_labs.ipynb` — Colab notebook for labs 6-3 & 6-4

## Homework

Place your homework deliverables in the `homework/` directory.

## Submission

1. Complete the lab exercises and homework
2. Commit and push your work
3. Submit via the course website submission panel
