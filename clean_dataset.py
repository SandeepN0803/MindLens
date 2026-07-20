import pandas as pd
import re
import os

df = pd.read_csv('data/synthetic_distortions_en_ollama.csv')

# The 5 categories generated before the regex filter was enforced
old_categories = [
    'Jumping to Conclusions',
    'Magnification and Catastrophizing',
    'Overgeneralization',
    'Black & White Thinking',
    'Personalization'
]

# The remaining categories that were generated WITH the regex filter
new_categories = [
    'Should Statements',
    'Emotional Reasoning',
    'Mental Filter',
    'No Distortion'
]

trigger_regex = re.compile(r'\b(always|never|should|must|ought|ruin|disaster|hate|completely|worthless|everyone|nobody|fault|terrible|useless|stupid)\b', re.IGNORECASE)

df_old = df[df['distortion_label'].isin(old_categories)].copy()
df_new = df[df['distortion_label'].isin(new_categories)].copy()

# Filter out trigger rows from the old categories
valid_old_rows = []
for idx, row in df_old.iterrows():
    text = str(row['text'])
    # Only keep it if it doesn't have a trigger word
    if not trigger_regex.search(text):
        valid_old_rows.append(row)

df_old_filtered = pd.DataFrame(valid_old_rows)

print("Original old rows:", len(df_old))
print("Filtered old rows:", len(df_old_filtered))
print("Rows per category after filter:")
print(df_old_filtered['distortion_label'].value_counts())

# Combine them back
df_final = pd.concat([df_old_filtered, df_new], ignore_index=True)

# Save the cleaned dataset back to the file
df_final.to_csv('data/synthetic_distortions_en_ollama.csv', index=False)
print(f"Cleaned dataset saved. Total rows: {len(df_final)}")
