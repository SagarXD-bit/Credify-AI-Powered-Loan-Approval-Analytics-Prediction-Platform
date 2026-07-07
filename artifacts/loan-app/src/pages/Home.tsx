import { useEffect, useState } from "react";
import { Link } from "wouter";
import { ArrowRight, BarChart3, Brain, Shield, Zap, TrendingUp, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { fetchDashboard, type DashboardKPIs } from "@/lib/api";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Predictions",
    description: "Ensemble ML models (Random Forest, Decision Tree, Logistic Regression) analyze applicant data to predict loan approval probability.",
  },
  {
    icon: Shield,
    title: "Risk Assessment",
    description: "Comprehensive risk profiling with explainable AI — understand exactly why a decision was made.",
  },
  {
    icon: TrendingUp,
    title: "Financial Advisor",
    description: "Get personalized recommendations to improve approval odds, including optimal loan amounts and repayment terms.",
  },
  {
    icon: BarChart3,
    title: "Analytics Dashboard",
    description: "Real-time KPIs, approval trends, demographic insights, and model performance metrics at a glance.",
  },
  {
    icon: Zap,
    title: "What-If Simulator",
    description: "Experiment with different financial scenarios and see instant impact on your approval probability.",
  },
  {
    icon: ArrowUpRight,
    title: "Model Benchmarks",
    description: "Three models compared by accuracy, precision, recall, and F1 score — the best is auto-selected for predictions.",
  },
];

const flowSteps = [
  { step: "01", title: "Data Intake", detail: "Capture applicant profile, income, debt, loan requirement, and credit characteristics." },
  { step: "02", title: "Feature Scoring", detail: "Transform inputs into risk signals like debt-to-income ratio and repayment capacity bands." },
  { step: "03", title: "Model Decision", detail: "Trained ML models estimate approval probability, confidence, and key drivers." },
  { step: "04", title: "Financial Advice", detail: "Generate personalized recommendations to improve the applicant's financial profile." },
];

export default function Home() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);

  useEffect(() => {
    fetchDashboard()
      .then((data) => setKpis(data.kpis))
      .catch(() => {});
  }, []);

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border/40">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-blue-600/5" />
        <div className="mx-auto max-w-7xl px-4 py-20 md:px-8 md:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-xs font-medium text-cyan-700 dark:border-cyan-800 dark:bg-cyan-950 dark:text-cyan-300">
              🚀 AI-Powered Lending Intelligence
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl">
              Smarter Loan Decisions with{" "}
              <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
                AI
              </span>
            </h1>
            <p className="mt-6 text-lg text-muted-foreground md:text-xl">
              Credify combines machine learning, financial analysis, and explainable AI to deliver instant,
              fair, and transparent loan approval recommendations.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <Button asChild size="lg" className="rounded-full">
                <Link href="/prediction">
                  Try Loan Prediction <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="rounded-full">
                <Link href="/dashboard">View Analytics</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      {kpis && (
        <section className="border-b border-border/40 bg-muted/30">
          <div className="mx-auto max-w-7xl px-4 py-12 md:px-8">
            <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
              {[
                { label: "Applications Reviewed", value: kpis.total_applications.toLocaleString() },
                { label: "Approval Rate", value: `${kpis.approval_rate}%` },
                { label: "Loans Approved", value: kpis.approved_loans.toLocaleString() },
                { label: "Avg Loan Amount", value: `₹${kpis.average_loan_amount_k}K` },
              ].map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="text-3xl font-bold">{stat.value}</p>
                  <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Features */}
      <section className="py-20 md:py-28">
        <div className="mx-auto max-w-7xl px-4 md:px-8">
          <div className="mx-auto max-w-2xl text-center mb-12">
            <h2 className="text-3xl font-bold">Everything you need for intelligent lending</h2>
            <p className="mt-4 text-muted-foreground">Credify provides a complete toolkit for data-driven loan approval decisions.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <Card key={feature.title} className="border-border/50 transition-shadow hover:shadow-md">
                <CardContent className="p-6">
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="border-t border-border/40 bg-muted/30 py-20 md:py-28">
        <div className="mx-auto max-w-7xl px-4 md:px-8">
          <div className="mx-auto max-w-2xl text-center mb-12">
            <h2 className="text-3xl font-bold">How It Works</h2>
            <p className="mt-4 text-muted-foreground">From data intake to financial advice in four simple steps.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-4">
            {flowSteps.map((step) => (
              <div key={step.step} className="relative text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                  {step.step}
                </div>
                <h3 className="font-semibold mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 md:py-28">
        <div className="mx-auto max-w-7xl px-4 md:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold">Ready to make smarter lending decisions?</h2>
            <p className="mt-4 text-muted-foreground">Try the prediction engine with real ML models trained on actual loan data.</p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <Button asChild size="lg" className="rounded-full">
                <Link href="/prediction">Get Started <ArrowRight className="ml-2 h-4 w-4" /></Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="rounded-full">
                <Link href="/ai-model">Learn About the AI</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
