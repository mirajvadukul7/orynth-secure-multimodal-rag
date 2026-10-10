"use client";
import { useState, useEffect } from "react";
import { FileText, Lock } from "lucide-react";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/documents", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    })
    .then(res => res.json())
    .then(data => setDocs(data.documents || []));
  }, []);

  return (
    <div className="p-8 h-full overflow-y-auto">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
        <FileText className="w-6 h-6 mr-3 text-blue-400" /> Authorized Documents
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {docs.map((doc: any) => (
          <div key={doc.id} className="bg-zinc-900 border border-zinc-800 p-5 rounded-2xl flex flex-col group hover:border-zinc-700 transition-colors">
            <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-4">
              <FileText className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-white font-medium mb-1 truncate">{doc.filename}</h3>
            <p className="text-xs text-zinc-500 mb-4">{doc.document_type.toUpperCase()} • ID: {doc.source_id}</p>
            
            <div className="mt-auto flex items-center justify-between pt-4 border-t border-zinc-800/50 text-xs">
              <span className={`px-2 py-1 rounded font-medium ${doc.classification === 'PUBLIC' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                {doc.classification}
              </span>
              <span className="flex items-center text-zinc-500">
                <Lock className="w-3 h-3 mr-1" /> Authorized
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
