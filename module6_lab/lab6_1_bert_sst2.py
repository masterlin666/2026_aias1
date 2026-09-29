"""
Module 6 - Lab 6-1
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

import torch
from transformers import BertForSequenceClassification, BertTokenizer
from datasets import load_dataset

# Load model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Load SST-2 dataset
dataset = load_dataset("glue", "sst2")

# Tokenize
def tokenize_fn(examples):
    return tokenizer(
        examples["sentence"],
        padding="max_length",
        truncation=True,
        max_length=128,
    )

tokenized_dataset = dataset.map(tokenize_fn, batched=True)
tokenized_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# Evaluate before finetuning
model.eval()
correct = 0
total = 0
val_data = tokenized_dataset["validation"]

with torch.no_grad():
    for i in range(min(200, len(val_data))):  # Evaluate on first 200 samples
        inputs = {
            "input_ids": val_data[i]["input_ids"].unsqueeze(0),
            "attention_mask": val_data[i]["attention_mask"].unsqueeze(0),
        }
        outputs = model(**inputs)
        pred = outputs.logits.argmax(dim=-1).item()
        correct += (pred == val_data[i]["label"].item())
        total += 1

print(f"Accuracy BEFORE finetuning: {correct / total:.4f}")
print(f"(Expected: ~0.50, since classification head is random)")

# ============================================================
# Part B
# ============================================================

total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"Total parameters:     {total_params:>15,}")
print(f"Trainable parameters: {trainable_params:>15,}")
print(f"Trainable fraction:   {trainable_params / total_params:.4%}")

# ============================================================
# Part C
# ============================================================

from transformers import Trainer, TrainingArguments
import evaluate

metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = logits.argmax(axis=-1)
    return metric.compute(predictions=predictions, references=labels)

training_args = TrainingArguments(
    output_dir="./bert_sst2_results",
    num_train_epochs=3,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    warmup_steps=100,
    weight_decay=0.01,
    learning_rate=2e-5,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    load_best_model_at_end=True,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    compute_metrics=compute_metrics,
)

trainer.train()

# Evaluate after finetuning
results = trainer.evaluate()
print(f"\nAccuracy AFTER finetuning: {results['eval_accuracy']:.4f}")
print(f"(Expected: ~0.90-0.93)")
