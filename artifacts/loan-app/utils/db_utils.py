"""
SQLite database utilities for storing loan predictions and applicant details.
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "loan_predictions.db")


def get_connection():
    """Get a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            gender TEXT,
            married TEXT,
            dependents TEXT,
            education TEXT,
            self_employed TEXT,
            applicant_income REAL,
            coapplicant_income REAL,
            loan_amount REAL,
            loan_amount_term REAL,
            credit_history REAL,
            property_area TEXT,
            prediction TEXT NOT NULL,
            probability REAL NOT NULL,
            confidence TEXT NOT NULL,
            model_used TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_prediction(applicant_data: dict, prediction: str, probability: float, model_used: str = "Best Model"):
    """
    Save a prediction result to the database.

    Args:
        applicant_data: Dictionary of applicant features.
        prediction: 'Approved' or 'Rejected'.
        probability: Approval probability (0-1).
        model_used: Name of the model used.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if probability >= 0.80:
        confidence = "High"
    elif probability >= 0.60:
        confidence = "Medium"
    else:
        confidence = "Low"

    cursor.execute("""
        INSERT INTO predictions (
            timestamp, gender, married, dependents, education, self_employed,
            applicant_income, coapplicant_income, loan_amount, loan_amount_term,
            credit_history, property_area, prediction, probability, confidence, model_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        applicant_data.get("Gender", ""),
        applicant_data.get("Married", ""),
        applicant_data.get("Dependents", ""),
        applicant_data.get("Education", ""),
        applicant_data.get("Self_Employed", ""),
        applicant_data.get("ApplicantIncome", 0),
        applicant_data.get("CoapplicantIncome", 0),
        applicant_data.get("LoanAmount", 0),
        applicant_data.get("Loan_Amount_Term", 0),
        applicant_data.get("Credit_History", 0),
        applicant_data.get("Property_Area", ""),
        prediction,
        round(probability, 4),
        confidence,
        model_used,
    ))
    conn.commit()
    conn.close()


def get_predictions(search_term: str = "") -> pd.DataFrame:
    """
    Retrieve prediction history from the database.

    Args:
        search_term: Optional filter string to match against gender, prediction, property_area, etc.

    Returns:
        DataFrame of prediction records.
    """
    conn = get_connection()
    if search_term:
        query = """
            SELECT * FROM predictions
            WHERE gender LIKE ? OR married LIKE ? OR prediction LIKE ?
               OR property_area LIKE ? OR confidence LIKE ? OR education LIKE ?
            ORDER BY timestamp DESC
        """
        term = f"%{search_term}%"
        df = pd.read_sql_query(query, conn, params=(term, term, term, term, term, term))
    else:
        df = pd.read_sql_query("SELECT * FROM predictions ORDER BY timestamp DESC", conn)
    conn.close()
    return df


def get_summary_stats() -> dict:
    """Return summary statistics for the predictions stored in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction = 'Approved'")
    approved = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction = 'Rejected'")
    rejected = cursor.fetchone()[0]
    conn.close()
    return {"total": total, "approved": approved, "rejected": rejected}


def delete_prediction(pred_id: int):
    """Delete a prediction record by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
    conn.commit()
    conn.close()
