"use client";

import React from "react";
import {
  BarChart3,
  Clock3,
  Database,
  FileText,
  Globe,
  Loader2,
  Trash2,
  Upload,
} from "lucide-react";

interface DocsTabProps {
  files: string[];
  isUploading: boolean;
  scrapeUrl: string;
  setScrapeUrl: (val: string) => void;
  isScraping: boolean;
  documentStats: { pdfs: number; tables: number; websites: number; total: number };
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
  handleUrlScrape: () => Promise<void>;
}

export const DocsTab: React.FC<DocsTabProps> = ({
  files,
  isUploading,
  scrapeUrl,
  setScrapeUrl,
  isScraping,
  documentStats,
  handleFileUpload,
  handleUrlScrape,
}) => {
  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-20 md:pb-0">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="mb-2 flex items-center gap-2 text-xs font-medium text-emerald-200">
            <Database size={15} />
            Knowledge ingestion
          </p>
          <h2 className="text-3xl font-semibold">Private Knowledge Base</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Upload internal files or scrape approved websites, then index the content for semantic retrieval.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="flex min-w-0 rounded-lg border border-white/10 bg-white/[0.04] p-1">
            <input
              type="text"
              value={scrapeUrl}
              onChange={(e) => setScrapeUrl(e.target.value)}
              placeholder="https://company-site.com/policy"
              className="min-w-0 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-600"
            />
            <button
              onClick={handleUrlScrape}
              disabled={isScraping}
              className="flex items-center gap-2 rounded-lg bg-violet-500 px-4 py-2 text-sm font-medium hover:bg-violet-400 disabled:opacity-50"
            >
              {isScraping ? <Loader2 size={16} className="animate-spin" /> : <Globe size={16} />}
              Scrape
            </button>
          </div>
          <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-sky-400/30 bg-sky-400/10 px-4 py-3 text-sm font-medium text-sky-100 hover:bg-sky-400/20">
            {isUploading ? <Loader2 size={17} className="animate-spin" /> : <Upload size={17} />}
            Upload document
            <input type="file" accept=".pdf,.txt,.csv,.xlsx,.docx" className="hidden" onChange={handleFileUpload} />
          </label>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard title="Indexed sources" value={documentStats.total.toString()} icon={<Database size={19} />} tone="sky" />
        <MetricCard title="PDF documents" value={documentStats.pdfs.toString()} icon={<FileText size={19} />} tone="rose" />
        <MetricCard title="Tables" value={documentStats.tables.toString()} icon={<BarChart3 size={19} />} tone="emerald" />
        <MetricCard title="Web sources" value={documentStats.websites.toString()} icon={<Globe size={19} />} tone="violet" />
      </div>

      <div className="overflow-hidden rounded-lg border border-white/10 bg-[#101218]">
        <table className="w-full min-w-[680px] text-left">
          <tbody className="divide-y divide-white/5">
            {files.map((file, i) => (
              <tr key={`${file}-${i}`} className="hover:bg-white/[0.03]">
                <td className="px-6 py-4 text-sm font-medium">{file}</td>
                <td className="px-6 py-4 text-xs text-slate-400">
                  {file.startsWith("http") ? "WEB" : file.split(".").pop()?.toUpperCase()}
                </td>
                <td className="px-6 py-4 text-xs text-slate-400">{"Parse > Chunk > Embed > Upsert"}</td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1.5 rounded-md bg-emerald-400/10 px-2 py-1 text-xs font-medium text-emerald-200">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                    Indexed
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button className="rounded-md p-2 text-slate-500 hover:bg-rose-400/10 hover:text-rose-300" aria-label="Delete source">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {files.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-14 text-center text-sm text-slate-500">
                  Upload a PDF, Excel file, document, or approved URL to show the ingestion pipeline.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

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
        <Clock3 size={15} className="text-slate-600" />
      </div>
      <p className="text-2xl font-semibold">{value}</p>
      <p className="mt-1 text-sm text-slate-500">{title}</p>
    </div>
  );
}
