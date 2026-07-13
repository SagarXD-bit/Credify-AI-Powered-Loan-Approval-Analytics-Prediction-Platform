"""
Shared filesystem paths for the Credify Python backend.

On Vercel:
  - Model files & dataset come from the deployed repo (read-only but accessible)
  - Database goes to /tmp/ (writable, but ephemeral between cold starts)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
DATA_PATH = DATA_DIR / "loan_data.csv"

# Model files are committed to the repo
MODEL_DIR = APP_DIR / "model"
BEST_MODEL_PATH = MODEL_DIR / "best_model.joblib"
MODEL_META_PATH = MODEL_DIR / "model_meta.joblib"


def _resolve_runtime_root() -> Path:
    configured_root = os.getenv("CREDIFY_RUNTIME_DIR")
    if configured_root:
        return Path(configured_root)
    if os.getenv("VERCEL"):
        return Path(tempfile.gettempdir()) / "credify-runtime"
    return APP_DIR


RUNTIME_ROOT = _resolve_runtime_root()
DATABASE_DIR = RUNTIME_ROOT / "database"
DB_PATH = DATABASE_DIR / "loan_predictions.db"
