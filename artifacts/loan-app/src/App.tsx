import { useMemo, useState } from "react";
import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useToast } from "@/hooks/use-toast";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

type LoanFormState = {
  applicantName: string;
  monthlyIncome: number;
  loanAmount: number;
  creditScore: number;
  employmentYears: number;
  monthlyDebt: number;
};

const defaultForm: LoanFormState = {
  applicantName: "",
  monthlyIncome: 85000,
  loanAmount: 1200000,
  creditScore: 720,
  employmentYears: 4,
  monthlyDebt: 18000,
};

type StatCard = {
  title: string;
  value: string;
  detail: string;
  accent: string;
};

const statCards: StatCard[] = [
  {
    title: "Applications Reviewed",
    value: "12,408",
    detail: "+8.4% from last month",
    accent: "from-sky-500 to-blue-700",
  },
  {
    title: "Approval Rate",
    value: "67.3%",
    detail: "Current policy profile",
    accent: "from-emerald-500 to-teal-700",
  },
  {
    title: "Average Risk Score",
    value: "41 / 100",
    detail: "Lower is better",
    accent: "from-amber-500 to-orange-700",
  },
  {
    title: "Fraud Flags",
    value: "1.7%",
    detail: "Actively monitored",
    accent: "from-rose-500 to-red-700",
  },
];

const recentApplications = [
  { name: "Aarav Sharma", amount: "Rs 9.5L", score: 768, status: "Approved" },
  { name: "Riya Mehta", amount: "Rs 4.2L", score: 641, status: "Review" },
  { name: "Kabir Jain", amount: "Rs 16.0L", score: 589, status: "Declined" },
  { name: "Isha Nair", amount: "Rs 7.8L", score: 709, status: "Approved" },
];

type HomeTab = "dashboard" | "how-it-works" | "advice";

const flowSteps = [
  {
    title: "1. Data Intake",
    detail: "We capture applicant profile, income, debt, loan requirement, and credit characteristics.",
  },
  {
    title: "2. Feature Scoring",
    detail: "Inputs are transformed into risk signals like debt-to-income ratio and repayment capacity bands.",
  },
  {
    title: "3. Model Decision",
    detail: "A weighted model estimates approval probability, confidence, and key positive or negative drivers.",
  },
  {
    title: "4. Human Review",
    detail: "Borderline applications can be escalated for manual review with context from the explanation panel.",
  },
];

const applicantAdvice = [
  {
    title: "Keep debt-to-income under 35%",
    detail: "Pay off short-term debt first and avoid taking fresh obligations before applying.",
  },
  {
    title: "Build a stronger credit profile",
    detail: "Pay EMIs and card dues on time, and keep credit utilization moderate.",
  },
  {
    title: "Improve income stability",
    detail: "Lenders prefer consistent salary or business inflows for at least 6 to 12 months.",
  },
  {
    title: "Apply for realistic loan amounts",
    detail: "Requesting a loan aligned to repayment capacity significantly improves approval odds.",
  },
];

function Home() {
  const { toast } = useToast();
  const [form, setForm] = useState<LoanFormState>(defaultForm);
  const [activeTab, setActiveTab] = useState<HomeTab>("dashboard");

  const handleWatermarkClick = () => {
    const { dismiss } = toast({
      title: "Opening Developer Portfolio...",
      description: "Launching in a new tab.",
    });

    setTimeout(() => {
      dismiss();
      window.open("https://sagar-rawat.vercel.app/", "_blank", "noopener,noreferrer");
    }, 2300);
  };

  const debtToIncomeRatio = useMemo(() => {
    if (form.monthlyIncome <= 0) {
      return 100;
    }

    return Number(((form.monthlyDebt / form.monthlyIncome) * 100).toFixed(1));
  }, [form.monthlyDebt, form.monthlyIncome]);

  const decision = useMemo(() => {
    let score = 0;

    score += Math.min(35, (form.creditScore - 300) / 550 * 35);
    score += Math.min(30, (form.monthlyIncome / 200000) * 30);
    score += Math.min(15, (form.employmentYears / 10) * 15);
    score -= Math.min(20, debtToIncomeRatio * 0.45);
    score -= Math.min(12, (form.loanAmount / Math.max(form.monthlyIncome, 1)) * 0.3);

    const probability = Math.max(0.05, Math.min(0.95, score / 60));
    const approved = probability >= 0.55;

    return {
      probability,
      approved,
      confidence:
        probability >= 0.75 || probability <= 0.3
          ? "High"
          : probability >= 0.62 || probability <= 0.4
            ? "Medium"
            : "Low",
      reasons: [
        form.creditScore >= 700
          ? "Strong credit profile"
          : "Credit history needs improvement",
        debtToIncomeRatio < 35
          ? "Healthy debt-to-income ratio"
          : "Debt obligations are relatively high",
        form.employmentYears >= 3
          ? "Stable employment tenure"
          : "Limited employment history",
      ],
    };
  }, [debtToIncomeRatio, form.creditScore, form.employmentYears, form.loanAmount, form.monthlyIncome]);

  const setNumberField = (key: keyof LoanFormState, value: string) => {
    setForm((prev) => ({
      ...prev,
      [key]: key === "applicantName" ? value : Number(value),
    }));
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 pb-12 pt-6 md:px-8">
        <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-linear-to-br from-slate-900 via-blue-950 to-cyan-900 p-7 text-white shadow-xl md:p-10">
          <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-cyan-400/20 blur-2xl" />
          <div className="pointer-events-none absolute -bottom-24 left-0 h-64 w-64 rounded-full bg-fuchsia-300/10 blur-2xl" />
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-200">Credify Platform</p>
          <h1 className="mt-3 text-3xl font-black leading-tight md:text-5xl">AI Loan Approval Dashboard</h1>
          <p className="mt-4 max-w-2xl text-sm text-slate-200 md:text-base">
            Review applications, gauge lending risk, and generate instant decision signals in one workspace.
          </p>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <button
              type="button"
              onClick={() => setActiveTab("dashboard")}
              className={`rounded-xl px-4 py-3 text-sm font-semibold transition ${
                activeTab === "dashboard"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              Dashboard
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("how-it-works")}
              className={`rounded-xl px-4 py-3 text-sm font-semibold transition ${
                activeTab === "how-it-works"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              How It Works
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("advice")}
              className={`rounded-xl px-4 py-3 text-sm font-semibold transition ${
                activeTab === "advice"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              Advice Center
            </button>
          </div>
        </section>

        {activeTab === "dashboard" ? (
          <>
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {statCards.map((item) => (
                <article
                  key={item.title}
                  className={`rounded-2xl border border-white/30 bg-linear-to-br ${item.accent} p-5 text-white shadow-lg transition-transform duration-300 hover:-translate-y-1`}
                >
                  <p className="text-xs uppercase tracking-widest text-white/80">{item.title}</p>
                  <p className="mt-3 text-3xl font-extrabold">{item.value}</p>
                  <p className="mt-1 text-xs text-white/80">{item.detail}</p>
                </article>
              ))}
            </section>

            <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
              <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5">
                  <h2 className="text-xl font-bold">Loan Decision Form</h2>
                  <p className="text-sm text-slate-600">Enter applicant data to generate a live approval recommendation.</p>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="flex flex-col gap-2 text-sm font-medium text-slate-700 sm:col-span-2">
                    Applicant Name
                    <input
                      className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-cyan-500 transition focus:ring-2"
                      placeholder="e.g. Neha Kapoor"
                      value={form.applicantName}
                      onChange={(event) => setNumberField("applicantName", event.target.value)}
                    />
                  </label>

                  <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
                    Monthly Income (Rs)
                    <input
                      type="number"
                      min={0}
                      className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-cyan-500 transition focus:ring-2"
                      value={form.monthlyIncome}
                      onChange={(event) => setNumberField("monthlyIncome", event.target.value)}
                    />
                  </label>

                  <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
                    Loan Amount (Rs)
                    <input
                      type="number"
                      min={0}
                      className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-cyan-500 transition focus:ring-2"
                      value={form.loanAmount}
                      onChange={(event) => setNumberField("loanAmount", event.target.value)}
                    />
                  </label>

                  <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
                    Credit Score
                    <input
                      type="number"
                      min={300}
                      max={900}
                      className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-cyan-500 transition focus:ring-2"
                      value={form.creditScore}
                      onChange={(event) => setNumberField("creditScore", event.target.value)}
                    />
                  </label>

                  <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
                    Employment Years
                    <input
                      type="number"
                      min={0}
                      max={45}
                      className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-cyan-500 transition focus:ring-2"
                      value={form.employmentYears}
                      onChange={(event) => setNumberField("employmentYears", event.target.value)}
                    />
                  </label>

                  <label className="flex flex-col gap-2 text-sm font-medium text-slate-700 sm:col-span-2">
                    Monthly Debt (Rs)
                    <input
                      type="number"
                      min={0}
                      className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-cyan-500 transition focus:ring-2"
                      value={form.monthlyDebt}
                      onChange={(event) => setNumberField("monthlyDebt", event.target.value)}
                    />
                  </label>
                </div>
              </article>

              <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-xl font-bold">Live Decision Preview</h2>
                <p className="mt-1 text-sm text-slate-600">Instant score based on the current form values.</p>

                <div
                  className={`mt-5 rounded-2xl border p-5 ${
                    decision.approved
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-rose-200 bg-rose-50"
                  }`}
                >
                  <p className="text-xs uppercase tracking-widest text-slate-500">Decision</p>
                  <p className={`mt-2 text-3xl font-black ${decision.approved ? "text-emerald-700" : "text-rose-700"}`}>
                    {decision.approved ? "Approved" : "Declined"}
                  </p>
                  <p className="mt-2 text-sm text-slate-700">
                    Approval Probability: <span className="font-bold">{Math.round(decision.probability * 100)}%</span>
                  </p>
                  <p className="mt-1 text-sm text-slate-700">
                    Confidence: <span className="font-bold">{decision.confidence}</span>
                  </p>
                </div>

                <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-xs uppercase tracking-widest text-slate-500">Risk Signals</p>
                  <p className="mt-2 text-sm text-slate-700">Debt-to-income ratio: {debtToIncomeRatio}%</p>
                  <ul className="mt-3 space-y-2 text-sm text-slate-700">
                    {decision.reasons.map((reason) => (
                      <li key={reason} className="rounded-lg bg-white px-3 py-2">
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>
              </article>
            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold">Recent Applications</h2>
              <p className="mt-1 text-sm text-slate-600">Snapshot of recently processed requests.</p>

              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full border-separate border-spacing-y-2">
                  <thead>
                    <tr className="text-left text-xs uppercase tracking-widest text-slate-500">
                      <th className="px-3 py-2">Applicant</th>
                      <th className="px-3 py-2">Loan Amount</th>
                      <th className="px-3 py-2">Credit Score</th>
                      <th className="px-3 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentApplications.map((item) => (
                      <tr key={item.name} className="rounded-xl bg-slate-50 text-sm text-slate-700">
                        <td className="rounded-l-xl px-3 py-3 font-medium">{item.name}</td>
                        <td className="px-3 py-3">{item.amount}</td>
                        <td className="px-3 py-3">{item.score}</td>
                        <td className="rounded-r-xl px-3 py-3">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                              item.status === "Approved"
                                ? "bg-emerald-100 text-emerald-700"
                                : item.status === "Declined"
                                  ? "bg-rose-100 text-rose-700"
                                  : "bg-amber-100 text-amber-700"
                            }`}
                          >
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        ) : null}

        {activeTab === "how-it-works" ? (
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold">How This Works</h2>
            <p className="mt-2 text-sm text-slate-600">
              Credify combines input validation, risk feature engineering, and probability scoring to guide fairer lending decisions.
            </p>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {flowSteps.map((step) => (
                <article key={step.title} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <h3 className="text-base font-bold text-slate-900">{step.title}</h3>
                  <p className="mt-2 text-sm text-slate-700">{step.detail}</p>
                </article>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-cyan-200 bg-cyan-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-cyan-800">Transparency Note</p>
              <p className="mt-2 text-sm text-cyan-900">
                This UI currently uses a demo scoring formula for instant feedback. You can connect it to your trained model/API for production-grade decisions.
              </p>
            </div>
          </section>
        ) : null}

        {activeTab === "advice" ? (
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold">Advice For Applicants</h2>
            <p className="mt-2 text-sm text-slate-600">
              Practical steps applicants can take before submitting a loan request.
            </p>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {applicantAdvice.map((tip) => (
                <article key={tip.title} className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
                  <h3 className="text-base font-bold text-emerald-900">{tip.title}</h3>
                  <p className="mt-2 text-sm text-emerald-800">{tip.detail}</p>
                </article>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-amber-800">Quick Checklist Before Applying</p>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-amber-900">
                <li>Check credit report and correct errors.</li>
                <li>Gather salary slips, bank statements, and ID proofs.</li>
                <li>Use EMI calculators to select a manageable tenure.</li>
                <li>Avoid multiple loan applications in a short period.</li>
              </ul>
            </div>
          </section>
        ) : null}
      </div>

      <button
        type="button"
        onClick={handleWatermarkClick}
        className="fixed bottom-4 right-4 z-50 rounded-full border border-slate-300 bg-white/90 px-4 py-2 text-xs font-semibold tracking-wide text-slate-700 shadow-lg backdrop-blur transition hover:-translate-y-0.5 hover:bg-white hover:text-slate-900"
      >
        Crafted by Sagar Rawat
      </button>
    </div>
  );
}

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
