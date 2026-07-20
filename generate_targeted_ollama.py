import os
import json
import time
import requests
import pandas as pd
import re

CATEGORIES = {
    "Jumping to Conclusions": {
        "definition": "Making a negative interpretation even though there are no definite facts that convincingly support the conclusion. This includes mind reading and fortune telling.",
        "seed_examples": [
            "She didn't text me back immediately, she must be ignoring me.",
            "I just know this presentation is going to go terribly.",
            "They're whispering, they must be talking about me."
        ],
        "target": 150,
        "trigger_rate": 0.35
    },
    "Overgeneralization": {
        "definition": "Viewing a single negative event as a never-ending pattern of defeat. Using words like 'always' or 'never'.",
        "seed_examples": [
            "I didn't get the job. I will never get hired anywhere.",
            "He yelled at me. People are always mean to me.",
            "I forgot my keys again, I always mess everything up."
        ],
        "target": 150,
        "trigger_rate": 0.35
    },
    "No Distortion": {
        "definition": "A balanced, realistic, and objective thought that acknowledges both positives and negatives without cognitive distortions.",
        "seed_examples": [
            "I made a mistake at work, but I learned from it and will do better next time.",
            "I'm disappointed I didn't win the game, but I played well.",
            "I had an argument with my friend, but we can talk it out later."
        ],
        "target": 100,
        "trigger_rate": 0.20
    }
}

PROMPT_TEMPLATE = """You are an expert cognitive behavioral therapist and data generator. Generate {count} realistic, diverse journal entries that reflect the following category: "{category}".

Definition:
{definition}

Examples of this category's tone/style (for reference only — do NOT reuse these sentences, structures, or their key words):
{seed_examples}

CRITICAL — Lexical and structural diversity:
This category is often expressed using a small set of "trigger words" (e.g. "always/never", "ruin/disaster", "should/must", "hate me"). A model trained only on entries containing these obvious words will fail to recognize the same thought pattern expressed in different language. To prevent this:
1. At most {trigger_rate_pct}% of entries may contain an obvious trigger word for this category. The rest must express the same underlying thought pattern through descriptive situations, indirect reasoning, physical sensations, or recalled dialogue.
2. Vary the sentence structure: use declarative statements, internal monologues, recounted interactions, rhetorical questions, and varying lengths.
3. Keep the output strictly in valid JSON format.

Output Format: Return ONLY a valid JSON array of strings. Do not include markdown formatting or explanations.
Example:
[
  "First journal entry...",
  "Second journal entry...",
  "Third journal entry..."
]"""

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

def generate_entries(category, definition, seed_examples, count, trigger_rate):
    prompt = PROMPT_TEMPLATE.format(
        count=count,
        category=category,
        definition=definition,
        seed_examples="\n".join(f"- {s}" for s in seed_examples),
        trigger_rate_pct=int(trigger_rate * 100)
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 2048
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        text = data.get("response", "").strip()
        entries = []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        entries = v
                        break
                if not entries:
                    for v in parsed.values():
                        if isinstance(v, str):
                            entries.append(v)
            elif isinstance(parsed, list):
                entries = parsed
        except Exception:
            pass

        if not isinstance(entries, list):
            return []
            
        return entries
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    output_path = "data/synthetic_distortions_en_ollama.csv"
    existing_df = pd.read_csv(output_path)
    trigger_regex = re.compile(r'\b(always|never|should|must|ought|ruin|disaster|hate|completely|worthless|everyone|nobody|fault|terrible|useless|stupid)\b', re.IGNORECASE)

    for category, spec in CATEGORIES.items():
        print(f"\n--- Generating for: {category} ---")
        cat_existing = existing_df[existing_df['distortion_label'] == category]
        category_entries = set(cat_existing['text'].dropna().tolist())
        trigger_count = sum(bool(trigger_regex.search(str(text))) for text in category_entries)
        
        target = spec['target']
        trigger_budget = int(target * spec['trigger_rate'])
        
        batch_size = 50
        max_attempts = 15
        attempts = 0
        
        while len(category_entries) < target and attempts < max_attempts:
            needed = target - len(category_entries)
            current_batch = min(batch_size, needed * 2)
            
            entries = generate_entries(category, spec["definition"], spec["seed_examples"], current_batch, spec["trigger_rate"])
            
            new_rows = []
            for e in entries:
                if isinstance(e, str) and len(e.strip()) > 5:
                    text_val = e.strip()
                    if text_val not in category_entries:
                        has_trigger = bool(trigger_regex.search(text_val))
                        if has_trigger and trigger_count >= trigger_budget:
                            continue
                            
                        category_entries.add(text_val)
                        if has_trigger: trigger_count += 1
                        
                        # Mark relaxed constraints for documentation, but don't break csv schema
                        new_rows.append({"text": text_val, "distortion_label": category, "language": "en"})
                        
                        if len(category_entries) >= target:
                            break
            
            if new_rows:
                pd.DataFrame(new_rows).to_csv(output_path, mode='a', header=False, index=False)
            
            attempts += 1
            print(f"  Progress: {len(category_entries)}/{target} unique entries.")
            time.sleep(1)
            
    # Shuffle
    df = pd.read_csv(output_path)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    print("Done")

if __name__ == "__main__":
    main()
