"use client";
import { Card } from "./ui";
import { Activity, CalendarClock, Gauge, AlertTriangle } from "lucide-react";

function Stat({ icon: Icon, label, value, tone = "text-white" }: any) {
  return (
    <Card className="p-4 flex items-center gap-3">
      <div className="p-2 rounded-lg bg-white/5"><Icon size={18} className={tone} /></div>
      <div>
        <div className="text-[11px] uppercase tracking-wide text-muted">{label}</div>
        <div className={`text-lg font-semibold ${tone}`}>{value}</div>
      </div>
    </Card>
  );
}

export function CustomerOverview({ customer, risk, sentiment }: any) {
  const health = customer?.health ?? "—";
  const riskLevel = risk?.risk_level ?? "—";
  const riskTone = riskLevel === "High" ? "text-rose-400" : riskLevel === "Medium" ? "text-amber-300" : "text-emerald-400";
  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">{customer?.name || "Customer"}</h1>
      <p className="text-muted text-sm mb-4">Customer Success · pre-renewal decision view</p>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Stat icon={Gauge} label="Health Score" value={health} />
        <Stat icon={CalendarClock} label="Renewal" value={customer?.renewal_days != null ? `${customer.renewal_days} days` : "—"} />
        <Stat icon={Activity} label="Sentiment" value={sentiment || "—"} />
        <Stat icon={AlertTriangle} label="Risk Level" value={riskLevel} tone={riskTone} />
      </div>
    </div>
  );
}
