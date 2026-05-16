"use client";

import React, { useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import {
  Activity,
  BarChart3,
  Brain,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Cpu,
  Database,
  FileText,
  Gauge,
  Globe,
  Layers,
  Loader2,
  LockKeyhole,
  MessageSquare,
  Search,
  Send,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  Upload,
  Zap,
} from "lucide-react";
import axios from "axios";
import { motion } from "framer-motion";

const getApiBase = () => {
  if (typeof window === "undefined") return "http://localhost:8000";
  const hostname = window.location.hostname;

  // If local, use localhost:8000
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return "http://localhost:8000";
  }

  // In production, return an empty string to use RELATIVE paths
  return ""; 
};



interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  logs?: string[];
}

interface AuthSnapshot {
  authHydrated: boolean;
  isAuthenticated: boolean;
  userRole: string | null;
  userFullName: string | null;
}

type ActiveTab = "chat" | "docs" | "analytics";

const serverAuthSnapshot: AuthSnapshot = {
  authHydrated: false,
  isAuthenticated: false,
  userRole: null,
  userFullName: null,
};

let cachedAuthSnapshot = serverAuthSnapshot;

const getAuthSnapshot = (): AuthSnapshot => {
  if (typeof window === "undefined") {
    return serverAuthSnapshot;
  }

  const token = localStorage.getItem("token");
  const nextSnapshot = {
    authHydrated: true,
    isAuthenticated: Boolean(token),
    userRole: localStorage.getItem("role"),
    userFullName: localStorage.getItem("fullName"),
  };

  if (
    cachedAuthSnapshot.authHydrated === nextSnapshot.authHydrated &&
    cachedAuthSnapshot.isAuthenticated === nextSnapshot.isAuthenticated &&
    cachedAuthSnapshot.userRole === nextSnapshot.userRole &&
    cachedAuthSnapshot.userFullName === nextSnapshot.userFullName
  ) {
    return cachedAuthSnapshot;
  }

  cachedAuthSnapshot = nextSnapshot;
  return cachedAuthSnapshot;
};

const subscribeToAuthChanges = (callback: () => void) => {
  if (typeof window === "undefined") {
    return () => {};
  }

  window.addEventListener("storage", callback);
  window.addEventListener("authchange", callback);

  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener("authchange", callback);
  };
};

const notifyAuthChanged = () => {
  window.dispatchEvent(new Event("authchange"));
};

const starterPrompts = [
  "What is today's weather in Dhaka?",
  "Summarize the latest uploaded policy document",
  "Which sources support this answer?",
];

const agentPipeline = [
  { label: "Live Data", detail: "Routes weather and API questions to real-time connectors", icon: Globe, color: "text-emerald-300" },
  { label: "Retriever", detail: "Semantic search over private knowledge", icon: Search, color: "text-sky-300" },
  { label: "Generator", detail: "Grounded synthesis with source context", icon: Brain, color: "text-violet-300" },
  { label: "Compliance", detail: "PII and policy guardrails before response", icon: ShieldCheck, color: "text-emerald-300" },
];

const complianceSignals = [
  { label: "PII redaction", value: "Active", tone: "text-emerald-300" },
  { label: "Source grounding", value: "Required", tone: "text-sky-300" },
  { label: "Admin controls", value: "Enabled", tone: "text-amber-300" },
];

export default function Dashboard() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Welcome to Nexus Intelligence. Ask a question and I will search company knowledge, synthesize an answer, and show the agent trace.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [files, setFiles] = useState<string[]>([]);
  const [scrapeUrl, setScrapeUrl] = useState("");
  const [isScraping, setIsScraping] = useState(false);
  const [activeTab, setActiveTab] = useState<ActiveTab>("chat");
  const [selectedProvider, setSelectedProvider] = useState("ollama");

  const auth = useSyncExternalStore(
    subscribeToAuthChanges,
    getAuthSnapshot,
    () => serverAuthSnapshot,
  );
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [registerFullName, setRegisterFullName] = useState("");
  const [authMessage, setAuthMessage] = useState("");

  const chatEndRef = useRef<HTMLDivElement>(null);

  const documentStats = useMemo(() => {
    const pdfs = files.filter((file) => file.toLowerCase().endsWith(".pdf")).length;
    const tables = files.filter((file) => /\.(csv|xlsx|xls)$/i.test(file)).length;
    const websites = files.filter((file) => file.startsWith("http")).length;

    return { pdfs, tables, websites, total: files.length };
  }, [files]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    setAuthMessage("");
    try {
      const params = new URLSearchParams();
      params.append("username", loginEmail);
      params.append("password", loginPassword);

      const response = await axios.post(`${getApiBase()}/api/v1/auth/login`, params);
      const data = response.data;

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", data.role);
      localStorage.setItem("fullName", data.full_name);

      notifyAuthChanged();
    } catch {
      setLoginError("Invalid credentials. Try admin@mgi.org or user@mgi.org");
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    setAuthMessage("");

    if (!registerFullName.trim()) {
      setLoginError("Please enter your full name.");
      return;
    }

    try {
      await axios.post(`${getApiBase()}/api/v1/auth/register`, {
        email: loginEmail,
        password: loginPassword,
        full_name: registerFullName,
      });

      setAuthMessage("Account created. You can sign in now.");
      setAuthMode("login");
      setLoginPassword("");
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        setLoginError(String(error.response.data.detail));
      } else {
        setLoginError("Could not create account. Please try again.");
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("fullName");
    notifyAuthChanged();
    setMessages([{ role: "assistant", content: "Welcome back. Please login." }]);
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (nextInput = input) => {
    if (!nextInput.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: nextInput };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        `${getApiBase()}/api/v1/chat`, 
        { 
          message: nextInput,
          provider: selectedProvider
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const botMessage: Message = {
        role: "assistant",
        content: response.data.answer,
        sources: response.data.sources,
        logs: response.data.agent_logs,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I could not reach the AI engine. Please confirm the FastAPI backend is running on port 8000.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    setIsUploading(true);
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${getApiBase()}/api/v1/upload`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFiles((prev) => [...prev, file.name]);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        alert(`Upload Failed: ${error.response.data.detail}`);
      } else {
        alert("Failed to upload file. Check if backend is running.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleUrlScrape = async () => {
    if (!scrapeUrl.trim()) return;
    setIsScraping(true);
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${getApiBase()}/api/v1/scrape`, { url: scrapeUrl }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFiles((prev) => [...prev, scrapeUrl]);
      setScrapeUrl("");
      alert("Website successfully scraped and indexed.");
    } catch {
      alert("Failed to scrape website");
    } finally {
      setIsScraping(false);
    }
  };

  const handleFeedback = async (query: string, answer: string, isPositive: boolean) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${getApiBase()}/api/v1/feedback`, { query, answer, is_positive: isPositive }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("Thank you for your feedback.");
    } catch (error) {
      console.error("Feedback error", error);
    }
  };

  if (!auth.authHydrated) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#08090d] text-white">
        <Loader2 size={26} className="animate-spin text-sky-300" />
      </div>
    );
  }

  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#08090d] text-white">
        <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">
          <section className="flex flex-col justify-between border-r border-white/10 p-6 md:p-10">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-sky-500 text-white shadow-lg shadow-sky-500/20">
                <Activity size={24} />
              </div>
              <div>
                <p className="text-lg font-semibold">Nexus Intelligence</p>
                <p className="text-xs text-slate-400">Private enterprise RAG platform</p>
              </div>
            </div>

            <div className="max-w-2xl py-14">
              <div className="mb-5 inline-flex items-center gap-2 rounded-lg border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-medium text-emerald-200">
                <Sparkles size={14} />
                Multi-agent AI for secure company knowledge
              </div>
              <h1 className="text-4xl font-semibold leading-tight text-white md:text-6xl">
                Ask your enterprise data. Get grounded answers with governance.
              </h1>
              <p className="mt-5 max-w-xl text-sm leading-6 text-slate-400 md:text-base">
                A recruiter-friendly showcase of FastAPI, Next.js, Pinecone, document ingestion, semantic retrieval,
                agent orchestration, and compliance checks in one product experience.
              </p>

              <div className="mt-8 grid gap-3 sm:grid-cols-3">
                <LoginFeature icon={<Database size={18} />} title="RAG Search" value="Pinecone" />
                    <LoginFeature icon={<Cpu size={18} />} title="AI Agents" value="API + RAG routing" />
                <LoginFeature icon={<LockKeyhole size={18} />} title="Security" value="JWT access" />
              </div>
            </div>

            <p className="text-xs text-slate-500">Built for MGI interview demo readiness.</p>
          </section>

          <section className="flex items-center justify-center p-6">
            <div className="w-full max-w-[420px] rounded-lg border border-white/10 bg-white/[0.04] p-6 shadow-2xl shadow-black/30">
              <div className="mb-7">
                <p className="text-sm text-slate-400">Secure access</p>
                <h2 className="mt-1 text-2xl font-semibold">
                  {authMode === "login" ? "Enterprise Login" : "Create Account"}
                </h2>
              </div>

              <div className="mb-5 grid grid-cols-2 gap-2 rounded-lg border border-white/10 bg-black/20 p-1">
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("login");
                    setLoginError("");
                    setAuthMessage("");
                  }}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    authMode === "login" ? "bg-sky-500 text-white" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("register");
                    setLoginError("");
                    setAuthMessage("");
                  }}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    authMode === "register" ? "bg-sky-500 text-white" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Sign Up
                </button>
              </div>

              <form onSubmit={authMode === "login" ? handleLogin : handleRegister} className="space-y-4">
                {authMode === "register" && (
                  <label className="block">
                    <span className="mb-2 block text-sm text-slate-300">Full Name</span>
                    <input
                      type="text"
                      value={registerFullName}
                      onChange={(e) => setRegisterFullName(e.target.value)}
                      className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm outline-none transition-colors focus:border-sky-400"
                      placeholder="New User"
                    />
                  </label>
                )}
                <label className="block">
                  <span className="mb-2 block text-sm text-slate-300">Email / Username</span>
                  <input
                    type="text"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm outline-none transition-colors focus:border-sky-400"
                    placeholder="admin@mgi.org"
                  />
                </label>
                <label className="block">
                  <span className="mb-2 block text-sm text-slate-300">Password</span>
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm outline-none transition-colors focus:border-sky-400"
                    placeholder="password"
                  />
                </label>

                {authMessage && <p className="text-center text-xs text-emerald-300">{authMessage}</p>}
                {loginError && <p className="text-center text-xs text-rose-300">{loginError}</p>}

                <button
                  type="submit"
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-sky-500 py-3 text-sm font-semibold text-white transition-colors hover:bg-sky-400"
                >
                  <LockKeyhole size={16} />
                  {authMode === "login" ? "Sign In" : "Create Account"}
                </button>
              </form>

              <div className="mt-6 rounded-lg border border-white/10 bg-black/20 p-4 text-xs text-slate-400">
                <p className="mb-2 font-medium text-slate-200">Demo accounts</p>
                <p>Admin: admin@mgi.org / Admin@123</p>
                <p>User: user@mgi.org / user123</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#08090d] text-white md:flex-row">
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
            {auth.userRole === "admin" && (
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

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/10 bg-[#101218]/95 px-4 md:px-7">
          <div className="flex items-center gap-3 text-xs text-slate-400 md:text-sm">
            <span className="hidden sm:inline">System health</span>
            <span className="flex items-center gap-2 rounded-lg border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-emerald-200">
              <span className="h-2 w-2 rounded-full bg-emerald-300" />
              Operational
            </span>
            <span className="hidden rounded-lg border border-white/10 px-3 py-1.5 text-slate-400 lg:inline-flex">
              API: {getApiBase().replace("http://", "")}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium">{auth.userFullName}</p>
              <p className="text-xs uppercase text-slate-500">{auth.userRole}</p>
            </div>
            <button onClick={handleLogout} className="rounded-lg px-3 py-2 text-xs text-rose-300 hover:bg-rose-400/10">
              Logout
            </button>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-500 text-sm font-semibold">
              {auth.userFullName?.charAt(0) ?? "U"}
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-7">
          {activeTab === "chat" && (
            <div className="grid h-full gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
              <section className="flex min-h-[680px] flex-col rounded-lg border border-white/10 bg-[#0d0f14]">
                <div className="border-b border-white/10 p-5">
                  <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
                    <div>
                      <div className="mb-2 flex items-center gap-2 text-xs font-medium text-sky-200">
                        <Sparkles size={15} />
                        Multi-agent intelligence assistant
                      </div>
                      <div className="flex items-center gap-4">
                        <h2 className="text-2xl font-semibold">Ask company knowledge with confidence</h2>
                        <select 
                          value={selectedProvider}
                          onChange={(e) => setSelectedProvider(e.target.value)}
                          className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-sky-200 outline-none transition-colors focus:border-sky-400"
                        >
                          <option value="openai">GPT-4o (OpenAI)</option>
                          <option value="grok">Grok-2 (X.AI)</option>
                          <option value="gemini">Gemini 1.5 Flash</option>
                          <option value="bedrock">AWS Bedrock (Llama 3)</option>
                          <option value="ollama">Local Llama (Ollama)</option>
                        </select>
                      </div>
                      <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                        The assistant retrieves trusted context, generates a grounded answer, then applies compliance
                        checks before showing the response.
                      </p>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <MiniMetric label="Docs" value={documentStats.total.toString()} />
                      <MiniMetric label="Agents" value="4" />
                      <MiniMetric label="Mode" value="API + RAG" />
                    </div>
                  </div>
                </div>

                <div className="flex-1 space-y-5 overflow-y-auto p-5">
                  {messages.map((msg, idx) => (
                    <motion.div
                      key={`${msg.role}-${idx}`}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[92%] rounded-lg p-4 text-sm leading-6 md:max-w-[78%] ${
                          msg.role === "user"
                            ? "bg-sky-500 text-white"
                            : "border border-white/10 bg-white/[0.04] text-slate-200"
                        }`}
                      >
                        <p>{msg.content}</p>

                        {msg.logs && (
                          <div className="mt-4 flex flex-wrap gap-2 border-t border-white/10 pt-3">
                            {msg.logs.map((log, i) => (
                              <span key={i} className="flex items-center gap-1 rounded-md bg-black/20 px-2 py-1 text-[11px] text-slate-300">
                                <Activity size={11} className="text-sky-300" />
                                {log}
                              </span>
                            ))}
                          </div>
                        )}

                        {msg.sources && msg.sources.length > 0 && (
                          <div className="mt-4 flex flex-col gap-3 border-t border-white/10 pt-3 sm:flex-row sm:items-center sm:justify-between">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-[11px] text-slate-500">Sources</span>
                              {msg.sources.map((src, i) => (
                                <span key={i} className="flex items-center gap-1 rounded-md bg-sky-400/10 px-2 py-1 text-[11px] text-sky-200">
                                  <FileText size={11} />
                                  {src}
                                </span>
                              ))}
                            </div>
                            {msg.role === "assistant" && idx > 0 && (
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleFeedback(messages[idx - 1].content, msg.content, true)}
                                  className="rounded-md p-1.5 text-slate-500 hover:bg-emerald-400/10 hover:text-emerald-300"
                                  aria-label="Positive feedback"
                                >
                                  <ThumbsUp size={14} />
                                </button>
                                <button
                                  onClick={() => handleFeedback(messages[idx - 1].content, msg.content, false)}
                                  className="rounded-md p-1.5 text-slate-500 hover:bg-rose-400/10 hover:text-rose-300"
                                  aria-label="Negative feedback"
                                >
                                  <ThumbsDown size={14} />
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-400">
                        <Loader2 size={16} className="animate-spin text-sky-300" />
                        Agent pipeline is retrieving, reasoning, and checking compliance...
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                <div className="border-t border-white/10 bg-[#101218] p-4">
                  <div className="mb-3 flex flex-wrap gap-2">
                    {starterPrompts.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => handleSendMessage(prompt)}
                        className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300 hover:border-sky-400/40 hover:bg-sky-400/10 hover:text-sky-100"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-black/20 p-1">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                      placeholder="Ask anything about your documents..."
                      className="min-w-0 flex-1 bg-transparent px-4 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-600"
                    />
                    <button
                      onClick={() => handleSendMessage()}
                      disabled={isLoading}
                      className="flex h-11 w-11 items-center justify-center rounded-lg bg-sky-500 text-white transition-colors hover:bg-sky-400 disabled:opacity-50"
                      aria-label="Send message"
                    >
                      <Send size={18} />
                    </button>
                  </div>
                </div>
              </section>

              <aside className="space-y-5">
                <Panel title="Agent Pipeline" icon={<Layers size={17} />}>
                  <div className="space-y-3">
                    {agentPipeline.map((agent) => (
                      <div key={agent.label} className="flex gap-3 rounded-lg border border-white/10 bg-white/[0.03] p-3">
                        <agent.icon size={18} className={agent.color} />
                        <div>
                          <p className="text-sm font-medium text-slate-100">{agent.label}</p>
                          <p className="mt-1 text-xs leading-5 text-slate-500">{agent.detail}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </Panel>

                <Panel title="Executive Signals" icon={<Gauge size={17} />}>
                  <div className="grid gap-3">
                    <Signal label="Answer grounding" value="Source aware" tone="emerald" />
                    <Signal label="Live API tools" value="Weather ready" tone="sky" />
                    <Signal label="Data posture" value="Private index" tone="violet" />
                  </div>
                </Panel>
              </aside>
            </div>
          )}

          {activeTab === "docs" && (
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
                  <thead className="border-b border-white/10 bg-white/[0.03] text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-6 py-4 font-medium">Document Name</th>
                      <th className="px-6 py-4 font-medium">Type</th>
                      <th className="px-6 py-4 font-medium">Pipeline</th>
                      <th className="px-6 py-4 font-medium">Status</th>
                      <th className="px-6 py-4 font-medium">Action</th>
                    </tr>
                  </thead>
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
          )}

          {activeTab === "analytics" && (
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
          )}
        </div>

        <div className="flex shrink-0 justify-around border-t border-white/10 bg-[#101218] p-2 md:hidden">
          <MobileNav icon={<MessageSquare size={20} />} label="Chat" active={activeTab === "chat"} onClick={() => setActiveTab("chat")} />
          {auth.userRole === "admin" && (
            <>
              <MobileNav icon={<Database size={20} />} label="Docs" active={activeTab === "docs"} onClick={() => setActiveTab("docs")} />
              <MobileNav icon={<ShieldCheck size={20} />} label="Control" active={activeTab === "analytics"} onClick={() => setActiveTab("analytics")} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}

function LoginFeature({ icon, title, value }: { icon: React.ReactNode; title: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
      <div className="mb-3 text-sky-200">{icon}</div>
      <p className="text-sm font-medium">{title}</p>
      <p className="mt-1 text-xs text-slate-500">{value}</p>
    </div>
  );
}

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
        active ? "bg-sky-500 text-white shadow-lg shadow-sky-500/15" : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
      }`}
    >
      <span className="flex items-center gap-3">
        {icon}
        <span className="min-w-0 flex-1">
          <span className="block text-sm font-medium">{label}</span>
          <span className={`mt-1 block text-xs ${active ? "text-sky-50/80" : "text-slate-600"}`}>{description}</span>
        </span>
        {active && <ChevronRight size={15} />}
      </span>
    </button>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-3">
      <p className="text-base font-semibold">{value}</p>
      <p className="mt-1 text-[11px] text-slate-500">{label}</p>
    </div>
  );
}

function MetricCard({ title, value, icon, tone }: { title: string; value: string; icon: React.ReactNode; tone: "sky" | "emerald" | "violet" | "rose" }) {
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

function Signal({ label, value, tone }: { label: string; value: string; tone: "emerald" | "sky" | "violet" }) {
  const toneClass = {
    emerald: "text-emerald-200 bg-emerald-400/10",
    sky: "text-sky-200 bg-sky-400/10",
    violet: "text-violet-200 bg-violet-400/10",
  }[tone];

  return (
    <div className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] p-3">
      <span className="text-sm text-slate-400">{label}</span>
      <span className={`rounded-md px-2 py-1 text-xs font-medium ${toneClass}`}>{value}</span>
    </div>
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

function MobileNav({ icon, label, active, onClick }: { icon: React.ReactNode; label: string; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`rounded-lg px-4 py-2 text-xs ${active ? "bg-sky-500 text-white" : "text-slate-500"}`}>
      <span className="flex flex-col items-center gap-1">
        {icon}
        {label}
      </span>
    </button>
  );
}
