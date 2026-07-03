import json
import logging
import urllib.request
import urllib.error
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

# Static fallback dictionary of reframing templates if Ollama is down
STATIC_REFRAMINGS = {
    "Catastrophizing": "It's easy to assume the worst-case scenario. Try to consider what is the most likely outcome, rather than the worst one.",
    "Black & White Thinking": "Situations are rarely entirely good or entirely bad. Can you find a middle ground or a shade of grey here?",
    "Mind Reading": "We can't know for sure what others are thinking. Is there another possible explanation for their behavior?",
    "Overgeneralization": "One negative event doesn't mean a never-ending pattern of defeat. Try looking at this as a single, isolated incident.",
    "Personalization": "Not everything is your fault or within your control. Acknowledge the external factors that played a role here.",
    "Emotional Reasoning": "Feelings aren't always facts. Even though you feel this way right now, does the objective evidence support it?",
    "Should Statements": "Try to replace 'should' or 'must' with 'prefer' or 'it would be nice if'. It takes the unnecessary pressure off.",
    "Magnification": "This feels huge right now, but will it matter in a week, a month, or a year?",
    "Mental Filter": "You're focusing heavily on the negative details. What are some positive or neutral things that also happened?",
    "Jumping to Conclusions": "You're predicting a negative outcome without evidence. What facts do you actually have right now?"
}

def generate_reframing_ollama(distortion: str, text: str) -> str:
    """Calls local Ollama Mistral model to generate a reframing."""
    prompt = (
        f"You are a compassionate CBT therapist. The user wrote this journal entry: '{text}'. "
        f"They are experiencing the cognitive distortion of '{distortion}'. "
        f"Provide ONE gentle, concise reframing suggestion in 2-3 sentences. Do not be preachy. "
        f"Be warm and human. Never diagnose."
    )
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    req = urllib.request.Request(
        OLLAMA_API_URL, 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        return result.get('response', "").strip()
    except (urllib.error.URLError, TimeoutError) as e:
        logger.warning(f"Ollama API failed: {e}. Falling back to static reframing.")
        return ""

def reframe_distortions(text: str, distortions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Generates reframing suggestions for detected distortions.
    Only processes distortions with a confidence > 0.6.
    
    Args:
        text (str): The journal entry.
        distortions (List[dict]): The list of detected distortions.
        
    Returns:
        List[Dict[str, str]]: List of reframed thoughts.
    """
    reframings = []
    
    for dist in distortions:
        confidence = dist.get("confidence", 0.0)
        label = dist.get("label", "")
        
        # Only reframe if confidence is reasonably high
        if confidence > 0.6 and label:
            # Try Ollama first
            reframed_text = generate_reframing_ollama(label, text)
            
            # Fallback to static dictionary
            if not reframed_text:
                reframed_text = STATIC_REFRAMINGS.get(label, "Consider looking at this from a more balanced perspective.")
                
            reframings.append({
                "distortion": label,
                "reframed": reframed_text
            })
            
    return reframings

if __name__ == "__main__":
    # Test fallback directly
    sample = [{"label": "Catastrophizing", "confidence": 0.8}]
    print(reframe_distortions("I failed the test, my life is over.", sample))
