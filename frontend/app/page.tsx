"use client";
import { useState } from "react";
import { api, SAMPLE_PAYLOAD, Recommendation } from "@/lib/api";
import { CustomerOverview } from "@/components/CustomerOverview";
import { AgentTimeline } from "@/components/AgentTimeline";
import { RecommendationCard } from "@/components/RecommendationCard";
import { EvidencePanel } from "@/components/EvidencePanel";
import { Card, CardHeader, CardBody, Button } from "@/components/ui";
import { Upload, Sparkles } from "lucide-react";

export default function Dashboard() {
  const [form, setForm] = useState({
    transcript: SAMPLE_PAYLOAD.transcript,
    crm: JSON.stringify(SAMPLE_PAYLOAD.crm, null, 2),
    email: SAMPLE_PAYLOAD.email,
    support_ticket: SAMPLE_PAYLOAD.support_ticket,
    notes: SAMPLE_PAYLOAD.notes,
  });
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [error, setError] = useState("");

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  async function analyze() {
    setRunning(true); setError(""); setResult(null); setRecs([]); setSelected(null);
    try {
      const payload: any = { ...form };
      try { payload.crm = JSON.parse(form.crm); } catch { /* send as string */ }
      const data = await api.analyze(payload);
      setResult(data);
      setRecs(data.recommendations || []);
    } catch (e: any) {
      setError(e.message || "Analysis failed. Is the backend running on :8000?");
    } finally {
      setRunning(false);
    }
  }

  async function decide(id: string, kind: "approve" | "reject" | "modify", text?: string) {
    let updated;
    if (kind === "approve") updated = await api.approve(id);
    else if (kind === "reject") updated = await api.reject(id);
    else updated = await api.modify(id, text || "");
    setRecs((rs) => rs.map((r) => (r.id === id ? { ...r, ...updated.recommendation } : r)));
  }

  return (
    <div className="space-y-6">
      <CustomerOverview
        customer={result?.customer}
        risk={result?.risk}
        sentiment={result?.conversation?.sentiment}
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* LEFT: inputs + timeline */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="font-medium flex items-center gap-2"><Upload size={16}/> Customer Information</CardHeader>
            <CardBody className="space-y-3">
              {[
                ["transcript", "Meeting transcript", 4],
                ["crm", "CRM (JSON)", 4],
                ["email", "Email", 2],
                ["support_ticket", "Support ticket", 2],
                ["notes", "Customer notes", 2],
              ].map(([k, label, rows]: any) => (
                <div key={k}>
                  <label className="text-xs text-muted">{label}</label>
                  <textarea rows={rows} value={(form as any)[k]} onChange={(e) => set(k, e.target.value)}
                    className="w-full mt-1 bg-ink border border-white/10 rounded-lg px-2 py-1.5 text-xs font-mono" />
                </div>
              ))}
              <Button onClick={analyze} disabled={running}>
                <span className="inline-flex items-center gap-2">
                  <Sparkles size={15} /> {running ? "Running agents…" : "Analyze & Recommend"}
                </span>
              </Button>
              {error && <p className="text-xs text-rose-400">{error}</p>}
            </CardBody>
          </Card>

          <AgentTimeline trace={result?.trace || []} running={running} />
        </div>

        {/* CENTER: recommendations */}
        <div className="space-y-3">
          <h2 className="font-medium">Next Best Actions {recs.length ? `(${recs.length})` : ""}</h2>
          {!recs.length && !running && (
            <Card><CardBody className="text-sm text-muted">Run an analysis to generate the top 5 Next Best Actions.</CardBody></Card>
          )}
          {recs.map((r) => (
            <RecommendationCard key={r.id} rec={r}
              onApprove={() => decide(r.id, "approve")}
              onReject={() => decide(r.id, "reject")}
              onModify={(t) => decide(r.id, "modify", t)}
              onInspect={() => setSelected(r)} />
          ))}
        </div>

        {/* RIGHT: evidence */}
        <div className="space-y-6">
          <EvidencePanel rec={selected} />
          {result?.risk?.risks?.length ? (
            <Card>
              <CardHeader className="font-medium">Detected Risks</CardHeader>
              <CardBody className="space-y-2 text-sm">
                {result.risk.risks.map((rk: any, i: number) => (
                  <div key={i} className="border-l-2 border-rose-500/50 pl-2">
                    <div className="text-slate-200">{rk.type} · <span className="text-muted">{rk.severity}</span></div>
                    <div className="text-xs text-muted">{rk.reason}</div>
                  </div>
                ))}
              </CardBody>
            </Card>
          ) : null}
        </div>
      </div>
    </div>
  );
}
