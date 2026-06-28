"use client";
import { Card, CardHeader, CardBody } from "./ui";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const AGENTS = ["planner","conversation","crm","knowledge","risk","opportunity","recommendation","explanation","memory"];
const LABELS: Record<string,string> = {
  planner:"Planner", conversation:"Conversation", crm:"CRM", knowledge:"Knowledge",
  risk:"Risk", opportunity:"Opportunity", recommendation:"Recommendation",
  explanation:"Explanation", memory:"Memory",
};

export function AgentTimeline({ trace, running }: { trace: any[]; running: boolean }) {
  const done = new Set((trace || []).map((t) => t.agent));
  const msFor = (k: string) => (trace || []).find((t) => t.agent === k)?.ms;
  return (
    <Card>
      <CardHeader className="font-medium">Agent Execution Timeline</CardHeader>
      <CardBody className="space-y-1">
        {AGENTS.map((k, i) => {
          const complete = done.has(k);
          const isNext = running && !complete && AGENTS.slice(0, i).every((p) => done.has(p));
          return (
            <div key={k} className="flex items-center gap-3 py-1">
              {complete ? <CheckCircle2 size={18} className="text-emerald-400" />
                : isNext ? <Loader2 size={18} className="text-accent animate-spin" />
                : <Circle size={18} className="text-white/20" />}
              <span className={complete ? "text-slate-100" : "text-muted"}>{LABELS[k]}</span>
              {complete && msFor(k) != null && (
                <span className="ml-auto text-[11px] text-muted">{msFor(k)} ms</span>
              )}
            </div>
          );
        })}
      </CardBody>
    </Card>
  );
}
