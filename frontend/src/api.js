const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body.detail) detail = body.detail;
    } catch {
      // response had no JSON body; keep the status-based message
    }
    throw new Error(detail);
  }

  return response.json();
}

export const createOperation = (payload) =>
  request("/api/v1/operations", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const assessOperation = (operationId) =>
  request(`/api/v1/operations/${operationId}/assess`, { method: "POST" });

export const listRiskEvents = () => request("/api/v1/risk-events");

export const listAlerts = () => request("/api/v1/alerts");

export const getRiskHistory = (operationId) =>
  request(`/api/v1/operations/${operationId}/risk-history`);
