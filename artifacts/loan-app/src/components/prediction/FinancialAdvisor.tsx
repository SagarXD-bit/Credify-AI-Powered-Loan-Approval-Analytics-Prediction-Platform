import type { ApplicantPayload, PredictionResult } from "@/lib/api";

type FinancialMetrics = {
  monthlyEmi: number;
  debtToIncomeRatio: number;
  financialHealthScore: number;
  riskLevel: string;
  suggestedLoanAmount: number;
  suggestedTenure: number;
  recommendations: string[];
};

function calculateMetrics(form: ApplicantPayload, result: PredictionResult): FinancialMetrics {
  const annualRate = 0.09;
  const monthlyRate = annualRate / 12;
  const principal = form.LoanAmount * 1000;
  const months = form.Loan_Amount_Term;
  const emi = principal * monthlyRate * Math.pow(1 + monthlyRate, months) / (Math.pow(1 + monthlyRate, months) - 1);
  const monthlyEmi = Math.round(emi);
  const totalIncome = form.ApplicantIncome + form.CoapplicantIncome;
  const dti = totalIncome > 0 ? Math.round(((form.CoapplicantIncome > 0 ? 0 : 0) + monthlyEmi) / totalIncome * 100) : 0;
  const actualDti = totalIncome > 0 ? Math.round(monthlyEmi / totalIncome * 100) : 0;

  let healthScore = 50;
  if (form.Credit_History === 1) healthScore += 20;
  if (actualDti < 30) healthScore += 15;
  else if (actualDti < 45) healthScore += 5;
  else healthScore -= 10;
  if (form.Education === "Graduate") healthScore += 5;
  if (form.Self_Employed === "No") healthScore += 5;
  if (form.ApplicantIncome > 10000) healthScore += 5;
  healthScore = Math.max(0, Math.min(100, healthScore));

  const prob = result.approval_probability_percent;
  const riskLevel = prob >= 80 ? "Low" : prob >= 60 ? "Medium" : prob >= 40 ? "High" : "Very High";

  const maxEmi = totalIncome * 0.4;
  const suggestedLoanAmount = Math.round(maxEmi / (monthlyRate * Math.pow(1 + monthlyRate, months) / (Math.pow(1 + monthlyRate, months) - 1)) / 1000);

  let suggestedTenure = months;
  if (actualDti > 40) {
    const targetEmi = totalIncome * 0.3;
    const n = Math.log(targetEmi / (targetEmi - principal * monthlyRate)) / Math.log(1 + monthlyRate);
    suggestedTenure = Math.min(480, Math.max(12, Math.round(n)));
  }

  const recommendations: string[] = [];
  if (actualDti > 40) recommendations.push("Reduce your debt-to-income ratio by paying off existing debts or increasing your income.");
  if (result.approval_probability_percent < 70 && form.ApplicantIncome < 15000) recommendations.push("Consider increasing your income through additional sources or adding a co-applicant.");
  if (result.approval_probability_percent < 60 && form.LoanAmount > 300) recommendations.push("Requesting a lower loan amount may significantly improve your approval chances.");
  if (form.Credit_History === 0) recommendations.push("Building a credit history by using secured credit cards or small loans can help in future applications.");
  if (actualDti > 50) recommendations.push("Consider extending your repayment tenure to reduce monthly EMI burden.");
  if (form.CoapplicantIncome === 0 && result.approval_probability_percent < 70) recommendations.push("Adding a co-applicant with stable income could improve your approval probability.");
  if (recommendations.length === 0) recommendations.push("Your financial profile looks strong. Maintain your current practices.");

  return {
    monthlyEmi,
    debtToIncomeRatio: actualDti,
    financialHealthScore: healthScore,
    riskLevel,
    suggestedLoanAmount,
    suggestedTenure,
    recommendations,
  };
}

function getHealthColor(score: number) {
  if (score >= 75) return "text-emerald-600";
  if (score >= 50) return "text-amber-600";
  return "text-rose-600";
}

function getHealthBg(score: number) {
  if (score >= 75) return "bg-emerald-100 dark:bg-emerald-900";
  if (score >= 50) return "bg-amber-100 dark:bg-amber-900";
  return "bg-rose-100 dark:bg-rose-900";
}

function getRiskColor(level: string) {
  switch (level) {
    case "Low": return "text-emerald-600";
    case "Medium": return "text-amber-600";
    case "High": return "text-rose-600";
    default: return "text-red-700";
  }
}

function getRiskBg(level: string) {
  switch (level) {
    case "Low": return "bg-emerald-100 dark:bg-emerald-900";
    case "Medium": return "bg-amber-100 dark:bg-amber-900";
    case "High": return "bg-rose-100 dark:bg-rose-900";
    default: return "bg-red-100 dark:bg-red-900";
  }
}

export function FinancialAdvisor({
  form,
  result,
}: {
  form: ApplicantPayload;
  result: PredictionResult;
}) {
  const metrics = calculateMetrics(form, result);

  return (
    <div className="space-y-6">
      {/* Decision Banner */}
      <div
        className={`rounded-2xl border p-6 text-center ${
          result.approved
            ? "border-emerald-200 bg-gradient-to-br from-emerald-50 to-teal-50 dark:border-emerald-800 dark:from-emerald-950 dark:to-teal-950"
            : "border-rose-200 bg-gradient-to-br from-rose-50 to-pink-50 dark:border-rose-800 dark:from-rose-950 dark:to-pink-950"
        }`}
      >
        <p className={`text-4xl font-black ${result.approved ? "text-emerald-700 dark:text-emerald-400" : "text-rose-700 dark:text-rose-400"}`}>
          {result.prediction}
        </p>
        <p className="mt-2 text-sm text-muted-foreground">
          Approval Probability: <span className="font-bold">{result.approval_probability_percent}%</span>
        </p>
        <p className="text-sm text-muted-foreground">
          Confidence: <span className="font-bold">{result.confidence}</span>
        </p>
        <p className="text-xs text-muted-foreground mt-1">Model: {result.model_used}</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <MetricCard label="Approval Probability" value={`${result.approval_probability_percent}%`} />
        <MetricCard label="Risk Level" value={metrics.riskLevel} valueClass={getRiskColor(metrics.riskLevel)} badgeBg={getRiskBg(metrics.riskLevel)} />
        <MetricCard label="Confidence" value={result.confidence} />
        <MetricCard label="Financial Health" value={`${metrics.financialHealthScore}/100`} valueClass={getHealthColor(metrics.financialHealthScore)} badgeBg={getHealthBg(metrics.financialHealthScore)} />
        <MetricCard label="Est. Monthly EMI" value={`₹${metrics.monthlyEmi.toLocaleString()}`} />
        <MetricCard label="Debt-to-Income" value={`${metrics.debtToIncomeRatio}%`} />
      </div>

      {/* Suggestions */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-2">
        <MetricCard label="Suggested Loan" value={`₹${metrics.suggestedLoanAmount}K`} />
        <MetricCard label="Suggested Tenure" value={`${metrics.suggestedTenure} months`} />
      </div>

      {/* Key Factors */}
      <div className="rounded-xl border border-border/50 bg-card p-5">
        <p className="text-xs uppercase tracking-widest text-muted-foreground font-semibold mb-3">Key Factors</p>
        <ul className="space-y-2">
          {result.explanations.map((reason, i) => (
            <li key={i} className="rounded-lg bg-muted px-3 py-2 text-sm">{reason.replace(/\*\*/g, "")}</li>
          ))}
        </ul>
      </div>

      {/* Recommendations */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-5 dark:border-amber-800 dark:bg-amber-950">
        <p className="text-xs uppercase tracking-widest font-semibold mb-3 text-amber-800 dark:text-amber-300">
          Financial Advisor Recommendations
        </p>
        <ul className="space-y-2">
          {metrics.recommendations.map((rec, i) => (
            <li key={i} className="flex gap-2 text-sm text-amber-900 dark:text-amber-200">
              <span className="mt-0.5 shrink-0">💡</span>
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Simple Language Explanation */}
      <div className="rounded-xl border border-border/50 bg-card p-5">
        <p className="text-xs uppercase tracking-widest text-muted-foreground font-semibold mb-2">In Plain English</p>
        <p className="text-sm text-muted-foreground">
          {result.approved
            ? `Based on your profile, the AI model predicts a high likelihood of loan approval. Your ${form.Credit_History === 1 ? "good credit history" : "credit profile"} ${form.Credit_History === 1 ? "strongly supports" : "could be improved for"} this application. The recommended actions above can further strengthen your application.`
            : `The AI model currently predicts a lower approval probability for your application. The key areas to focus on are highlighted in the recommendations above. Even small improvements to your financial profile can significantly impact approval chances.`}
        </p>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  valueClass,
  badgeBg,
}: {
  label: string;
  value: string;
  valueClass?: string;
  badgeBg?: string;
}) {
  return (
    <div className="rounded-xl border border-border/50 bg-card p-4">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className={`text-lg font-bold ${valueClass || ""}`}>{value}</p>
    </div>
  );
}
