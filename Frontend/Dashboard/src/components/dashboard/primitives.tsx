import type { ReactNode } from "react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
      <div>
        {eyebrow && (
          <div className="text-[11px] uppercase tracking-[0.22em] text-primary font-medium mb-1.5">
            {eyebrow}
          </div>
        )}
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">{title}</h1>
        {description && (
          <p className="text-sm text-muted-foreground mt-1.5 max-w-2xl">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Panel({
  title,
  subtitle,
  actions,
  children,
  className = "",
}: {
  title?: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel p-5 ${className}`}>
      {(title || actions) && (
        <header className="flex items-start justify-between mb-4">
          <div>
            {title && <h3 className="text-sm font-semibold tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}

export function Stat({
  label,
  value,
  delta,
  trend,
  icon: Icon,
  accent = "primary",
}: {
  label: string;
  value: string | number;
  delta?: string;
  trend?: "up" | "down";
  icon?: React.ComponentType<{ className?: string }>;
  accent?: "primary" | "destructive" | "success" | "warning" | "accent";
}) {
  const accentClass: Record<string, string> = {
    primary: "from-primary/30 to-primary/5 text-primary",
    destructive: "from-destructive/30 to-destructive/5 text-destructive",
    success: "from-success/30 to-success/5 text-success",
    warning: "from-warning/30 to-warning/5 text-warning",
    accent: "from-accent/30 to-accent/5 text-accent",
  };
  const trendGood = trend === "up";
  return (
    <div className="panel p-5 relative overflow-hidden">
      <div className={`absolute -top-12 -right-12 h-32 w-32 rounded-full bg-gradient-to-br ${accentClass[accent]} blur-2xl opacity-60 pointer-events-none`} />
      <div className="flex items-center justify-between relative">
        <span className="text-xs uppercase tracking-wider text-muted-foreground">{label}</span>
        {Icon && (
          <div className={`h-8 w-8 grid place-items-center rounded-md border border-border bg-card ${accentClass[accent].split(" ").slice(-1)[0]}`}>
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>
      <div className="mt-3 font-display text-3xl font-semibold tracking-tight relative">
        {value}
      </div>
      {delta && (
        <div className={`mt-2 inline-flex items-center gap-1 text-xs font-medium ${trendGood ? "text-success" : "text-destructive"}`}>
          {trendGood ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
          {delta}
          <span className="text-muted-foreground font-normal">vs 24h</span>
        </div>
      )}
    </div>
  );
}

export function RiskBadge({ level }: { level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" }) {
  const map = {
    LOW: "bg-success/15 text-success border-success/30",
    MEDIUM: "bg-warning/15 text-warning border-warning/30",
    HIGH: "bg-accent/15 text-accent border-accent/40",
    CRITICAL: "bg-destructive/15 text-destructive border-destructive/40",
  } as const;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase ${map[level]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {level}
    </span>
  );
}

export function StatusDot({ status }: { status: "healthy" | "degraded" | "down" }) {
  const map = {
    healthy: "text-success",
    degraded: "text-warning",
    down: "text-destructive",
  } as const;
  return (
    <span className={`relative inline-flex h-2 w-2 ${map[status]}`}>
      <span className="pulse-dot absolute inset-0" />
      <span className="relative h-2 w-2 rounded-full bg-current" />
    </span>
  );
}