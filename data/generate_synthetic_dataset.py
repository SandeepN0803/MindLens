import os
import csv
import json
import time
from openai import OpenAI

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Set your API key as an environment variable before running:
#   export OPENAI_API_KEY="sk-..."
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

OUTPUT_CSV = "synthetic_distortions_en.csv"
EXAMPLES_PER_CATEGORY = 150
MODEL_NAME = "gpt-4o"  # or 'gpt-3.5-turbo' (drop response_format if using 3.5)

# Merged/disambiguated categories:
# - Magnification folded into Catastrophizing (near-identical in most CBT taxonomies)
# - Mind Reading folded into Jumping to Conclusions (its standard parent category,
#   alongside Fortune Telling)
# - Added "No Distortion" so the classifier learns what a balanced entry looks like,
#   not just "always predict some distortion"
DISTORTION_DEFINITIONS = {
    "Magnification and Catastrophizing": "Exaggerating the importance of negative events, or assuming the absolute worst possible outcome will happen regardless of logic.",
    "Black & White Thinking": "Thinking in absolute extremes (e.g., if something isn't perfect, it's a total failure) with no middle ground. Often uses words like 'always', 'every', or 'never'.",
    "Jumping to Conclusions": "Assuming you know what others are thinking negatively about you (mind reading), or predicting that things will turn out badly without actual evidence (fortune telling).",
    "Overgeneralization": "Seeing a single negative event as a never-ending pattern of defeat. Drawing broad negative conclusions from limited evidence.",
    "Personalization": "Taking disproportionate responsibility and blaming yourself for events outside of your control, or assuming others' negative behavior is entirely because of you.",
    "Emotional Reasoning": "Assuming that because you feel a certain negative way, it must represent objective truth (e.g., 'I feel hopeless, so the situation must be hopeless').",
    "Should Statements": "Having rigid, inflexible rules about how you or others 'should', 'must', or 'ought' to behave, leading to intense guilt, frustration, or anger when expectations aren't met.",
    "Mental Filter": "Focusing exclusively on a single negative detail or event while entirely ignoring or rejecting all positive or neutral aspects of a situation.",
    "No Distortion": "A rational, balanced, and healthy journal entry. It may describe negative events or difficult emotions, but does so objectively without exaggerating, catastrophizing, or employing any cognitive distortions.",
}

# Few-shot seed anchors: kept short and included in the prompt to steer tone
# toward authentic diary writing rather than generic textbook phrasing.
SEED_EXAMPLES = {
    "Magnification and Catastrophizing": [
        "My chest felt tight for a second and now I'm sure something is seriously wrong with my heart.",
    ],
    "Black & White Thinking": [
        "I made one mistake in the presentation, so the whole thing was a complete failure.",
    ],
    "Jumping to Conclusions": [
        "She didn't reply to my text in an hour, she must think I'm annoying now.",
        "I know I'm going to bomb this exam no matter how much I study.",
    ],
    "Overgeneralization": [
        "I forgot her birthday, I always mess up the things that matter to people.",
    ],
    "Personalization": [
        "My friend has been quiet lately, it must be something I did.",
    ],
    "Emotional Reasoning": [
        "I feel like a fraud at work, so I must actually be bad at my job.",
    ],
    "Should Statements": [
        "I should be over this breakup by now, there's something wrong with me for still being sad.",
    ],
    "Mental Filter": [
        "The performance review had eight positive comments and one suggestion, but all I can think about is that one criticism.",
    ],
    "No Distortion": [
        "Today was busy but manageable. I got most of my tasks done and had a nice walk in the evening.",
        "I made a mistake in the meeting, but I corrected it and my manager said it was no big deal.",
    ],
}

# ==============================================================================
# PROMPT TEMPLATE
# ==============================================================================
PROMPT_TEMPLATE = """You are an expert cognitive behavioral therapist and data generator. Generate {count} realistic, diverse journal entries that reflect the following category: "{category}".

Definition:
{definition}

Examples of this category's tone/style (for reference only, do not repeat these):
{seed_examples}

Instructions:
1. Ensure the entries strongly and clearly reflect this specific category.
2. Vary the severity: some mild daily frustrations, others deeper anxious/low-mood thoughts (or balanced, everyday reflections for "No Distortion").
3. Vary the phrasing, length (short sentence to a paragraph), and tone.
4. Vary the topics: relationships, work, school, self-image, health, mundane daily events, etc.
5. Make them sound like authentic, human-written journal entries, not textbook examples.
6. Return your response as a JSON object with a single key "entries" containing a list of exactly {count} strings, like this:
{{"entries": ["Journal entry 1...", "Journal entry 2..."]}}
"""

# ==============================================================================
# GENERATION
# ==============================================================================
def generate_entries_for_category(category: str, definition: str, count: int) -> list:
    print(f"Generating {count} examples for {category}...")
    seeds = "\n".join(f"- {s}" for s in SEED_EXAMPLES.get(category, []))
    prompt = PROMPT_TEMPLATE.format(
        category=category, definition=definition, count=count, seed_examples=seeds
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that outputs JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"} if "gpt-4" in MODEL_NAME else None,
        )
        content = response.choices[0].message.content

        try:
            data = json.loads(content)
            if isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        return v
                return []
            elif isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            print(f"  [warn] Failed to parse JSON for {category}. Raw output: {content[:200]}...")
            return []

    except Exception as e:
        print(f"  [warn] Error during API call for {category}: {e}")
        return []


def main():
    all_dataset_rows = []
    batch_size = 50

    for category, definition in DISTORTION_DEFINITIONS.items():
        batches = EXAMPLES_PER_CATEGORY // batch_size
        remainder = EXAMPLES_PER_CATEGORY % batch_size

        category_entries = []
        for _ in range(batches):
            category_entries.extend(generate_entries_for_category(category, definition, batch_size))
            time.sleep(2)  # avoid rate limits

        if remainder > 0:
            category_entries.extend(generate_entries_for_category(category, definition, remainder))
            time.sleep(2)

        for entry in category_entries:
            if isinstance(entry, str) and entry.strip():
                all_dataset_rows.append({"text": entry.strip(), "label": category, "language": "en"})

        print(f"Successfully generated {len(category_entries)} entries for {category}.")

    # Single deduplication pass over the full in-memory dataset
    print("\nRunning deduplication pass...")
    seen_texts = set()
    deduped_rows = []
    for row in all_dataset_rows:
        norm_text = row["text"].lower().strip()
        if norm_text and norm_text not in seen_texts:
            seen_texts.add(norm_text)
            deduped_rows.append(row)
    print(f"Removed {len(all_dataset_rows) - len(deduped_rows)} exact duplicate entries.")

    # Single write pass
    print(f"Writing {len(deduped_rows)} rows to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "distortion_label", "language"])
        for row in deduped_rows:
            writer.writerow([row["text"], row["label"], row["language"]])

    print("\nClass distribution:")
    counts = {}
    for row in deduped_rows:
        counts[row["label"]] = counts.get(row["label"], 0) + 1
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")

    print("\nDone!")


if __name__ == "__main__":
    main()
