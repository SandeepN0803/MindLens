import os
import json
import time
import pandas as pd
import getpass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Get API key from env or prompt user
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY not found in environment or .env file.")
    api_key = getpass.getpass("Please paste your OpenAI API key (sk-...) and press Enter: ").strip()
    if not api_key:
        print("Error: No API key provided.")
        exit(1)

# Initialize client
client = OpenAI(api_key=api_key)
MODEL_NAME = "gpt-4o-mini"

# Sanity Check
def test_api():
    try:
        print("Running API sanity check...")
        test = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": "Say OK"}], max_tokens=5)
        print("API check passed! Response:", test.choices[0].message.content)
        return True
    except Exception as e:
        print(f"API check failed: {e}")
        return False

# Categories and their definitions
categories = {
    "Magnification and Catastrophizing": "Exaggerating the importance of negative events or expecting the absolute worst-case scenario to happen.",
    "Black & White Thinking": "Viewing situations in extreme, either/or categories with no middle ground or shades of gray.",
    "Jumping to Conclusions": "Making negative interpretations without actual evidence, either through mind reading or fortune telling.",
    "Overgeneralization": "Taking one negative event and seeing it as a never-ending pattern of defeat.",
    "Personalization": "Blaming yourself for something that wasn't entirely your fault, or taking things personally that have nothing to do with you.",
    "Emotional Reasoning": "Assuming that because you feel a certain way, it must be true (e.g., 'I feel like a failure, therefore I am one').",
    "Should Statements": "Motivating yourself with 'shoulds', 'musts', or 'oughts', which often leads to guilt or frustration when expectations aren't met.",
    "Mental Filter": "Focusing exclusively on a single negative detail while ignoring all the positive aspects of a situation.",
    "No Distortion": "A balanced, realistic reflection on an event, acknowledging both positive and negative aspects without cognitive distortions."
}

# Seed examples (to provide context to the LLM)
seed_examples = {
    "Magnification and Catastrophizing": [
        "I felt a tiny pain in my chest and immediately thought I was having a heart attack and going to die.",
        "My boss asked to see me, so I know I'm going to get fired and lose my house."
    ],
    "Black & White Thinking": [
        "If I don't get an A on this test, I'm a complete failure as a student.",
        "Since I ate a piece of cake on my diet, the whole week is ruined and I should just give up."
    ],
    "Jumping to Conclusions": [
        "My friend didn't text back right away, so she must be mad at me for what I said yesterday.",
        "I just know this party is going to be terrible and everyone will think I'm awkward."
    ],
    "Overgeneralization": [
        "I went on one bad date, which proves I'm never going to find love and will be alone forever.",
        "I messed up the recipe; I literally can't do anything right."
    ],
    "Personalization": [
        "My son got a bad grade on his math test. It's because I'm a terrible parent who doesn't help him enough.",
        "The project at work failed, and even though there were five of us, I know it's all my fault."
    ],
    "Emotional Reasoning": [
        "I feel so overwhelmed by this task, so it must be completely impossible to finish.",
        "I feel guilty, so I must have done something horribly wrong even if I can't remember what."
    ],
    "Should Statements": [
        "I really should be exercising every single day if I want to consider myself healthy.",
        "He shouldn't be acting like that; people must always follow the rules."
    ],
    "Mental Filter": [
        "I got a glowing performance review but my manager mentioned one tiny area for improvement, so my review was awful.",
        "I had a great time on vacation except for the one day it rained, which completely ruined the trip."
    ],
    "No Distortion": [
        "I'm disappointed I didn't get the promotion, but I know I've been doing good work and another opportunity will come.",
        "I felt anxious before the presentation, which is normal, but I managed to get through it okay."
    ]
}

PROMPT_TEMPLATE = """You are an expert cognitive behavioral therapist and data generator. Generate {count} realistic, diverse journal entries that reflect the following category: "{category}".

Definition:
{definition}

Examples of this category's tone/style (for reference only — do NOT reuse these sentences, structures, or their key words):
{seed_examples}

CRITICAL — Lexical and structural diversity:
This category is often expressed using a small set of "trigger words" (e.g. "always/never", "ruin/disaster", "should/must", "hate me"). A model trained only on entries containing these obvious words will fail to recognize the same thought pattern expressed in different language. To prevent this:
1. At most 20% of entries may contain an obvious trigger word for this category. The rest must express the same underlying thought pattern through different situations, vocabulary, and indirect phrasing.
2. Vary sentence structure significantly — do not repeat the same grammatical template (e.g. "I feel X, so I must be Y") across entries. Mix first-person reflection, rhetorical questions, recounted dialogue, and stream-of-consciousness fragments.
3. Vary specificity — some entries should be about a very concrete, mundane event; others should be more abstract or about a recurring feeling.

Additional instructions:
4. Vary severity: some mild daily frustrations, others deeper anxious/low-mood thoughts (or balanced, everyday reflections for "No Distortion").
5. Vary topics: relationships, work, school, self-image, health, finances, parenting, friendships, mundane daily events, etc.
6. Make them sound like authentic, human-written journal entries — natural, sometimes messy, never textbook-sounding.
7. Ensure the entries strongly and clearly reflect this specific category to someone trained in CBT, even without the trigger words.

Return your response as a JSON object with a single key "entries" containing a list of exactly {count} strings, like this:
{{"entries": ["Journal entry 1...", "Journal entry 2..."]}}
"""

def generate_entries_for_category(category, definition, count=150):
    seeds = "\\n".join([f"- {ex}" for ex in seed_examples[category]])
    prompt = PROMPT_TEMPLATE.format(
        count=count,
        category=category,
        definition=definition,
        seed_examples=seeds
    )
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )
    
    try:
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("entries", [])
    except Exception as e:
        print(f"Error parsing JSON for {category}: {e}")
        return []

def main():
    if not test_api():
        return
    
    all_entries = []
    
    for category, definition in categories.items():
        print(f"Generating for {category}...")
        
        # Requesting 150 entries in one go might hit max_tokens, so let's do batches of 50.
        category_entries = []
        for i in range(3):
            entries = generate_entries_for_category(category, definition, count=50)
            category_entries.extend(entries)
            print(f"  Batch {i+1}/3: Got {len(entries)} entries")
            time.sleep(2) # Avoid rate limits
            
        print(f"Total for {category}: {len(category_entries)}\n")
        
        for text in category_entries:
            all_entries.append({
                "text": text,
                "distortion_label": category
            })
            
    df = pd.DataFrame(all_entries)
    print(f"Total entries generated: {len(df)}")
    
    assert len(df) > 1000, "Dataset generation failed to produce >1000 entries."
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_distortions_en.csv', index=False)
    print("Saved successfully to data/synthetic_distortions_en.csv")

if __name__ == "__main__":
    main()
