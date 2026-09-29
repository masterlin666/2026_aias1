import torch
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np
import evaluate

# 1. 模型與資料集 (BERT-base 有 110M 參數)
model_name = "bert-base-uncased"
dataset = load_dataset("imdb")

tokenizer = AutoTokenizer.from_pretrained(model_name)

# 取小量數據確保 3 分鐘內跑完並拿到數據
train_dataset = dataset["train"].shuffle(seed=42).select(range(500))
test_dataset = dataset["test"].shuffle(seed=42).select(range(100))

def tokenize_fn(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_train = train_dataset.map(tokenize_fn, batched=True)
tokenized_test = test_dataset.map(tokenize_fn, batched=True)

# 2. LoRA 配置 (針對 BERT 的 Query 和 Value 層)
config = LoraConfig(
    r=8, 
    lora_alpha=16, 
    target_modules=["query", "value"], 
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_CLS # 序列分類任務
)

base_model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
model = get_peft_model(base_model, config)

print("--- 訓練參數統計 ---")
model.print_trainable_parameters()

# 3. 訓練設定
metric = evaluate.load("accuracy")
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

training_args = TrainingArguments(
    output_dir="./bert-lora-imdb",
    learning_rate=2e-4,
    per_device_train_batch_size=16,
    num_train_epochs=3,
    eval_strategy="epoch",
    save_strategy="no",
    logging_steps=5,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    compute_metrics=compute_metrics,
)

# 執行訓練
print("開始訓練...")
trainer.train()

# 4. 定性分析 (取出 3 個範例)
print("\n--- 定性分析範例 ---")
sentences = [
    "This movie was fantastic and I loved the acting!",
    "It was a boring film with a predictable plot.",
    "The cinematography was okay, but the story was weak."
]
model.eval()
for s in sentences:
    inputs = tokenizer(s, return_tensors="pt").to(model.device)
    with torch.no_grad():
        logits = model(**inputs).logits
    pred = torch.argmax(logits, dim=-1).item()
    label = "Positive" if pred == 1 else "Negative"
    print(f"Text: {s} -> Prediction: {label}")