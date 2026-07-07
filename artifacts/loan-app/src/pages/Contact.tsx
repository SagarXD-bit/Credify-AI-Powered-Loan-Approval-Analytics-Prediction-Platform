import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Mail, Github, Linkedin, Globe } from "lucide-react";

export default function Contact() {
  const { toast } = useToast();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({ title: "Message sent!", description: "Thanks for reaching out. I'll get back to you soon." });
    setName("");
    setEmail("");
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-16 md:px-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold">Get in Touch</h1>
        <p className="mt-4 text-muted-foreground">
          Have questions, suggestions, or want to collaborate? Reach out.
        </p>

        <div className="grid gap-8 md:grid-cols-2 mt-10">
          <Card className="border-border/50">
            <CardContent className="p-6">
              <h2 className="font-semibold mb-4">Send a Message</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Name</label>
                  <Input value={name} onChange={(e) => setName(e.target.value)} required placeholder="Your name" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Email</label>
                  <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="your@email.com" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Message</label>
                  <Textarea rows={5} required placeholder="Your message..." />
                </div>
                <Button type="submit" className="w-full rounded-full">Send Message</Button>
              </form>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <Card className="border-border/50">
              <CardContent className="p-5 flex items-center gap-4">
                <Globe className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">Portfolio</p>
                  <a href="https://sagar-rawat.vercel.app" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-primary">
                    sagar-rawat.vercel.app
                  </a>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border/50">
              <CardContent className="p-5 flex items-center gap-4">
                <Github className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">GitHub</p>
                  <a href="https://github.com/sagar-rawat" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-primary">
                    github.com/sagar-rawat
                  </a>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border/50">
              <CardContent className="p-5 flex items-center gap-4">
                <Linkedin className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">LinkedIn</p>
                  <a href="https://linkedin.com/in/sagar-rawat" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-primary">
                    linkedin.com/in/sagar-rawat
                  </a>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border/50">
              <CardContent className="p-5 flex items-center gap-4">
                <Mail className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">Email</p>
                  <a href="mailto:sagar@example.com" className="text-sm text-muted-foreground hover:text-primary">
                    sagar@example.com
                  </a>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
