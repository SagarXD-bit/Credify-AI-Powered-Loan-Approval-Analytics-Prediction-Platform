"""
Data utilities: loading, cleaning, and preprocessing loan datasets.
"""

import io
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from utils.runtime_paths import DATA_PATH

CATEGORICAL_COLS = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"]
NUMERIC_COLS = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History"]
TARGET_COL = "Loan_Status"
FEATURE_COLS = CATEGORICAL_COLS + NUMERIC_COLS


def load_raw_data(uploaded_file=None) -> pd.DataFrame:
    """
    Load loan dataset from an uploaded file or the default CSV.

    Args:
        uploaded_file: A Streamlit uploaded file object, or None to use the built-in dataset.

    Returns:
        Raw DataFrame.
    """
    if uploaded_file is not None:
        content = uploaded_file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    else:
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Default dataset not found at {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values and fix data types.

    Strategy:
    - Categorical: fill with mode
    - Numeric: fill with median
    - Dependents '3+': replace with 3

    Args:
        df: Raw DataFrame.

    Returns:
        Cleaned DataFrame.
    """
    df = df.copy()

    # Normalize Dependents
    if "Dependents" in df.columns:
        df["Dependents"] = df["Dependents"].replace("3+", "3")

    # Fill missing categoricals with mode
    for col in CATEGORICAL_COLS:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numerics with median
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    return df


def encode_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Label-encode categorical columns so they can be used by ML models.

    Args:
        df: Cleaned DataFrame.

    Returns:
        (Encoded DataFrame, dict of LabelEncoder per column)
    """
    df = df.copy()
    encoders = {}

    for col in CATEGORICAL_COLS:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    return df, encoders


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """Encode Loan_Status: Y -> 1, N -> 0."""
    df = df.copy()
    if TARGET_COL in df.columns:
        df[TARGET_COL] = df[TARGET_COL].map({"Y": 1, "N": 0})
    return df


def prepare_features(df: pd.DataFrame):
    """
    Full pipeline: clean -> encode categories -> encode target -> split X/y.

    Args:
        df: Raw DataFrame.

    Returns:
        (X, y, encoders, cleaned_df)
    """
    cleaned = clean_data(df)
    encoded, encoders = encode_features(cleaned)
    encoded = encode_target(encoded)

    available_features = [c for c in FEATURE_COLS if c in encoded.columns]
    X = encoded[available_features]
    y = encoded[TARGET_COL] if TARGET_COL in encoded.columns else None

    return X, y, encoders, cleaned


def encode_single_input(input_dict: dict) -> np.ndarray:
    """
    Encode a single applicant input dict into a numeric feature vector
    using hardcoded ordinal mappings (avoids needing saved encoders).

    Args:
        input_dict: Dict with keys matching FEATURE_COLS.

    Returns:
        1D numpy array ready for model.predict / model.predict_proba.
    """
    gender_map = {"Male": 1, "Female": 0}
    married_map = {"Yes": 1, "No": 0}
    dependents_map = {"0": 0, "1": 1, "2": 2, "3": 3, "3+": 3}
    education_map = {"Graduate": 0, "Not Graduate": 1}
    self_employed_map = {"Yes": 1, "No": 0}
    property_area_map = {"Rural": 0, "Semiurban": 1, "Urban": 2}

    row = [
        gender_map.get(str(input_dict.get("Gender", "Male")), 1),
        married_map.get(str(input_dict.get("Married", "No")), 0),
        dependents_map.get(str(input_dict.get("Dependents", "0")), 0),
        education_map.get(str(input_dict.get("Education", "Graduate")), 0),
        self_employed_map.get(str(input_dict.get("Self_Employed", "No")), 0),
        property_area_map.get(str(input_dict.get("Property_Area", "Urban")), 2),
        float(input_dict.get("ApplicantIncome", 0)),
        float(input_dict.get("CoapplicantIncome", 0)),
        float(input_dict.get("LoanAmount", 0)),
        float(input_dict.get("Loan_Amount_Term", 360)),
        float(input_dict.get("Credit_History", 1)),
    ]
    return np.array(row).reshape(1, -1)


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame showing missing value counts and percentages."""
    missing = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    return pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct}).loc[missing > 0]
