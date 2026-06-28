// Minimal shadcn-style primitives (Card / Badge / Button) using Tailwind.
import * as React from "react";

export function Card({ children, className = "" }: any) {
  return (
    <div className={`rounded-xl border border-white/10 bg-card/80 backdrop-blur shadow-lg ${className}`}>
      {children}
    </div>
  );
}
export function CardHeader({ children, className = "" }: any) {
  return <div className={`p-4 border-b border-white/10 ${className}`}>{children}</div>;
}
export function CardBody({ children, className = "" }: any) {
  return <div className={`p-4 ${className}`}>{children}</div>;
}

const PRIORITY: Record<string, string> = {
  High: "bg-rose-500/20 text-rose-300 border-rose-500/40",
  Medium: "bg-amber-500/20 text-amber-300 border-amber-500/40",
  Low: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
};
export function Badge({ children, tone }: { children: React.ReactNode; tone?: string }) {
  const cls = (tone && PRIORITY[tone]) || "bg-indigo-500/20 text-indigo-300 border-indigo-500/40";
  return <span className={`text-xs px-2 py-0.5 rounded-full border ${cls}`}>{children}</span>;
}

export function Button({ children, onClick, variant = "primary", disabled }: any) {
  const map: Record<string, string> = {
    primary: "bg-accent hover:bg-indigo-500 text-white",
    ghost: "bg-white/5 hover:bg-white/10 text-slate-200 border border-white/10",
    success: "bg-emerald-600 hover:bg-emerald-500 text-white",
    danger: "bg-rose-600 hover:bg-rose-500 text-white",
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition disabled:opacity-40 ${map[variant]}`}
    >
      {children}
    </button>
  );
}
