import time
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Import ML pipeline modules
from lang_detector import detect_language
from sentiment_model import analyze_sentiment
from emotion_model import analyze_emotion
from distortion_model import detect_distortions
from reframing_engine import reframe_distortions

# Import DB functions
from database import init_db, save_journal_entry, save_analysis_result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize database on startup
init_db()

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Analyzes a journal entry and returns sentiment, emotions, and distortions.
    """
    start_time = time.time()
    
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
        
    text = data.get("text")
    user_id = data.get("user_id", "anonymous")
    
    # Generate unique IDs
    entry_id = str(uuid.uuid4())
    result_id = str(uuid.uuid4())
    
    # 1. Language Detection
    lang_result = detect_language(text)
    detected_language = lang_result["language"]
    language_code = lang_result["language_code"]
    language_confidence = lang_result["confidence"]
    
    # 2. Sentiment Analysis
    sentiment_result = analyze_sentiment(text, language_code)
    
    # 3. Emotion Analysis
    emotions = analyze_emotion(text, language_code)
    
    # Need to get English translation if not English, for distortion detection
    from emotion_model import translate_to_english
    english_text = translate_to_english(text, language_code)
    
    # 4. Cognitive Distortions
    distortions = detect_distortions(english_text if language_code != "en" else text)
    
    # 5. Reframing
    reframings = reframe_distortions(text, distortions)
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    timestamp = datetime.utcnow().isoformat()
    
    # Save to Database
    try:
        save_journal_entry(
            entry_id=entry_id,
            user_id=user_id,
            raw_text=text,
            detected_language=detected_language,
            language_confidence=language_confidence
        )
        save_analysis_result(
            result_id=result_id,
            entry_id=entry_id,
            sentiment_label=sentiment_result["label"],
            sentiment_confidence=sentiment_result["confidence"],
            emotions=emotions,
            distortions=distortions,
            reframings=reframings,
            processing_time_ms=processing_time_ms
        )
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Failed to save to database"}), 500

    # Construct full response matching the requested schema
    response_payload = {
        "entry_id": entry_id,
        "input_text": text,
        "detected_language": detected_language,
        "language_confidence": language_confidence,
        "sentiment": sentiment_result,
        "emotions": emotions,
        "distortions": distortions,
        "reframings": reframings,
        "processing_time_ms": processing_time_ms,
        "timestamp": timestamp
    }
    
    return jsonify(response_payload), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
