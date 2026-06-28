import type { ComponentType } from "react";

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AttackType = "NORMAL" | "BRUTE_FORCE" | "CREDENTIAL_STUFFING";
export type LoginStatus = "SUCCESS" | "FAILED";

export interface LoginEvent {
  event_id: string;
  timestamp: string;
  username: string;
  role: "Customer" | "Admin";
  ip_address: string;
  country: string;
  city: string;
  device: string;
  browser: string;
  login_status: LoginStatus;
  attack_type: AttackType;
  failed_attempts: number;
  risk_score: number;
  risk_level: RiskLevel;
}

const COUNTRIES: [string, string][] = [
  ["United States", "New York"],
  ["Germany", "Berlin"],
  ["Brazil", "São Paulo"],
  ["India", "Mumbai"],
  ["Japan", "Tokyo"],
  ["Russia", "Moscow"],
  ["Nigeria", "Lagos"],
  ["United Kingdom", "London"],
  ["China", "Shanghai"],
  ["Singapore", "Singapore"],
];

const DEVICES = ["Windows", "macOS", "Linux", "Android", "iOS"];
const BROWSERS = ["Chrome", "Firefox", "Edge", "Safari"];

function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

function randIp(rand: () => number) {
  return `${Math.floor(rand() * 223) + 1}.${Math.floor(rand() * 255)}.${Math.floor(rand() * 255)}.${Math.floor(rand() * 255)}`;
}

export function generateEvents(count = 60): LoginEvent[] {
  const rand = seeded(42);
  const now = Date.now();
  return Array.from({ length: count }).map((_, i) => {
    const r = rand();
    const attack: AttackType =
      r > 0.95 ? "CREDENTIAL_STUFFING" : r > 0.88 ? "BRUTE_FORCE" : "NORMAL";
    const status: LoginStatus = attack === "NORMAL" ? (rand() > 0.1 ? "SUCCESS" : "FAILED") : "FAILED";
    const score =
      attack === "CREDENTIAL_STUFFING"
        ? 78 + rand() * 22
        : attack === "BRUTE_FORCE"
        ? 55 + rand() * 35
        : rand() * 45;
    const level: RiskLevel =
      score >= 80 ? "CRITICAL" : score >= 60 ? "HIGH" : score >= 30 ? "MEDIUM" : "LOW";
    const [country, city] = COUNTRIES[Math.floor(rand() * COUNTRIES.length)];
    return {
      event_id: `evt_${(now - i * 7777).toString(36)}`,
      timestamp: new Date(now - i * 1000 * (10 + rand() * 50)).toISOString(),
      username: `user_${Math.floor(rand() * 9999).toString().padStart(4, "0")}`,
      role: rand() > 0.92 ? "Admin" : "Customer",
      ip_address: randIp(rand),
      country,
      city,
      device: DEVICES[Math.floor(rand() * DEVICES.length)],
      browser: BROWSERS[Math.floor(rand() * BROWSERS.length)],
      login_status: status,
      attack_type: attack,
      failed_attempts: attack === "NORMAL" ? Math.floor(rand() * 2) : Math.floor(rand() * 12) + 3,
      risk_score: Math.round(score * 10) / 10,
      risk_level: level,
    };
  });
}

export const traffic24h = Array.from({ length: 24 }).map((_, h) => {
  const rand = seeded(100 + h);
  const base = 200 + Math.sin((h / 24) * Math.PI * 2) * 120 + rand() * 60;
  const attacks = Math.max(0, Math.round(rand() * 40 + (h > 22 || h < 5 ? 30 : 5)));
  return {
    hour: `${h.toString().padStart(2, "0")}:00`,
    logins: Math.round(base),
    attacks,
    blocked: Math.round(attacks * 0.78),
  };
});

export const riskDistribution = [
  { level: "Low", value: 71, color: "var(--success)" },
  { level: "Medium", value: 18, color: "var(--warning)" },
  { level: "High", value: 8, color: "var(--accent)" },
  { level: "Critical", value: 3, color: "var(--destructive)" },
];

export const attackBreakdown = [
  { type: "Brute Force", count: 412 },
  { type: "Credential Stuffing", count: 287 },
  { type: "Geo Anomaly", count: 156 },
  { type: "Velocity", count: 98 },
  { type: "Device Switch", count: 73 },
];

export const modelMetrics = [
  { epoch: 1, accuracy: 0.82, precision: 0.78, recall: 0.71, f1: 0.74 },
  { epoch: 2, accuracy: 0.87, precision: 0.84, recall: 0.79, f1: 0.81 },
  { epoch: 3, accuracy: 0.91, precision: 0.89, recall: 0.85, f1: 0.87 },
  { epoch: 4, accuracy: 0.93, precision: 0.92, recall: 0.88, f1: 0.9 },
  { epoch: 5, accuracy: 0.945, precision: 0.94, recall: 0.91, f1: 0.925 },
  { epoch: 6, accuracy: 0.953, precision: 0.95, recall: 0.93, f1: 0.94 },
];

export const services: { name: string; status: "healthy" | "degraded" | "down"; latency: string; uptime: string }[] = [
  { name: "Kafka Broker", status: "healthy", latency: "4ms", uptime: "99.99%" },
  { name: "MongoDB Cluster", status: "healthy", latency: "11ms", uptime: "99.98%" },
  { name: "ML Inference", status: "healthy", latency: "38ms", uptime: "99.92%" },
  { name: "Event Consumer", status: "degraded", latency: "112ms", uptime: "99.71%" },
  { name: "Rules Engine", status: "healthy", latency: "6ms", uptime: "99.99%" },
  { name: "Geo Service", status: "healthy", latency: "22ms", uptime: "99.95%" },
];

export const topUsers = generateEvents(120)
  .filter((e) => e.attack_type !== "NORMAL")
  .slice(0, 8)
  .map((e) => ({
    username: e.username,
    country: e.country,
    attempts: 20 + Math.floor(Math.random() * 80),
    risk: e.risk_score,
    level: e.risk_level,
  }));

export type IconType = ComponentType<{ className?: string }>;