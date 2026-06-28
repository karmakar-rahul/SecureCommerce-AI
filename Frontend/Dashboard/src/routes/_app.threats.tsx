import { createFileRoute } from "@tanstack/react-router";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Globe2, ShieldAlert, Flame, Crosshair } from "lucide-react";
import { PageHeader, Panel, RiskBadge, Stat } from "@/components/dashboard/primitives";
import { attackBreakdown, generateEvents } from "@/lib/mock-data";

export const Route = createFileRoute("/_app/threats")({
  head: () => ({
    meta: [
      { title: "Threat Analysis · SecureCommerce AI" },
      { name: "description", content: "Investigate attacks, hotspots and high-risk incidents." },
    ],
  }),
  component: ThreatsPage,
});

const COLORS = ["oklch(0.65 0.24 25)", "oklch(0.6 0.22 295)", "oklch(0.8 0.17 75)", "oklch(0.78 0.16 195)", "oklch(0.72 0.18 150)"];

function ThreatsPage() {
  const incidents = generateEvents(60).filter((e) => e.attack_type !== "NORMAL").slice(0, 10);
  const byCountry = Object.entries(
    generateEvents(200).filter((e) => e.attack_type !== "NORMAL").reduce<Record<string, number>>((acc, e) => {
      acc[e.country] = (acc[e.country] ?? 0) + 1;
      return acc;
    }, {})
  )
    .map(([country, count]) => ({ country, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 7);

  return (
    <div>
      <PageHeader
        eyebrow="Detection"
        title="Threat Analysis"
        description="Drill into attack patterns, geographic hotspots and the highest-risk incidents from the last 24 hours."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <Stat label="Brute force" value="412" delta="+22%" trend="down" icon={Flame} accent="destructive" />
        <Stat label="Credential stuffing" value="287" delta="+11%" trend="down" icon={Crosshair} accent="accent" />
        <Stat label="Geo anomalies" value="156" delta="-4%" trend="up" icon={Globe2} accent="warning" />
        <Stat label="High-risk users" value="84" delta="+6" trend="down" icon={ShieldAlert} accent="primary" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mt-4">
        <Panel title="Attacks by category" subtitle="Last 24h">
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={attackBreakdown} layout="vertical" margin={{ left: 24, right: 16 }}>
                <CartesianGrid stroke="oklch(1 0 0 / 0.06)" horizontal={false} />
                <XAxis type="number" stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="type" stroke="oklch(0.85 0.02 240)" fontSize={12} tickLine={false} axisLine={false} width={130} />
                <Tooltip contentStyle={{ background: "oklch(0.22 0.025 250)", border: "1px solid oklch(0.32 0.03 250)", borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {attackBreakdown.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Top source countries" subtitle="Where the attacks originate">
          <ul className="divide-y divide-border/60">
            {byCountry.map((c, i) => {
              const max = byCountry[0].count;
              const pct = (c.count / max) * 100;
              return (
                <li key={c.country} className="py-2.5 flex items-center gap-4">
                  <span className="text-xs font-mono text-muted-foreground w-5">{(i + 1).toString().padStart(2, "0")}</span>
                  <span className="text-sm font-medium w-44">{c.country}</span>
                  <div className="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-destructive to-accent" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-sm font-mono w-12 text-right">{c.count}</span>
                </li>
              );
            })}
          </ul>
        </Panel>
      </div>

      <Panel className="mt-4" title="Top incidents" subtitle="Critical & high-risk events awaiting triage">
        <div className="overflow-x-auto -mx-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-b border-border">
                <th className="px-5 py-2 font-medium">Event</th>
                <th className="px-3 py-2 font-medium">User</th>
                <th className="px-3 py-2 font-medium">Attack</th>
                <th className="px-3 py-2 font-medium">Failed</th>
                <th className="px-3 py-2 font-medium">Source</th>
                <th className="px-3 py-2 font-medium">Score</th>
                <th className="px-3 py-2 font-medium">Risk</th>
                <th className="px-3 py-2 font-medium" />
              </tr>
            </thead>
            <tbody>
              {incidents.map((e) => (
                <tr key={e.event_id} className="border-b border-border/50 last:border-0 hover:bg-secondary/40">
                  <td className="px-5 py-2 font-mono text-xs text-primary">{e.event_id.slice(0, 14)}</td>
                  <td className="px-3 py-2">{e.username}</td>
                  <td className="px-3 py-2 text-xs font-mono">{e.attack_type}</td>
                  <td className="px-3 py-2 font-mono">{e.failed_attempts}</td>
                  <td className="px-3 py-2 text-xs">{e.city}, {e.country} · <span className="text-muted-foreground font-mono">{e.ip_address}</span></td>
                  <td className="px-3 py-2 font-mono">{e.risk_score.toFixed(1)}</td>
                  <td className="px-3 py-2"><RiskBadge level={e.risk_level} /></td>
                  <td className="px-3 py-2 text-right">
                    <button className="text-xs font-medium text-primary hover:underline">Investigate →</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}