"""
Shared filesystem paths for the Credify Python backend.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"


def _resolve_runtime_root() -> Path:
    configured_root = os.getenv("CREDIFY_RUNTIME_DIR")
    if configured_root:
        return Path(configured_root)

    if os.getenv("VERCEL"):
        return Path(tempfile.gettempdir()) / "credify-runtime"

    return APP_DIR


RUNTIME_ROOT = _resolve_runtime_root()
MODEL_DIR = RUNTIME_ROOT / "model"
DATABASE_DIR = RUNTIME_ROOT / "database"
DATA_PATH = DATA_DIR / "loan_data.csv"
BEST_MODEL_PATH = MODEL_DIR / "best_model.joblib"
MODEL_META_PATH = MODEL_DIR / "model_meta.joblib"
DB_PATH = DATABASE_DIR / "loan_predictions.db"
