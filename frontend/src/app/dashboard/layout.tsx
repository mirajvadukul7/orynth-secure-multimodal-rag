"use client";
import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Shield, MessageSquare, Database, FileText, Activity, LogOut, Settings } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
      return;
    }
    
    fetch("http://localhost:8000/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => {
      if (data.id) setUser(data);
      else router.push("/");
    })
    .catch(() => router.push("/"));
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  if (!user) return <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-400">Loading AegisRAG...</div>;

  const navItems = [
    { label: "Secure Chat", href: "/dashboard", icon: MessageSquare },
    { label: "Documents", href: "/dashboard/documents", icon: FileText },
    { label: "Security Trace", href: "/dashboard/security", icon: Shield },
  ];

  if (user.role_id === "ADMIN") {
    navItems.push({ label: "Admin Lab", href: "/dashboard/admin", icon: Activity });
  }

  return (
    <div className="flex h-screen bg-zinc-950 overflow-hidden">
      {/* Sidebar */}
      <div className="w-72 bg-zinc-900/50 border-r border-zinc-800/80 flex flex-col backdrop-blur-md">
        <div className="p-6 flex items-center space-x-3 border-b border-zinc-800/80">
          <div className="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center">
            <Shield className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white">AegisRAG</h1>
            <p className="text-xs text-blue-400 font-medium">Zero-Leakage AI</p>
          </div>
        </div>

        <div className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {navItems.map(item => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} 
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                  isActive 
                    ? "bg-blue-500/10 text-blue-400 font-medium border border-blue-500/20" 
                    : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200 border border-transparent"
                }`}>
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </div>

        <div className="p-4 border-t border-zinc-800/80 mt-auto bg-zinc-900/30">
          <div className="flex items-center justify-between px-2 mb-4">
            <div className="flex flex-col">
              <span className="text-sm font-medium text-white">{user.username}</span>
              <span className="text-xs text-zinc-500 flex items-center mt-0.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>
                Role: {user.role_id}
              </span>
            </div>
            <button onClick={handleLogout} className="p-2 text-zinc-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative bg-black bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-900/40 via-black to-black">
        {children}
      </div>
    </div>
  );
}
