import { createFileRoute } from "@tanstack/react-router";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Filter, Pause, RefreshCw } from "lucide-react";
import { PageHeader, Panel, RiskBadge } from "@/components/dashboard/primitives";
import { generateEvents, traffic24h } from "@/lib/mock-data";

export const Route = createFileRoute("/_app/live")({
  head: () => ({
    meta: [
      { title: "Live Monitor · SecureCommerce AI" },
      { name: "description", content: "Streaming login events from the detection pipeline." },
    ],
  }),
  component: LivePage,
});

function LivePage() {
  const events = generateEvents(24);
  return (
    <div>
      <PageHeader
        eyebrow="Streams"
        title="Live Event Monitor"
        description="Tail the login_events Kafka topic in real time. Filter, pause, and inspect anomalies as they happen."
        actions={
          <div className="flex items-center gap-2">
            <button className="inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium hover:bg-secondary">
              <Filter className="h-3.5 w-3.5" /> Filters
            </button>
            <button className="inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium hover:bg-secondary">
              <Pause className="h-3.5 w-3.5" /> Pause
            </button>
            <button className="inline-flex items-center gap-1.5 rounded-md border border-primary/50 bg-primary/10 text-primary px-3 py-1.5 text-xs font-medium hover:bg-primary/20">
              <RefreshCw className="h-3.5 w-3.5" /> Streaming
            </button>
          </div>
        }
      />

      <Panel title="Events per minute" subtitle="Rolling 24h">
        <div className="h-44">
          <ResponsiveContainer>
            <BarChart data={traffic24h} margin={{ left: -16, right: 8 }}>
              <CartesianGrid stroke="oklch(1 0 0 / 0.06)" vertical={false} />
              <XAxis dataKey="hour" stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: "oklch(0.22 0.025 250)", border: "1px solid oklch(0.32 0.03 250)", borderRadius: 8, fontSize: 12 }}
              />
              <Bar dataKey="logins" fill="oklch(0.78 0.16 195)" radius={[3, 3, 0, 0]} />
              <Bar dataKey="blocked" fill="oklch(0.65 0.24 25)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel className="mt-4" title="Live event tail" subtitle="login_events · partition 0–3">
        <div className="overflow-x-auto -mx-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-b border-border">
                <th className="px-5 py-2 font-medium">Time</th>
                <th className="px-3 py-2 font-medium">Event</th>
                <th className="px-3 py-2 font-medium">User</th>
                <th className="px-3 py-2 font-medium">IP</th>
                <th className="px-3 py-2 font-medium">Location</th>
                <th className="px-3 py-2 font-medium">Device</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Score</th>
                <th className="px-3 py-2 font-medium">Risk</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.event_id} className="border-b border-border/50 last:border-0 hover:bg-secondary/40">
                  <td className="px-5 py-2 font-mono text-xs text-muted-foreground whitespace-nowrap">
                    {new Date(e.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-3 py-2 font-mono text-xs text-primary">{e.event_id.slice(0, 12)}</td>
                  <td className="px-3 py-2">{e.username}</td>
                  <td className="px-3 py-2 font-mono text-xs">{e.ip_address}</td>
                  <td className="px-3 py-2 text-xs">{e.city}, {e.country}</td>
                  <td className="px-3 py-2 text-xs">{e.device} · {e.browser}</td>
                  <td className="px-3 py-2">
                    <span className={`text-xs font-medium ${e.login_status === "SUCCESS" ? "text-success" : "text-destructive"}`}>
                      {e.login_status}
                    </span>
                  </td>
                  <td className="px-3 py-2 font-mono text-xs">{e.risk_score.toFixed(1)}</td>
                  <td className="px-3 py-2"><RiskBadge level={e.risk_level} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}