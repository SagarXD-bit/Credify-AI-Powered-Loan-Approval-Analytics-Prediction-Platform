import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import type { ApplicantPayload } from "@/lib/api";

interface Props {
  form: ApplicantPayload;
  originalProb: number;
  onSubmit: (adjusted: ApplicantPayload) => void;
}

export function WhatIfSimulator({ form, originalProb, onSubmit }: Props) {
  const [income, setIncome] = useState(form.ApplicantIncome);
  const [coIncome, setCoIncome] = useState(form.CoapplicantIncome);
  const [loanAmount, setLoanAmount] = useState(form.LoanAmount);
  const [tenure, setTenure] = useState(form.Loan_Amount_Term);
  const [creditHistory, setCreditHistory] = useState(form.Credit_History);

  const adjusted: ApplicantPayload = useMemo(
    () => ({
      ...form,
      ApplicantIncome: income,
      CoapplicantIncome: coIncome,
      LoanAmount: loanAmount,
      Loan_Amount_Term: tenure,
      Credit_History: creditHistory as 0 | 1,
    }),
    [form, income, coIncome, loanAmount, tenure, creditHistory],
  );

  return (
    <Card className="border-cyan-200 dark:border-cyan-800">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <span>🔮</span> What-If Simulator
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Adjust values below to see how changes affect your approval probability.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label>Applicant Income (₹)</Label>
          <Input type="number" value={income} onChange={(e) => setIncome(Number(e.target.value))} min={0} />
        </div>
        <div>
          <Label>Co-applicant Income (₹)</Label>
          <Input type="number" value={coIncome} onChange={(e) => setCoIncome(Number(e.target.value))} min={0} />
        </div>
        <div>
          <Label>Loan Amount (₹ thousands)</Label>
          <Input type="number" value={loanAmount} onChange={(e) => setLoanAmount(Number(e.target.value))} min={1} />
        </div>
        <div>
          <Label>Repayment Tenure: {tenure} months ({Math.round(tenure / 12)} yrs)</Label>
          <Slider min={12} max={480} step={12} value={[tenure]} onValueChange={([v]) => setTenure(v)} className="mt-2" />
        </div>
        <div>
          <Label>Credit History</Label>
          <select
            className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            value={creditHistory}
            onChange={(e) => setCreditHistory(Number(e.target.value) as 0 | 1)}
          >
            <option value={1}>Good (meets guidelines)</option>
            <option value={0}>None / Poor</option>
          </select>
        </div>
        <button
          onClick={() => onSubmit(adjusted)}
          className="w-full rounded-xl bg-cyan-600 px-4 py-3 text-sm font-bold text-white shadow transition hover:bg-cyan-700"
        >
          Simulate Changes
        </button>
      </CardContent>
    </Card>
  );
}
