"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, Bot, FileText, CheckCircle2, Sparkles, Zap,
  Target, Download, FileDown, FileCheck, ScrollText, RefreshCw, AlertCircle, Send
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { analyzeJob, refineDocument, generateFile } from "@/lib/api";

const STAGED_MESSAGES = [
  "Booting AI agents...",
  "Parsing your resume structure...",
  "Did you know? Recruiters spend only 6 seconds on a resume.",
  "Decoding job requirements...",
  "Mapping skill alignment...",
  "Tip: Use action verbs like 'Spearheaded' or 'Architected'.",
  "Rewriting resume bullets...",
  "Optimizing for ATS keywords...",
  "Tip: Quantify achievements with percentages and numbers.",
  "Crafting your personalized cover letter...",
  "Finalizing your career package...",
  "Almost there! Generating high-quality PDF...",
];

type ResultTab = "resume" | "cover_letter";

interface Result {
  cover_letter: string;
  optimized_resume: string;
  pdf_url: string;
  doc_url: string;
  candidate_name?: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [activeTab, setActiveTab] = useState<ResultTab>("resume");
  const [error, setError] = useState<string | null>(null);
  const [refineText, setRefineText] = useState("");
  const [refining, setRefining] = useState(false);
  const [refineError, setRefineError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isDownloading, setIsDownloading] = useState<"pdf" | "docx" | null>(null);

  // Simulated Progress
  useEffect(() => {
    if (loading) {
      let currentProgress = 0;
      const interval = setInterval(() => {
        currentProgress += Math.random() * 8 + 2;
        if (currentProgress > 95) currentProgress = 95;
        setProgress(Math.floor(currentProgress));
        const msgIndex = Math.min(
          Math.floor((currentProgress / 100) * STAGED_MESSAGES.length),
          STAGED_MESSAGES.length - 1
        );
        setLoadingMessage(STAGED_MESSAGES[msgIndex]);
      }, 1200);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !jobDescription) return;
    setLoading(true);
    setResult(null);
    setError(null);
    setProgress(0);
    setActiveTab("resume");

    try {
      const data = await analyzeJob(file, jobDescription);
      setProgress(100);
      setTimeout(() => {
        setResult(data);
        setLoading(false);
      }, 600);
    } catch (err: any) {
      setError(err.message || "Analysis failed. Please check the backend is running.");
      setLoading(false);
    }
  };

  const handleRefine = async () => {
    if (!result || !refineText.trim()) return;
    setRefining(true);
    setRefineError(null);
    try {
      const data = await refineDocument({
        doc_type: activeTab,
        current_content: activeTab === "resume" ? result.optimized_resume : result.cover_letter,
        instructions: refineText,
        candidate_name: result.candidate_name || "Candidate",
        contact_info: "",
      });
      setResult((prev) => prev ? {
        ...prev,
        ...(activeTab === "resume"
          ? { optimized_resume: data.refined_content, pdf_url: data.pdf_url || prev.pdf_url, doc_url: data.doc_url || prev.doc_url }
          : { cover_letter: data.refined_content }),
      } : prev);
      setRefineText("");
    } catch (err: any) {
      setRefineError(err.message || "Refinement failed");
    } finally {
      setRefining(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setFile(null);
    setJobDescription("");
    setProgress(0);
  };

  const handleDownload = async (format: "pdf" | "docx") => {
    if (!result) return;
    setIsDownloading(format);
    try {
      // 1. Generate the file on-demand with latest content
      const content = activeTab === "resume" ? result.optimized_resume : result.cover_letter;
      const genData = await generateFile({
        content,
        candidate_name: result.candidate_name || "Candidate",
        contact_info: "",
        format,
      });

      // 2. Trigger download
      const url = `${BACKEND}/static/${genData.file_url}`;
      const filename = `${result.candidate_name || "Application"}_${activeTab}.${format}`;
      
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error("Download failed", err);
      setError("Failed to generate file. Please try again.");
    } finally {
      setIsDownloading(null);
    }
  };

  const BACKEND = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  return (
    <main className="min-h-screen bg-[#020617] text-slate-200 selection:bg-blue-500/30 overflow-x-hidden relative">

      {/* Ambient Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[70%] h-[70%] bg-blue-600/8 rounded-full blur-[140px]" />
        <div className="absolute -bottom-[20%] -right-[10%] w-[60%] h-[60%] bg-indigo-600/8 rounded-full blur-[140px]" />
        <div className="absolute top-[40%] left-[40%] w-[30%] h-[30%] bg-violet-600/5 rounded-full blur-[100px]" />
      </div>

      {/* Navbar */}
      <nav className="relative z-10 border-b border-slate-800/50 backdrop-blur-md bg-slate-950/60">
        <div className="max-w-7xl mx-auto px-6 h-18 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-1 bg-slate-900/50 border border-slate-700 rounded-xl shadow-lg shadow-blue-500/10 overflow-hidden">
              <img src="/logo.png" alt="JobPilot Logo" className="w-8 h-8 object-cover rounded-lg" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              JobPilot <span className="text-blue-400 font-black">AI</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="bg-slate-800/60 text-emerald-400 px-3 py-1.5 rounded-full text-xs font-bold border border-emerald-500/20 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
              Local AI · Ollama
            </span>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-6 pb-12">

        {/* Hero */}
        <div className="text-center mb-8">
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold px-3 py-1.5 rounded-full mb-4 tracking-wider uppercase">
              <Sparkles className="w-3 h-3" /> Multi-Agent Resume Intelligence
            </span>
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight mb-2 leading-tight">
              Land the Interview.<br />
              <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                Every Single Time.
              </span>
            </h1>
            <p className="text-slate-400 text-base max-w-xl mx-auto">
              Local agents rewrite your resume and craft a personalized cover letter — in seconds.
            </p>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

          {/* ── Left Panel: Input Form ── */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-4 space-y-6"
          >
            <form onSubmit={handleSubmit} className="bg-slate-900/50 p-7 rounded-3xl border border-slate-800 backdrop-blur-xl shadow-2xl space-y-7">

              {/* Step 1 — Resume Upload */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-black flex items-center justify-center">1</span>
                  <span className="text-sm font-bold text-slate-300 uppercase tracking-wider">Your Resume</span>
                </div>
                <div className="relative group">
                  <input
                    type="file"
                    accept=".pdf"
                    id="resume-upload"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                  <div className={`h-28 flex flex-col items-center justify-center border-2 border-dashed rounded-2xl transition-all duration-300
                    ${file
                      ? "border-blue-500/60 bg-blue-500/5 shadow-inner shadow-blue-500/5"
                      : "border-slate-700 group-hover:border-blue-500/40 group-hover:bg-slate-800/30"
                    }`}>
                    {file ? (
                      <div className="text-center px-4">
                        <CheckCircle2 className="w-7 h-7 text-blue-400 mx-auto mb-1" />
                        <span className="font-semibold text-blue-300 text-xs truncate max-w-[180px] block mx-auto">{file.name}</span>
                      </div>
                    ) : (
                      <>
                        <Upload className="w-6 h-6 mb-1 text-slate-500 group-hover:text-blue-400 transition-colors" />
                        <p className="text-slate-400 font-medium text-xs">Drop PDF here</p>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Step 2 — Job Description */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-black flex items-center justify-center">2</span>
                  <span className="text-sm font-bold text-slate-300 uppercase tracking-wider">Job Description</span>
                </div>
                <textarea
                  id="job-description"
                  placeholder="Paste the full job description here..."
                  className="w-full h-40 bg-slate-950/50 border border-slate-800 rounded-2xl p-4 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all resize-none text-slate-300 placeholder-slate-600 text-sm leading-relaxed"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                />
              </div>

              {/* What you'll get */}
              <div className="bg-slate-800/30 rounded-2xl p-4 space-y-2">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">You&apos;ll receive</p>
                {[
                  { icon: FileCheck, label: "ATS-optimized Resume (PDF + DOCX)" },
                  { icon: ScrollText, label: "Personalized Cover Letter" },
                ].map(({ icon: Icon, label }) => (
                  <div key={label} className="flex items-center gap-2.5 text-slate-400 text-sm">
                    <Icon className="w-4 h-4 text-blue-400 flex-shrink-0" />
                    <span>{label}</span>
                  </div>
                ))}
              </div>

              {/* Submit */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                id="generate-btn"
                disabled={loading || !file || !jobDescription}
                className="w-full relative overflow-hidden bg-gradient-to-r from-blue-600 to-indigo-600 disabled:from-slate-800 disabled:to-slate-700 disabled:opacity-50 text-white font-bold py-4 rounded-2xl shadow-xl shadow-blue-500/10 transition-all"
              >
                <span className="relative flex items-center justify-center gap-2 text-base">
                  {loading ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Running Agents...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate My Application
                    </>
                  )}
                </span>
              </motion.button>

              {result && (
                <button type="button" onClick={handleReset} className="w-full flex items-center justify-center gap-2 text-slate-500 hover:text-slate-300 text-sm transition-colors py-1">
                  <RefreshCw className="w-3.5 h-3.5" /> Start over
                </button>
              )}
            </form>
          </motion.div>

          {/* ── Right Panel: Results ── */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="lg:col-span-8 min-h-[600px] relative"
          >
            <AnimatePresence mode="wait">

              {/* Loading State */}
              {loading && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-full min-h-[600px] flex flex-col items-center justify-center bg-slate-900/30 rounded-3xl border border-slate-800/50 p-12 text-center"
                >
                  <div className="relative w-44 h-44 mb-10">
                    <svg className="w-full h-full rotate-[-90deg]">
                      <circle cx="88" cy="88" r="80" stroke="currentColor" strokeWidth="7" fill="transparent" className="text-slate-800" />
                      <motion.circle
                        cx="88" cy="88" r="80"
                        stroke="url(#grad)" strokeWidth="7" fill="transparent"
                        strokeDasharray={502}
                        initial={{ strokeDashoffset: 502 }}
                        animate={{ strokeDashoffset: 502 - (502 * progress) / 100 }}
                        strokeLinecap="round"
                        transition={{ duration: 0.4 }}
                      />
                      <defs>
                        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#3b82f6" />
                          <stop offset="100%" stopColor="#818cf8" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center text-4xl font-black text-white">
                      {progress}%
                    </div>
                  </div>
                  <motion.p
                    key={loadingMessage}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xl font-semibold text-blue-300 mb-3"
                  >
                    {loadingMessage}
                  </motion.p>
                  <p className="text-slate-500 text-sm">This takes 1-3 minutes. Your AI agents are working hard.</p>
                </motion.div>
              )}

              {/* Error State */}
              {!loading && error && (
                <motion.div
                  key="error"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="h-full min-h-[400px] flex flex-col items-center justify-center bg-red-900/10 rounded-3xl border border-red-500/20 p-12 text-center"
                >
                  <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
                  <h3 className="text-lg font-bold text-red-300 mb-2">Something went wrong</h3>
                  <p className="text-slate-400 text-sm max-w-sm">{error}</p>
                  <button onClick={handleReset} className="mt-6 flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-300 px-5 py-2.5 rounded-xl text-sm font-medium transition-colors">
                    <RefreshCw className="w-4 h-4" /> Try Again
                  </button>
                </motion.div>
              )}

              {/* Result State */}
              {!loading && result && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-5"
                >
                  {/* Downloads Card */}
                  <div className="bg-gradient-to-br from-blue-600/15 to-indigo-600/15 rounded-3xl border border-blue-500/25 p-6 shadow-xl">
                    <div className="flex items-center justify-between mb-5">
                      <div className="flex items-center gap-2.5">
                        <Zap className="text-yellow-400 w-5 h-5" />
                        <h2 className="text-lg font-bold text-white">
                          {result.candidate_name
                            ? `${result.candidate_name}'s Application Pack`
                            : "Application Pack Ready"}
                        </h2>
                      </div>
                      <span className="text-xs font-bold text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-3 py-1 rounded-full">
                        Ready to send
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => handleDownload("pdf")}
                        disabled={isDownloading !== null}
                        className="flex items-center justify-center gap-2.5 bg-white text-slate-900 font-bold py-3.5 rounded-2xl hover:bg-blue-50 active:scale-95 transition-all text-sm shadow-md disabled:opacity-50"
                      >
                        {isDownloading === "pdf" ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <FileDown className="w-4 h-4" />
                        )}
                        Download PDF
                      </button>
                      <button
                        onClick={() => handleDownload("docx")}
                        disabled={isDownloading !== null}
                        className="flex items-center justify-center gap-2.5 bg-slate-800 border border-slate-700 text-white font-bold py-3.5 rounded-2xl hover:bg-slate-700 active:scale-95 transition-all text-sm disabled:opacity-50"
                      >
                        {isDownloading === "docx" ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Download className="w-4 h-4" />
                        )}
                        Download DOCX
                      </button>
                    </div>
                  </div>

                  {/* Tabbed Content */}
                  <div className="bg-slate-900/50 rounded-3xl border border-slate-800 overflow-hidden shadow-xl">

                    {/* Tab Bar */}
                    <div className="flex border-b border-slate-800 bg-slate-900/80 items-center justify-between pr-4">
                      <div className="flex flex-1">
                        {([
                          { id: "resume",       label: "Optimized Resume",   icon: FileText },
                          { id: "cover_letter", label: "Cover Letter",       icon: ScrollText },
                        ] as { id: ResultTab; label: string; icon: any }[]).map(({ id, label, icon: Icon }) => (
                          <button
                            key={id}
                            id={`tab-${id}`}
                            onClick={() => setActiveTab(id)}
                            className={`flex-1 flex items-center justify-center gap-2 py-4 text-sm font-semibold transition-all
                              ${activeTab === id
                                ? "text-blue-400 border-b-2 border-blue-500 bg-blue-500/5"
                                : "text-slate-500 hover:text-slate-300"
                              }`}
                          >
                            <Icon className="w-4 h-4" />
                            {label}
                          </button>
                        ))}
                      </div>
                      <button
                        onClick={() => setIsEditing(!isEditing)}
                        className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold transition-all border
                          ${isEditing 
                            ? "bg-blue-500/20 text-blue-400 border-blue-500/30" 
                            : "bg-slate-800/50 text-slate-400 border-slate-700 hover:text-slate-200"
                          }`}
                      >
                        {isEditing ? "Viewing Mode" : "Manual Edit"}
                      </button>
                    </div>

                    {/* Tab Content */}
                    <div className="p-8 overflow-y-auto max-h-[500px] custom-scrollbar bg-slate-950/20">
                      <AnimatePresence mode="wait">
                        {isEditing ? (
                          <motion.div
                            key="editing"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="h-full"
                          >
                            <textarea
                              className="w-full h-[450px] bg-transparent border-none outline-none text-slate-300 font-mono text-sm leading-relaxed resize-none custom-scrollbar"
                              value={activeTab === "resume" ? result.optimized_resume : result.cover_letter}
                              onChange={(e) => {
                                const newVal = e.target.value;
                                setResult(prev => prev ? {
                                  ...prev,
                                  [activeTab === "resume" ? "optimized_resume" : "cover_letter"]: newVal
                                } : prev);
                              }}
                            />
                          </motion.div>
                        ) : (
                          activeTab === "resume" ? (
                            <motion.div
                              key="resume-tab"
                              initial={{ opacity: 0, x: -8 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: 8 }}
                              className="prose prose-invert prose-sm prose-blue max-w-none
                                prose-headings:text-blue-300 prose-headings:font-bold prose-headings:tracking-wide
                                prose-h2:text-base prose-h2:uppercase prose-h2:border-b prose-h2:border-slate-700 prose-h2:pb-1
                                prose-strong:text-slate-200 prose-li:text-slate-300 prose-p:text-slate-300"
                            >
                              <ReactMarkdown>{result.optimized_resume || "_No resume content returned._"}</ReactMarkdown>
                            </motion.div>
                          ) : (
                            <motion.div
                              key="letter-tab"
                              initial={{ opacity: 0, x: 8 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: -8 }}
                              className="prose prose-invert prose-sm prose-blue max-w-none
                                prose-headings:text-white prose-p:text-slate-300 prose-p:leading-relaxed
                                prose-strong:text-slate-200"
                            >
                              <ReactMarkdown>{result.cover_letter || "_No cover letter returned._"}</ReactMarkdown>
                            </motion.div>
                          )
                        )}
                      </AnimatePresence>
                    </div>

                    {/* Refine UI Section */}
                    <div className="p-6 bg-slate-950/50 border-t border-slate-800">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="p-1.5 bg-blue-500/10 rounded-lg">
                          <Bot className="w-4 h-4 text-blue-400" />
                        </div>
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Refine with AI</span>
                      </div>
                      
                      <div className="relative group">
                        <textarea
                          placeholder={`E.g. "Make the tone more formal" or "Highlight my Python experience more"`}
                          className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-4 pr-16 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all resize-none text-sm text-slate-300 placeholder-slate-600 min-h-[80px]"
                          value={refineText}
                          onChange={(e) => setRefineText(e.target.value)}
                          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleRefine())}
                        />
                        <button
                          onClick={handleRefine}
                          disabled={refining || !refineText.trim()}
                          className="absolute right-3 bottom-3 p-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white rounded-xl transition-all shadow-lg shadow-blue-600/20 active:scale-95"
                        >
                          {refining ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                          ) : (
                            <Send className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                      {refineError && (
                        <p className="text-xs text-red-400 mt-2 flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" /> {refineError}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Empty State */}
              {!loading && !result && !error && (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="min-h-[600px] flex flex-col items-center justify-center bg-slate-900/10 rounded-3xl border-2 border-dashed border-slate-800 p-12 text-center"
                >
                  <div className="w-20 h-20 rounded-full bg-slate-800/50 flex items-center justify-center mb-6">
                    <Bot className="w-10 h-10 text-slate-600" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-300 mb-3">Agents Standing By</h3>
                  <p className="text-slate-500 max-w-xs leading-relaxed text-sm">
                    Upload your resume PDF and paste a job description to get your tailored resume + cover letter.
                  </p>
                  <div className="mt-8 grid grid-cols-3 gap-4 text-center">
                    {[
                      { icon: FileText, label: "Parse Resume" },
                      { icon: Target,   label: "Analyze JD"  },
                      { icon: Sparkles, label: "Generate"    },
                    ].map(({ icon: Icon, label }) => (
                      <div key={label} className="flex flex-col items-center gap-2 text-slate-600">
                        <div className="w-10 h-10 rounded-xl bg-slate-800/50 flex items-center justify-center">
                          <Icon className="w-5 h-5" />
                        </div>
                        <span className="text-xs font-medium">{label}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </main>
  );
}
