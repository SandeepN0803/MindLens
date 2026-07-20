import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import sys
sys.path.append('backend')
from eval_utils import evaluate_predictions

model_dir = 'backend/models/distortion_model'
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)
model.eval()

import os
import json
threshold_path = os.path.join(model_dir, 'best_thresholds.json')
if os.path.exists(threshold_path):
    with open(threshold_path, 'r') as f:
        best_thresholds = json.load(f)
        # Convert string keys to ints
        best_thresholds = {int(k): float(v) for k, v in best_thresholds.items()}
else:
    best_thresholds = {i: 0.4 for i in range(9)}
print(f"Using per-class thresholds: {best_thresholds}")

# 10 completely organic sentences, one for each core distortion + 1 no distortion
organic_sentences = [
    # Magnification and Catastrophizing
    ("I have a slight headache, which probably means I have a brain tumor and I'm going to die next week.", "Magnification and Catastrophizing"),
    # Black & White Thinking
    ("If I don't get the lead role in the play, my entire acting career is over and I'm worthless.", "Black & White Thinking"),
    # Jumping to Conclusions
    ("I noticed the manager closed her door when I walked by, she's definitely planning to lay me off.", "Jumping to Conclusions"),
    # Overgeneralization
    ("I stumbled over a word during my presentation, which just proves I'm incapable of public speaking ever.", "Overgeneralization"),
    # Personalization
    ("It started raining just as the outdoor concert began, I bring bad luck to everyone around me.", "Personalization"),
    # Emotional Reasoning
    ("I woke up feeling really anxious this morning, so I just know something terrible is going to happen today.", "Emotional Reasoning"),
    # Should Statements
    ("I ought to be married by now, and because I'm not, there's a fundamental flaw in who I am.", "Should Statements"),
    # Mental Filter
    ("The chef said my dish was brilliant and cooked perfectly, but added a pinch of salt at the end. My dish was a complete disaster.", "Mental Filter"),
    # No Distortion
    ("I didn't get the grade I wanted on the midterm, but I know what I need to study differently for the final.", "No Distortion"),
    # Multi-label (Jumping to Conclusions + Personalization + Emotional Reasoning)
    ("I feel so guilty, my friend didn't invite me to the party, so they must hate me and it's because I'm too annoying.", "Jumping to Conclusions,Personalization,Emotional Reasoning")
]

all_labels = ['Magnification and Catastrophizing', 'Black & White Thinking', 'Jumping to Conclusions', 'Overgeneralization', 'Personalization', 'Emotional Reasoning', 'Should Statements', 'Mental Filter', 'No Distortion']
label2id = {l: i for i, l in enumerate(all_labels)}

print("Evaluating Organic Test Set...")
y_true = []
y_pred = []

for text, true_label_str in organic_sentences:
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.sigmoid(logits).squeeze().tolist()
    
    # Threshold using best_thresholds
    pred_vec = [1 if p >= best_thresholds[i] else 0 for i, p in enumerate(probs)]
    y_pred.append(pred_vec)
    
    # Ground truth
    true_vec = [0] * len(all_labels)
    for l in true_label_str.split(','):
        true_vec[label2id[l.strip()]] = 1
    y_true.append(true_vec)

    # Print individual results
    pred_labels = [all_labels[i] for i, val in enumerate(pred_vec) if val == 1]
    print(f"\nText: {text}")
    print(f"True: {true_label_str}")
    print(f"Pred: {', '.join(pred_labels)}")
    print(f"Probs: {[round(p, 3) for p in probs]}")

metrics = evaluate_predictions(y_true, y_pred)
print("\n--- Organic Set Metrics ---")
print(f"Macro F1: {metrics.get('f1_score_macro', 0):.3f}")
print(f"Micro F1: {metrics.get('f1_score_micro', 0):.3f}")
print(f"Exact Match: {metrics.get('accuracy', 0):.3f}")
