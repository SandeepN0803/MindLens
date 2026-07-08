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


# 1. Load Datasets (Single-label + Targeted Multi-label)
df1 = pd.read_csv('data/synthetic_distortions_en.csv')
df2 = pd.read_csv('data/synthetic_distortions_multilabel_en.csv')
df = pd.concat([df1, df2], ignore_index=True)
# Shuffle the dataset so multi-label examples are distributed
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f'Total rows loaded: {len(df)}')
df.head()


# 3. Split Dataset (GroupShuffleSplit to prevent template leakage)
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


# 7. Train Model
trainer.train()


# 8. Evaluate on Test Set
test_results = trainer.evaluate(test_dataset)
print(test_results)


# 9. Save Fine-Tuned Model
output_dir = 'backend/models/distortion_model'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f'Model saved to {output_dir}')


# 9. Save Fine-Tuned Model
# output_dir = 'backend/models/distortion_model'
# model.save_pretrained(output_dir)
# tokenizer.save_pretrained(output_dir)
# print(f'Model saved to {output_dir}')
