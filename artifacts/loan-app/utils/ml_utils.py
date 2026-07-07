"""
Machine learning utilities: training, evaluation, model persistence, and prediction.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix,
)
from utils.runtime_paths import BEST_MODEL_PATH, MODEL_DIR, MODEL_META_PATH


def get_models() -> dict:
    """Return a dict of model name -> untrained sklearn estimator."""
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
    }


def train_and_evaluate(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> dict:
    """
    Split data, train all models, evaluate each, pick the best by F1-score,
    save the best model and its metadata to disk.

    Args:
        X: Feature matrix.
        y: Target vector.
        test_size: Fraction of data for the test split.

    Returns:
        Dict mapping model name -> {accuracy, precision, recall, f1, confusion_matrix, model}.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    results = {}
    for name, model in get_models().items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results[name] = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_test, y_pred, zero_division=0), 4),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "model": model,
            "feature_names": list(X.columns),
        }

    # Select best by F1-score
    best_name = max(results, key=lambda n: results[n]["f1"])
    best_model = results[best_name]["model"]

    # Persist best model + metadata
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, BEST_MODEL_PATH)
    joblib.dump({
        "best_model_name": best_name,
        "feature_names": list(X.columns),
        "metrics": {n: {k: v for k, v in r.items() if k != "model"} for n, r in results.items()},
    }, MODEL_META_PATH)

    return results, best_name


def load_best_model():
    """Load the previously saved best model from disk. Returns None if not found."""
    if os.path.exists(BEST_MODEL_PATH):
        return joblib.load(BEST_MODEL_PATH)
    return None


def load_model_meta() -> dict | None:
    """Load model metadata (best model name, feature names, metrics) from disk."""
    if os.path.exists(MODEL_META_PATH):
        return joblib.load(MODEL_META_PATH)
    return None


def predict_loan(model, feature_vector: np.ndarray) -> tuple[str, float, str]:
    """
    Run inference on a single applicant's feature vector.

    Args:
        model: Trained sklearn estimator.
        feature_vector: Shape (1, n_features) numpy array.

    Returns:
        (prediction_label, approval_probability, confidence_level)
    """
    proba = model.predict_proba(feature_vector)[0]
    approval_prob = float(proba[1])
    prediction = "Approved" if approval_prob >= 0.5 else "Rejected"

    if approval_prob >= 0.80:
        confidence = "High"
    elif approval_prob >= 0.60:
        confidence = "Medium"
    else:
        confidence = "Low"

    return prediction, approval_prob, confidence


def get_feature_importances(model, feature_names: list) -> pd.DataFrame | None:
    """
    Extract feature importances for tree-based models.

    Returns:
        DataFrame with Feature and Importance columns, sorted descending. None for LR.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        return None

    df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
    return df.sort_values("Importance", ascending=False).reset_index(drop=True)


def get_decision_explanation(feature_vector: np.ndarray, feature_names: list, model) -> list[str]:
    """
    Generate a plain-English explanation of the top factors driving the prediction.

    Args:
        feature_vector: Shape (1, n_features) array.
        feature_names: List of feature names matching the vector.
        model: Trained model.

    Returns:
        List of explanation strings.
    """
    importances_df = get_feature_importances(model, feature_names)
    if importances_df is None:
        return ["No detailed explanation available for this model type."]

    top_factors = importances_df.head(3)
    explanations = []
    values = feature_vector[0]

    labels = {
        "Credit_History": {1: "positive credit history", 0: "no credit history"},
        "Education": {0: "graduate education", 1: "non-graduate education"},
        "Gender": {1: "male applicant", 0: "female applicant"},
        "Married": {1: "married applicant", 0: "unmarried applicant"},
        "Self_Employed": {1: "self-employed", 0: "salaried employment"},
        "Property_Area": {0: "rural property area", 1: "semiurban property area", 2: "urban property area"},
        "Dependents": lambda v: f"{int(v)} dependent(s)",
    }

    for _, row in top_factors.iterrows():
        feat = row["Feature"]
        importance = row["Importance"]
        try:
            idx = feature_names.index(feat)
            val = values[idx]
        except ValueError:
            continue

        if feat in labels:
            label_map = labels[feat]
            if callable(label_map):
                desc = label_map(val)
            else:
                desc = label_map.get(int(val), f"value {val}")
        elif feat == "ApplicantIncome":
            desc = f"applicant income of ₹{val:,.0f}"
        elif feat == "LoanAmount":
            desc = f"loan amount of ₹{val:,.0f}K"
        elif feat == "CoapplicantIncome":
            desc = f"co-applicant income of ₹{val:,.0f}"
        else:
            desc = f"{feat} = {val}"

        explanations.append(
            f"**{feat}** (importance: {importance:.2%}) — {desc} is a key factor."
        )

    return explanations
