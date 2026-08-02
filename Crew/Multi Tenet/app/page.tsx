import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Bot,
  Building2,
  Check,
  Lock,
  ShieldCheck,
  Sparkles,
  Users,
  Workflow,
  Zap,
} from "lucide-react";

import { Navbar } from "@/components/landing/navbar";
import { DemoButton } from "@/components/landing/demo-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

function HeroMockup() {
  return (
    <div className="mx-auto mt-14 max-w-4xl">
      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-2xl">
        <div className="flex items-center gap-1.5 border-b border-border bg-muted/40 px-4 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-destructive/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-warning/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-success/60" />
          <span className="ml-3 text-xs text-muted-foreground">app.tenantdesk.ai</span>
        </div>
        <div className="flex">
          <div className="hidden w-44 shrink-0 border-r border-border p-3 sm:block">
            {[
              { label: "Dashboard", active: true },
              { label: "Knowledge", badge: "V2" },
              { label: "Agents", badge: "V2" },
              { label: "Tickets", badge: "V2" },
              { label: "Analytics", badge: "V4" },
              { label: "Users" },
              { label: "Billing" },
            ].map((item) => (
              <div
                key={item.label}
                className={`mb-1 flex items-center justify-between rounded-md px-2.5 py-1.5 text-xs ${
                  item.active
                    ? "bg-primary/10 font-medium text-primary"
                    : "text-muted-foreground"
                }`}
              >
                {item.label}
                {item.badge && (
                  <span className="rounded-full bg-muted px-1.5 text-[9px] text-muted-foreground">
                    {item.badge}
                  </span>
                )}
              </div>
            ))}
          </div>
          <div className="flex-1 space-y-3 p-4">
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: "Members", value: "12", accent: "text-primary" },
                { label: "Your role", value: "owner", accent: "text-success" },
                { label: "Events (7d)", value: "243", accent: "text-warning" },
                { label: "Plan", value: "free", accent: "" },
              ].map((kpi) => (
                <div key={kpi.label} className="rounded-lg border border-border bg-background p-2.5">
                  <p className="text-[10px] text-muted-foreground">{kpi.label}</p>
                  <p className={`mt-0.5 text-sm font-semibold ${kpi.accent}`}>{kpi.value}</p>
                </div>
              ))}
            </div>
            <div className="rounded-lg border border-border bg-background p-3">
              <p className="text-[10px] text-muted-foreground">Activity — last 7 days</p>
              <div className="mt-2 flex h-16 items-end gap-1.5">
                {[35, 60, 45, 80, 55, 95, 70].map((height, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-t bg-gradient-to-t from-indigo-500 to-violet-400"
                    style={{ height: `${height}%` }}
                  />
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10">
                <Bot className="h-3.5 w-3.5 text-primary" />
              </div>
              <div className="flex-1 rounded-lg border border-border bg-background px-3 py-1.5 text-[11px] text-muted-foreground">
                Your AI crew resolved 8 tickets today…
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const FEATURES = [
  {
    icon: ShieldCheck,
    title: "Tenant isolation",
    text: "Every workspace is a sealed namespace. Knowledge, tickets and users never leak across tenants.",
  },
  {
    icon: Bot,
    title: "Hierarchical AI crew",
    text: "A manager agent routes work to knowledge, support, escalation and report agents using CrewAI.",
  },
  {
    icon: BookOpen,
    title: "Own knowledge base",
    text: "Upload PDFs, DOCX, Markdown and FAQs. Each tenant gets its own RAG pipeline over Qdrant.",
  },
  {
    icon: Workflow,
    title: "Checkpointed flows",
    text: "Long-running workflows with pause, resume, retry and human approval steps.",
  },
  {
    icon: BarChart3,
    title: "Usage analytics",
    text: "Track requests, tokens, response times and cost — per workspace, per plan.",
  },
  {
    icon: Lock,
    title: "Secure by default",
    text: "JWT auth, bcrypt hashing, role-based access and a full audit trail for every action.",
  },
];

const STEPS = [
  {
    step: "01",
    title: "Create a workspace",
    text: "Sign up free and name your workspace — your isolated tenant is ready in seconds.",
  },
  {
    step: "02",
    title: "Invite your team",
    text: "Add members with roles from owner to agent. Permissions are enforced on every endpoint.",
  },
  {
    step: "03",
    title: "Add knowledge & agents",
    text: "Upload your docs, spin up the AI crew, and let flows handle tickets around the clock.",
  },
];

const PLANS = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "For teams trying out AI support.",
    features: ["500 AI requests / month", "10 knowledge documents", "5 team seats", "Community support"],
    highlight: false,
    cta: "Start free",
    href: "/register",
  },
  {
    name: "Pro",
    price: "$49",
    period: "/month",
    description: "For growing support teams.",
    features: ["5,000 AI requests / month", "100 knowledge documents", "50 team seats", "Priority processing", "Basic analytics"],
    highlight: true,
    cta: "Start free trial",
    href: "/register",
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For organizations at scale.",
    features: ["Unlimited usage", "Unlimited knowledge", "Unlimited users", "Advanced analytics", "Dedicated support"],
    highlight: false,
    cta: "Contact us",
    href: "/register",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[500px] bg-gradient-to-b from-indigo-500/10 to-transparent" />
        <div className="relative mx-auto max-w-6xl px-4 pb-10 pt-16 text-center sm:px-6 sm:pt-24">
          <Badge className="mb-5" variant="secondary">
            <Sparkles className="h-3.5 w-3.5" />
            CrewAI · FastAPI · Next.js · Free stack
          </Badge>
          <h1 className="mx-auto max-w-3xl text-4xl font-bold leading-tight tracking-tight sm:text-6xl">
            Your own{" "}
            <span className="bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent">
              AI support crew
            </span>{" "}
            for every tenant
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-muted-foreground">
            TenantDesk is a multi-tenant AI support platform. Each organization gets isolated
            knowledge, orchestrated agents and full control — deployable on a free stack.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/register">
              <Button size="lg" className="w-full sm:w-auto">
                Start free
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <DemoButton size="lg" />
          </div>
          <p className="mt-4 text-xs text-muted-foreground">
            No account or credit card required · jump straight into the live demo
          </p>
          <HeroMockup />
        </div>
      </section>

      <section id="features" className="border-t border-border bg-muted/30 py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Production-grade AI SaaS features
            </h2>
            <p className="mt-3 text-muted-foreground">
              Everything a modern AI support platform needs — built with free and open
              technologies.
            </p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((feature) => (
              <Card key={feature.title} className="transition-shadow hover:shadow-md">
                <CardContent className="p-6">
                  <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="mt-4 font-semibold">{feature.title}</h3>
                  <p className="mt-1.5 text-sm text-muted-foreground">{feature.text}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="how" className="py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">How it works</h2>
            <p className="mt-3 text-muted-foreground">
              From signup to a working AI support team in minutes.
            </p>
          </div>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {STEPS.map((step) => (
              <div key={step.step} className="relative">
                <p className="text-sm font-bold text-primary">{step.step}</p>
                <h3 className="mt-2 text-lg font-semibold">{step.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{step.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="pricing" className="border-t border-border bg-muted/30 py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Simple, free to start</h2>
            <p className="mt-3 text-muted-foreground">
              Usage limits scale with your plan. Metering and quota enforcement are live.
            </p>
          </div>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {PLANS.map((plan) => (
              <Card
                key={plan.name}
                className={`flex flex-col ${plan.highlight ? "border-primary shadow-lg" : ""}`}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{plan.name}</CardTitle>
                    {plan.highlight && <Badge>Most popular</Badge>}
                  </div>
                  <div className="mt-2 flex items-baseline gap-1">
                    <span className="text-3xl font-bold">{plan.price}</span>
                    <span className="text-sm text-muted-foreground">{plan.period}</span>
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <ul className="space-y-2.5">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2 text-sm">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                        <span className="text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link href={plan.href} className="w-full">
                    <Button className="w-full" variant={plan.highlight ? "default" : "outline"}>
                      {plan.cta}
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="mx-auto max-w-4xl px-4 sm:px-6">
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-700 p-10 text-center text-white sm:p-14">
            <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
            <div className="relative">
              <Building2 className="mx-auto h-10 w-10" />
              <h2 className="mt-4 text-3xl font-bold tracking-tight">
                Deploy your own AI support platform
              </h2>
              <p className="mx-auto mt-3 max-w-xl text-white/80">
                Full source, Docker Compose, free-tier deployment guides and a complete
                documentation suite.
              </p>
              <Link href="/register">
                <Button size="lg" className="mt-8 bg-white text-indigo-700 hover:bg-white/90">
                  <Zap className="h-4 w-4" />
                  Get started free
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-border py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
              <Building2 className="h-3.5 w-3.5" />
            </div>
            <span className="text-sm font-semibold">TenantDesk AI</span>
          </div>
          <div className="flex items-center gap-5 text-sm text-muted-foreground">
            <a href="#features" className="hover:text-foreground">
              Features
            </a>
            <a href="#pricing" className="hover:text-foreground">
              Pricing
            </a>
            <Link href="/login" className="hover:text-foreground">
              Login
            </Link>
            <Link href="/register" className="hover:text-foreground">
              Register
            </Link>
          </div>
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Users className="h-3.5 w-3.5" />
            © {new Date().getFullYear()} TenantDesk AI
          </p>
        </div>
      </footer>
    </div>
  );
}
