import sys
import os
import gradio as gr
import json

# Add backend directory to path so we can import the ML modules
sys.path.append(os.path.abspath('backend'))

from lang_detector import detect_language
from sentiment_model import analyze_sentiment
from emotion_model import analyze_emotion, translate_to_english
from distortion_model import detect_distortions
from reframing_engine import reframe_distortions

def process_journal_entry(text):
    if not text.strip():
        return "Please enter a journal entry."

    # 1. Language Detection
    lang_result = detect_language(text)
    language_code = lang_result["language_code"]
    
    # 2. Sentiment & Emotion Analysis
    sentiment = analyze_sentiment(text, language_code)
    emotions = analyze_emotion(text, language_code)
    
    # 3. Translation for Distortion Model (if needed)
    english_text = translate_to_english(text, language_code) if language_code != "en" else text
    
    # 4. Distortion Detection
    distortions = detect_distortions(english_text)
    
    # 5. Reframing
    reframings = reframe_distortions(text, distortions)
    
    # Format output
    output = f"**Detected Language:** {lang_result['language']} (Confidence: {lang_result['confidence']:.2f})\n\n"
    output += f"**Sentiment:** {sentiment['label']} (Confidence: {sentiment['confidence']:.2f})\n\n"
    
    output += "**Emotions:**\n"
    for em in emotions:
        output += f"- {em['label']}: {em['score']:.2f}\n"
    
    output += "\n**Cognitive Distortions Detected:**\n"
    if not distortions:
         output += "None detected.\n"
    for dist in distortions:
        output += f"- {dist['distortion']} (Confidence: {dist['confidence']:.2f})\n"
        
    output += "\n**Reframing Suggestions:**\n"
    if not reframings:
        output += "No reframing suggestions needed.\n"
    for ref in reframings:
        output += f"- {ref}\n"
        
    return output

demo = gr.Interface(
    fn=process_journal_entry,
    inputs=gr.Textbox(lines=5, placeholder="Write your journal entry here... (English, Hindi, Kannada, Telugu, Tamil)"),
    outputs=gr.Markdown(),
    title="MindLens Demo",
    description="Multilingual Mental Health Journal Analyzer. Detects sentiment, emotions, and cognitive distortions, and provides reframing suggestions.",
    examples=[
        ["I failed the test again, I'm always going to be a failure. Everything is going wrong."],
        ["मुझे आज बहुत घबराहट हो रही है, मुझे लगता है कि सब कुछ खराब हो जाएगा।"]
    ]
)

if __name__ == "__main__":
    demo.launch()
