import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_dir = 'backend/models/distortion_model'
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)
model.eval()

text = "I went to the grocery store today"
all_labels = ['Magnification and Catastrophizing', 'Black & White Thinking', 'Jumping to Conclusions', 'Overgeneralization', 'Personalization', 'Emotional Reasoning', 'Should Statements', 'Mental Filter', 'No Distortion']

inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=128)
with torch.no_grad():
    outputs = model(**inputs)
logits = outputs.logits
probs = torch.sigmoid(logits).squeeze().tolist()

print("\n--- Neutral Test ---")
for label, prob in zip(all_labels, probs):
    print(f"{label}: {prob:.4f}")
