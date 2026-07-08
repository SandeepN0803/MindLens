import os
import csv
import json
import time
from openai import OpenAI

# ==============================================================================
# CONFIGURATION
# ==============================================================================
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

OUTPUT_CSV = "synthetic_distortions_multilabel_en.csv"
EXAMPLES_PER_PAIR = 40
MODEL_NAME = "gpt-4o"

DISTORTION_PAIRS = [
    ("Magnification and Catastrophizing", "Emotional Reasoning"),
    ("Should Statements", "Personalization"),
    ("Black & White Thinking", "Overgeneralization"),
    ("Mental Filter", "Jumping to Conclusions"),
    ("Magnification and Catastrophizing", "Jumping to Conclusions"),
    ("Personalization", "Emotional Reasoning")
]

PROMPT_TEMPLATE = """You are an expert cognitive behavioral therapist and data generator. 
Generate {count} realistic, diverse journal entries that simultaneously exhibit BOTH of the following cognitive distortions:
1. {cat1}
2. {cat2}

Instructions:
1. Ensure the entries strongly and clearly reflect both specific categories interacting together in a natural way.
2. Vary the severity: some mild daily frustrations, others deeper anxious/low-mood thoughts.
3. Vary the phrasing, length (short sentence to a paragraph), and tone.
4. Make them sound like authentic, human-written journal entries, not textbook examples.
5. Return your response as a JSON object with a single key "entries" containing a list of exactly {count} strings, like this:
{{"entries": ["Journal entry 1...", "Journal entry 2..."]}}
"""

def generate_entries_for_pair(cat1: str, cat2: str, count: int) -> list:
    print(f"Generating {count} examples for {cat1} + {cat2}...")
    prompt = PROMPT_TEMPLATE.format(cat1=cat1, cat2=cat2, count=count)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that outputs JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content

        try:
            data = json.loads(content)
            if isinstance(data, dict) and "entries" in data:
                return data["entries"]
            return []
        except json.JSONDecodeError:
            print(f"  [warn] Failed to parse JSON. Raw output: {content[:200]}...")
            return []
    except Exception as e:
        print(f"  [warn] Error during API call: {e}")
        return []

def main():
    all_dataset_rows = []
    batch_size = 20

    for cat1, cat2 in DISTORTION_PAIRS:
        batches = EXAMPLES_PER_PAIR // batch_size
        remainder = EXAMPLES_PER_PAIR % batch_size
        
        category_entries = []
        for _ in range(batches):
            category_entries.extend(generate_entries_for_pair(cat1, cat2, batch_size))
            time.sleep(2)

        if remainder > 0:
            category_entries.extend(generate_entries_for_pair(cat1, cat2, remainder))
            time.sleep(2)

        label_str = f"{cat1},{cat2}"
        for entry in category_entries:
            if isinstance(entry, str) and entry.strip():
                all_dataset_rows.append({"text": entry.strip(), "label": label_str, "language": "en"})

        print(f"Successfully generated {len(category_entries)} entries for {label_str}.")

    print(f"Writing {len(all_dataset_rows)} rows to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "distortion_label", "language"])
        for row in all_dataset_rows:
            writer.writerow([row["text"], row["label"], row["language"]])

    print("\nDone!")

if __name__ == "__main__":
    main()
