"""
Module 6 - Lab 6-3
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

from unsloth import FastLanguageModel

# Load LLaMA-3.2 1B (4-bit quantized for memory efficiency)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-1B",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Apply LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

# Print parameter summary
model.print_trainable_parameters()

# ============================================================
# Part B
# ============================================================

FastLanguageModel.for_inference(model)

test_prompts = [
    "Explain what LoRA is in simple terms.",
    "Write a Python function that reverses a string.",
    "What are the benefits of parameter-efficient finetuning?",
]

print("=== BEFORE Finetuning ===\n")
for prompt in test_prompts:
    inputs = tokenizer(
        f"### Instruction:\n{prompt}\n\n### Response:\n",
        return_tensors="pt",
    ).to("cuda")
    outputs = model.generate(
        **inputs, max_new_tokens=200, temperature=0.7, do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}\n")
    print("-" * 60)

# ============================================================
# Part C
# ============================================================

from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# Load dataset
dataset = load_dataset("mlabonne/FineTome-100k", split="train[:5000]")

# Format for instruction tuning
def format_prompt(example):
    return {"text": f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"}

dataset = dataset.map(format_prompt)

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=1,
        output_dir="outputs",
        report_to="none",
    ),
)

print("Starting training...")
trainer.train()
print("Training complete!")

# ============================================================
# Part D
# ============================================================

FastLanguageModel.for_inference(model)

print("\n=== AFTER Finetuning ===\n")
for prompt in test_prompts:
    inputs = tokenizer(
        f"### Instruction:\n{prompt}\n\n### Response:\n",
        return_tensors="pt",
    ).to("cuda")
    outputs = model.generate(
        **inputs, max_new_tokens=200, temperature=0.7, do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}\n")
    print("-" * 60)

# ============================================================
# Part E
# ============================================================

# Save just the LoRA adapter weights
model.save_pretrained("lora_adapter")

# Check the size of the saved adapter
import os
adapter_size = sum(
    os.path.getsize(os.path.join("lora_adapter", f))
    for f in os.listdir("lora_adapter")
)
print(f"LoRA adapter size: {adapter_size / 1e6:.1f} MB")
print(f"(Compare to full model: ~2500 MB in FP16)")
