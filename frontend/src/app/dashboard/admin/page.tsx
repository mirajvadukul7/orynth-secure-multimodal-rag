"use client";
import { useState, useEffect } from "react";
import { Activity, Users, FileText, Database, AlertTriangle, CheckCircle2 } from "lucide-react";

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [tests, setTests] = useState<any>([]);
  const [testResults, setTestResults] = useState<any>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchStats();
    fetchTests();
  }, []);

  const fetchStats = async () => {
    const res = await fetch("http://localhost:8000/api/admin/stats", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    });
    if (res.ok) setStats(await res.json());
  };

  const fetchTests = async () => {
    const res = await fetch("http://localhost:8000/api/security/tests", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    });
    if (res.ok) {
      const data = await res.json();
      setTests(data.tests);
    }
  };

  const runTests = async () => {
    setRunning(true);
    try {
      const res = await fetch("http://localhost:8000/api/security/tests/run", {
        method: "POST",
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      });
      if (res.ok) {
        const data = await res.json();
        setTestResults(data.results);
      }
    } finally {
      setRunning(false);
    }
  };

  if (!stats) return <div className="p-8 text-zinc-400">Loading admin data...</div>;

  return (
    <div className="p-8 h-full overflow-y-auto">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
        <Activity className="w-6 h-6 mr-3 text-blue-400" /> System Overview
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
          <div className="flex items-center text-zinc-400 mb-2">
            <Users className="w-4 h-4 mr-2" /> Total Users
          </div>
          <div className="text-3xl font-bold text-white">{stats.total_users}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
          <div className="flex items-center text-zinc-400 mb-2">
            <FileText className="w-4 h-4 mr-2" /> Documents
          </div>
          <div className="text-3xl font-bold text-white">{stats.total_documents}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
          <div className="flex items-center text-zinc-400 mb-2">
            <Database className="w-4 h-4 mr-2" /> Vector Chunks
          </div>
          <div className="text-3xl font-bold text-white">{stats.total_chunks}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
          <div className="flex items-center text-red-400 mb-2">
            <AlertTriangle className="w-4 h-4 mr-2" /> Security Violations
          </div>
          <div className="text-3xl font-bold text-white">{stats.security_violations}</div>
        </div>
      </div>

      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center">
          <ShieldAlert className="w-5 h-5 mr-3 text-emerald-400" /> Security Test Lab
        </h2>
        <button 
          onClick={runTests}
          disabled={running}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium text-sm transition-colors disabled:opacity-50"
        >
          {running ? "Running Tests..." : "Run Security Suite"}
        </button>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-950/50 border-b border-zinc-800 text-zinc-400">
            <tr>
              <th className="px-6 py-4 font-medium">Test ID</th>
              <th className="px-6 py-4 font-medium">Scenario</th>
              <th className="px-6 py-4 font-medium">Expected</th>
              <th className="px-6 py-4 font-medium">Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/50 text-zinc-300">
            {tests.map((t: any) => {
              const res = testResults?.find((r: any) => r.id === t.id);
              return (
                <tr key={t.id} className="hover:bg-zinc-800/20 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs">{t.id}</td>
                  <td className="px-6 py-4">{t.name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${t.expected === 'PASS' || t.expected === 'ALLOWED' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                      {t.expected}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {res ? (
                      res.status === "PASS" ? (
                        <span className="flex items-center text-emerald-400 font-medium"><CheckCircle2 className="w-4 h-4 mr-1.5" /> PASS</span>
                      ) : (
                        <span className="flex items-center text-red-400 font-medium"><AlertTriangle className="w-4 h-4 mr-1.5" /> FAIL</span>
                      )
                    ) : (
                      <span className="text-zinc-600">-</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Ensure the icon is imported
import { ShieldAlert } from "lucide-react";
