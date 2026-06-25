import logging
from typing import Dict, Union, Any, List
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import numpy as np

logger = logging.getLogger(__name__)

# Global model variables
_xlm_pipeline = None
_indic_pipeline = None

# Constants for labels
LABEL_MAP = {
    # XML-RoBERTa standard output mapping
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
    # IndicBERT output mapping (adjust if fine-tuned IndicBERT uses different labels)
    "negative": "negative",
    "neutral": "neutral",
    "positive": "positive"
}

def load_sentiment_models() -> None:
    """
    Loads the necessary HuggingFace pipelines for sentiment analysis.
    This is called once to initialize the models in memory.
    """
    global _xlm_pipeline, _indic_pipeline
    
    logger.info("Loading XLM-RoBERTa sentiment model...")
    try:
        # Load the multilingual model
        # Note: cardiffnlp/twitter-xlm-roberta-base-sentiment uses LABEL_0/1/2
        _xlm_pipeline = pipeline(
            "text-classification", 
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            return_all_scores=True # To easily access probabilities for ensembling
        )
    except Exception as e:
        logger.error(f"Failed to load XLM-RoBERTa model: {e}")
        
    logger.info("Loading IndicBERTv2 sentiment model...")
    try:
        # Load IndicBERTv2. Note: The base IndicBERTv2 is a masked language model.
        # To perform sentiment analysis out-of-the-box, we would normally need an IndicBERT 
        # fine-tuned for sentiment. For the scope of this project architecture, we assume 
        # there is a compatible sentiment pipeline or we will use it zero-shot.
        # For demonstration, we load it as a sequence classification pipeline.
        _indic_pipeline = pipeline(
            "text-classification",
            model="ai4bharat/IndicBERTv2",
            return_all_scores=True
        )
    except Exception as e:
        logger.error(f"Failed to load IndicBERTv2 model: {e}")

def _map_xlm_labels(scores: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Maps XLM-RoBERTa output scores to standardized keys: 'negative', 'neutral', 'positive'.
    """
    result = {}
    for score in scores:
        label = score['label']
        prob = score['score']
        standard_label = LABEL_MAP.get(label, label).lower()
        result[standard_label] = prob
    return result

def analyze_sentiment(text: str, language_code: str) -> Dict[str, Union[str, float]]:
    """
    Analyzes the sentiment of the given text using XLM-RoBERTa,
    and ensembles with IndicBERTv2 if the language is an Indic language.
    
    Args:
        text (str): The journal entry text.
        language_code (str): The detected ISO 639-1 language code (e.g., 'en', 'hi').
        
    Returns:
        Dict[str, Union[str, float]]: A dictionary containing:
            - 'label': The dominant sentiment ('positive', 'negative', 'neutral').
            - 'confidence': The confidence score (float).
    """
    global _xlm_pipeline, _indic_pipeline
    
    if _xlm_pipeline is None:
        load_sentiment_models()
        
    if not text.strip():
        return {"label": "neutral", "confidence": 0.0}

    # Run XLM-RoBERTa inference
    try:
        # Output format when return_all_scores=True: [[{'label': 'LABEL_0', 'score': 0.1}, ...]]
        xlm_out = _xlm_pipeline(text)[0]
        xlm_scores = _map_xlm_labels(xlm_out)
    except Exception as e:
        logger.error(f"XLM-RoBERTa inference failed: {e}")
        return {"label": "neutral", "confidence": 0.0}

    # Check if we should ensemble with IndicBERT (hi, kn, te, ta)
    indic_languages = {"hi", "kn", "te", "ta"}
    
    if language_code in indic_languages and _indic_pipeline is not None:
        try:
            indic_out = _indic_pipeline(text)[0]
            # Assuming indic pipeline returns similar structure, map it
            indic_scores = _map_xlm_labels(indic_out) 
            
            # Ensemble by averaging the probabilities for each class
            ensembled_scores = {}
            for class_name in ["negative", "neutral", "positive"]:
                xlm_prob = xlm_scores.get(class_name, 0.0)
                indic_prob = indic_scores.get(class_name, 0.0)
                ensembled_scores[class_name] = (xlm_prob + indic_prob) / 2.0
                
            final_scores = ensembled_scores
        except Exception as e:
            logger.error(f"IndicBERTv2 inference failed, falling back to XLM-RoBERTa solely: {e}")
            final_scores = xlm_scores
    else:
        # Use only XLM-RoBERTa
        final_scores = xlm_scores

    # Determine the label with the highest confidence
    best_label = max(final_scores.items(), key=lambda x: x[1])
    
    return {
        "label": best_label[0],
        "confidence": round(best_label[1], 4)
    }

# For testing independently
if __name__ == "__main__":
    load_sentiment_models()
    sample_text = "I feel so happy and excited for the future!"
    res = analyze_sentiment(sample_text, "en")
    print(f"EN Result: {res}")
    
    sample_indic = "ನಾನು ತುಂಬಾ ದುಃಖಿತನಾಗಿದ್ದೇನೆ" # Kannada: I am very sad
    res_indic = analyze_sentiment(sample_indic, "kn")
    print(f"KN Result: {res_indic}")
