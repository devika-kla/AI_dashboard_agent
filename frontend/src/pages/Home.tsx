import { useState, KeyboardEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Clock,
  LayoutDashboard,
  TerminalSquare,
  Play,
  Sparkles,
  X,
  AlertCircle,
} from "lucide-react";

interface DashboardRequest {
  kpis: string[];
  verbose?: boolean;
  session_id?: string;
}

interface DashboardResponse {
  html: string;
  panel_count: number;
  execution_time_ms: number;
  session_id?: string | null;
}

async function generateDashboardApi(req: DashboardRequest): Promise<DashboardResponse> {
  const res = await fetch("/api/dashboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export default function Home() {
  const [kpis, setKpis] = useState<string[]>(["revenue", "top customers", "sales by country"]);
  const [kpiInput, setKpiInput] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [verbose, setVerbose] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const mutation = useMutation<DashboardResponse, Error, DashboardRequest>({
    mutationFn: generateDashboardApi,
    onSuccess: (data) => {
      showToast(`Generated ${data.panel_count} panels in ${data.execution_time_ms}ms`, "success");
    },
    onError: (err) => {
      showToast(err.message || "Generation failed", "error");
    },
  });

  const showToast = (message: string, type: "success" | "error") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleAddKpi = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && kpiInput.trim()) {
      e.preventDefault();
      if (!kpis.includes(kpiInput.trim())) {
        setKpis([...kpis, kpiInput.trim()]);
      }
      setKpiInput("");
    }
  };

  const removeKpi = (kpiToRemove: string) => {
    setKpis(kpis.filter((k) => k !== kpiToRemove));
  };

  const handleGenerate = () => {
    if (kpis.length === 0) {
      showToast("Please add at least one KPI keyword.", "error");
      return;
    }
    mutation.mutate({ kpis, verbose, session_id: sessionId || undefined });
  };

  const lastResult = mutation.data;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Header */}
      <header className="border-b border-[#334155] bg-[#1e293b]/60 backdrop-blur sticky top-0 z-50">
        <div className="max-w-screen-xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/40">
              <Activity className="w-4 h-4 text-primary" />
            </div>
            <div>
              <h1 className="font-bold text-base leading-tight tracking-tight">
                Chinook<span className="text-primary">Insights</span>
              </h1>
              <p className="text-[10px] text-[#64748b] uppercase tracking-widest font-mono">
                Data Workbench
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono text-[#64748b]">
            {lastResult && (
              <div className="flex items-center gap-2 bg-[#1e293b] px-3 py-1.5 rounded-md border border-[#334155]">
                <Clock className="w-3 h-3 text-primary" />
                <span>Last run: {lastResult.execution_time_ms}ms</span>
              </div>
            )}
            {(lastResult?.session_id || sessionId) && (
              <div className="flex items-center gap-2 bg-[#1e293b] px-3 py-1.5 rounded-md border border-[#334155]">
                <TerminalSquare className="w-3 h-3 text-primary" />
                <span>Session: {lastResult?.session_id || sessionId}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-screen-xl mx-auto w-full px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left panel */}
        <aside className="lg:col-span-4 xl:col-span-3">
          <div className="bg-[#1e293b] border border-[#334155] rounded-xl shadow-xl p-5 space-y-5">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-4 h-4 text-primary" />
                <h2 className="font-semibold text-sm">Query Configuration</h2>
              </div>
              <p className="text-xs text-[#64748b]">Instruct the AI agent to extract insights.</p>
            </div>

            {/* KPI input */}
            <div className="space-y-2">
              <label className="text-[10px] uppercase tracking-wider text-[#64748b] font-medium">
                KPI Keywords
              </label>
              <div className="flex flex-wrap gap-1.5 min-h-[32px]">
                <AnimatePresence>
                  {kpis.map((kpi) => (
                    <motion.span
                      key={kpi}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.7 }}
                      transition={{ duration: 0.12 }}
                      className="inline-flex items-center gap-1 bg-primary/10 text-primary border border-primary/25 text-xs px-2 py-1 rounded-full"
                      data-testid={`badge-kpi-${kpi}`}
                    >
                      {kpi}
                      <button
                        onClick={() => removeKpi(kpi)}
                        className="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
                        data-testid={`button-remove-kpi-${kpi}`}
                      >
                        <X className="w-2.5 h-2.5" />
                      </button>
                    </motion.span>
                  ))}
                </AnimatePresence>
              </div>
              <input
                type="text"
                placeholder="Type KPI and press Enter..."
                value={kpiInput}
                onChange={(e) => setKpiInput(e.target.value)}
                onKeyDown={handleAddKpi}
                className="w-full bg-[#0f172a] border border-[#334155] rounded-lg px-3 py-2 text-sm text-foreground placeholder:text-[#475569] focus:outline-none focus:ring-1 focus:ring-primary/50 focus:border-primary/50 transition"
                data-testid="input-kpi"
              />
            </div>

            {/* Session ID */}
            <div className="space-y-2">
              <label className="text-[10px] uppercase tracking-wider text-[#64748b] font-medium">
                Session ID (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. session-123"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                className="w-full bg-[#0f172a] border border-[#334155] rounded-lg px-3 py-2 text-sm font-mono text-foreground placeholder:text-[#475569] focus:outline-none focus:ring-1 focus:ring-primary/50 focus:border-primary/50 transition"
                data-testid="input-session-id"
              />
            </div>

            {/* Verbose toggle */}
            <div className="flex items-center justify-between p-3 rounded-lg border border-[#334155] bg-[#0f172a]/50">
              <div>
                <p className="text-sm font-medium">Verbose Logging</p>
                <p className="text-xs text-[#64748b]">Enable detailed agent reasoning</p>
              </div>
              <button
                role="switch"
                aria-checked={verbose}
                onClick={() => setVerbose(!verbose)}
                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none ${
                  verbose ? "bg-primary" : "bg-[#334155]"
                }`}
                data-testid="switch-verbose"
              >
                <span
                  className={`pointer-events-none inline-block h-4 w-4 rounded-full bg-white shadow-lg transform transition-transform duration-200 ${
                    verbose ? "translate-x-4" : "translate-x-0"
                  }`}
                />
              </button>
            </div>

            {/* Generate button */}
            <button
              onClick={handleGenerate}
              disabled={mutation.isPending}
              className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold text-sm px-4 py-2.5 rounded-lg shadow-lg shadow-primary/20 transition-all active:scale-[0.98]"
              data-testid="button-generate"
            >
              {mutation.isPending ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Analyzing Database...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Generate Dashboard
                </>
              )}
            </button>
          </div>
        </aside>

        {/* Right panel — dashboard output */}
        <section className="lg:col-span-8 xl:col-span-9">
          <div className="bg-[#1e293b]/40 border border-[#334155] rounded-xl shadow-2xl min-h-[600px] flex flex-col overflow-hidden">
            {mutation.isPending ? (
              <div className="flex-1 flex flex-col items-center justify-center p-12 text-center" data-testid="status-generating">
                <div className="relative w-16 h-16 mb-6">
                  <div className="absolute inset-0 rounded-full border-4 border-primary/20 animate-ping" style={{ animationDuration: "2s" }} />
                  <div className="absolute inset-2 rounded-full bg-primary/20 animate-pulse flex items-center justify-center">
                    <Activity className="w-6 h-6 text-primary" />
                  </div>
                </div>
                <h3 className="text-lg font-medium mb-2">AI Agent is Analyzing</h3>
                <p className="text-sm text-[#64748b] max-w-sm">
                  Querying the Chinook database, computing metrics, and assembling insight panels...
                </p>
              </div>
            ) : lastResult ? (
              <div className="flex flex-col h-full" data-testid="content-dashboard">
                <div className="flex-1 p-2">
                  <iframe
                    srcDoc={lastResult.html}
                    className="w-full min-h-[600px] h-full border-none rounded-md"
                    title="Generated Dashboard"
                    sandbox="allow-scripts allow-same-origin"
                    data-testid="iframe-dashboard"
                  />
                </div>
                <div className="bg-[#0f172a]/60 border-t border-[#334155] px-6 py-2.5 flex items-center justify-between text-xs font-mono text-[#64748b]">
                  <div className="flex items-center gap-5">
                    <span className="flex items-center gap-1.5">
                      <LayoutDashboard className="w-3.5 h-3.5" /> Panels: {lastResult.panel_count}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" /> Time: {lastResult.execution_time_ms}ms
                    </span>
                  </div>
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]" />
                    Dashboard Ready
                  </span>
                </div>
              </div>
            ) : mutation.isError ? (
              <div className="flex-1 flex flex-col items-center justify-center p-12 text-center" data-testid="status-error">
                <div className="w-14 h-14 rounded-2xl bg-red-500/10 flex items-center justify-center border border-red-500/20 mb-5">
                  <AlertCircle className="w-7 h-7 text-red-400" />
                </div>
                <h3 className="text-lg font-medium mb-2 text-red-400">Generation Failed</h3>
                <p className="text-sm text-[#64748b] max-w-sm">{mutation.error?.message}</p>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-12 text-center opacity-60" data-testid="status-empty">
                <div className="w-14 h-14 rounded-2xl bg-[#293548] flex items-center justify-center border border-[#334155] mb-5 rotate-3">
                  <LayoutDashboard className="w-7 h-7 text-[#475569]" />
                </div>
                <h3 className="text-lg font-medium mb-2">Awaiting Instructions</h3>
                <p className="text-sm text-[#64748b] max-w-sm">
                  Configure your KPIs in the panel and click Generate Dashboard to run the AI agent against the Chinook music store database.
                </p>
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className={`fixed bottom-6 right-6 flex items-center gap-3 px-4 py-3 rounded-lg border shadow-xl text-sm font-medium z-50 ${
              toast.type === "success"
                ? "bg-emerald-900/90 border-emerald-700/50 text-emerald-200"
                : "bg-red-900/90 border-red-700/50 text-red-200"
            }`}
          >
            {toast.type === "error" && <AlertCircle className="w-4 h-4 shrink-0" />}
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
