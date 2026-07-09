"use client";

import React from "react";
import {
  Activity,
  CheckCircle2,
  Cpu,
  Database,
  Globe,
  Layers,
  LockKeyhole,
  ShieldAlert,
  ShieldCheck,
  Zap,
} from "lucide-react";

const complianceSignals = [
  { label: "PII redaction (Email, Phone, SSN)", value: "Active", tone: "text-emerald-300" },
  { label: "Credit Card check (Luhn)", value: "Active", tone: "text-emerald-300" },
  { label: "ABA Routing check (RTN)", value: "Active", tone: "text-emerald-300" },
  { label: "IBAN protection", value: "Active", tone: "text-emerald-300" },
  { label: "Source grounding", value: "Required", tone: "text-sky-300" },
  { label: "Admin controls", value: "Enabled", tone: "text-amber-300" },
];

export const AnalyticsTab: React.FC = () => {
  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <p className="mb-2 flex items-center gap-2 text-xs font-medium text-amber-200">
          <ShieldAlert size={15} />
          Governance and reliability
        </p>
        <h2 className="text-3xl font-semibold">Compliance Command Center</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          This view explains the enterprise thinking behind the system: retrieval confidence, traceability,
          redaction, and controls that matter to real organizations.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <MetricCard title="Grounded responses" value="100%" icon={<CheckCircle2 size={19} />} tone="emerald" />
        <MetricCard title="Agent stages" value="4" icon={<Layers size={19} />} tone="sky" />
        <MetricCard title="Access model" value="JWT" icon={<LockKeyhole size={19} />} tone="violet" />
      </div>

      <div className="grid gap-5 lg:grid-cols-[1fr_360px]">
        <Panel title="Enterprise Architecture" icon={<Cpu size={17} />}>
          <div className="grid gap-3 md:grid-cols-2">
            <ArchitectureItem title="Next.js Client" detail="Responsive app shell with protected dashboard state." icon={<Globe size={18} />} />
            <ArchitectureItem title="FastAPI Backend" detail="Async endpoints for auth, chat, upload, scrape, and feedback." icon={<Zap size={18} />} />
            <ArchitectureItem title="Live API Connectors" detail="Weather questions route to Open-Meteo before RAG fallback." icon={<Globe size={18} />} />
            <ArchitectureItem title="Pinecone Vector Store" detail="Embeddings power semantic search over private sources." icon={<Database size={18} />} />
            <ArchitectureItem title="Compliance Agent" detail="Policy and sensitive-data checks before answer delivery." icon={<ShieldCheck size={18} />} />
          </div>
        </Panel>

        <Panel title="Control Signals" icon={<Activity size={17} />}>
          <div className="space-y-3">
            {complianceSignals.map((signal) => (
              <div key={signal.label} className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] p-3">
                <span className="text-sm text-slate-400">{signal.label}</span>
                <span className={`text-sm font-medium ${signal.tone}`}>{signal.value}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
};

function Panel({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-white/10 bg-[#101218] p-5">
      <div className="mb-4 flex items-center gap-2 text-sm font-semibold">
        <span className="text-sky-200">{icon}</span>
        {title}
      </div>
      {children}
    </section>
  );
}

function ArchitectureItem({ title, detail, icon }: { title: string; detail: string; icon: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
      <div className="mb-3 text-sky-200">{icon}</div>
      <p className="text-sm font-medium text-slate-100">{title}</p>
      <p className="mt-2 text-xs leading-5 text-slate-500">{detail}</p>
    </div>
  );
}

function MetricCard({
  title,
  value,
  icon,
  tone,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  tone: "sky" | "emerald" | "violet" | "rose";
}) {
  const toneClass = {
    sky: "bg-sky-400/10 text-sky-200 border-sky-400/20",
    emerald: "bg-emerald-400/10 text-emerald-200 border-emerald-400/20",
    violet: "bg-violet-400/10 text-violet-200 border-violet-400/20",
    rose: "bg-rose-400/10 text-rose-200 border-rose-400/20",
  }[tone];

  return (
    <div className="rounded-lg border border-white/10 bg-[#101218] p-5">
      <div className="mb-4 flex items-center justify-between">
        <span className={`rounded-lg border p-2 ${toneClass}`}>{icon}</span>
      </div>
      <p className="text-2xl font-semibold">{value}</p>
      <p className="mt-1 text-sm text-slate-500">{title}</p>
    </div>
  );
}
