import sys
import os
import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

sys.path.append(os.path.abspath('../backend'))
import eval_utils

# 1. Load Dataset
df = pd.read_csv('../data/synthetic_distortions_en.csv')
print(f'Total rows loaded: {len(df)}')
print(df.head())

# 2. Prepare Labels
labels = df['distortion_label'].unique().tolist()
num_labels = len(labels)
label2id = {label: i for i, label in enumerate(labels)}
id2label = {i: label for i, label in enumerate(labels)}

df['label'] = df['distortion_label'].map(label2id)

# 3. Split Dataset
train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

print(f'Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}')

# 4. Tokenization
MODEL_NAME = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=128)

train_dataset = Dataset.from_pandas(train_df[['text', 'label']]).map(tokenize_function, batched=True)
val_dataset = Dataset.from_pandas(val_df[['text', 'label']]).map(tokenize_function, batched=True)
test_dataset = Dataset.from_pandas(test_df[['text', 'label']]).map(tokenize_function, batched=True)

# 5. Model Initialization
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=num_labels, 
    id2label=id2label, 
    label2id=label2id
)

# 6. Training Configuration
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=1, # Reduced for quick testing
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy='epoch',
    save_strategy='epoch',
    load_best_model_at_end=True,
    report_to="none" # Disable wandb/etc logging
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    metrics = eval_utils.evaluate_predictions(labels, predictions, target_names=list(label2id.keys()))
    return {'accuracy': metrics['accuracy'], 'f1': metrics['f1_score']}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# 7. Train Model
print("Starting training...")
trainer.train()

# 8. Evaluate on Test Set
print("Evaluating on test set...")
test_results = trainer.evaluate(test_dataset)
print("Test Results:", test_results)

# 9. Save Fine-Tuned Model
output_dir = '../backend/models/distortion_model'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f'Model saved to {output_dir}')
