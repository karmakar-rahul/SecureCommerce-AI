import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { getSummary, getEvents } from "@/lib/api";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, AlertTriangle, ShieldCheck, UserX, Zap } from "lucide-react";
import { PageHeader, Panel, RiskBadge, Stat } from "@/components/dashboard/primitives";
import { generateEvents, riskDistribution, traffic24h } from "@/lib/mock-data";

export const Route = createFileRoute("/_app/")({
  head: () => ({
    meta: [
      { title: "Overview · SecureCommerce AI" },
      { name: "description", content: "Real-time threat operations overview." },
    ],
  }),
  component: OverviewPage,
});

function OverviewPage() {
  const [recent, setRecent] = useState<any[]>([]);

  const [summary, setSummary] = useState({
      total_events: 0,
      attacks: 0,
      anomalies: 0,
      high_risk: 0,
  });

  useEffect(() => {
    const load = async () => {
      try {
        const [summaryData, eventData] = await Promise.all([
          getSummary(),
          getEvents(),
        ]);

        setSummary(summaryData);
        setRecent(eventData);
      } catch (err) {
        console.error(err);
      }
    };

    load();
    const timer = setInterval(load, 2000);
    return () => clearInterval(timer);
  }, []);
  return (
    <div>
      <PageHeader
        eyebrow="Operations · Live"
        title="Threat Operations Overview"
        description="Real-time view of login traffic, anomalies and active incidents across all SecureCommerce properties."
        actions={
          <button className="rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium hover:bg-secondary">
            Last 24 hours ▾
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <Stat label="Logins / 24h" value={summary.total_events.toLocaleString()} delta="+12.4%" trend="up" icon={Activity} accent="primary" />
        <Stat label="Anomalies detected" value={summary.anomalies.toLocaleString()} delta="+38.1%" trend="down" icon={AlertTriangle} accent="warning" />
        <Stat label="Attacks blocked" value={summary.attacks.toLocaleString()} delta="+19.7%" trend="up" icon={ShieldCheck} accent="success" />
        <Stat label="Critical incidents" value={summary.high_risk.toLocaleString()} delta="+4" trend="down" icon={UserX} accent="destructive" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 mt-4">
        <Panel className="xl:col-span-2" title="Login traffic vs attacks" subtitle="Hourly volume — last 24h">
          <div className="h-72">
            <ResponsiveContainer>
              <AreaChart data={traffic24h} margin={{ left: -16, right: 8, top: 8 }}>
                <defs>
                  <linearGradient id="gLogins" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="oklch(0.78 0.16 195)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="oklch(0.78 0.16 195)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gAttacks" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="oklch(0.65 0.24 25)" stopOpacity={0.6} />
                    <stop offset="100%" stopColor="oklch(0.65 0.24 25)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="oklch(1 0 0 / 0.06)" vertical={false} />
                <XAxis dataKey="hour" stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "oklch(0.22 0.025 250)",
                    border: "1px solid oklch(0.32 0.03 250)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Area type="monotone" dataKey="logins" stroke="oklch(0.78 0.16 195)" strokeWidth={2} fill="url(#gLogins)" />
                <Area type="monotone" dataKey="attacks" stroke="oklch(0.65 0.24 25)" strokeWidth={2} fill="url(#gAttacks)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Risk distribution" subtitle="Current session population">
          <div className="h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={riskDistribution} dataKey="value" nameKey="level" innerRadius={55} outerRadius={90} paddingAngle={3} stroke="oklch(0.22 0.025 250)">
                  {riskDistribution.map((d) => (
                    <Cell key={d.level} fill={d.color} />
                  ))}
                </Pie>
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    background: "oklch(0.22 0.025 250)",
                    border: "1px solid oklch(0.32 0.03 250)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 mt-4">
        <Panel className="xl:col-span-2" title="Latest events" subtitle="Streaming from Kafka · login_events">
          <div className="overflow-x-auto -mx-5">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-b border-border">
                  <th className="px-5 py-2 font-medium">Time</th>
                  <th className="px-3 py-2 font-medium">User</th>
                  <th className="px-3 py-2 font-medium">Location</th>
                  <th className="px-3 py-2 font-medium">Type</th>
                  <th className="px-3 py-2 font-medium">Risk</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((e: any) => (
                  <tr
                    key={e.event_id}
                    className="border-b border-border/60 last:border-0 hover:bg-secondary/40"
                  >
                    <td className="px-5 py-2.5 font-mono text-xs text-muted-foreground">
                      {new Date(e.timestamp).toLocaleTimeString()}
                    </td>

                    <td className="px-3 py-2.5">
                      <div className="font-medium">{e.username}</div>
                      <div className="text-xs text-muted-foreground">
                        {e.role}
                      </div>
                    </td>

                    <td className="px-3 py-2.5 text-xs">
                      <div>
                        {e.city}, {e.country}
                      </div>

                      <div className="font-mono text-muted-foreground">
                        {e.ip_address}
                      </div>
                    </td>

                    <td className="px-3 py-2.5 text-xs font-mono">
                      {e.attack_type}
                    </td>

                    <td className="px-3 py-2.5">
                      <RiskBadge
                        level={e.alert?.risk_level ?? "LOW"}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Pipeline health" subtitle="Live throughput">
          <ul className="space-y-3 text-sm">
            {[
              { label: "Producer", value: "4.2k ev/s", pct: 86, color: "bg-primary" },
              { label: "Kafka topic lag", value: "12 ms", pct: 18, color: "bg-success" },
              { label: "Consumer", value: "4.1k ev/s", pct: 84, color: "bg-primary" },
              { label: "ML inference p95", value: "38 ms", pct: 42, color: "bg-accent" },
              { label: "Mongo writes", value: "3.9k ev/s", pct: 78, color: "bg-primary" },
            ].map((m) => (
              <li key={m.label}>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">{m.label}</span>
                  <span className="font-mono">{m.value}</span>
                </div>
                <div className="mt-1.5 h-1.5 rounded-full bg-secondary overflow-hidden">
                  <div className={`h-full ${m.color}`} style={{ width: `${m.pct}%` }} />
                </div>
              </li>
            ))}
          </ul>
          <div className="mt-5 rounded-md border border-border bg-card/60 p-3 flex items-center gap-3">
            <Zap className="h-4 w-4 text-primary" />
            <div className="text-xs">
              <div className="font-medium">Auto-scaling armed</div>
              <div className="text-muted-foreground">3 replicas ready · region us-east-1</div>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}