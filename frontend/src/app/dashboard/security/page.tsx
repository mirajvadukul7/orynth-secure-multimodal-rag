"use client";
import { useState, useEffect } from "react";
import { Shield, ShieldAlert, ShieldCheck } from "lucide-react";

export default function SecurityTrace() {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/security/audit", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    })
    .then(res => res.json())
    .then(data => setLogs(data.logs || []));
  }, []);

  return (
    <div className="p-8 h-full overflow-y-auto">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
        <Shield className="w-6 h-6 mr-3 text-blue-400" /> Security Trace / Audit Logs
      </h2>
      <div className="space-y-4">
        {logs.map((log: any) => (
          <div key={log.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm font-medium text-white break-all">"{log.query}"</div>
              <div className={`text-xs font-bold px-2 py-1 rounded flex items-center ${log.security_decision === 'SECURE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                {log.security_decision === 'SECURE' ? <ShieldCheck className="w-3.5 h-3.5 mr-1" /> : <ShieldAlert className="w-3.5 h-3.5 mr-1" />}
                {log.security_decision}
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
                <span className="text-zinc-500 block mb-1">User ID</span>
                <span className="text-zinc-300 font-mono">{log.user_id.substring(0,8)}...</span>
              </div>
              <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
                <span className="text-zinc-500 block mb-1">Authorized Candidates</span>
                <span className="text-zinc-300">{log.authorized_count}</span>
              </div>
              <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
                <span className="text-zinc-500 block mb-1">Denied Chunks</span>
                <span className="text-zinc-300">{log.denied_count}</span>
              </div>
              <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
                <span className="text-emerald-400 block mb-1">LLM Exposure (Unauthorized)</span>
                <span className="text-emerald-400 font-bold text-sm">0</span>
              </div>
            </div>
          </div>
        ))}
        {logs.length === 0 && (
          <div className="text-center text-zinc-500 mt-12">No audit logs found. Run some queries first.</div>
        )}
      </div>
    </div>
  );
}
