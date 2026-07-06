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

def process_journal_entry(text, manual_language):
    if not text.strip():
        return "Please enter a journal entry."

    # 1. Language Detection
    if manual_language == "Auto-Detect":
        lang_result = detect_language(text)
        language_code = lang_result["language_code"]
        language_name = lang_result["language"]
        lang_confidence = f"{lang_result['confidence']:.2f}"
    else:
        # Map manual language to code
        lang_map = {"English": "en", "Hindi": "hi", "Kannada": "kn", "Telugu": "te", "Tamil": "ta"}
        language_code = lang_map.get(manual_language, "en")
        language_name = manual_language
        lang_confidence = "1.00 (Manual Selection)"
    
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
    output = f"**Detected Language:** {language_name} (Confidence: {lang_confidence})\n\n"
    output += f"**Sentiment:** {sentiment['label']} (Confidence: {sentiment['confidence']:.2f})\n\n"
    
    output += "**Emotions:**\n"
    for em in emotions:
        output += f"- {em['label']}: {em['score']:.2f}\n"
    
    output += "\n**Cognitive Distortions Detected:**\n"
    if not distortions:
         output += "None detected.\n"
    for dist in distortions:
        output += f"- {dist['label']} (Confidence: {dist['confidence']:.2f})\n"
        
    output += "\n**Reframing Suggestions:**\n"
    if not reframings:
        output += "No reframing suggestions needed.\n"
    for ref in reframings:
        output += f"- **{ref['distortion']}**: {ref['reframed']}\n"
        
    return output

with gr.Blocks(title="MindLens Demo") as demo:
    gr.Markdown("# MindLens: Multilingual Mental Health Journal Analyzer")
    gr.Markdown("Detects sentiment, emotions, and cognitive distortions, and provides CBT reframing suggestions.")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input Area
            journal_input = gr.Textbox(
                lines=8, 
                placeholder="Write your journal entry here...",
                label="Journal Entry"
            )
            language_dropdown = gr.Dropdown(
                choices=["Auto-Detect", "English", "Hindi", "Kannada", "Telugu", "Tamil"],
                value="Auto-Detect",
                label="Language Setting"
            )
            submit_btn = gr.Button("Analyze Journal", variant="primary")
            
            gr.Examples(
                examples=[
                    ["I failed the test again, I'm always going to be a failure. Everything is going wrong.", "Auto-Detect"],
                    ["मुझे आज बहुत घबराहट हो रही है, मुझे लगता है कि सब कुछ खराब हो जाएगा।", "Hindi"]
                ],
                inputs=[journal_input, language_dropdown]
            )
            
        with gr.Column(scale=1):
            # Output Area
            analysis_output = gr.Markdown(label="Analysis Results", value="*Results will appear here...*")
            
    # Connect the button to the function
    submit_btn.click(
        fn=process_journal_entry,
        inputs=[journal_input, language_dropdown],
        outputs=analysis_output
    )

if __name__ == "__main__":
    demo.launch()
