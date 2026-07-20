import os
import logging
from typing import List, Dict, Union, Any
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)

# The 9 predefined categories (8 distortions + No Distortion)
DISTORTIONS = [
    "Magnification and Catastrophizing",
    "Black & White Thinking",
    "Jumping to Conclusions",
    "Overgeneralization",
    "Personalization",
    "Emotional Reasoning",
    "Should Statements",
    "Mental Filter",
    "No Distortion"
]

# Global variables for model
_distortion_tokenizer = None
_distortion_model = None
_best_thresholds = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "distortion_model")

def load_distortion_model() -> None:
    """
    Loads the fine-tuned DistilBERT model for multi-label cognitive distortion classification.
    Expects the model to be saved in /backend/models/distortion_model/
    """
    global _distortion_tokenizer, _distortion_model, _best_thresholds
    
    if os.path.exists(MODEL_PATH):
        logger.info(f"Loading custom distortion model from {MODEL_PATH}")
        try:
            _distortion_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            _distortion_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
            
            # Load thresholds if they exist
            import json
            thresh_path = os.path.join(MODEL_PATH, "best_thresholds.json")
            if os.path.exists(thresh_path):
                with open(thresh_path, 'r') as f:
                    _best_thresholds = json.load(f)
            else:
                _best_thresholds = {str(i): 0.4 for i in range(len(DISTORTIONS))}
                
        except Exception as e:
            logger.error(f"Failed to load custom distortion model: {e}")
    else:
        logger.warning(f"Custom model path {MODEL_PATH} not found. Mocking model for now.")

def detect_distortions(text: str) -> List[Dict[str, Union[str, float]]]:
    """
    Detects cognitive distortions in the text using multi-label classification.
    
    Args:
        text (str): The English journal entry (or translated to English).
        
    Returns:
        List[Dict[str, Union[str, float]]]: A list containing the top detected distortion, if any.
        Format: [{'label': 'Overgeneralization', 'confidence': 0.88, 'trigger_phrase': '...'}]
    """
    global _distortion_tokenizer, _distortion_model, _best_thresholds
    
    if not text.strip():
        return []
        
    if _distortion_tokenizer is None or _distortion_model is None:
        load_distortion_model()
        
    # If the model STILL isn't loaded (e.g., path doesn't exist), return mock data for testing
    if _distortion_model is None:
        logger.debug("Using mock data for distortion detection.")
        # Simple mock logic based on keywords for demonstration until fine-tuning is done
        mock_results = []
        lower_text = text.lower()
        if "always" in lower_text or "never" in lower_text:
            mock_results.append({"label": "Overgeneralization", "confidence": 0.88, "trigger_phrase": "always/never"})
        elif "ruin" in lower_text or "disaster" in lower_text:
            mock_results.append({"label": "Magnification and Catastrophizing", "confidence": 0.75, "trigger_phrase": "ruin/disaster"})
        return mock_results

    try:
        # Tokenize input
        inputs = _distortion_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Inference
        with torch.no_grad():
            outputs = _distortion_model(**inputs)
            
        # Multi-label classification uses Sigmoid
        logits = outputs.logits
        probs = torch.sigmoid(logits)[0].numpy()
        
        detected = []
        for idx, prob in enumerate(probs):
            thresh = _best_thresholds.get(str(idx), 0.4) if _best_thresholds else 0.4
            if prob >= thresh:  # Dynamic threshold for multi-label
                label = DISTORTIONS[idx]
                if label != "No Distortion":
                    detected.append({
                        "label": label,
                        "confidence": round(float(prob), 4),
                        "trigger_phrase": text[:20] + "..."  # Mock trigger phrase
                    })
                
        # Sort by confidence descending
        detected.sort(key=lambda x: x["confidence"], reverse=True)
        return detected
        
    except Exception as e:
        logger.error(f"Distortion detection failed: {e}")
        return [{"error": True}]

if __name__ == "__main__":
    load_distortion_model()
    print(detect_distortions("I always ruin everything, this is a disaster!"))
