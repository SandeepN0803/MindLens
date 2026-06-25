import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = "mindlens.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """
    Initializes the SQLite schema with the required tables.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    logger.info("Initializing database schema...")
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Journal Entries Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                detected_language TEXT,
                language_confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis Results Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id TEXT PRIMARY KEY,
                entry_id TEXT NOT NULL,
                sentiment_label TEXT,
                sentiment_confidence REAL,
                emotions_json TEXT,
                distortions_json TEXT,
                reframings_json TEXT,
                processing_time_ms INTEGER,
                FOREIGN KEY (entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE
            )
        """)
        
        # User Feedback Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id TEXT PRIMARY KEY,
                entry_id TEXT NOT NULL,
                corrected_sentiment TEXT,
                corrected_distortions TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE
            )
        """)
        
        # Enables foreign key constraints on SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
    logger.info("Database schema initialized successfully.")

def save_journal_entry(
    entry_id: str, 
    user_id: str, 
    raw_text: str, 
    detected_language: str, 
    language_confidence: float
) -> None:
    """Inserts a new journal entry."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO journal_entries (id, user_id, raw_text, detected_language, language_confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (entry_id, user_id, raw_text, detected_language, language_confidence))
        conn.commit()

def save_analysis_result(
    result_id: str,
    entry_id: str,
    sentiment_label: str,
    sentiment_confidence: float,
    emotions: List[Dict[str, Any]],
    distortions: List[Dict[str, Any]],
    reframings: List[Dict[str, Any]],
    processing_time_ms: int
) -> None:
    """Inserts analysis results linked to a journal entry."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analysis_results 
            (id, entry_id, sentiment_label, sentiment_confidence, emotions_json, distortions_json, reframings_json, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result_id,
            entry_id,
            sentiment_label,
            sentiment_confidence,
            json.dumps(emotions, ensure_ascii=False),
            json.dumps(distortions, ensure_ascii=False),
            json.dumps(reframings, ensure_ascii=False),
            processing_time_ms
        ))
        conn.commit()

def save_user_feedback(
    feedback_id: str,
    entry_id: str,
    corrected_sentiment: Optional[str],
    corrected_distortions: Optional[List[Dict[str, Any]]]
) -> None:
    """Saves user feedback for fine-tuning."""
    distortions_json = json.dumps(corrected_distortions, ensure_ascii=False) if corrected_distortions else None
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO user_feedback (id, entry_id, corrected_sentiment, corrected_distortions)
            VALUES (?, ?, ?, ?)
        """, (feedback_id, entry_id, corrected_sentiment, distortions_json))
        conn.commit()

def delete_entry(entry_id: str) -> bool:
    """
    Deletes a journal entry by ID.
    Cascade delete will remove linked analysis_results and user_feedback.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # Ensure foreign keys PRAGMA is active for cascade to work
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0
        
if __name__ == "__main__":
    init_db()
