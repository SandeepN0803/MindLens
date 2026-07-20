import os
import json
import time
import requests
import pandas as pd
import re

# Define the 9 categories + No Distortion with descriptions and seed examples
CATEGORIES = {
    "Magnification and Catastrophizing": {
        "definition": "Exaggerating the importance of negative events or minimizing the importance of positive events, often predicting the worst possible outcome.",
        "seed_examples": [
            "If I fail this test, my whole life is ruined.",
            "My chest hurts a little, I must be having a heart attack.",
            "I made a typo in the email, my boss is going to fire me."
        ]
    },
    "Black & White Thinking": {
        "definition": "Thinking in absolute, all-or-nothing terms. If a situation falls short of perfect, it is seen as a total failure.",
        "seed_examples": [
            "I ate a piece of cake on my diet, so I'm a complete failure.",
            "If I'm not the best in the class, I'm the worst.",
            "He didn't agree with my idea, so he must hate me."
        ]
    },
    "Jumping to Conclusions": {
        "definition": "Making a negative interpretation even though there are no definite facts that convincingly support the conclusion. This includes mind reading and fortune telling.",
        "seed_examples": [
            "She didn't text me back immediately, she must be ignoring me.",
            "I just know this presentation is going to go terribly.",
            "They're whispering, they must be talking about me."
        ]
    },
    "Overgeneralization": {
        "definition": "Viewing a single negative event as a never-ending pattern of defeat. Using words like 'always' or 'never'.",
        "seed_examples": [
            "I didn't get the job. I will never get hired anywhere.",
            "He yelled at me. People are always mean to me.",
            "I forgot my keys again, I always mess everything up."
        ]
    },
    "Personalization": {
        "definition": "Believing that you are entirely to blame for something bad that happened, or that other people's behavior is a reaction to you, without considering other factors.",
        "seed_examples": [
            "My son is struggling in school, it must be because I'm a bad mother.",
            "It rained on our picnic, it's all my fault for choosing today.",
            "My friend is quiet today, I must have done something to upset her."
        ]
    },
    "Emotional Reasoning": {
        "definition": "Assuming that negative emotions necessarily reflect the way things really are. 'I feel it, therefore it must be true.'",
        "seed_examples": [
            "I feel so overwhelmed, so my problems must be impossible to solve.",
            "I feel like a fraud, so I must really be incompetent.",
            "I feel guilty, so I must have done something bad."
        ]
    },
    "Should Statements": {
        "definition": "Trying to motivate oneself or judging others with 'shoulds', 'musts', or 'oughts'. This leads to guilt or frustration when expectations aren't met.",
        "seed_examples": [
            "I should be exercising every day, I'm so lazy.",
            "He shouldn't have spoken to me that way.",
            "I must never make mistakes at work."
        ]
    },
    "Mental Filter": {
        "definition": "Focusing exclusively on a single negative detail and dwelling on it, so that the vision of all reality becomes darkened, ignoring the positives.",
        "seed_examples": [
            "I got an A- on the test, but I can only think about the one question I missed.",
            "My performance review was great, but my boss made one minor suggestion and now I feel terrible.",
            "I had a great day but I spilled coffee on my shirt, so the whole day is ruined."
        ]
    },
    "No Distortion": {
        "definition": "A balanced, realistic, and objective thought that acknowledges both positives and negatives without cognitive distortions.",
        "seed_examples": [
            "I made a mistake at work, but I learned from it and will do better next time.",
            "I'm disappointed I didn't win the game, but I played well.",
            "I had an argument with my friend, but we can talk it out later."
        ]
    }
}

PROMPT_TEMPLATE = """You are an expert cognitive behavioral therapist and data generator. Generate {count} realistic, diverse journal entries that reflect the following category: "{category}".

Definition:
{definition}

Examples of this category's tone/style (for reference only — do NOT reuse these sentences, structures, or their key words):
{seed_examples}

CRITICAL — Lexical and structural diversity:
This category is often expressed using a small set of "trigger words" (e.g. "always/never", "ruin/disaster", "should/must", "hate me"). A model trained only on entries containing these obvious words will fail to recognize the same thought pattern expressed in different language. To prevent this:
1. At most 20% of entries may contain an obvious trigger word for this category. The rest must express the same underlying thought pattern through descriptive situations, indirect reasoning, physical sensations, or recalled dialogue.
2. Vary the sentence structure: use declarative statements, internal monologues, recounted interactions, rhetorical questions, and varying lengths.
3. Keep the output strictly in valid JSON format.

Output Format: Return ONLY a valid JSON array of strings. Do not include markdown formatting or explanations.
Example:
[
  "First journal entry...",
  "Second journal entry...",
  "Third journal entry..."
]"""

# The local Ollama endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"
# Choose a fast, capable model available in Ollama (e.g. llama3, phi3, mistral)
MODEL_NAME = "llama3.1" # Change this if you use a different model

def generate_entries_for_category(category, definition, seed_examples, count=50):
    prompt = PROMPT_TEMPLATE.format(
        count=count,
        category=category,
        definition=definition,
        seed_examples="\n".join(f"- {s}" for s in seed_examples)
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.8, # slightly higher temp for diversity
            "num_predict": 2048
        }
    }

    print(f"Calling Ollama ({MODEL_NAME}) for {count} entries in {category}...")
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Parse the JSON response
        text = data.get("response", "").strip()
        entries = []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                # Check if it's {"entries": [...]}
                for v in parsed.values():
                    if isinstance(v, list):
                        entries = v
                        break
                # If still empty, it might be {"1": "text", "2": "text"}
                if not entries:
                    for v in parsed.values():
                        if isinstance(v, str):
                            entries.append(v)
            elif isinstance(parsed, list):
                entries = parsed
        except Exception:
            pass

        if not isinstance(entries, list) or len(entries) == 0:
            print(f"Warning: Unexpected JSON format. Expected list, got {type(parsed)}")
            print("Raw text:", text)
            return []
            
        print(f"  -> Generated {len(entries)} valid entries.")
        return entries
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama. Is Ollama running on your machine?")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Ollama for {category}: {e}")
        print("Raw output:", text)
        return []
    except Exception as e:
        print(f"Error generating entries for {category}: {e}")
        return []

def main():
    # Sanity Check (generate just 2 entries for one category to test)
    print("Performing sanity check with Ollama...")
    cat_name = list(CATEGORIES.keys())[0]
    cat_data = CATEGORIES[cat_name]
    
    test_entries = generate_entries_for_category(
        category=cat_name,
        definition=cat_data["definition"],
        seed_examples=cat_data["seed_examples"],
        count=2
    )
    
    if not test_entries:
        print("Sanity check failed! Please ensure Ollama is running and the model is downloaded.")
        return
        
    print(f"\nSanity check successful! Model returned:\n{test_entries}\n")
    print("Proceeding with full generation loop (this may take a while depending on your hardware)...\n")

    # Generate the dataset
    all_rows = []
    
    output_path = "data/synthetic_distortions_en_ollama.csv"
    # Ensure file is clear or write headers if it doesn't exist
    if not os.path.exists(output_path):
        if not os.path.exists("data"):
            os.makedirs("data")
        pd.DataFrame(columns=["text", "distortion_label", "language"]).to_csv(output_path, index=False)
        existing_df = pd.DataFrame(columns=["text", "distortion_label", "language"])
    else:
        existing_df = pd.read_csv(output_path)

    # Regex for trigger words
    trigger_regex = re.compile(r'\b(always|never|should|must|ought|ruin|disaster|hate|completely|worthless|everyone|nobody|fault|terrible|useless|stupid)\b', re.IGNORECASE)

    for category, spec in CATEGORIES.items():
        print(f"\n--- Generating for: {category} ---")
        
        # Load existing entries for this category
        cat_existing = existing_df[existing_df['distortion_label'] == category]
        category_entries = set(cat_existing['text'].dropna().tolist())
        trigger_count = sum(bool(trigger_regex.search(str(text))) for text in category_entries)
        
        # Generate 100 unique entries per category
        target = 100
        trigger_budget = int(target * 0.20)  # max 20 trigger entries

        
        batch_size = 50
        max_attempts = 15
        attempts = 0
        
        while len(category_entries) < target and attempts < max_attempts:
            needed = target - len(category_entries)
            current_batch = min(batch_size, needed * 2) # ask for more to account for discards
            
            entries = generate_entries_for_category(
                category=category,
                definition=spec["definition"],
                seed_examples=spec["seed_examples"],
                count=current_batch
            )
            
            # Add to set to guarantee uniqueness and check triggers
            new_rows = []
            for e in entries:
                if isinstance(e, str) and len(e.strip()) > 5:
                    text_val = e.strip()
                    if text_val not in category_entries:
                        has_trigger = bool(trigger_regex.search(text_val))
                        
                        if has_trigger and trigger_count >= trigger_budget:
                            continue # skip, we're out of trigger budget
                            
                        category_entries.add(text_val)
                        if has_trigger:
                            trigger_count += 1
                        
                        new_rows.append({"text": text_val, "distortion_label": category, "language": "en"})
                        
                        if len(category_entries) >= target:
                            break
            
            # Append new rows incrementally to avoid losing progress
            if new_rows:
                pd.DataFrame(new_rows).to_csv(output_path, mode='a', header=False, index=False)
            
            attempts += 1
            print(f"  Progress: {len(category_entries)}/{target} unique entries.")
            time.sleep(1) # brief pause
            
        if len(category_entries) < target:
            print(f"Warning: Only generated {len(category_entries)} for {category} after {max_attempts} attempts.")
            
        # Append to master list just for tracking
        for text in category_entries:
            all_rows.append({"text": text, "distortion_label": category, "language": "en"})

    print(f"\nGeneration complete! Total rows: {len(all_rows)}")
    
    # Read the final file, shuffle it, and overwrite
    df = pd.read_csv(output_path)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    print(f"Saved successfully and shuffled to {output_path}")

if __name__ == "__main__":
    main()
