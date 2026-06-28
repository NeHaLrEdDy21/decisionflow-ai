"use client";
import { Card, CardBody, Badge } from "./ui";
import { Brain, Check, X, Pencil, FileSearch } from "lucide-react";

const ICONS: Record<string, any> = {
  approved: Check, rejected: X, modified: Pencil, analysis: FileSearch,
};
const TONE: Record<string, string> = {
  approved: "text-emerald-400", rejected: "text-rose-400",
  modified: "text-amber-300", analysis: "text-indigo-300",
};

export function MemoryTimeline({ items }: { items: any[] }) {
  if (!items?.length) {
    return <Card><CardBody className="text-sm text-muted">No stored interactions yet. Approve a recommendation to build memory.</CardBody></Card>;
  }
  return (
    <div className="relative pl-6">
      <div className="absolute left-2 top-0 bottom-0 w-px bg-white/10" />
      {items.map((m) => {
        const key = m.result || m.kind;
        const Icon = ICONS[key] || Brain;
        return (
          <div key={m.id} className="relative mb-4">
            <div className="absolute -left-[18px] top-1 bg-ink rounded-full p-0.5">
              <Icon size={15} className={TONE[key] || "text-muted"} />
            </div>
            <Card>
              <CardBody className="py-3">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-sm">{m.action}</div>
                  <Badge>{(m.result || m.kind || "").toUpperCase()}</Badge>
                </div>
                <div className="text-xs text-muted mt-1">
                  {m.customer_name} · {new Date(m.created_at).toLocaleString()}
                </div>
                {m.detail?.reason && <div className="text-xs text-slate-300 mt-1">{m.detail.reason}</div>}
              </CardBody>
            </Card>
          </div>
        );
      })}
    </div>
  );
}
