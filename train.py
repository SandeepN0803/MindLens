import sys
import os
import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

sys.path.append(os.path.abspath('backend'))
import eval_utils


# 1. Load Datasets (Single-label + Targeted Multi-label)
df1 = pd.read_csv('data/synthetic_distortions_en.csv')
df2 = pd.read_csv('data/synthetic_distortions_multilabel_en.csv')
df = pd.concat([df1, df2], ignore_index=True)
# Shuffle the dataset so multi-label examples are distributed
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f'Total rows loaded: {len(df)}')
df.head()


# 2. Prepare Labels (Multi-hot format)
# We explicitly list all 9 core labels
all_labels = ['Magnification and Catastrophizing', 'Black & White Thinking', 'Jumping to Conclusions', 'Overgeneralization', 'Personalization', 'Emotional Reasoning', 'Should Statements', 'Mental Filter', 'No Distortion']
num_labels = len(all_labels)
label2id = {label: i for i, label in enumerate(all_labels)}
id2label = {i: label for i, label in enumerate(all_labels)}

def to_multihot(label_str):
    vec = [0.0] * num_labels
    if isinstance(label_str, str):
        for l in label_str.split(','):
            l = l.strip()
            if l in label2id:
                vec[label2id[l]] = 1.0
    return vec

df['label'] = df['distortion_label'].apply(to_multihot)
df.head()


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


# 5. Model Initialization (Multi-label BCE Loss)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=num_labels, 
    id2label=id2label, 
    label2id=label2id,
    problem_type='multi_label_classification'
)


# 6. Training Configuration
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy='epoch',
    save_strategy='epoch',
    load_best_model_at_end=True
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    # Apply sigmoid for independent probabilities
    probs = torch.sigmoid(torch.tensor(logits)).numpy()
    # Threshold at 0.4
    predictions = (probs > 0.4).astype(int)
    metrics = eval_utils.evaluate_predictions(labels, predictions, target_names=list(label2id.keys()))
    return {'f1_macro': metrics['f1_score_macro'], 'f1_micro': metrics['f1_score_micro']}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)


# 7. Train Model
trainer.train()  # Uncomment to run training


# 8. Evaluate on Test Set
test_results = trainer.evaluate(test_dataset)
print(test_results)


# 9. Save Fine-Tuned Model
output_dir = 'backend/models/distortion_model'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f'Model saved to {output_dir}')


