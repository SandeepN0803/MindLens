import logging
from typing import Dict, Union, Any
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapping of ISO language codes to human-readable names
LANGUAGE_MAP: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "te": "Telugu",
    "ta": "Tamil"
}

def detect_language(text: str) -> Dict[str, Union[str, float]]:
    """
    Detects the language of the given text using the langdetect library.
    
    Args:
        text (str): The input text to analyze.
        
    Returns:
        Dict[str, Union[str, float]]: A dictionary containing:
            - 'language': Human-readable language name (e.g., 'English', 'Hindi', 'uncertain')
            - 'language_code': ISO 639-1 language code (e.g., 'en', 'hi')
            - 'confidence': Confidence score of the detection (float between 0 and 1)
            
    Behavior:
        - If the detected language is not in the supported list (en, hi, kn, te, ta),
          it will default to 'English' / 'en' but retain the actual confidence.
        - If the confidence is below 0.85, it returns 'uncertain' as the language name,
          defaults to 'en' as the code, and retains the actual confidence.
        - If text is empty or detection fails entirely, it defaults to English with 0.0 confidence.
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for language detection.")
        return {
            "language": "English",
            "language_code": "en",
            "confidence": 0.0
        }
        
    try:
        # detect_langs returns a list of Language objects (e.g., [en:0.999995])
        langs = detect_langs(text)
        
        if not langs:
            raise ValueError("No languages detected.")
            
        # The first element is the most probable language
        best_match = langs[0]
        detected_code = best_match.lang
        confidence = round(float(best_match.prob), 4)
        
        # Check if the confidence meets our 0.85 threshold
        if confidence < 0.85:
            logger.info(f"Low confidence ({confidence}) for detected code '{detected_code}'. Defaulting to uncertain/English.")
            return {
                "language": "uncertain",
                "language_code": "en",
                "confidence": confidence
            }
            
        # Map the detected code to our supported languages
        if detected_code in LANGUAGE_MAP:
            return {
                "language": LANGUAGE_MAP[detected_code],
                "language_code": detected_code,
                "confidence": confidence
            }
        else:
            logger.info(f"Detected code '{detected_code}' is not natively supported. Defaulting to English.")
            return {
                # We return 'English' as a fallback, but you might want to return 'uncertain' instead.
                # Project spec says "default to English model", so we'll route it as English.
                "language": "English",
                "language_code": "en",
                "confidence": confidence
            }
            
    except (LangDetectException, ValueError) as e:
        logger.error(f"Language detection failed: {e}. Defaulting to English.")
        return {
            "language": "English",
            "language_code": "en",
            "confidence": 0.0
        }
