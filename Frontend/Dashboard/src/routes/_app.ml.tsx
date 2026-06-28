import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { Brain, Gauge, Layers, TrendingUp } from "lucide-react";
import { PageHeader, Panel, Stat } from "@/components/dashboard/primitives";
import { modelMetrics } from "@/lib/mock-data";
import { getML } from "@/lib/api";

export const Route = createFileRoute("/_app/ml")({
  head: () => ({
    meta: [
      { title: "ML Analytics · SecureCommerce AI" },
      { name: "description", content: "Model performance, drift and feature importance." },
    ],
  }),
  component: MLPage,
});

const features = [
  { name: "failed_attempts", importance: 0.92 },
  { name: "travel_speed_kmh", importance: 0.81 },
  { name: "unique_ip_count", importance: 0.74 },
  { name: "login_attempt_rate", importance: 0.66 },
  { name: "country_switch_rate", importance: 0.58 },
  { name: "device_switch_rate", importance: 0.49 },
  { name: "is_business_hours", importance: 0.32 },
  { name: "response_time_ms", importance: 0.21 },
];

function MLPage() {
  const [ml, setML] = useState({
      accuracy: 97.12,
      precision: 52.60,
      recall: 52.55,
      f1: 52.58,

      tn: 68799,
      fp: 1038,
      fn: 1040,
      tp: 1152,

      samples: 72029,
      model: "Isolation Forest",
      last_updated: ""
    });

useEffect(() => {

    const load = async () => {
        try {
            setML(await getML());
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
        eyebrow="Intelligence"
        title="ML Analytics"
        description="Performance metrics of the Isolation Forest model used for anomaly detection in SecureCommerce-AI."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <Stat
          label="Accuracy"
          value={`${ml.accuracy.toFixed(2)}%`}
          icon={Gauge}
          accent="success"
        />

        <Stat
          label="Precision"
          value={`${ml.precision.toFixed(2)}%`}
          icon={TrendingUp}
          accent="primary"
        />

        <Stat
          label="Recall"
          value={`${ml.recall.toFixed(2)}%`}
          icon={Layers}
          accent="accent"
        />

        <Stat
          label="F1 Score"
          value={`${ml.f1.toFixed(2)}%`}
          icon={Brain}
          accent="primary"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 mt-4">
        <Panel className="xl:col-span-2" title="Training metrics over epochs" subtitle={ml.model}>
          <div className="h-80">
            <ResponsiveContainer>
              <LineChart data={modelMetrics} margin={{ left: -16, right: 8, top: 8 }}>
                <CartesianGrid stroke="oklch(1 0 0 / 0.06)" vertical={false} />
                <XAxis dataKey="epoch" stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="oklch(0.72 0.03 245)" fontSize={11} domain={[0.6, 1]} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: "oklch(0.22 0.025 250)", border: "1px solid oklch(0.32 0.03 250)", borderRadius: 8, fontSize: 12 }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="accuracy" stroke="oklch(0.78 0.16 195)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="precision" stroke="oklch(0.6 0.22 295)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="recall" stroke="oklch(0.72 0.18 150)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="f1" stroke="oklch(0.8 0.17 75)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Feature importance" subtitle="Engineered features used during training">
          <ul className="space-y-3">
            {features.map((f) => (
              <li key={f.name}>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono">{f.name}</span>
                  <span className="text-muted-foreground">{f.importance.toFixed(2)}</span>
                </div>
                <div className="mt-1.5 h-1.5 rounded-full bg-secondary overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary to-accent" style={{ width: `${f.importance * 100}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mt-4">
        <Panel title="Confusion matrix" subtitle={`Validation Dataset · ${ml.samples.toLocaleString()} Events`}>
          <div className="grid grid-cols-3 gap-2 text-center text-sm">
            <div />
            <div className="text-xs text-muted-foreground py-1">Pred · Benign</div>
            <div className="text-xs text-muted-foreground py-1">Pred · Attack</div>
            <div className="text-xs text-muted-foreground py-2 text-right pr-2">Benign</div>
            <div className="panel p-4 bg-success/10 border-success/30">
              <div className="text-2xl font-display font-semibold text-success">{ml.tn.toLocaleString()}</div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">True neg.</div>
            </div>
            <div className="panel p-4 bg-warning/10 border-warning/30">
              <div className="text-2xl font-display font-semibold text-warning">{ml.fp.toLocaleString()}</div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">False pos.</div>
            </div>
            <div className="text-xs text-muted-foreground py-2 text-right pr-2">Attack</div>
            <div className="panel p-4 bg-destructive/10 border-destructive/30">
              <div className="text-2xl font-display font-semibold text-destructive">{ml.fn.toLocaleString()}</div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">False neg.</div>
            </div>
            <div className="panel p-4 bg-primary/10 border-primary/40">
              <div className="text-2xl font-display font-semibold text-primary">{ml.tp.toLocaleString()}</div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">True pos.</div>
            </div>
          </div>
        </Panel>

        <Panel title="Model registry" subtitle="Versions in rotation">
          <ul className="space-y-2 text-sm">
            {[
              { ver: "v1.0",status: "Production",traffic: "100%",acc: `${ml.accuracy.toFixed(2)}%`,tone: "primary" },
              { ver: "v3.1", status: "Shadow", traffic: "0%", acc: "94.1%", tone: "muted" },
              { ver: "v3.0", status: "Archived", traffic: "—", acc: "92.7%", tone: "muted" },
              { ver: "v3.3-rc", status: "Canary", traffic: "5%", acc: "95.8%", tone: "accent" },
            ].map((m) => (
              <li key={m.ver} className="flex items-center gap-3 rounded-md border border-border bg-card/60 px-3 py-2">
                <div className="font-mono text-sm">{m.ver}</div>
                <div className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                  m.tone === "primary" ? "border-primary/40 text-primary bg-primary/10" :
                  m.tone === "accent" ? "border-accent/40 text-accent bg-accent/10" :
                  "border-border text-muted-foreground"
                }`}>{m.status}</div>
                <div className="ml-auto flex items-center gap-4 text-xs">
                  <span className="text-muted-foreground">Traffic <span className="text-foreground font-mono">{m.traffic}</span></span>
                  <span className="text-muted-foreground">Acc <span className="text-foreground font-mono">{m.acc}</span></span>
                </div>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}