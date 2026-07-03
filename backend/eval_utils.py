from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import numpy as np

def evaluate_predictions(y_true, y_pred, target_names=None):
    """
    Computes standard evaluation metrics for predictions.
    
    Args:
        y_true (list or np.array): True labels
        y_pred (list or np.array): Predicted labels
        target_names (list of str, optional): Names of the classes for the classification report
        
    Returns:
        dict: A dictionary containing accuracy, precision, recall, f1, and a detailed report.
    """
    # Use macro average to handle class imbalance well
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
    recall = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    report = classification_report(y_true, y_pred, target_names=target_names, zero_division=0)
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "report": report
    }

def print_evaluation_report(metrics_dict, model_name="Model"):
    """
    Prints a formatted evaluation report.
    """
    print(f"--- Evaluation Report for {model_name} ---")
    print(f"Accuracy:  {metrics_dict['accuracy']:.4f}")
    print(f"Precision: {metrics_dict['precision']:.4f}")
    print(f"Recall:    {metrics_dict['recall']:.4f}")
    print(f"F1 Score:  {metrics_dict['f1_score']:.4f}")
    print("\nDetailed Classification Report:")
    print(metrics_dict['report'])
    print("-" * 40)
