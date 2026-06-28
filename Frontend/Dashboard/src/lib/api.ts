export interface DashboardSummary {
  total_events: number;
  attacks: number;
  anomalies: number;
  high_risk: number;
}

const API = "http://localhost:8000/api";

export async function getSummary(): Promise<DashboardSummary> {
  const response = await fetch(`${API}/summary`);

  if (!response.ok) {
    throw new Error("Unable to fetch summary");
  }

  return response.json();
}

export async function getEvents() {
  const response = await fetch(`${API}/events`);

  if (!response.ok) {
    throw new Error("Unable to fetch events");
  }

  return response.json();
}
export async function getML() {
    const response = await fetch("http://localhost:8000/api/ml");

    if (!response.ok) {
        throw new Error("Unable to fetch ML metrics");
    }

    return response.json();
}

export async function getSystem() {
    const response = await fetch("http://localhost:8000/api/system");

    if (!response.ok) {
        throw new Error("Unable to fetch system status");
    }

    return response.json();
}