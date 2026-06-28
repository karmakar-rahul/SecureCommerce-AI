import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  Brain,
  LayoutDashboard,
  Radar,
  ServerCog,
  ShieldAlert,
  Users,
  Bell,
  Search,
  ShieldCheck,
} from "lucide-react";
import type { ComponentType } from "react";

const nav: { to: string; label: string; icon: ComponentType<{ className?: string }> }[] = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/live", label: "Live Monitor", icon: Activity },
  { to: "/threats", label: "Threat Analysis", icon: ShieldAlert },
  { to: "/ml", label: "ML Analytics", icon: Brain },
  { to: "/users", label: "User Behaviour", icon: Users },
  { to: "/system", label: "System Status", icon: ServerCog },
];

export function DashboardLayout() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 shrink-0 border-r border-sidebar-border bg-sidebar hidden lg:flex flex-col">
        <div className="px-6 py-6 flex items-center gap-2.5 border-b border-sidebar-border">
          <div className="relative h-9 w-9 rounded-lg bg-gradient-to-br from-primary to-accent grid place-items-center shadow-[0_0_24px_-6px_oklch(0.78_0.16_195/0.7)]">
            <ShieldCheck className="h-5 w-5 text-primary-foreground" />
          </div>
          <div className="leading-tight">
            <div className="font-display font-semibold text-sidebar-foreground">SecureCommerce</div>
            <div className="text-[10px] uppercase tracking-[0.18em] text-primary">AI · Threat Ops</div>
          </div>
        </div>

        <nav className="flex-1 px-3 py-5 space-y-1">
          <div className="px-3 pb-2 text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
            Operations
          </div>
          {nav.map(({ to, label, icon: Icon }) => {
            const active = to === "/" ? pathname === "/" : pathname.startsWith(to);
            return (
              <Link
                key={to}
                to={to}
                className={`group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground border border-sidebar-border"
                    : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
                }`}
              >
                <Icon className={`h-4 w-4 ${active ? "text-primary" : "text-sidebar-foreground/60 group-hover:text-primary"}`} />
                <span>{label}</span>
                {active && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_8px_oklch(0.78_0.16_195)]" />}
              </Link>
            );
          })}
        </nav>

        <div className="m-3 panel p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Radar className="h-3.5 w-3.5 text-primary" />
            <span>Detection engine</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="pulse-dot absolute inset-0 text-success" />
              <span className="relative h-2 w-2 rounded-full bg-success" />
            </span>
            <span className="text-sm font-medium">Online · v1.0.0</span>
          </div>
          <div className="mt-3 text-[11px] text-muted-foreground font-mono">
            Ingest 4.2k ev/s · 6 nodes
          </div>
        </div>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col">
        <header className="h-16 border-b border-border bg-card/40 backdrop-blur sticky top-0 z-30 flex items-center px-6 gap-4">
          <div className="lg:hidden flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <span className="font-display font-semibold">SecureCommerce</span>
          </div>
          <div className="flex-1 max-w-md hidden md:flex items-center gap-2 rounded-md border border-input bg-input/40 px-3 py-1.5">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              placeholder="Search users, events, IPs…"
              className="bg-transparent outline-none text-sm flex-1 placeholder:text-muted-foreground"
            />
            <kbd className="text-[10px] font-mono text-muted-foreground border border-border rounded px-1.5 py-0.5">⌘K</kbd>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <button className="relative rounded-md border border-border p-2 hover:bg-secondary">
              <Bell className="h-4 w-4" />
              <span className="absolute top-1 right-1 h-1.5 w-1.5 rounded-full bg-destructive" />
            </button>
            <div className="hidden sm:flex items-center gap-2 pl-3 border-l border-border">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-accent grid place-items-center text-xs font-semibold text-primary-foreground">
                RK
              </div>
              <div className="text-xs leading-tight">
                <div className="font-medium">Rahul Karmakar</div>
                <div className="text-muted-foreground">Big Data Analyst</div>
                <div className="text-sm text-muted-foreground">@karmakar-rahul</div>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}