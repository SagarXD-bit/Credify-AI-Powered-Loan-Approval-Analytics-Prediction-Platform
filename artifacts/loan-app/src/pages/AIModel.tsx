import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { fetchModelMeta, fetchFeatureImportances } from "@/lib/api";

export default function AIModel() {
  const [meta, setMeta] = useState<Record<string, any> | null>(null);
  const [importances, setImportances] = useState<{ Feature: string; Importance: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchModelMeta().then(setMeta).catch(() => {}),
      fetchFeatureImportances()
        .then((d) => setImportances(d.feature_importances || []))
        .catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-10 md:px-8 space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 rounded-xl" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  const modelName = meta?.best_model_name || "Decision Tree";
  const metrics = meta?.metrics || {};

  const metricsRows = Object.entries(metrics).map(([name, m]: [string, any]) => ({
    name,
    accuracy: m.accuracy ? (m.accuracy * 100).toFixed(1) : "-",
    precision: m.precision ? (m.precision * 100).toFixed(1) : "-",
    recall: m.recall ? (m.recall * 100).toFixed(1) : "-",
    f1: m.f1 ? (m.f1 * 100).toFixed(1) : "-",
    isBest: name === modelName,
  }));

  const chartData = Object.entries(metrics).map(([name, m]: [string, any]) => ({
    name,
    ...(m.accuracy !== undefined ? { Accuracy: +(m.accuracy * 100).toFixed(1) } : {}),
    ...(m.precision !== undefined ? { Precision: +(m.precision * 100).toFixed(1) } : {}),
    ...(m.recall !== undefined ? { Recall: +(m.recall * 100).toFixed(1) } : {}),
    ...(m.f1 !== undefined ? { "F1 Score": +(m.f1 * 100).toFixed(1) } : {}),
  }));

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">AI Model</h1>
        <p className="text-muted-foreground mt-1">Understanding the machine learning pipeline behind Credify.</p>
      </div>

      {/* Pipeline Overview */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {[
          { step: "1", title: "Dataset", desc: "171 records, 12 features from Kaggle loan data" },
          { step: "2", title: "Preprocessing", desc: "Handle missing values, encode categoricals, split train/test" },
          { step: "3", title: "Training", desc: "3 models compared, best by F1-score auto-selected" },
          { step: "4", title: "Prediction", desc: "Real-time inference with explainable AI output" },
        ].map((s) => (
          <Card key={s.step} className="border-border/50">
            <CardContent className="p-5">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">{s.step}</div>
              <h3 className="font-semibold text-sm mb-1">{s.title}</h3>
              <p className="text-xs text-muted-foreground">{s.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Dataset Info */}
      <Card className="mb-8 border-border/50">
        <CardHeader>
          <CardTitle className="text-base">Dataset & Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <h4 className="font-medium text-sm mb-2">Categorical Features (Label Encoded)</h4>
              <div className="flex flex-wrap gap-2">
                {["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"].map((f) => (
                  <Badge key={f} variant="secondary">{f}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium text-sm mb-2">Numerical Features</h4>
              <div className="flex flex-wrap gap-2">
                {["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History"].map((f) => (
                  <Badge key={f} variant="secondary">{f}</Badge>
                ))}
              </div>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            Missing values are imputed (categorical → mode, numerical → median). Target: Loan_Status (Y/N) encoded as 1/0.
          </p>
        </CardContent>
      </Card>

      {/* Model Metrics */}
      <Card className="mb-8 border-border/50">
        <CardHeader>
          <CardTitle className="text-base">Model Performance</CardTitle>
        </CardHeader>
        <CardContent>
          {metricsRows.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-3 font-medium">Model</th>
                    <th className="pb-3 font-medium">Accuracy</th>
                    <th className="pb-3 font-medium">Precision</th>
                    <th className="pb-3 font-medium">Recall</th>
                    <th className="pb-3 font-medium">F1 Score</th>
                  </tr>
                </thead>
                <tbody>
                  {metricsRows.map((r) => (
                    <tr key={r.name} className="border-b last:border-0">
                      <td className="py-3 font-medium">
                        {r.name} {r.isBest && <Badge className="ml-2 text-xs">⭐ Best</Badge>}
                      </td>
                      <td className="py-3">{r.accuracy}%</td>
                      <td className="py-3">{r.precision}%</td>
                      <td className="py-3">{r.recall}%</td>
                      <td className="py-3">{r.f1}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Train a model on the Prediction page to see metrics.</p>
          )}
        </CardContent>
      </Card>

      {/* Metrics Chart */}
      {chartData.length > 0 && (
        <Card className="mb-8 border-border/50">
          <CardHeader>
            <CardTitle className="text-base">Metrics Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis domain={[0, 100]} className="text-xs" />
                <Tooltip />
                <Bar dataKey="Accuracy" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Precision" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Recall" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="F1 Score" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Feature Importance */}
      <Card className="mb-8 border-border/50">
        <CardHeader>
          <CardTitle className="text-base">Feature Importance ({modelName})</CardTitle>
        </CardHeader>
        <CardContent>
          {importances.length > 0 ? (
            <ResponsiveContainer width="100%" height={Math.max(200, importances.length * 35)}>
              <BarChart data={importances} layout="vertical" margin={{ left: 100 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis type="number" domain={[0, 1]} className="text-xs" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <YAxis dataKey="Feature" type="category" className="text-xs" width={120} />
                <Tooltip formatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
                <Bar dataKey="Importance" fill="#22d3ee" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">Feature importance data not available. Train the model first.</p>
          )}
        </CardContent>
      </Card>

      {/* Workflow */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="text-base">Prediction Workflow</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-3 text-sm text-muted-foreground">
            <li className="flex gap-3"><span className="font-bold text-primary">1.</span> User submits applicant data via the form</li>
            <li className="flex gap-3"><span className="font-bold text-primary">2.</span> Data is encoded using the same pipeline as training</li>
            <li className="flex gap-3"><span className="font-bold text-primary">3.</span> Trained model runs inference (predict + predict_proba)</li>
            <li className="flex gap-3"><span className="font-bold text-primary">4.</span> Result is stored in the database for audit/history</li>
            <li className="flex gap-3"><span className="font-bold text-primary">5.</span> Feature importance generates plain-English explanations</li>
            <li className="flex gap-3"><span className="font-bold text-primary">6.</span> Financial Advisor computes additional metrics and recommendations</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
