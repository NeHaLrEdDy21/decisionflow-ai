"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MemoryTimeline } from "@/components/MemoryTimeline";
import { Button } from "@/components/ui";
import { RefreshCw } from "lucide-react";

export default function MemoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try { const d = await api.memory(); setItems(d.memory || []); }
    finally { setLoading(false); }
  }
  useEffect(() => { load(); }, []);

  const approved = items.filter((i) => i.result === "approved");
  const rejected = items.filter((i) => i.result === "rejected");

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Memory Timeline</h1>
          <p className="text-muted text-sm">Customer history · approved & rejected decisions feed future recommendations.</p>
        </div>
        <Button variant="ghost" onClick={load}>
          <span className="inline-flex items-center gap-2"><RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Refresh</span>
        </Button>
      </div>
      <div className="flex gap-3 text-sm">
        <span className="text-emerald-400">{approved.length} approved</span>
        <span className="text-rose-400">{rejected.length} rejected</span>
        <span className="text-muted">{items.length} total entries</span>
      </div>
      <MemoryTimeline items={items} />
    </div>
  );
}
