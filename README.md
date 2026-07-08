# MindLens

MindLens is a Multilingual Mental Health Journal Analyzer that tracks emotions and detects cognitive distortions using advanced NLP techniques. It supports multiple languages (English, Hindi, Kannada, Telugu, Tamil).

## 🧠 Core Features & Architecture

MindLens runs a multi-layered NLP pipeline to extract meaningful insights from journal entries:

1. **Language Detection**: Automatically identifies the language of the journal entry (using `langdetect`).
2. **Sentiment & Emotion Analysis**: Leverages robust models like XLM-RoBERTa and DistilRoBERTa to classify sentiment (Positive/Negative/Neutral) and specific emotions (Joy, Fear, Anger, etc.).
3. **Cognitive Distortion Detection**: Currently uses a **keyword-based heuristics fallback** (e.g. flagging "always/never" as *Overgeneralization*). The codebase is fully prepared for a custom-trained DistilBERT model to classify 10 CBT-defined cognitive distortions once fine-tuned on a labeled dataset.
4. **Reframing Engine**: Suggests healthier, alternative perspectives for detected distortions.

## 🔒 Privacy & Local Inference
**Privacy is a first-class feature of MindLens.** 
Unlike most mental health applications that send sensitive journal data to external servers, MindLens is designed for **100% local inference**. All natural language processing, including the transformer models for sentiment and emotion detection, run locally on the user's machine. All journal entries and analysis results are stored securely in a local SQLite database (`mindlens.db`). Your data never leaves your device.

## 🚀 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/MindLens.git
   cd MindLens
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Backend API:**
   ```bash
   python backend/app.py
   ```
   The Flask server will start on `http://127.0.0.1:5001`.

4. **Run the Gradio Demo:**
   To launch the interactive web interface (great for HuggingFace Spaces deployment):
   ```bash
   python gradio_app.py
   ```

## 📄 Research Potential
The multilingual capability combined with deep cognitive distortion detection makes this project a strong candidate for research in NLP and computational psychology, specifically tailored for Indic languages. Evaluating this pipeline on curated datasets presents novel research angles suitable for EMNLP, ACL, or ICON.

## 📊 Evaluation & Fine-Tuning
Check the `notebooks/` directory for:
- `model_evaluation.ipynb`: Setup to calculate Accuracy, F1-Score, and other standard metrics on test sets.
- `distortion_finetuning.ipynb`: Provides a complete DistilBERT fine-tuning pipeline, ready to be executed once a labeled cognitive distortion dataset is provided.