import torch
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
import numpy as np
import evaluate
import time

# 1. 模型與資料集 (與 LoRA 保持完全一致)
model_name = "bert-base-uncased"
dataset = load_dataset("imdb")
tokenizer = AutoTokenizer.from_pretrained(model_name)

train_dataset = dataset["train"].shuffle(seed=42).select(range(500))
test_dataset = dataset["test"].shuffle(seed=42).select(range(100))

def tokenize_fn(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_train = train_dataset.map(tokenize_fn, batched=True)
tokenized_test = test_dataset.map(tokenize_fn, batched=True)

# 2. 載入原始模型 (不使用 LoRA)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# 統計可訓練參數
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total trainable parameters: {trainable_params}")

# 3. 訓練設定 (與 LoRA 保持完全一致)
metric = evaluate.load("accuracy")
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

training_args = TrainingArguments(
    output_dir="./bert-full-finetune",
    learning_rate=2e-5, # Full FT 通常使用較小的 LR
    per_device_train_batch_size=16,
    num_train_epochs=3,
    eval_strategy="epoch",
    save_strategy="no",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    compute_metrics=compute_metrics,
)

# 執行訓練並計時
start_time = time.time()
trainer.train()
end_time = time.time()

print(f"Total training time: {end_time - start_time:.2f} seconds")
print(f"Peak GPU memory: {torch.cuda.max_memory_allocated() / 1024**2:.2f} MB")