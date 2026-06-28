import { createFileRoute } from "@tanstack/react-router";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useEffect, useState } from "react";
import { Cpu, Database, HardDrive, Network } from "lucide-react";
import { PageHeader, Panel, Stat, StatusDot } from "@/components/dashboard/primitives";
import { getSystem } from "@/lib/api";

export const Route = createFileRoute("/_app/system")({
  head: () => ({
    meta: [
      { title: "System Status · SecureCommerce AI" },
      { name: "description", content: "Infrastructure health, throughput and SLOs." },
    ],
  }),
  component: SystemPage,
});

const latency = Array.from({ length: 30 }).map((_, i) => ({
  t: i,
  p50: Math.round(18 + Math.sin(i / 3) * 4 + (i % 5)),
  p95: Math.round(42 + Math.sin(i / 2.5) * 8 + (i % 7)),
  p99: Math.round(78 + Math.sin(i / 2) * 12 + (i % 9)),
}));

function SystemPage() {
  const [system, setSystem] = useState({
    kafka: "Unknown",
    mongodb: "Unknown",
    producer: "Unknown",
    consumer: "Unknown",

    dataset_size: 0,
    attacks: 0,
    anomalies: 0,

    model: "Isolation Forest",
    version: "v1.0",
    last_updated: ""
  });
  const serviceList: {
    name: string;
    status: "healthy" | "degraded" | "down";
    text: string;
  }[] = [
      {
        name: "Kafka Broker",
        status: system.kafka === "Running" ? "healthy" : "down",
        text: system.kafka,
      },
      {
        name: "MongoDB",
        status: system.mongodb === "Running" ? "healthy" : "down",
        text: system.mongodb,
      },
      {
        name: "Producer",
        status: system.producer === "Available" ? "healthy" : "degraded",
        text: system.producer,
      },
      {
        name: "Consumer",
        status: system.consumer === "Available" ? "healthy" : "degraded",
        text: system.consumer,
      },
      {
        name: "Isolation Forest",
        status: "healthy",
        text: system.model,
      },
  ];
  useEffect(() => {
    const load = async () => {
        try {
            setSystem(await getSystem());
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
        eyebrow="Infrastructure"
        title="System Status"
        description="Live health of the detection pipeline — Kafka, MongoDB, the ML inference service and downstream workers."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <Stat
          label="Dataset Size"
          value={system.dataset_size.toLocaleString()}
          icon={Database}
          accent="primary"
        />

        <Stat
          label="Detected Attacks"
          value={system.attacks.toLocaleString()}
          icon={Cpu}
          accent="warning"
        />  

        <Stat
          label="ML Anomalies"
          value={system.anomalies.toLocaleString()}
          icon={HardDrive}
          accent="accent"
        />

        <Stat
          label="Model"
          value={system.model}
          icon={Network}
          accent="success"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 mt-4">
        <Panel className="xl:col-span-2" title="Inference latency" subtitle="ml-engine · 30-minute window">
          <div className="h-72">
            <ResponsiveContainer>
              <AreaChart data={latency} margin={{ left: -16, right: 8 }}>
                <defs>
                  <linearGradient id="p99" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="oklch(0.65 0.24 25)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="oklch(0.65 0.24 25)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="p95" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="oklch(0.8 0.17 75)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="oklch(0.8 0.17 75)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="p50" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="oklch(0.78 0.16 195)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="oklch(0.78 0.16 195)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="oklch(1 0 0 / 0.06)" vertical={false} />
                <XAxis dataKey="t" stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="oklch(0.72 0.03 245)" fontSize={11} tickLine={false} axisLine={false} unit="ms" />
                <Tooltip contentStyle={{ background: "oklch(0.22 0.025 250)", border: "1px solid oklch(0.32 0.03 250)", borderRadius: 8, fontSize: 12 }} />
                <Area type="monotone" dataKey="p99" stroke="oklch(0.65 0.24 25)" fill="url(#p99)" strokeWidth={2} />
                <Area type="monotone" dataKey="p95" stroke="oklch(0.8 0.17 75)" fill="url(#p95)" strokeWidth={2} />
                <Area type="monotone" dataKey="p50" stroke="oklch(0.78 0.16 195)" fill="url(#p50)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Services" subtitle="Pipeline components">
          <ul className="space-y-2">
              {serviceList.map((s) => (
                  <li
                      key={s.name}
                      className="rounded-md border border-border bg-card/60 px-3 py-2.5 flex items-center gap-3"
                  >
                      <StatusDot status={s.status} />

                      <div className="flex-1">
                          <div className="text-sm font-medium">
                              {s.name}
                          </div>

                          <div className="text-[11px] text-muted-foreground">
                              {s.text}
                          </div>
                      </div>
                  </li>
            ))}
          </ul>
        </Panel>
      </div>

      <Panel className="mt-4" title="Recent system events">
        <ul className="space-y-2 text-sm">
          {[
            {
        lvl: "INFO",
        tone: "primary",
        msg: `Kafka Broker : ${system.kafka}`
    },
    {
        lvl: "INFO",
        tone: "primary",
        msg: `MongoDB : ${system.mongodb}`
    },
    {
        lvl: "INFO",
        tone: "accent",
        msg: `Producer : ${system.producer}`
    },
    {
        lvl: "INFO",
        tone: "accent",
        msg: `Consumer : ${system.consumer}`
    },
    {
        lvl: "INFO",
        tone: "primary",
        msg: `Last Updated : ${system.last_updated}`
    }
          ].map((e, i) => (
            <li key={i} className="flex items-start gap-3 rounded-md border border-border bg-card/40 px-3 py-2">
              <span className="font-mono text-xs text-muted-foreground w-20">LIVE</span>
              <span className={`text-[10px] uppercase tracking-wider font-semibold w-14 ${
                e.tone === "warning" ? "text-warning" :
                e.tone === "destructive" ? "text-destructive" :
                e.tone === "accent" ? "text-accent" : "text-primary"
              }`}>{e.lvl}</span>
              <span className="text-sm">{e.msg}</span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}