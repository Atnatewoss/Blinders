"use client";

import { useState, useRef, useEffect } from "react";
import { 
  Plus, 
  ArrowRight, 
  Search, 
  Command, 
  Shield, 
  Cpu, 
  Activity, 
  Lock, 
  ChevronRight,
  User,
  MoreHorizontal,
  RefreshCw,
  Award,
  Stethoscope,
  BarChart3,
  LayoutDashboard,
  Users,
  ShoppingBag,
  Hash
} from "lucide-react";
import { type VerifyResponse, verifyRequest, type PlayerState, fetchState } from "../lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  result?: VerifyResponse;
};

const ROLES = [
  { id: "atnatewos", name: "Atnatewos", title: "Manager", description: "Top-tier authority. Handles the budget and player transfers." },
  { id: "coach_joe", name: "Coach Joe", title: "Coach", description: "Tactical authority. Handles team selection and captaincy." },
  { id: "dr_smith", name: "Dr. Smith", title: "Staff", description: "Medical authority. Can view risk reports and mark injuries." },
  { id: "guest_user", name: "Guest User", title: "Guest", description: "Read-only access to team data." }
];

const SUGGESTIONS = [
  "Trade Saka for Palmer.",
  "Make Haaland the captain.",
  "Mark Saka as injured.",
  "View the security risk report."
];

export default function Home() {
  const [hasMounted, setHasMounted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [activeRole, setActiveRole] = useState(ROLES[0]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"chat" | "squad" | "market">("chat");
  const [squad, setSquad] = useState<PlayerState[]>([]);
  const [market, setMarket] = useState<PlayerState[]>([]);
  const [bank, setBank] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setHasMounted(true);
    loadState();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, activeTab]);

  if (!hasMounted) return <div className="min-h-screen bg-black" />;

  async function loadState() {
    try {
      const data = await fetchState();
      setSquad(data.squad);
      setMarket(data.market);
      setBank(data.bank);
    } catch (err) {
      console.error("Failed to load state:", err);
    }
  }

  async function handleSend(text: string) {
    if (!text.trim() || loading) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await verifyRequest(text, activeRole.id);
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.decision.final_decision === "ALLOW" ? "Execution authorized." : "Execution blocked.",
        result: res
      };
      setMessages(prev => [...prev, botMsg]);
      if (res.decision.final_decision === "ALLOW") {
        setTimeout(loadState, 1000);
      }
    } catch (err) {
      setMessages(prev => [...prev, { id: "err", role: "assistant", content: "Engine offline." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-black text-white selection:bg-white selection:text-black subtle-grid flex flex-col font-mono overflow-x-hidden">
      {/* Top Bar */}
      <nav className="h-14 border-b border-[#1a1a1a] flex items-center justify-between px-6 bg-black/80 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            <span className="text-xs font-bold tracking-[0.2em] uppercase hidden sm:inline">Blinders</span>
          </div>
          
          <div className="flex items-center gap-1 bg-[#111] p-1 rounded-md border border-[#1a1a1a]">
            <TabBtn active={activeTab === "chat"} onClick={() => setActiveTab("chat")} icon={<LayoutDashboard className="w-3 h-3" />} label="Core" />
            <TabBtn active={activeTab === "squad"} onClick={() => setActiveTab("squad")} icon={<Users className="w-3 h-3" />} label="Squad" />
            <TabBtn active={activeTab === "market"} onClick={() => setActiveTab("market")} icon={<ShoppingBag className="w-3 h-3" />} label="Market" />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 text-[10px] text-slate-500 mr-4">
            <span className="font-bold text-slate-700">BANK:</span>
            <span className="text-white">£{bank.toFixed(1)}M</span>
          </div>
          
          <div className="flex bg-[#111] border border-[#1a1a1a] rounded-md p-0.5">
            {ROLES.map((role, index) => (
              <div key={role.id} className="relative group/tooltip">
                <button
                  onClick={() => setActiveRole(role)}
                  className={`px-3 py-1 text-[10px] font-bold rounded transition-colors whitespace-nowrap ${
                    activeRole.id === role.id ? "bg-white text-black" : "text-slate-500 hover:text-white"
                  }`}
                >
                  {role.title}
                </button>
                <div className={`absolute top-full mt-2 w-48 p-2 bg-black border border-white/20 rounded shadow-2xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all z-[100] text-center pointer-events-none ${
                  index > 2 ? "right-0" : "left-1/2 -translate-x-1/2"
                }`}>
                  <div className="text-[9px] text-white font-bold tracking-wider leading-relaxed">
                    {role.description}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </nav>

      <main className="flex-1 flex flex-col items-center p-6 md:p-12 overflow-y-auto pb-40" ref={scrollRef}>
        <div className="w-full max-w-2xl space-y-12">
          
          {activeTab === "chat" && (
            <>
              {messages.length === 0 && (
                <div className="py-20 space-y-8 animate-in fade-in duration-1000">
                  <div className="space-y-2">
                    <h1 className="text-4xl font-bold tracking-tighter text-white uppercase italic">Blinders G.1</h1>
                    <p className="text-slate-500 text-sm max-w-sm leading-relaxed font-sans">
                      Neuro-symbolic governance layer. Every intent is matched against the constitutional AtomSpace.
                    </p>
                  </div>
                  <div className="grid gap-2">
                    {SUGGESTIONS.map(s => (
                      <button 
                        key={s} 
                        onClick={() => handleSend(s)}
                        className="flex items-center justify-between p-4 bg-[#050505] border border-[#1a1a1a] hover:border-white/20 transition-all group text-left"
                      >
                        <span className="text-xs text-slate-400 group-hover:text-white">{s}</span>
                        <Plus className="w-3 h-3 text-slate-700 group-hover:text-white" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-12">
                {messages.map((msg) => (
                  <div key={msg.id} className="space-y-6 animate-in slide-in-from-bottom-2 duration-500">
                    <div className="flex items-start gap-4">
                      <div className={`mt-1 w-6 h-6 flex items-center justify-center border ${msg.role === "user" ? "border-slate-800" : "border-white bg-white text-black"}`}>
                        {msg.role === "user" ? <User className="w-3 h-3" /> : <Cpu className="w-3 h-3" />}
                      </div>
                      <div className="space-y-6 flex-1">
                        <div className="text-sm leading-relaxed text-slate-300 font-sans">
                          {msg.content}
                        </div>
                        {msg.result && <DecisionCard res={msg.result} />}
                      </div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex items-center gap-4 text-slate-600 animate-pulse pb-20">
                    <div className="w-6 h-6 border border-slate-900 flex items-center justify-center">
                      <Activity className="w-3 h-3" />
                    </div>
                    <span className="text-[10px] font-bold tracking-[0.3em] uppercase">Reasoning Proof...</span>
                  </div>
                )}
                <div className="h-40" />
              </div>
            </>
          )}

          {activeTab === "squad" && (
            <div className="space-y-8 animate-in fade-in duration-500">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight">Active Squad</h2>
                <div className="flex items-center gap-4">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest border border-slate-800 px-2 py-0.5 rounded">Blinders Elite FC</p>
                  <p className="text-[10px] text-emerald-500 font-bold uppercase tracking-widest border border-emerald-900/30 bg-emerald-500/5 px-2 py-0.5 rounded">{squad.length} / 15 Players</p>
                </div>
              </div>
              <div className="border border-[#1a1a1a] bg-[#050505] overflow-hidden rounded-lg">
                <PlayerTable players={squad} />
              </div>
            </div>
          )}

          {activeTab === "market" && (
            <div className="space-y-8 animate-in fade-in duration-500">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight">Player Market</h2>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest border border-slate-800 px-2 py-0.5 rounded w-fit">Constitutional DB: v1.0</p>
              </div>
              <div className="border border-[#1a1a1a] bg-[#050505] overflow-hidden rounded-lg">
                <PlayerTable players={market} />
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Input */}
      {activeTab === "chat" && (
        <div className="p-6 border-t border-[#1a1a1a] bg-black/80 backdrop-blur-md fixed bottom-0 left-0 right-0 z-40">
          <div className="max-w-2xl mx-auto flex items-center gap-4 bg-[#080808] border border-[#1a1a1a] p-2 focus-within:border-white/50 transition-colors">
            <Command className="w-4 h-4 text-slate-700 ml-2" />
            <input 
              className="flex-1 bg-transparent border-none outline-none text-sm p-2 text-white placeholder:text-slate-800"
              placeholder={`Instruct ${activeRole.name}...`}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSend(input)}
            />
            <button 
              onClick={() => handleSend(input)}
              className="p-2 bg-white text-black hover:bg-slate-200 transition-colors"
            >
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function TabBtn({ active, onClick, icon, label }: any) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-1.5 rounded text-[10px] font-bold uppercase tracking-wider transition-colors ${
        active ? "bg-white text-black" : "text-slate-500 hover:text-white"
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

function PlayerTable({ players }: { players: PlayerState[] }) {
  return (
    <table className="w-full text-left text-xs font-sans">
      <thead className="bg-[#111] border-b border-[#1a1a1a]">
        <tr>
          <th className="p-4 font-bold text-slate-500 uppercase tracking-widest text-[9px] w-12 text-center">#</th>
          <th className="p-4 font-bold text-slate-500 uppercase tracking-widest text-[9px]">Player</th>
          <th className="p-4 font-bold text-slate-500 uppercase tracking-widest text-[9px]">Club</th>
          <th className="p-4 font-bold text-slate-500 uppercase tracking-widest text-[9px]">Pos</th>
          <th className="p-4 font-bold text-slate-500 uppercase tracking-widest text-[9px]">Price</th>
          <th className="p-4 font-bold text-slate-500 uppercase tracking-widest text-[9px]">Status</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-[#1a1a1a]">
        {players.map((p, i) => (
          <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
            <td className="p-4 text-slate-700 font-mono text-[10px] text-center group-hover:text-white transition-colors">{i + 1}</td>
            <td className="p-4 font-bold text-white">{p.name}</td>
            <td className="p-4 text-slate-400">{p.club}</td>
            <td className="p-4 text-slate-500 uppercase tracking-widest text-[10px]">{p.pos}</td>
            <td className="p-4 font-mono text-white">£{p.price.toFixed(1)}M</td>
            <td className="p-4">
              <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest ${
                p.status === "fit" ? "bg-emerald-500/10 text-emerald-500" : "bg-red-500/10 text-red-500"
              }`}>
                {p.status}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function DecisionCard({ res }: { res: VerifyResponse }) {
  const isAllowed = res.decision.final_decision === "ALLOW";

  return (
    <div className={`border p-8 space-y-10 animate-in zoom-in-95 duration-500 bg-[#020202] ${isAllowed ? "border-white/10" : "border-red-900/40"}`}>
      <div className="flex items-center justify-between border-b border-[#1a1a1a] pb-6">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${isAllowed ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"}`} />
          <span className="text-[10px] font-bold tracking-[0.4em] uppercase">{isAllowed ? "Authorized" : "Blocked"}</span>
        </div>
        <div className="flex items-center gap-4 text-[9px] text-slate-600 font-bold uppercase tracking-widest">
          <span>Subject: {res.decision.subject}</span>
          <div className="w-[1px] h-3 bg-[#1a1a1a]" />
          <span>Role: {res.plan.role || "Verified"}</span>
        </div>
      </div>

      <div className="grid gap-10">
        <section className="space-y-4">
          <span className="text-[9px] font-bold text-slate-600 uppercase tracking-[0.2em]">Interpreted Agent Plan</span>
          <div className="grid gap-3">
            {res.plan.actions.map((act, i) => (
              <div key={i} className="flex items-start gap-4 p-4 bg-[#080808] border border-[#1a1a1a]">
                <div className="mt-1">
                  {act.action === "transfer_player" && <RefreshCw className="w-3.5 h-3.5 text-blue-500" />}
                  {act.action === "set_captain" && <Award className="w-3.5 h-3.5 text-amber-500" />}
                  {act.action === "update_player_status" && <Stethoscope className="w-3.5 h-3.5 text-emerald-500" />}
                  {act.action === "view_risk_report" && <BarChart3 className="w-3.5 h-3.5 text-purple-500" />}
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-white leading-relaxed">
                    Plan to <span className="font-bold">{act.action.replace("_", " ")}</span> 
                    {act.player && <span> for <span className="text-white font-bold">{act.player}</span></span>}
                    {act.player_in && <span>: <span className="text-emerald-400 font-bold">{act.player_in}</span> in, <span className="text-red-400 font-bold">{act.player_out}</span> out</span>}
                  </p>
                  <p className="text-[10px] text-slate-500 italic">"Reason: {act.reason}"</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-5">
          <span className="text-[9px] font-bold text-slate-600 uppercase tracking-[0.2em]">Symbolic Verification Trace</span>
          <div className="space-y-6">
            {res.decision.actions.map((act, i) => (
              <div key={i} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className={`text-[9px] px-2 py-0.5 border font-bold uppercase ${act.allowed ? "border-emerald-900/50 text-emerald-500 bg-emerald-500/5" : "border-red-900/50 text-red-500 bg-red-500/5"}`}>
                    {act.decision}
                  </div>
                  <span className="text-[11px] font-bold uppercase tracking-widest text-slate-400">{act.action.action}</span>
                </div>
                <div className="pl-6 space-y-3 border-l border-[#1a1a1a]">
                  {act.reasoning_trace.map((t, ti) => (
                    <div key={ti} className="text-[10px] text-slate-500 flex items-start gap-3 leading-relaxed">
                      <div className="mt-1.5 w-1 h-1 rounded-full bg-slate-800 shrink-0" />
                      {t}
                    </div>
                  ))}
                  {act.violated_constraints.map((v, vi) => (
                    <div key={vi} className="text-[10px] text-red-400 flex items-start gap-3 bg-red-950/20 p-3 border border-red-900/20 leading-relaxed font-bold">
                      <Lock className="w-3 h-3 mt-0.5 shrink-0" />
                      {v}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-4 pt-4 border-t border-[#1a1a1a]">
          <span className="text-[9px] font-bold text-slate-600 uppercase tracking-[0.2em]">Live Execution Result</span>
          <div className="space-y-2">
            {res.execution_results.map((r, i) => (
              <div key={i} className="text-[11px] font-mono text-emerald-500 flex items-center gap-3">
                <ChevronRight className="w-3 h-3 text-emerald-900" />
                {r}
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
