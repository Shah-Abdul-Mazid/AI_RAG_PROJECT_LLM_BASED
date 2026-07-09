import React from "react";
import { ActiveTab } from "@/types";
import {
  Activity,
  CheckCircle2,
  ChevronRight,
  Database,
  MessageSquare,
  ShieldCheck,
} from "lucide-react";

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  userRole: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  userRole,
}) => {
  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-white/10 bg-[#101218] md:flex">
      <div className="p-6">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-500 text-white">
            <Activity size={21} />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Nexus Intelligence</h1>
            <p className="text-xs text-slate-500">Enterprise AI Command</p>
          </div>
        </div>

        <nav className="space-y-2">
          <NavItem
            icon={<MessageSquare size={18} />}
            label="AI Assistant"
            description="Ask grounded questions"
            active={activeTab === "chat"}
            onClick={() => setActiveTab("chat")}
          />
          {userRole === "admin" && (
            <>
              <NavItem
                icon={<Database size={18} />}
                label="Knowledge Base"
                description="Ingest documents and web data"
                active={activeTab === "docs"}
                onClick={() => setActiveTab("docs")}
              />
              <NavItem
                icon={<ShieldCheck size={18} />}
                label="Compliance"
                description="Controls, agents, risk signals"
                active={activeTab === "analytics"}
                onClick={() => setActiveTab("analytics")}
              />
            </>
          )}
        </nav>
      </div>

      <div className="mt-auto p-6">
        <div className="rounded-lg border border-sky-400/20 bg-sky-400/10 p-4">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-xs font-semibold text-sky-200">Production demo</span>
            <CheckCircle2 size={16} className="text-emerald-300" />
          </div>
          <p className="text-xs leading-5 text-slate-400">
            JWT auth, vector search, upload pipeline, web scrape, feedback loop, and agent trace.
          </p>
        </div>
      </div>
    </aside>
  );
};

function NavItem({
  icon,
  label,
  description,
  active,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  description: string;
  active?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-lg px-4 py-3 text-left transition-colors ${
        active
          ? "bg-sky-500 text-white shadow-lg shadow-sky-500/15"
          : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
      }`}
    >
      <span className="flex items-center gap-3">
        {icon}
        <span className="min-w-0 flex-1">
          <span className="block text-sm font-medium">{label}</span>
          <span className={`mt-1 block text-xs ${active ? "text-sky-50/80" : "text-slate-600"}`}>
            {description}
          </span>
        </span>
        {active && <ChevronRight size={15} />}
      </span>
    </button>
  );
}
