"""
Module 6 - Lab 6-4
Extracted from lab_assignment.md
"""


# ============================================================
# Part A
# ============================================================

import json

# We will use BERT + SST-2 for this experiment since it is fast to train
from transformers import BertForSequenceClassification, BertTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
import evaluate

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
dataset = load_dataset("glue", "sst2")

def tokenize_fn(examples):
    return tokenizer(examples["sentence"], padding="max_length", truncation=True, max_length=128)

tokenized_dataset = dataset.map(tokenize_fn, batched=True)
tokenized_dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])

metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = logits.argmax(axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# Ranks to test
ranks = [4, 8, 16, 32]
results = {}

for r in ranks:
    print(f"\n{'='*50}")
    print(f"Training with LoRA rank = {r}")
    print(f"{'='*50}")

    # Load fresh base model
    base_model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased", num_labels=2
    )

    # Apply LoRA
    lora_config = LoraConfig(
        r=r,
        lora_alpha=r,  # Keep alpha = r for fair comparison
        target_modules=["query", "value"],
        lora_dropout=0.1,
        bias="none",
        task_type="SEQ_CLS",
    )
    lora_model = get_peft_model(base_model, lora_config)

    # Count params
    trainable = sum(p.numel() for p in lora_model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in lora_model.parameters())

    # Train
    training_args = TrainingArguments(
        output_dir=f"./lora_rank_{r}",
        num_train_epochs=3,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=64,
        warmup_steps=100,
        weight_decay=0.01,
        learning_rate=2e-4,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=100,
        report_to="none",
    )

    trainer = Trainer(
        model=lora_model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        compute_metrics=compute_metrics,
    )

    trainer.train()
    eval_results = trainer.evaluate()

    results[r] = {
        "rank": r,
        "trainable_params": trainable,
        "total_params": total,
        "trainable_fraction": trainable / total,
        "accuracy": eval_results["eval_accuracy"],
    }

    print(f"Rank {r}: {trainable:,} params ({trainable/total:.4%}), "
          f"Accuracy: {eval_results['eval_accuracy']:.4f}")

# Print summary table
print(f"\n{'='*70}")
print(f"{'Rank':>6} | {'Trainable':>12} | {'Fraction':>10} | {'Accuracy':>10}")
print(f"{'-'*6}-+-{'-'*12}-+-{'-'*10}-+-{'-'*10}")
for r, res in sorted(results.items()):
    print(f"{res['rank']:>6} | {res['trainable_params']:>12,} | "
          f"{res['trainable_fraction']:>9.4%} | {res['accuracy']:>9.4f}")

# Save results
with open("rank_sweep_results.json", "w") as f:
    json.dump(results, f, indent=2)

# ============================================================
# Part B
# ============================================================

import matplotlib.pyplot as plt

ranks_list = sorted(results.keys())
params_list = [results[r]["trainable_params"] for r in ranks_list]
acc_list = [results[r]["accuracy"] for r in ranks_list]

fig, ax1 = plt.subplots(figsize=(8, 5))

color1 = "#2196F3"
color2 = "#FF5722"

ax1.set_xlabel("LoRA Rank", fontsize=12)
ax1.set_ylabel("Accuracy", fontsize=12, color=color1)
ax1.plot(ranks_list, acc_list, "o-", color=color1, linewidth=2, markersize=8, label="Accuracy")
ax1.tick_params(axis="y", labelcolor=color1)
ax1.set_ylim([0.80, 0.95])

ax2 = ax1.twinx()
ax2.set_ylabel("Trainable Parameters", fontsize=12, color=color2)
ax2.bar(ranks_list, params_list, alpha=0.3, color=color2, width=2, label="Params")
ax2.tick_params(axis="y", labelcolor=color2)

plt.title("LoRA Rank vs Accuracy and Parameter Count (BERT + SST-2)", fontsize=13)
fig.tight_layout()
plt.savefig("rank_vs_accuracy.png", dpi=150, bbox_inches="tight")
plt.show()

print("Plot saved to rank_vs_accuracy.png")
