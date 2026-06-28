"use client";
import { Card, CardHeader, CardBody } from "./ui";
import { FileText, Database, BookOpen, Scale } from "lucide-react";

function Block({ icon: Icon, title, children }: any) {
  return (
    <div>
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted mb-1">
        <Icon size={13} /> {title}
      </div>
      <div className="text-sm text-slate-200">{children}</div>
    </div>
  );
}

export function EvidencePanel({ rec }: { rec: any }) {
  if (!rec) {
    return (
      <Card>
        <CardHeader className="font-medium">Evidence Panel</CardHeader>
        <CardBody className="text-sm text-muted">
          Select <span className="text-slate-200">Evidence</span> on a recommendation to see why it was suggested.
        </CardBody>
      </Card>
    );
  }
  const e = rec.evidence || {};
  return (
    <Card>
      <CardHeader className="font-medium">Evidence · {rec.action}</CardHeader>
      <CardBody className="space-y-4">
        <Block icon={FileText} title="Transcript">{e.transcript || "—"}</Block>
        <Block icon={Database} title="CRM">{e.crm || "—"}</Block>
        <Block icon={BookOpen} title="Knowledge">
          {(e.knowledge || []).length ? (
            <ul className="list-disc ml-4 space-y-0.5">
              {(e.knowledge || []).map((k: string, i: number) => <li key={i}>{k}</li>)}
            </ul>
          ) : "—"}
        </Block>
        <Block icon={Scale} title="Business Rules">
          <ul className="list-disc ml-4 space-y-0.5">
            {(e.business_rules || []).map((b: string, i: number) => <li key={i}>{b}</li>)}
          </ul>
        </Block>
      </CardBody>
    </Card>
  );
}
