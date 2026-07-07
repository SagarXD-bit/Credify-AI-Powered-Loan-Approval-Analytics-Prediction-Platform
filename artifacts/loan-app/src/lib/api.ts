export type ApplicantPayload = {
  Gender: "Male" | "Female";
  Married: "Yes" | "No";
  Dependents: "0" | "1" | "2" | "3" | "3+";
  Education: "Graduate" | "Not Graduate";
  Self_Employed: "Yes" | "No";
  ApplicantIncome: number;
  CoapplicantIncome: number;
  LoanAmount: number;
  Loan_Amount_Term: number;
  Credit_History: 0 | 1;
  Property_Area: "Urban" | "Semiurban" | "Rural";
};

export type PredictionResult = {
  prediction_id: number;
  prediction: string;
  approved: boolean;
  approval_probability_percent: number;
  confidence: string;
  model_used: string;
  explanations: string[];
};

export type DashboardKPIs = {
  total_applications: number;
  approved_loans: number;
  rejected_loans: number;
  approval_rate: number;
  average_loan_amount_k: number;
};

export type HistoryRecord = {
  id: number;
  timestamp: string;
  gender: string;
  prediction: string;
  probability: number;
  confidence: string;
  loan_amount: number;
};

const API_BASE = import.meta.env.DEV
  ? "http://localhost:8000"
  : "/api";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Server error (HTTP ${res.status})`);
  }
  return res.json();
}

export async function fetchDashboard(): Promise<{
  kpis: DashboardKPIs;
  charts: Record<string, unknown>;
  source: string;
}> {
  const res = await fetch(`${API_BASE}/dashboard`);
  return handleResponse(res);
}

export async function fetchPredictionHistory(limit = 10): Promise<{ records: HistoryRecord[]; summary: Record<string, number> }> {
  const res = await fetch(`${API_BASE}/predictions/history?limit=${limit}`);
  return handleResponse(res);
}

export async function submitPrediction(data: ApplicantPayload): Promise<PredictionResult> {
  const res = await fetch(`${API_BASE}/predictions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export async function fetchModelMeta(): Promise<{
  best_model_name: string;
  feature_names: string[];
  metrics: Record<string, Record<string, number>>;
}> {
  const res = await fetch(`${API_BASE}/models/meta`);
  return handleResponse(res);
}

export async function fetchFeatureImportances(): Promise<{
  best_model_name: string;
  feature_importances: { Feature: string; Importance: number }[];
}> {
  const res = await fetch(`${API_BASE}/models/feature-importances`);
  return handleResponse(res);
}
