// Thin client for the DecisionFlow AI backend.
const BASE = process.env.NEXT_PUBLIC_API_BASE || "/api";

async function req(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

export type Recommendation = {
  id: string;
  action: string;
  priority: string;
  confidence: number;
  business_impact: string;
  reason: string;
  expected_outcome: string;
  status: string;
  evidence?: Record<string, any>;
};

export const api = {
  analyze: (payload?: any) =>
    req("/analyze", { method: "POST", body: JSON.stringify(payload || {}) }),
  recommendations: (customerId?: string) =>
    req(`/recommendations${customerId ? `?customer_id=${customerId}` : ""}`),
  approve: (recommendation_id: string, modified_action?: string) =>
    req("/approve", { method: "POST", body: JSON.stringify({ recommendation_id, modified_action }) }),
  reject: (recommendation_id: string) =>
    req("/reject", { method: "POST", body: JSON.stringify({ recommendation_id }) }),
  modify: (recommendation_id: string, modified_action: string) =>
    req("/modify", { method: "POST", body: JSON.stringify({ recommendation_id, modified_action }) }),
  memory: (customerId?: string) =>
    req(`/memory${customerId ? `?customer_id=${customerId}` : ""}`),
};

export const SAMPLE_PAYLOAD = {
  transcript:
    "CSM: How has the platform been? Customer: We like it a lot, adoption is strong. " +
    "But finance is evaluating pricing before renewal, and our security team now requires SSO. " +
    "Renewal is next month so we want to move quickly. The VP of Engineering signs off.",
  crm: { name: "ABC Technologies", health: 78, renewal_days: 20, arr: 42000 },
  email: "Finance is reviewing pricing before renewal. Please send an ROI summary and SSO timelines.",
  support_ticket: "Ticket #4821 High: SSO (SAML) implementation support for Okta. Required before renewal.",
  notes: "Champion: Mark (IT Director). Economic buyer: VP Engineering (unconfirmed). Expansion: Enterprise tier.",
};
