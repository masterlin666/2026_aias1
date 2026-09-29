import torch
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np
import evaluate

# 設定三種配置
configs_to_test = {
    "Config_A": ["query", "value"],
    "Config_B": ["query", "key", "value", "output.dense"],
    "Config_C": ["query", "key", "value", "output.dense", "intermediate.dense"]
}

module_results = {}

for name, modules in configs_to_test.items():
    print(f"\n🚀 測試配置 {name}: Modules = {modules}")
    torch.cuda.empty_cache()
    
    base_model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
    config = LoraConfig(r=16, lora_alpha=16, target_modules=modules, task_type=TaskType.SEQ_CLS)
    model = get_peft_model(base_model, config)
    
    trainable_params = model.get_nb_trainable_parameters()[0]
    
    trainer = Trainer(
        model=model,
        args=TrainingArguments(output_dir="./temp", per_device_train_batch_size=16, num_train_epochs=3, report_to="none"),
        train_dataset=tokenized_train
    )
    
    trainer.train()
    
    predictions = trainer.predict(tokenized_test)
    acc = metric.compute(predictions=np.argmax(predictions.predictions, axis=-1), references=predictions.label_ids)["accuracy"]
    
    module_results[name] = {
        "params": int(trainable_params),
        "accuracy": float(acc),
        "efficiency": float(acc / trainable_params * 1e6) # 每百萬參數貢獻度
    }
    print(f"✅ {name} 完成: Accuracy = {acc:.4f}, Params = {trainable_params}")

with open("hw28_3_results_modules.json", "w") as f:
    json.dump(module_results, f, indent=4)