import { Link } from "wouter";
import { Sparkles } from "lucide-react";

const quickLinks = [
  { href: "/", label: "Home" },
  { href: "/prediction", label: "Loan Prediction" },
  { href: "/dashboard", label: "Analytics" },
  { href: "/ai-model", label: "AI Model" },
];

const techStack = [
  "React", "TypeScript", "Tailwind CSS", "FastAPI",
  "scikit-learn", "PostgreSQL", "Vite", "shadcn/ui",
];

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-background">
      <div className="mx-auto max-w-7xl px-4 py-12 md:px-8">
        <div className="grid gap-8 md:grid-cols-3">
          <div>
            <Link href="/" className="flex items-center gap-2 font-bold text-lg mb-3">
              <Sparkles className="h-5 w-5 text-cyan-500" />
              <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
                Credify
              </span>
            </Link>
            <p className="text-sm text-muted-foreground max-w-xs">
              AI-powered loan approval analytics and prediction platform. Making lending decisions smarter, faster, and fairer.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-sm mb-3">Quick Links</h3>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-sm mb-3">Technology</h3>
            <div className="flex flex-wrap gap-2">
              {techStack.map((tech) => (
                <span
                  key={tech}
                  className="inline-flex items-center rounded-full border border-border px-2.5 py-0.5 text-xs font-medium text-muted-foreground"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 border-t border-border/40 pt-6 text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Credify. All rights reserved. Built for portfolio excellence.</p>
        </div>
      </div>
    </footer>
  );
}
