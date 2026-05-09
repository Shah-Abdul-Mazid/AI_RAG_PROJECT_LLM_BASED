"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Upload, 
  FileText, 
  Search, 
  Activity, 
  ShieldCheck, 
  Database, 
  Globe,
  Plus,
  Trash2,
  ChevronRight,
  Loader2,
  MessageSquare,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

// Dynamically set API_BASE based on where the frontend is running
const API_BASE = typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
  ? `http://${window.location.hostname}:8000` 
  : "http://localhost:8000";

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  logs?: string[];
}

export default function Dashboard() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Welcome to the Enterprise AI Intelligence Assistant. How can I help you analyze your documents today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [files, setFiles] = useState<string[]>([]);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'docs' | 'analytics'>('chat');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/v1/chat`, { message: input });
      const botMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        logs: response.data.agent_logs
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error connecting to the AI engine. Please ensure the backend is running.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    try {
      await axios.post(`${API_BASE}/api/v1/upload`, formData);
      setFiles(prev => [...prev, file.name]);
    } catch (error) {
      alert("Failed to upload file");
    } finally {
      setIsUploading(false);
    }
  };

  const handleUrlScrape = async () => {
    if (!scrapeUrl.trim()) return;
    setIsScraping(true);
    try {
      await axios.post(`${API_BASE}/api/v1/scrape`, { url: scrapeUrl });
      setFiles(prev => [...prev, scrapeUrl]);
      setScrapeUrl('');
      alert("Website successfully scraped and indexed!");
    } catch (error) {
      alert("Failed to scrape website");
    } finally {
      setIsScraping(false);
    }
  };

  const handleFeedback = async (query: string, answer: string, isPositive: boolean) => {
    try {
      await axios.post(`${API_BASE}/api/v1/feedback`, { query, answer, is_positive: isPositive });
      alert("Thank you for your feedback!");
    } catch (error) {
      console.error("Feedback error", error);
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0a0a] text-white font-sans overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-white/10 flex flex-col glass">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Activity size={18} className="text-white" />
            </div>
            <h1 className="text-xl font-bold gradient-text">Nexus Intelligence</h1>
          </div>

          <nav className="space-y-1">
            <NavItem 
              icon={<MessageSquare size={18} />} 
              label="AI Assistant" 
              active={activeTab === 'chat'} 
              onClick={() => setActiveTab('chat')} 
            />
            <NavItem 
              icon={<Database size={18} />} 
              label="Knowledge Base" 
              active={activeTab === 'docs'} 
              onClick={() => setActiveTab('docs')} 
            />
            <NavItem 
              icon={<ShieldCheck size={18} />} 
              label="Compliance" 
              active={activeTab === 'analytics'} 
              onClick={() => setActiveTab('analytics')} 
            />
          </nav>
        </div>

        <div className="mt-auto p-6">
          <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
            <h3 className="text-xs font-semibold text-blue-400 mb-1">PRO PLAN</h3>
            <p className="text-[10px] text-gray-400">Enterprise features enabled</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-white/10 flex items-center justify-between px-8 glass">
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span>Systems Status: </span>
            <span className="flex items-center gap-1.5 text-green-400">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              Operational
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-white/5 rounded-full transition-colors">
              <Globe size={20} className="text-gray-400" />
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 border border-white/20"></div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          {activeTab === 'chat' && (
            <div className="max-w-4xl mx-auto flex flex-col h-full">
              <div className="flex-1 space-y-6 mb-8">
                {messages.map((msg, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] rounded-2xl p-4 ${
                      msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-none' 
                      : 'bg-white/5 border border-white/10 text-gray-200 rounded-tl-none'
                    }`}>
                      <p className="text-sm leading-relaxed">{msg.content}</p>
                      
                      {msg.logs && (
                        <div className="mt-3 pt-3 border-t border-white/5 flex flex-wrap gap-2">
                          {msg.logs.map((log, i) => (
                            <span key={i} className="text-[10px] px-2 py-0.5 bg-white/5 rounded text-gray-400 flex items-center gap-1">
                              <Activity size={10} className="text-blue-400" /> {log}
                            </span>
                          ))}
                        </div>
                      )}

                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] text-gray-500">Sources:</span>
                            {msg.sources.map((src, i) => (
                              <span key={i} className="text-[10px] text-blue-400 hover:underline cursor-pointer flex items-center gap-1">
                                <FileText size={10} /> {src}
                              </span>
                            ))}
                          </div>
                          {msg.role === 'assistant' && idx > 0 && (
                            <div className="flex items-center gap-2">
                              <button 
                                onClick={() => handleFeedback(messages[idx-1].content, msg.content, true)}
                                className="p-1 hover:bg-white/10 rounded transition-colors text-gray-500 hover:text-green-400"
                              >
                                <ThumbsUp size={12} />
                              </button>
                              <button 
                                onClick={() => handleFeedback(messages[idx-1].content, msg.content, false)}
                                className="p-1 hover:bg-white/10 rounded transition-colors text-gray-500 hover:text-red-400"
                              >
                                <ThumbsDown size={12} />
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
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-4 rounded-tl-none flex items-center gap-3">
                      <Loader2 size={16} className="animate-spin text-blue-400" />
                      <span className="text-xs text-gray-400">Agent thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input Box */}
              <div className="sticky bottom-0 bg-[#0a0a0a] pb-4 pt-2">
                <div className="relative glass p-1 rounded-2xl flex items-center gap-2 border border-white/10">
                  <input 
                    type="text" 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask anything about your documents..."
                    className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-sm text-gray-200 placeholder:text-gray-500"
                  />
                  <button 
                    onClick={handleSendMessage}
                    disabled={isLoading}
                    className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 p-2.5 rounded-xl transition-all shadow-lg shadow-blue-600/20"
                  >
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'docs' && (
            <div className="max-w-5xl mx-auto">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-bold">Knowledge Base</h2>
                  <p className="text-gray-400 text-sm mt-1">Manage documents and websites ingested into the RAG system.</p>
                </div>
                <div className="flex flex-col items-end gap-3">
                  <div className="flex items-center gap-2">
                    <input 
                      type="text" 
                      value={scrapeUrl}
                      onChange={(e) => setScrapeUrl(e.target.value)}
                      placeholder="https://example.com"
                      className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm text-gray-200 outline-none w-64"
                    />
                    <button 
                      onClick={handleUrlScrape}
                      disabled={isScraping}
                      className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2"
                    >
                      {isScraping ? <Loader2 size={16} className="animate-spin" /> : <Globe size={16} />}
                      Scrape Link
                    </button>
                  </div>
                  <label className="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-2 rounded-xl cursor-pointer transition-all">
                    {isUploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
                    <span>Upload Document</span>
                    <input type="file" accept=".pdf,.txt,.csv,.xlsx,.docx" className="hidden" onChange={handleFileUpload} />
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <UploadCard 
                  title="PDF Documents" 
                  icon={<FileText className="text-red-400" />} 
                  count={files.filter(f => f.endsWith('.pdf')).length} 
                />
                <UploadCard 
                  title="CSV/Excel Data" 
                  icon={<Database className="text-green-400" />} 
                  count={files.filter(f => f.endsWith('.csv') || f.endsWith('.xlsx')).length} 
                />
                <UploadCard 
                  title="Web Sources" 
                  icon={<Globe className="text-blue-400" />} 
                  count={files.filter(f => f.startsWith('http')).length} 
                />
              </div>

              <div className="mt-12 glass rounded-2xl border border-white/10 overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-white/5 text-gray-400 text-xs uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-4 font-semibold">Document Name</th>
                      <th className="px-6 py-4 font-semibold">Type</th>
                      <th className="px-6 py-4 font-semibold">Status</th>
                      <th className="px-6 py-4 font-semibold">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {files.map((file, i) => (
                      <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                        <td className="px-6 py-4 text-sm font-medium">{file}</td>
                        <td className="px-6 py-4 text-xs text-gray-400">
                          {file.startsWith('http') ? 'WEB' : file.split('.').pop()?.toUpperCase()}
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-green-500/10 text-green-400 text-[10px] font-semibold">
                            <span className="w-1 h-1 rounded-full bg-green-400"></span>
                            Indexed
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <button className="text-gray-500 hover:text-red-400 transition-colors">
                            <Trash2 size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                    {files.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-6 py-12 text-center text-gray-500 italic text-sm">
                          No documents uploaded yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }: { icon: any, label: string, active?: boolean, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
        active 
        ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' 
        : 'text-gray-400 hover:text-white hover:bg-white/5'
      }`}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
      {active && <ChevronRight size={14} className="ml-auto opacity-50" />}
    </button>
  );
}

function UploadCard({ title, icon, count }: { title: string, icon: any, count: number }) {
  return (
    <div className="glass p-6 rounded-2xl border border-white/10 hover:border-white/20 transition-all group">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 rounded-xl bg-white/5 group-hover:bg-white/10 transition-colors">
          {icon}
        </div>
        <span className="text-2xl font-bold">{count}</span>
      </div>
      <h3 className="font-semibold text-gray-200">{title}</h3>
      <p className="text-xs text-gray-500 mt-1">Processed and vector-indexed.</p>
    </div>
  );
}
