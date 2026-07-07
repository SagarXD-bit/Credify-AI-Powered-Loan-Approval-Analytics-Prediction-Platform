"""
FastAPI entrypoint for the Credify loan analytics backend.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[1]
LOAN_APP_DIR = ROOT_DIR / "artifacts" / "loan-app"

if str(LOAN_APP_DIR) not in sys.path:
    sys.path.insert(0, str(LOAN_APP_DIR))

from utils.data_utils import (  # noqa: E402
    FEATURE_COLS,
    clean_data,
    encode_single_input,
    get_missing_summary,
    load_raw_data,
    prepare_features,
)
from utils.db_utils import (  # noqa: E402
    delete_prediction,
    get_predictions,
    get_summary_stats,
    init_db,
    save_prediction,
)
from utils.ml_utils import (  # noqa: E402
    get_decision_explanation,
    get_feature_importances,
    load_best_model,
    load_model_meta,
    predict_loan,
    train_and_evaluate,
)
from utils.runtime_paths import MODEL_DIR  # noqa: E402

app = FastAPI(
    title="Credify Loan API",
    version="1.0.0",
    summary="FastAPI backend for loan analytics, model training, and approval predictions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class ApplicantPayload(BaseModel):
    Gender: Literal["Male", "Female"] = "Male"
    Married: Literal["Yes", "No"] = "No"
    Dependents: Literal["0", "1", "2", "3", "3+"] = "0"
    Education: Literal["Graduate", "Not Graduate"] = "Graduate"
    Self_Employed: Literal["Yes", "No"] = "No"
    ApplicantIncome: float = Field(ge=0, default=5000)
    CoapplicantIncome: float = Field(ge=0, default=0)
    LoanAmount: float = Field(gt=0, default=150)
    Loan_Amount_Term: int = Field(gt=0, default=360)
    Credit_History: Literal[0, 1] = 1
    Property_Area: Literal["Urban", "Semiurban", "Rural"] = "Urban"


class DataInspectResponse(BaseModel):
    source: str
    summary: dict[str, Any]
    raw_preview: list[dict[str, Any]]
    cleaned_preview: list[dict[str, Any]]
    missing_summary: list[dict[str, Any]]
    statistical_summary: list[dict[str, Any]]


def _json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _records(df: pd.DataFrame, limit: int | None = None) -> list[dict[str, Any]]:
    frame = df.head(limit) if limit is not None else df
    return [
        {str(key): _json_safe(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def _read_uploaded_csv_bytes(file_bytes: bytes) -> pd.DataFrame:
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")

    try:
        return pd.read_csv(io.StringIO(file_bytes.decode("utf-8")))
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.") from exc
    except pd.errors.ParserError as exc:
        raise HTTPException(status_code=400, detail="Unable to parse the uploaded CSV file.") from exc


async def _load_dataset(uploaded_file: UploadFile | None = None) -> tuple[str, pd.DataFrame, pd.DataFrame]:
    if uploaded_file is None:
        try:
            raw_df = load_raw_data()
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return "default-dataset", raw_df, clean_data(raw_df)

    file_bytes = await uploaded_file.read()
    raw_df = _read_uploaded_csv_bytes(file_bytes)
    return uploaded_file.filename or "uploaded-dataset", raw_df, clean_data(raw_df)


def _build_dashboard_payload(df: pd.DataFrame) -> dict[str, Any]:
    total = len(df)
    approved = int((df["Loan_Status"] == "Y").sum()) if "Loan_Status" in df.columns else 0
    rejected = total - approved
    approval_rate = round((approved / total) * 100, 1) if total else 0.0
    avg_loan_amount = round(float(df["LoanAmount"].mean()), 1) if "LoanAmount" in df.columns else 0.0

    approval_by_credit_history = []
    if {"Credit_History", "Loan_Status"}.issubset(df.columns):
        chart = df.groupby(["Credit_History", "Loan_Status"]).size().reset_index(name="count")
        chart["credit_history"] = chart["Credit_History"].map({1.0: "Good Credit", 0.0: "No Credit"}).fillna("Unknown")
        chart["loan_status"] = chart["Loan_Status"].map({"Y": "Approved", "N": "Rejected"}).fillna(chart["Loan_Status"])
        approval_by_credit_history = _records(chart[["credit_history", "loan_status", "count"]])

    approval_by_education = []
    if {"Education", "Loan_Status"}.issubset(df.columns):
        chart = df.groupby(["Education", "Loan_Status"]).size().reset_index(name="count")
        chart["loan_status"] = chart["Loan_Status"].map({"Y": "Approved", "N": "Rejected"}).fillna(chart["Loan_Status"])
        approval_by_education = _records(chart[["Education", "loan_status", "count"]])

    approval_by_property_area = []
    if {"Property_Area", "Loan_Status"}.issubset(df.columns):
        chart = df.groupby(["Property_Area", "Loan_Status"]).size().reset_index(name="count")
        chart["loan_status"] = chart["Loan_Status"].map({"Y": "Approved", "N": "Rejected"}).fillna(chart["Loan_Status"])
        approval_by_property_area = _records(chart[["Property_Area", "loan_status", "count"]])

    income_distribution = []
    if "ApplicantIncome" in df.columns:
        counts, bins = np.histogram(df["ApplicantIncome"].dropna(), bins=20)
        income_distribution = [
            {
                "range_start": round(float(bins[index]), 2),
                "range_end": round(float(bins[index + 1]), 2),
                "count": int(counts[index]),
            }
            for index in range(len(counts))
        ]

    loan_amount_by_status = []
    if {"Loan_Status", "LoanAmount"}.issubset(df.columns):
        for status, series in df.groupby("Loan_Status")["LoanAmount"]:
            clean_series = series.dropna()
            if clean_series.empty:
                continue
            label = "Approved" if status == "Y" else "Rejected" if status == "N" else str(status)
            loan_amount_by_status.append(
                {
                    "loan_status": label,
                    "min": round(float(clean_series.min()), 2),
                    "q1": round(float(clean_series.quantile(0.25)), 2),
                    "median": round(float(clean_series.median()), 2),
                    "q3": round(float(clean_series.quantile(0.75)), 2),
                    "max": round(float(clean_series.max()), 2),
                }
            )

    approval_rate_by_segment = []
    if {"Gender", "Married", "Loan_Status"}.issubset(df.columns):
        chart = (
            df.groupby(["Gender", "Married"])["Loan_Status"]
            .apply(lambda series: round((series == "Y").sum() / len(series) * 100, 1))
            .reset_index(name="approval_rate")
        )
        chart["segment"] = chart["Gender"] + " · " + chart["Married"].map({"Yes": "Married", "No": "Single"}).fillna(chart["Married"])
        approval_rate_by_segment = _records(chart[["segment", "approval_rate"]])

    return {
        "kpis": {
            "total_applications": total,
            "approved_loans": approved,
            "rejected_loans": rejected,
            "approval_rate": approval_rate,
            "average_loan_amount_k": avg_loan_amount,
        },
        "charts": {
            "approval_by_credit_history": approval_by_credit_history,
            "approval_by_education": approval_by_education,
            "approval_by_property_area": approval_by_property_area,
            "income_distribution": income_distribution,
            "loan_amount_by_status": loan_amount_by_status,
            "approval_rate_by_gender_and_marital_status": approval_rate_by_segment,
        },
    }


def _build_data_inspection_payload(source: str, raw_df: pd.DataFrame, cleaned_df: pd.DataFrame, preview_rows: int) -> DataInspectResponse:
    approved_count = int((cleaned_df["Loan_Status"] == "Y").sum()) if "Loan_Status" in cleaned_df.columns else 0
    statistical_summary = cleaned_df.describe(include="all").T.reset_index().rename(columns={"index": "column"})
    missing_summary = get_missing_summary(raw_df).reset_index().rename(columns={"index": "column"})

    return DataInspectResponse(
        source=source,
        summary={
            "total_rows": len(cleaned_df),
            "total_columns": len(cleaned_df.columns),
            "missing_values": int(raw_df.isnull().sum().sum()),
            "approved_rows": approved_count,
            "required_features_present": [column for column in FEATURE_COLS if column in cleaned_df.columns],
            "target_present": "Loan_Status" in cleaned_df.columns,
        },
        raw_preview=_records(raw_df, preview_rows),
        cleaned_preview=_records(cleaned_df, preview_rows),
        missing_summary=_records(missing_summary),
        statistical_summary=_records(statistical_summary),
    )


def _serialize_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        key: {metric_name: metric_value for metric_name, metric_value in values.items() if metric_name != "model"}
        for key, values in metrics.items()
    }


def _load_active_model():
    model = load_best_model()
    meta = load_model_meta()
    if model is None or meta is None:
        raise HTTPException(
            status_code=404,
            detail="No trained model found. Call POST /models/train before requesting predictions.",
        )
    return model, meta


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "Credify Loan API",
        "version": app.version,
        "docs": "/docs",
        "health": "/healthz",
    }


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata/form-options")
def get_form_options() -> dict[str, Any]:
    return {
        "feature_columns": FEATURE_COLS,
        "categorical_options": {
            "Gender": ["Male", "Female"],
            "Married": ["Yes", "No"],
            "Dependents": ["0", "1", "2", "3", "3+"],
            "Education": ["Graduate", "Not Graduate"],
            "Self_Employed": ["No", "Yes"],
            "Property_Area": ["Urban", "Semiurban", "Rural"],
            "Credit_History": [1, 0],
        },
        "loan_amount_terms": [360, 180, 120, 240, 300, 480, 60, 36, 84],
    }


@app.get("/dashboard")
async def get_dashboard() -> dict[str, Any]:
    source, _, cleaned_df = await _load_dataset()
    payload = _build_dashboard_payload(cleaned_df)
    payload["source"] = source
    return payload


@app.post("/dashboard")
async def post_dashboard(dataset: UploadFile = File(...)) -> dict[str, Any]:
    source, _, cleaned_df = await _load_dataset(dataset)
    payload = _build_dashboard_payload(cleaned_df)
    payload["source"] = source
    return payload


@app.get("/dataset/inspect", response_model=DataInspectResponse)
async def inspect_default_dataset(
    preview_rows: int = Query(default=10, ge=1, le=100),
) -> DataInspectResponse:
    source, raw_df, cleaned_df = await _load_dataset()
    return _build_data_inspection_payload(source, raw_df, cleaned_df, preview_rows)


@app.post("/dataset/inspect", response_model=DataInspectResponse)
async def inspect_uploaded_dataset(
    dataset: UploadFile = File(...),
    preview_rows: int = Form(default=10),
) -> DataInspectResponse:
    if preview_rows < 1 or preview_rows > 100:
        raise HTTPException(status_code=400, detail="preview_rows must be between 1 and 100.")
    source, raw_df, cleaned_df = await _load_dataset(dataset)
    return _build_data_inspection_payload(source, raw_df, cleaned_df, preview_rows)


@app.post("/models/train")
async def train_models(
    test_size: float = Form(default=0.2),
    dataset: UploadFile | None = File(default=None),
) -> dict[str, Any]:
    if test_size < 0.1 or test_size > 0.4:
        raise HTTPException(status_code=400, detail="test_size must be between 0.10 and 0.40.")

    source, _, cleaned_df = await _load_dataset(dataset)
    if "Loan_Status" not in cleaned_df.columns:
        raise HTTPException(status_code=400, detail="Dataset must include a Loan_Status column for training.")

    X, y, _, _ = prepare_features(cleaned_df)
    if y is None or y.nunique() < 2:
        raise HTTPException(status_code=400, detail="Training requires at least two target classes in Loan_Status.")

    results, best_model_name = train_and_evaluate(X, y, test_size=test_size)
    meta = load_model_meta() or {}
    model = load_best_model()
    feature_importances = []
    if model is not None:
        feature_importance_df = get_feature_importances(model, meta.get("feature_names", list(X.columns)))
        if feature_importance_df is not None:
            feature_importances = _records(feature_importance_df)

    return {
        "source": source,
        "dataset_rows": len(cleaned_df),
        "feature_count": len(X.columns),
        "best_model_name": best_model_name,
        "saved_model_directory": str(MODEL_DIR),
        "metrics": _serialize_metrics(results),
        "feature_importances": feature_importances,
    }


@app.get("/models/meta")
def get_model_meta() -> dict[str, Any]:
    meta = load_model_meta()
    if meta is None:
        raise HTTPException(status_code=404, detail="No trained model metadata found.")
    return meta


@app.get("/models/feature-importances")
def get_model_feature_importances() -> dict[str, Any]:
    model, meta = _load_active_model()
    feature_importance_df = get_feature_importances(model, meta.get("feature_names", FEATURE_COLS))
    return {
        "best_model_name": meta.get("best_model_name"),
        "feature_importances": [] if feature_importance_df is None else _records(feature_importance_df),
    }


@app.post("/predictions")
def create_prediction(payload: ApplicantPayload) -> dict[str, Any]:
    model, meta = _load_active_model()
    applicant_data = payload.model_dump()
    feature_vector = encode_single_input(applicant_data)
    prediction, probability, confidence = predict_loan(model, feature_vector)
    prediction_id = save_prediction(applicant_data, prediction, probability, meta.get("best_model_name", "Best Model"))
    feature_names = meta.get("feature_names", list(applicant_data.keys()))
    explanations = get_decision_explanation(feature_vector, feature_names, model)

    return {
        "prediction_id": prediction_id,
        "prediction": prediction,
        "approved": prediction == "Approved",
        "approval_probability": round(probability, 4),
        "approval_probability_percent": round(probability * 100, 1),
        "confidence": confidence,
        "model_used": meta.get("best_model_name"),
        "feature_vector": feature_vector.flatten().tolist(),
        "explanations": explanations,
    }


@app.get("/predictions/summary")
def predictions_summary() -> dict[str, int]:
    return get_summary_stats()


@app.get("/predictions/history")
def prediction_history(
    search: str = Query(default=""),
    outcome: Literal["Approved", "Rejected"] | None = Query(default=None),
    confidence: Literal["High", "Medium", "Low"] | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
) -> dict[str, Any]:
    history_df = get_predictions(search)
    if outcome is not None:
        history_df = history_df[history_df["prediction"] == outcome]
    if confidence is not None:
        history_df = history_df[history_df["confidence"] == confidence]

    return {
        "summary": {
            "total": len(history_df),
            "approved": int((history_df["prediction"] == "Approved").sum()) if not history_df.empty else 0,
            "rejected": int((history_df["prediction"] == "Rejected").sum()) if not history_df.empty else 0,
        },
        "records": _records(history_df, limit),
    }


@app.delete("/predictions/history/{prediction_id}")
def remove_prediction(prediction_id: int) -> dict[str, Any]:
    delete_prediction(prediction_id)
    return {"deleted": True, "prediction_id": prediction_id}
