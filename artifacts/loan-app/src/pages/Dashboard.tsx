import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchDashboard, fetchPredictionHistory, type DashboardKPIs, type HistoryRecord } from "@/lib/api";

const COLORS = ["#22d3ee", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

export default function Dashboard() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchDashboard().then((d) => setKpis(d.kpis)),
      fetchPredictionHistory(10).then((d) => setHistory(d.records || [])),
    ]).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-10 md:px-8 space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  const pieData = kpis
    ? [
        { name: "Approved", value: kpis.approved_loans },
        { name: "Rejected", value: kpis.rejected_loans },
      ]
    : [];

  const historyChart =
    history.length > 0
      ? history
          .slice()
          .reverse()
          .map((r) => ({
            name: r.timestamp?.slice(5, 10) || `#${r.id}`,
            probability: Math.round(r.probability * 100),
          }))
      : [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        <p className="text-muted-foreground mt-1">Real-time KPIs and insights from the Credify prediction engine.</p>
      </div>

      {kpis && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground">Total Applications</p>
              <p className="text-3xl font-bold mt-1">{kpis.total_applications.toLocaleString()}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground">Approval Rate</p>
              <p className="text-3xl font-bold mt-1 text-emerald-600">{kpis.approval_rate}%</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground">Approved</p>
              <p className="text-3xl font-bold mt-1">{kpis.approved_loans.toLocaleString()}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground">Avg Loan Amount</p>
              <p className="text-3xl font-bold mt-1">₹{kpis.average_loan_amount_k}K</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Approval Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value" label>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={i === 0 ? "#10b981" : "#ef4444"} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Prediction Scores</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={historyChart}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis domain={[0, 100]} className="text-xs" />
                <Tooltip />
                <Bar dataKey="probability" fill="var(--color-primary, #3b82f6)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Prediction History</CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <p className="text-sm text-muted-foreground py-8 text-center">No predictions yet. Submit one on the Loan Prediction page.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-3 font-medium">Date</th>
                    <th className="pb-3 font-medium">Gender</th>
                    <th className="pb-3 font-medium">Amount</th>
                    <th className="pb-3 font-medium">Decision</th>
                    <th className="pb-3 font-medium">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((r) => (
                    <tr key={r.id} className="border-b last:border-0">
                      <td className="py-3">{r.timestamp?.slice(0, 10) || "-"}</td>
                      <td className="py-3">{r.gender}</td>
                      <td className="py-3">₹{r.loan_amount}K</td>
                      <td className="py-3">
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            r.prediction === "Approved"
                              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300"
                              : "bg-rose-100 text-rose-700 dark:bg-rose-900 dark:text-rose-300"
                          }`}
                        >
                          {r.prediction}
                        </span>
                      </td>
                      <td className="py-3">{r.confidence}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
