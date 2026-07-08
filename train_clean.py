import sys
import os
import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import GroupShuffleSplit
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

sys.path.append('backend')
import eval_utils

print('Loading datasets...')
df1 = pd.read_csv('data/synthetic_distortions_en_v2.csv')
df2 = pd.read_csv('data/synthetic_distortions_multilabel_en.csv')
df = pd.concat([df1, df2], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f'Total rows loaded: {len(df)}')

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

if 'template_id' not in df.columns:
    df['template_id'] = [f'custom_{i}' for i in range(len(df))]
else:
    df['template_id'] = df['template_id'].fillna(pd.Series([f'custom_{i}' for i in range(len(df))]))

gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
train_idx, temp_idx = next(gss.split(df, groups=df['template_id']))
train_df = df.iloc[train_idx]
temp_df = df.iloc[temp_idx].reset_index(drop=True)

gss_val = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
val_idx, test_idx = next(gss_val.split(temp_df, groups=temp_df['template_id']))
val_df = temp_df.iloc[val_idx]
test_df = temp_df.iloc[test_idx]

print(f'Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}')

MODEL_NAME = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=128)

train_dataset = Dataset.from_pandas(train_df[['text', 'label']]).map(tokenize_function, batched=True)
val_dataset = Dataset.from_pandas(val_df[['text', 'label']]).map(tokenize_function, batched=True)
test_dataset = Dataset.from_pandas(test_df[['text', 'label']]).map(tokenize_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=num_labels, 
    id2label=id2label, 
    label2id=label2id,
    problem_type='multi_label_classification'
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    probs = 1 / (1 + np.exp(-logits))  # Sigmoid
    preds = (probs > 0.4).astype(int)
    
    macro_f1 = eval_utils.f1_score(labels, preds, average='macro', zero_division=0)
    micro_f1 = eval_utils.f1_score(labels, preds, average='micro', zero_division=0)
    return {
        'f1_macro': macro_f1,
        'f1_micro': micro_f1
    }

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

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

print('Starting training...')
trainer.train()

print('Evaluating on test set...')
test_results = trainer.evaluate(test_dataset)
print('Test Results:', test_results)

output_dir = 'backend/models/distortion_model'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f'Model saved to {output_dir}')
