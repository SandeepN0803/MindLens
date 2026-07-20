# Dataset Caveats

## Synthetic Dataset Top-Up (Option 2)
The majority of the dataset (`synthetic_distortions_en_ollama.csv`) was generated under a strict **20% trigger-word cap** to ensure lexical diversity and prevent the model from learning obvious shortcuts.

However, during a targeted top-up using Llama 3.1 8B, the following categories were allowed relaxed constraints to overcome the local model's generation ceiling:

- **Jumping to Conclusions**: Generated up to 150 rows. The trigger-word cap was relaxed to **35%** for this category.
- **Overgeneralization**: Generated up to 150 rows. The trigger-word cap was relaxed to **35%** for this category.
- **No Distortion**: Generated up to 100 rows. The constraint was relaxed to accept more entries. 

**Note for Evaluation:** If the organic Macro F1 improves on these specific categories, it's important to track whether this is due to genuine new signal or partly because looser trigger-word constraints made these categories easier to learn via lexical shortcuts.
