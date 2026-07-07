import { Card, CardContent } from "@/components/ui/card";

const team = [
  { name: "Sagar Rawat", role: "Full-Stack Developer & ML Engineer", bio: "Built Credify as a portfolio project showcasing end-to-end fintech application development with AI/ML integration." },
];

const timeline = [
  { year: "Dataset", event: "Loan approval dataset from Kaggle with 171 records and 12 features" },
  { year: "ML Pipeline", event: "Trained and compared Logistic Regression, Decision Tree, and Random Forest" },
  { year: "Architecture", event: "React frontend + FastAPI backend + scikit-learn ML engine" },
  { year: "Deployment", event: "Vercel-ready configuration with serverless API functions" },
];

export default function About() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 md:px-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold">About Credify</h1>
        <p className="mt-4 text-muted-foreground leading-relaxed">
          Credify is an AI-powered loan approval analytics and prediction platform built as a portfolio project.
          It demonstrates end-to-end fintech application development combining modern frontend technologies
          with machine learning backend services.
        </p>

        <h2 className="text-2xl font-bold mt-12 mb-6">Project Timeline</h2>
        <div className="space-y-4">
          {timeline.map((item) => (
            <Card key={item.year} className="border-border/50">
              <CardContent className="flex items-start gap-4 p-5">
                <span className="shrink-0 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                  {item.year}
                </span>
                <p className="text-sm text-muted-foreground">{item.event}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <h2 className="text-2xl font-bold mt-12 mb-6">Developer</h2>
        <Card className="border-border/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-lg font-bold text-primary">
                SR
              </div>
              <div>
                <h3 className="font-semibold">{team[0].name}</h3>
                <p className="text-sm text-muted-foreground">{team[0].role}</p>
                <p className="text-sm text-muted-foreground mt-3">{team[0].bio}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <h2 className="text-2xl font-bold mt-12 mb-6">Tech Stack</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {[
            "React 19", "TypeScript", "Vite 7", "Tailwind CSS v4", "shadcn/ui", "Framer Motion",
            "FastAPI", "Python 3.11", "scikit-learn", "Pandas", "NumPy", "SQLite",
          ].map((tech) => (
            <Card key={tech} className="border-border/50">
              <CardContent className="p-3 text-center text-sm font-medium">{tech}</CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
