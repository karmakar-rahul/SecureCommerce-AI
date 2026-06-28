import { createFileRoute } from "@tanstack/react-router";
import { PageHeader, Panel, RiskBadge } from "@/components/dashboard/primitives";
import { generateEvents } from "@/lib/mock-data";
import type { RiskLevel } from "@/lib/mock-data";

export const Route = createFileRoute("/_app/users")({
  head: () => ({
    meta: [
      { title: "User Behaviour · SecureCommerce AI" },
      { name: "description", content: "Behavioural baselines and outliers per user." },
    ],
  }),
  component: UsersPage,
});

interface UserAgg {
  username: string;
  role: string;
  country: string;
  logins: number;
  failed: number;
  risk: number;
  level: RiskLevel;
}

function UsersPage() {
  const events = generateEvents(150);
  const map = new Map<string, UserAgg>();
  for (const e of events) {
    const cur = map.get(e.username) ?? {
      username: e.username,
      role: e.role,
      country: e.country,
      logins: 0,
      failed: 0,
      risk: 0,
      level: e.risk_level,
    };
    cur.logins += 1;
    if (e.login_status === "FAILED") cur.failed += 1;
    if (e.risk_score > cur.risk) {
      cur.risk = e.risk_score;
      cur.level = e.risk_level;
    }
    map.set(e.username, cur);
  }
  const byUser = Array.from(map.values()).sort((a, b) => b.risk - a.risk).slice(0, 14);

  return (
    <div>
      <PageHeader
        eyebrow="Behavioural"
        title="User Behaviour"
        description="Per-user baselines and outliers — failed attempts, location churn, device velocity and impossible travel."
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Panel title="Active users · 24h">
          <div className="font-display text-4xl font-semibold">38,204</div>
          <div className="text-xs text-muted-foreground mt-1">96.7% benign baseline</div>
        </Panel>
        <Panel title="Tracked anomalies">
          <div className="font-display text-4xl font-semibold text-warning">1,254</div>
          <div className="text-xs text-muted-foreground mt-1">Behavioural drift &gt; 2σ</div>
        </Panel>
        <Panel title="Quarantined sessions">
          <div className="font-display text-4xl font-semibold text-destructive">87</div>
          <div className="text-xs text-muted-foreground mt-1">Auto-blocked by rules engine</div>
        </Panel>
      </div>

      <Panel className="mt-4" title="High-risk users" subtitle="Highest max-score in the last 24h">
        <div className="overflow-x-auto -mx-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-b border-border">
                <th className="px-5 py-2 font-medium">User</th>
                <th className="px-3 py-2 font-medium">Role</th>
                <th className="px-3 py-2 font-medium">Primary location</th>
                <th className="px-3 py-2 font-medium">Logins</th>
                <th className="px-3 py-2 font-medium">Failed</th>
                <th className="px-3 py-2 font-medium">Max risk</th>
                <th className="px-3 py-2 font-medium">Level</th>
              </tr>
            </thead>
            <tbody>
              {byUser.map((u) => (
                <tr key={u.username} className="border-b border-border/50 last:border-0 hover:bg-secondary/40">
                  <td className="px-5 py-2.5">
                    <div className="flex items-center gap-2.5">
                      <div className="h-7 w-7 rounded-full bg-gradient-to-br from-primary/40 to-accent/40 grid place-items-center text-[10px] font-semibold">
                        {u.username.slice(-2).toUpperCase()}
                      </div>
                      <span className="font-medium">{u.username}</span>
                    </div>
                  </td>
                  <td className="px-3 py-2.5 text-xs">{u.role}</td>
                  <td className="px-3 py-2.5 text-xs">{u.country}</td>
                  <td className="px-3 py-2.5 font-mono">{u.logins}</td>
                  <td className="px-3 py-2.5 font-mono text-destructive">{u.failed}</td>
                  <td className="px-3 py-2.5 font-mono">{u.risk.toFixed(1)}</td>
                  <td className="px-3 py-2.5"><RiskBadge level={u.level} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}