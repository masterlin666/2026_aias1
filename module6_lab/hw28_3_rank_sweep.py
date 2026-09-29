import torch
import json
import matplotlib.pyplot as plt
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np
import evaluate

# 1. 環境準備
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

# 2. 定義 Sweep 範圍
ranks = [2, 4, 8, 16, 32, 64]
results = {}

print(f"🚀 開始執行 Rank Sweep 實驗，測試範圍: {ranks}")

for r in ranks:
    print(f"\n" + "="*40)
    print(f"正在測試 Rank r = {r} ...")
    
    # 物理清空顯存快取
    torch.cuda.empty_cache()
    
    # 重新載入模型
    base_model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    config = LoraConfig(
        r=r, 
        lora_alpha=16, 
        target_modules=["query", "value"], 
        task_type=TaskType.SEQ_CLS
    )
    model = get_peft_model(base_model, config)
    trainable_params = model.get_nb_trainable_parameters()[0] # 更穩定的獲取參數方式
    
    # 訓練設定：將 evaluation_strategy 改為 eval_strategy
    training_args = TrainingArguments(
        output_dir=f"./temp_rank_{r}",
        learning_rate=2e-4,
        per_device_train_batch_size=16,
        num_train_epochs=3,
        eval_strategy="no",        # 關鍵修正點：這裡去掉了 uation
        save_strategy="no",
        report_to="none",
        disable_tqdm=False, 
        push_to_hub=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
    )

    # 執行訓練
    trainer.train()
    
    # --- 重點：使用 predict 替代 evaluate ---
    print(f"Rank {r} 訓練完成，正在提取準確度...")
    predictions = trainer.predict(tokenized_test)
    preds = np.argmax(predictions.predictions, axis=-1)
    labels = predictions.label_ids
    final_acc = metric.compute(predictions=preds, references=labels)["accuracy"]
    
    results[r] = {
        "trainable_params": int(trainable_params),
        "accuracy": float(final_acc)
    }
    
    print(f"✅ Rank {r} 結果: Accuracy = {final_acc:.4f}, Params = {trainable_params}")

# 3. 儲存與繪圖
with open("hw28_3_results_rank.json", "w") as f:
    json.dump(results, f, indent=4)

# 繪圖邏輯保持不變...
r_list = sorted(results.keys())
acc_list = [results[k]["accuracy"] for k in r_list]
plt.figure(figsize=(8, 5))
plt.plot(r_list, acc_list, marker='o', color='royalblue', linewidth=2)
plt.title("LoRA Rank vs Accuracy")
plt.xlabel("Rank (r)")
plt.ylabel("Accuracy")
plt.grid(True, ls='--')
plt.savefig("rank_vs_accuracy.png")
plt.show()

print("\n🎉 全部實驗完成！請查看 rank_vs_accuracy.png")