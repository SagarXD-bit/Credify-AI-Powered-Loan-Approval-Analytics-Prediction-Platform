# Credify — AI-Powered Loan Approval Analytics & Prediction Platform

An end-to-end loan approval intelligence platform combining a **React** dashboard with a **FastAPI + scikit-learn** ML backend. Train models, predict approvals, and explore applicant data — all in one workspace.

## Architecture

```
┌──────────────────────┐     ┌──────────────────────────┐
│   React Dashboard    │     │   FastAPI Backend        │
│   (Vite + shadcn/ui) │────▶│   (api/index.py)         │
│   artifacts/loan-app │     │   /api/predictions       │
│                      │     │   /api/models/train      │
│   Live preview +     │     │   /api/dashboard         │
│   prediction form    │     │   /api/dataset/inspect   │
└──────────────────────┘     └─────────┬────────────────┘
                                       │
                          ┌────────────▼───────────────┐
                          │   ML Engine                 │
                          │   scikit-learn              │
                          │   Logistic Regression       │
                          │   Decision Tree             │
                          │   Random Forest             │
                          └────────────┬────────────────┘
                                       │
                          ┌────────────▼───────────────┐
                          │   Storage                   │
                          │   SQLite (dev)              │
                          │   PostgreSQL (prod via Neon)│
                          │   Joblib model artifacts    │
                          └────────────────────────────┘
```

## Project Structure

```
├── api/                      # FastAPI backend (Vercel serverless entry)
│   └── index.py              # All API routes
├── artifacts/
│   └── loan-app/             # React frontend
│       ├── src/
│       │   ├── App.tsx       # Main dashboard UI
│       │   ├── pages/        # Route pages
│       │   ├── components/   # shadcn/ui components
│       │   └── hooks/        # Custom React hooks
│       ├── utils/            # Python ML utilities
│       │   ├── data_utils.py # Data loading, cleaning, encoding
│       │   ├── ml_utils.py   # Model training, prediction, explanation
│       │   ├── db_utils.py   # SQLite/PostgreSQL persistence
│       │   └── runtime_paths.py # Vercel-aware filesystem paths
│       └── data/             # Default loan dataset (CSV)
├── lib/                      # Shared TypeScript libraries
│   ├── api-spec/             # OpenAPI spec + Orval codegen
│   ├── api-client-react/     # Generated React Query hooks
│   ├── api-zod/              # Generated Zod schemas
│   └── db/                   # Drizzle ORM + PostgreSQL schema
├── package.json              # pnpm workspace root
├── vercel.json               # Vercel deployment config
└── requirements.txt          # Python dependencies
```

## Quick Start

### Prerequisites

- Node.js >= 20
- pnpm >= 9
- Python >= 3.11

### Setup

```bash
# 1. Install JS dependencies
pnpm install

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Train the ML model
curl -X POST http://localhost:8000/models/train

# 4. Start the FastAPI backend
uvicorn api.index:app --reload --port 8000

# 5. In another terminal, start the React frontend
cd artifacts/loan-app
pnpm dev
```

Open `http://localhost:19058` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root with links |
| GET | `/healthz` | Health check |
| GET | `/metadata/form-options` | Available form field options |
| GET | `/dashboard` | Dashboard KPI and chart data |
| POST | `/dashboard` | Dashboard data for uploaded dataset |
| GET | `/dataset/inspect` | Default dataset inspection |
| POST | `/dataset/inspect` | Uploaded dataset inspection |
| POST | `/models/train` | Train all models, auto-select best |
| GET | `/models/meta` | Best model metadata |
| GET | `/models/feature-importances` | Feature importance for best model |
| POST | `/predictions` | Single loan prediction |
| GET | `/predictions/history` | Prediction history with filters |
| GET | `/predictions/summary` | Summary statistics |
| DELETE | `/predictions/history/{id}` | Delete a prediction record |

## Deployment (Vercel)

The project is configured for Vercel deployment:

1. **Frontend:** `cd artifacts/loan-app && vercel` (or connect repo)
2. **API:** Root-level `api/index.py` is auto-detected by Vercel as a serverless function
3. **Environment:** Set `CREDIFY_RUNTIME_DIR` to `/tmp/credify-runtime` on Vercel

For PostgreSQL in production:
```bash
# Set DATABASE_URL in Vercel environment variables
# Then update db_utils.py to use PostgreSQL via Drizzle ORM
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 7, Tailwind CSS v4, shadcn/ui |
| State | TanStack React Query, Wouter (routing) |
| Backend | FastAPI, Python 3.11 |
| ML | scikit-learn (Logistic Regression, Decision Tree, Random Forest) |
| Data | Pandas, NumPy, Joblib |
| Storage | SQLite (dev), PostgreSQL via Drizzle ORM (prod) |
| Infra | Vercel (serverless), pnpm workspaces |

## License

MIT
