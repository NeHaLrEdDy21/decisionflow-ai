"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Brain, Workflow } from "lucide-react";

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/memory", label: "Memory", icon: Brain },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <aside className="w-60 shrink-0 border-r border-white/10 bg-panel/60 backdrop-blur p-5">
      <div className="flex items-center gap-2 mb-8">
        <Workflow className="text-accent" size={22} />
        <div>
          <div className="font-semibold leading-tight">DecisionFlow AI</div>
          <div className="text-[11px] text-muted">Decision Intelligence</div>
        </div>
      </div>
      <nav className="space-y-1">
        {links.map(({ href, label, icon: Icon }) => {
          const active = path === href;
          return (
            <Link key={href} href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                active ? "bg-accent/20 text-white" : "text-muted hover:bg-white/5"
              }`}>
              <Icon size={16} /> {label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-10 text-[11px] text-muted leading-relaxed">
        Customer Success · SaaS<br />Next Best Action engine
      </div>
    </aside>
  );
}
