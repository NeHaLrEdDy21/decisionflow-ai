"use client";
import { useState } from "react";
import { Card, CardBody, Badge, Button } from "./ui";
import { Check, X, Pencil, Eye } from "lucide-react";
import type { Recommendation } from "@/lib/api";

export function RecommendationCard({ rec, onApprove, onReject, onModify, onInspect }: {
  rec: Recommendation;
  onApprove: () => void;
  onReject: () => void;
  onModify: (text: string) => void;
  onInspect: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(rec.action);

  const statusColor: Record<string, string> = {
    approved: "border-emerald-500/50", rejected: "border-rose-500/50",
    modified: "border-amber-500/50", pending: "border-white/10",
  };

  return (
    <Card className={`border ${statusColor[rec.status] || "border-white/10"}`}>
      <CardBody>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            {editing ? (
              <input value={draft} onChange={(e) => setDraft(e.target.value)}
                className="w-full bg-ink border border-white/15 rounded px-2 py-1 text-sm" />
            ) : (
              <h3 className="font-medium leading-snug">{rec.action}</h3>
            )}
          </div>
          <div className="flex flex-col items-end gap-1">
            <Badge tone={rec.priority}>{rec.priority}</Badge>
            <span className="text-[11px] text-muted">{rec.confidence}% conf.</span>
          </div>
        </div>

        <p className="text-sm text-slate-300 mt-2"><span className="text-muted">Why: </span>{rec.reason}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2 text-xs text-muted">
          <div><span className="text-slate-400">Impact:</span> {rec.business_impact}</div>
          <div><span className="text-slate-400">Outcome:</span> {rec.expected_outcome}</div>
        </div>

        {rec.status !== "pending" && (
          <div className="mt-2 text-xs">
            <Badge>{rec.status.toUpperCase()}</Badge>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mt-4">
          {editing ? (
            <>
              <Button variant="success" onClick={() => { onModify(draft); setEditing(false); }}>Save</Button>
              <Button variant="ghost" onClick={() => setEditing(false)}>Cancel</Button>
            </>
          ) : (
            <>
              <Button variant="success" onClick={onApprove}><span className="inline-flex items-center gap-1"><Check size={14}/>Approve</span></Button>
              <Button variant="danger" onClick={onReject}><span className="inline-flex items-center gap-1"><X size={14}/>Reject</span></Button>
              <Button variant="ghost" onClick={() => setEditing(true)}><span className="inline-flex items-center gap-1"><Pencil size={14}/>Modify</span></Button>
              <Button variant="ghost" onClick={onInspect}><span className="inline-flex items-center gap-1"><Eye size={14}/>Evidence</span></Button>
            </>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
