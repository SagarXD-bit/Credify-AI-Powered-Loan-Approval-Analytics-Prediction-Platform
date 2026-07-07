import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { submitPrediction, type ApplicantPayload, type PredictionResult } from "@/lib/api";
import { FinancialAdvisor } from "@/components/prediction/FinancialAdvisor";
import { WhatIfSimulator } from "@/components/prediction/WhatIfSimulator";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const defaultForm: ApplicantPayload = {
  Gender: "Male", Married: "No", Dependents: "0", Education: "Graduate",
  Self_Employed: "No", ApplicantIncome: 5000, CoapplicantIncome: 0,
  LoanAmount: 150, Loan_Amount_Term: 360, Credit_History: 1, Property_Area: "Urban",
};

export default function Prediction() {
  const { toast } = useToast();
  const [form, setForm] = useState<ApplicantPayload>(defaultForm);
  const [predicting, setPredicting] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const updateField = <K extends keyof ApplicantPayload>(key: K, value: ApplicantPayload[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (overrideForm?: ApplicantPayload) => {
    const payload = overrideForm || form;
    setPredicting(true);
    setError(null);
    setResult(null);

    try {
      const data = await submitPrediction(payload);
      setResult(data);
      if (!overrideForm) setForm(payload);
      toast({ title: "Prediction complete", description: `Result: ${data.prediction}` });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
      toast({ title: "Error", description: "Prediction failed. Is the model trained?", variant: "destructive" });
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Loan Prediction</h1>
        <p className="text-muted-foreground mt-1">Enter applicant details to get an AI-powered approval decision with financial advice.</p>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1.3fr_1fr]">
        {/* Form */}
        <div>
          <Card className="border-border/50">
            <CardContent className="p-6">
              <h2 className="text-lg font-bold mb-5">Applicant Information</h2>

              <div className="grid gap-4 sm:grid-cols-2">
                <LabelField label="Gender">
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.Gender} onChange={(e) => updateField("Gender", e.target.value as "Male" | "Female")}>
                    <option>Male</option><option>Female</option>
                  </select>
                </LabelField>
                <LabelField label="Married">
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.Married} onChange={(e) => updateField("Married", e.target.value as "Yes" | "No")}>
                    <option>No</option><option>Yes</option>
                  </select>
                </LabelField>
                <LabelField label="Dependents">
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.Dependents} onChange={(e) => updateField("Dependents", e.target.value as any)}>
                    <option>0</option><option>1</option><option>2</option><option>3</option><option>3+</option>
                  </select>
                </LabelField>
                <LabelField label="Education">
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.Education} onChange={(e) => updateField("Education", e.target.value as "Graduate" | "Not Graduate")}>
                    <option>Graduate</option><option>Not Graduate</option>
                  </select>
                </LabelField>
                <LabelField label="Employment">
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.Self_Employed} onChange={(e) => updateField("Self_Employed", e.target.value as "Yes" | "No")}>
                    <option value="No">Salaried</option><option value="Yes">Self-Employed</option>
                  </select>
                </LabelField>
                <LabelField label="Property Area">
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.Property_Area} onChange={(e) => updateField("Property_Area", e.target.value as any)}>
                    <option>Urban</option><option>Semiurban</option><option>Rural</option>
                  </select>
                </LabelField>
                <LabelField label="Applicant Income (₹)">
                  <input type="number" min={0} className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.ApplicantIncome} onChange={(e) => updateField("ApplicantIncome", Number(e.target.value))} />
                </LabelField>
                <LabelField label="Co-applicant Income (₹)">
                  <input type="number" min={0} className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.CoapplicantIncome} onChange={(e) => updateField("CoapplicantIncome", Number(e.target.value))} />
                </LabelField>
                <LabelField label="Loan Amount (₹K)">
                  <input type="number" min={1} className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.LoanAmount} onChange={(e) => updateField("LoanAmount", Number(e.target.value))} />
                </LabelField>
                <LabelField label={`Repayment Term (${Math.round(form.Loan_Amount_Term / 12)} yr${Math.round(form.Loan_Amount_Term / 12) > 1 ? 's' : ''})`}>
                  <input
                    type="number"
                    min={12}
                    max={480}
                    className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                    value={form.Loan_Amount_Term}
                    onChange={(e) => updateField("Loan_Amount_Term", Number(e.target.value))}
                  />
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {[12, 24, 36, 60, 84, 120, 180, 240, 360].map((m) => (
                      <button
                        key={m}
                        type="button"
                        onClick={() => updateField("Loan_Amount_Term", m)}
                        className={`rounded-md px-2 py-0.5 text-xs border transition ${
                          form.Loan_Amount_Term === m
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-border text-muted-foreground hover:border-primary/50"
                        }`}
                      >
                        {m >= 12 ? `${m / 12}y` : `${m}m`}
                      </button>
                    ))}
                  </div>
                </LabelField>
                <LabelField label="Credit History">
                  <select className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" value={form.Credit_History} onChange={(e) => updateField("Credit_History", Number(e.target.value) as 0 | 1)}>
                    <option value={1}>Good (meets guidelines)</option>
                    <option value={0}>None / Poor</option>
                  </select>
                </LabelField>
              </div>

              <button
                type="button"
                onClick={() => handleSubmit()}
                disabled={predicting}
                className="mt-6 w-full rounded-xl bg-primary px-4 py-3 text-sm font-bold text-primary-foreground shadow transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {predicting ? "Analysing..." : "Analyse & Predict Loan Approval"}
              </button>

              {error && (
                <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300">
                  {error}
                  <p className="mt-1 text-xs">Make sure the model is trained via POST /models/train.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* What-If Simulator */}
          {result && (
            <div className="mt-6">
              <WhatIfSimulator form={form} originalProb={result.approval_probability_percent} onSubmit={(adj) => handleSubmit(adj)} />
            </div>
          )}
        </div>

        {/* Result / Financial Advisor */}
        <div>
          {predicting ? (
            <Card className="border-border/50">
              <CardContent className="p-6 space-y-4">
                {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-16 rounded-xl" />)}
              </CardContent>
            </Card>
          ) : result ? (
            <FinancialAdvisor form={form} result={result} />
          ) : (
            <Card className="border-border/50">
              <CardContent className="flex items-center justify-center p-12">
                <div className="text-center">
                  <p className="text-4xl mb-4">📋</p>
                  <p className="text-muted-foreground">Fill in the form and click "Analyse & Predict"</p>
                  <p className="text-xs text-muted-foreground mt-2">The Financial Advisor will appear here with personalized recommendations.</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function LabelField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1.5 text-sm font-medium">
      {label}
      {children}
    </label>
  );
}
