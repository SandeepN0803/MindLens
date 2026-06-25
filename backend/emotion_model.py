import logging
from typing import List, Dict, Union, Any
from transformers import pipeline

logger = logging.getLogger(__name__)

# Global model variables
_emotion_pipeline = None
_translation_pipelines: Dict[str, Any] = {}

def load_emotion_model() -> None:
    """
    Loads the primary emotion classification pipeline.
    """
    global _emotion_pipeline
    if _emotion_pipeline is None:
        logger.info("Loading Emotion model (j-hartmann/emotion-english-distilroberta-base)...")
        try:
            _emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
        except Exception as e:
            logger.error(f"Failed to load Emotion model: {e}")

def get_translation_model(lang_code: str):
    """
    Lazily loads the translation model for a specific language code.
    Using Helsinki-NLP/opus-mt-{lang}-en
    """
    global _translation_pipelines
    if lang_code not in _translation_pipelines:
        model_name = f"Helsinki-NLP/opus-mt-{lang_code}-en"
        logger.info(f"Loading translation model {model_name}...")
        try:
            _translation_pipelines[lang_code] = pipeline("translation", model=model_name)
        except Exception as e:
            logger.error(f"Failed to load translation model for {lang_code}: {e}")
            return None
    return _translation_pipelines.get(lang_code)

def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translates non-English text to English.
    If the translation model fails or is unavailable, returns the original text as fallback.
    """
    if source_lang == "en":
        return text
        
    # Some language codes might need mapping to match Helsinki-NLP's supported codes
    # For instance, Helsinki-NLP might not have a direct model for every dialect,
    # but works for the major ones (hi, te, ta, etc.)
    # In a production app, we would handle missing models gracefully.
    translator = get_translation_model(source_lang)
    if translator is None:
        logger.warning(f"No translation available for {source_lang}. Passing original text.")
        return text
        
    try:
        translated_result = translator(text)
        translated_text = translated_result[0]['translation_text']
        logger.debug(f"Translated '{text}' to '{translated_text}'")
        return translated_text
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text

def analyze_emotion(text: str, language_code: str) -> List[Dict[str, Union[str, float]]]:
    """
    Analyzes emotions in text. Translates to English first if necessary.
    
    Args:
        text (str): The journal entry.
        language_code (str): The ISO 639-1 language code.
        
    Returns:
        List[Dict[str, Union[str, float]]]: Top 3 emotions with confidence scores.
        Format: [{'label': 'joy', 'confidence': 0.85}, ...]
    """
    global _emotion_pipeline
    
    if _emotion_pipeline is None:
        load_emotion_model()
        
    if not text.strip() or _emotion_pipeline is None:
        return []

    # Translate if not English
    english_text = translate_to_english(text, language_code)
    
    try:
        # returns [[{'label': 'joy', 'score': 0.8}, ...]]
        results = _emotion_pipeline(english_text)[0]
        
        # Sort by score descending
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Take top 3
        top_3 = sorted_results[:3]
        
        # Format the output
        formatted_emotions = [
            {
                "label": item['label'],
                "confidence": round(item['score'], 4)
            }
            for item in top_3
        ]
        return formatted_emotions
        
    except Exception as e:
        logger.error(f"Emotion analysis failed: {e}")
        return []

# Quick local test
if __name__ == "__main__":
    load_emotion_model()
    # Let's assume we mock translation if models aren't downloaded yet.
    # We will test an English phrase for now.
    print(analyze_emotion("I was terrified when I heard the loud noise.", "en"))
