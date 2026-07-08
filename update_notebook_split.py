import json

with open('notebooks/distortion_finetuning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update cell 1
cell_1_src = nb['cells'][0]['source']
for i, line in enumerate(cell_1_src):
    if line.startswith('from sklearn.model_selection'):
        cell_1_src[i] = 'from sklearn.model_selection import train_test_split, GroupShuffleSplit\n'

# Update cell 4
nb['cells'][3]['source'] = [
    "# 3. Split Dataset (GroupShuffleSplit to prevent template leakage)\n",
    "if 'template_id' not in df.columns:\n",
    "    df['template_id'] = [f'custom_{i}' for i in range(len(df))]\n",
    "else:\n",
    "    df['template_id'] = df['template_id'].fillna(pd.Series([f'custom_{i}' for i in range(len(df))]))\n",
    "\n",
    "gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)\n",
    "train_idx, temp_idx = next(gss.split(df, groups=df['template_id']))\n",
    "train_df = df.iloc[train_idx]\n",
    "temp_df = df.iloc[temp_idx].reset_index(drop=True)\n",
    "\n",
    "gss_val = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=42)\n",
    "val_idx, test_idx = next(gss_val.split(temp_df, groups=temp_df['template_id']))\n",
    "val_df = temp_df.iloc[val_idx]\n",
    "test_df = temp_df.iloc[test_idx]\n",
    "print(f'Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}')\n"
]

# Uncomment training and evaluate logic
nb['cells'][7]['source'] = [
    "# 7. Train Model\n",
    "trainer.train()\n"
]
nb['cells'][8]['source'] = [
    "# 8. Evaluate on Test Set\n",
    "test_results = trainer.evaluate(test_dataset)\n",
    "print(test_results)\n"
]
nb['cells'][9]['source'] = [
    "# 9. Save Fine-Tuned Model\n",
    "output_dir = '../backend/models/distortion_model'\n",
    "model.save_pretrained(output_dir)\n",
    "tokenizer.save_pretrained(output_dir)\n",
    "print(f'Model saved to {output_dir}')\n"
]

with open('notebooks/distortion_finetuning.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Notebook updated successfully.')
