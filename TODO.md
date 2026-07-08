# Backend Refactoring To-Dos

## Multi-label Classification Conversion
Currently, the frontend is built to assume the backend returns an array of 0 to N thought patterns (multi-label). While the Flask API currently returns this correct shape via a mock fallback in `distortion_model.py`, the actual model training pipeline needs to be updated to support multi-label classification properly. 

> *Note: Current `/api/analyze` responses are keyword-fallback, not the trained model — frontend integration tests pass but do not validate model quality.*

**Required Steps:**
- [ ] **Dataset Generation**: Update `generate_dataset_openai.py` (or similar scripts) to produce multi-label rows (e.g., tagging entries with multiple distortions using a comma-separated label column or one-hot columns).
- [ ] **Fine-tuning Notebook**: Update the `AutoModelForSequenceClassification` config to use `problem_type="multi_label_classification"`. Update the loss function to `BCEWithLogitsLoss`. Ensure multi-hot label tensors are used instead of integer class labels.
- [ ] **Evaluation Metrics**: Update `eval_utils.py` (and any metric computation in the notebooks) to compute multi-label F1 (micro/macro/per-label) rather than standard argmax-based accuracy.
