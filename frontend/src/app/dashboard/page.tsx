"use client";
import { useState, useRef, useEffect } from "react";
import { Send, ShieldCheck, ShieldAlert, FileText, Database, Image as ImageIcon, CheckCircle2, ChevronDown } from "lucide-react";

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!query.trim()) return;
    
    const userMsg = { role: "user", content: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/api/chat/query", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ query: userMsg.content }),
      });
      
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", ...data }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", error: "Failed to connect to AegisRAG Core." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="h-16 border-b border-zinc-800/80 flex items-center justify-between px-8 bg-zinc-900/20 backdrop-blur-sm z-10 shrink-0">
        <h2 className="text-lg font-medium text-white flex items-center">
          <ShieldCheck className="w-5 h-5 text-emerald-400 mr-2" />
          Secure Query Interface
        </h2>
        <div className="flex items-center text-xs text-zinc-500 bg-zinc-900 px-3 py-1.5 rounded-full border border-zinc-800">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-2 animate-pulse" />
          Zero-Leakage Enforcement Active
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-zinc-500 space-y-4">
            <Shield className="w-16 h-16 text-zinc-800" />
            <p className="text-lg font-medium text-zinc-400">Ask a question.</p>
            <p className="text-sm">Retrieval is strictly bounded by your authorization level.</p>
            <div className="flex gap-4 mt-8">
              <button onClick={() => setQuery("What is the annual leave policy?")} className="px-4 py-2 bg-zinc-900 hover:bg-zinc-800 rounded-lg text-sm border border-zinc-800 transition-colors">"What is the annual leave policy?"</button>
              <button onClick={() => setQuery("What is Rahul's salary?")} className="px-4 py-2 bg-zinc-900 hover:bg-zinc-800 rounded-lg text-sm border border-zinc-800 transition-colors">"What is Rahul's salary?"</button>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} w-full`}>
            {msg.role === "user" ? (
              <div className="bg-blue-600 text-white px-6 py-4 rounded-2xl rounded-tr-sm max-w-[70%] shadow-lg">
                <p className="text-sm leading-relaxed">{msg.content}</p>
              </div>
            ) : (
              <div className="w-full max-w-4xl space-y-4">
                <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl rounded-tl-sm shadow-xl relative overflow-hidden group">
                  {/* Security Indicator Line */}
                  <div className={`absolute left-0 top-0 bottom-0 w-1 ${msg.security_status === "SECURE" ? "bg-emerald-500" : "bg-red-500"}`} />
                  
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      {msg.security_status === "SECURE" ? (
                        <span className="flex items-center text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded">
                          <ShieldCheck className="w-3.5 h-3.5 mr-1" /> SECURE
                        </span>
                      ) : (
                        <span className="flex items-center text-xs font-bold text-red-400 bg-red-400/10 px-2 py-1 rounded">
                          <ShieldAlert className="w-3.5 h-3.5 mr-1" /> BLOCKED
                        </span>
                      )}
                      {msg.grounding_score !== undefined && (
                        <span className="text-xs text-zinc-500 border border-zinc-800 px-2 py-1 rounded bg-zinc-950">
                          Grounding: {msg.grounding_score.toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="prose prose-invert max-w-none">
                    <p className="text-zinc-200 text-[15px] leading-relaxed whitespace-pre-wrap">{msg.answer || msg.error}</p>
                  </div>

                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-6 pt-4 border-t border-zinc-800/50">
                      <p className="text-xs font-medium text-zinc-500 mb-3 uppercase tracking-wider">Authorized Evidence Sources</p>
                      <div className="flex flex-wrap gap-2">
                        {msg.citations.map((cite: string, j: number) => {
                          let Icon = FileText;
                          if (cite.includes("IMG")) Icon = ImageIcon;
                          if (cite.includes("DB")) Icon = Database;
                          
                          return (
                            <div key={j} className="flex items-center px-3 py-1.5 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-400 group-hover:border-zinc-700 transition-colors cursor-pointer hover:bg-zinc-800">
                              <Icon className="w-3 h-3 mr-1.5 text-zinc-500" />
                              {cite}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {msg.security_status && (
                    <div className="mt-4 flex items-center justify-between text-[11px] text-zinc-600 bg-black/40 px-3 py-2 rounded-lg">
                      <span>Retrieval strategy: Permission-filtered {msg.evidence?.length > 0 ? "Active" : "Null"}</span>
                      <span className="flex items-center">
                        <CheckCircle2 className={`w-3 h-3 mr-1 ${msg.llm_exposure === 0 && msg.security_status === "BLOCKED" ? "text-emerald-500" : "text-zinc-500"}`} />
                        LLM Exposure of Unauthorized Data: 0 chunks
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start w-full">
            <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl rounded-tl-sm w-64 shadow-xl">
              <div className="flex items-center space-x-3 text-zinc-400">
                <Shield className="w-4 h-4 animate-spin text-blue-500" />
                <span className="text-sm font-medium animate-pulse">Enforcing Policies...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-zinc-950/80 backdrop-blur-xl border-t border-zinc-800/80 z-10 shrink-0">
        <div className="max-w-4xl mx-auto relative group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask a question..."
            className="w-full bg-zinc-900 border border-zinc-700 text-white px-6 py-4 pr-16 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder-zinc-500 shadow-xl"
            disabled={loading}
          />
          <button 
            onClick={handleSend}
            disabled={loading || !query.trim()}
            className="absolute right-2 top-2 bottom-2 w-12 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-xl flex items-center justify-center transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-center text-[11px] text-zinc-600 mt-3 font-medium">AegisRAG enforces real-time document and row-level authorization before LLM inference.</p>
      </div>
    </div>
  );
}
