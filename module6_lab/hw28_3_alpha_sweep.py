import torch
import json
import matplotlib.pyplot as plt
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np
import evaluate

# 1. 環境與資料 (同 Part A)
model_name = "bert-base-uncased"
dataset = load_dataset("imdb")
tokenizer = AutoTokenizer.from_pretrained(model_name)
train_dataset = dataset["train"].shuffle(seed=42).select(range(500))
test_dataset = dataset["test"].shuffle(seed=42).select(range(100))

def tokenize_fn(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_train = train_dataset.map(tokenize_fn, batched=True)
tokenized_test = test_dataset.map(tokenize_fn, batched=True)
metric = evaluate.load("accuracy")

# 2. 定義 Alpha Sweep 範圍 (固定 r=16)
alphas = [8, 16, 32, 64]
results = {}

print(f"🚀 開始執行 Alpha Sweep 實驗 (固定 r=16)")

for alpha in alphas:
    print(f"\n測試 Alpha α = {alpha} ...")
    torch.cuda.empty_cache()
    
    base_model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    config = LoraConfig(
        r=16, 
        lora_alpha=alpha, 
        target_modules=["query", "value"], 
        task_type=TaskType.SEQ_CLS
    )
    model = get_peft_model(base_model, config)
    
    training_args = TrainingArguments(
        output_dir=f"./temp_alpha_{alpha}",
        learning_rate=2e-4,
        per_device_train_batch_size=16,
        num_train_epochs=3,
        eval_strategy="no",
        save_strategy="no",
        report_to="none"
    )

    trainer = Trainer(model=model, args=training_args, train_dataset=tokenized_train)
    trainer.train()
    
    # 預測與評估
    predictions = trainer.predict(tokenized_test)
    preds = np.argmax(predictions.predictions, axis=-1)
    acc = metric.compute(predictions=preds, references=predictions.label_ids)["accuracy"]
    
    results[alpha] = float(acc)
    print(f"✅ Alpha {alpha} 完成: Accuracy = {acc:.4f}")

# 3. 儲存與繪圖
with open("hw28_3_results_alpha.json", "w") as f:
    json.dump(results, f, indent=4)

plt.figure(figsize=(8, 5))
plt.plot(list(results.keys()), list(results.values()), marker='o', color='orange')
plt.title("LoRA Alpha vs Accuracy (Fixed r=16)")
plt.xlabel("Alpha (α)")
plt.ylabel("Accuracy")
plt.grid(True)
plt.savefig("alpha_vs_accuracy.png")
plt.show()