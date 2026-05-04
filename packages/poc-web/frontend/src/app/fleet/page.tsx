"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

const FleetMap = dynamic(() => import("@/components/FleetMap"), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Vessel {
  id: string;
  name: string;
  flag: string;
  type: string;
  imo: string;
  lat: number;
  lon: number;
  status: string;
  risk_level: string;
  defects: string[];
  last_inspection: string;
  next_port: string;
}

interface FleetData {
  vessels: Vessel[];
  summary: { total: number; green: number; yellow: number; red: number };
}

const RISK_COLOR: Record<string, string> = {
  low: "text-green-400",
  medium: "text-yellow-400",
  high: "text-red-400",
};
const STATUS_DOT: Record<string, string> = {
  green: "bg-green-400",
  yellow: "bg-yellow-400",
  red: "bg-red-400",
};

export default function FleetPage() {
  const [data, setData] = useState<FleetData | null>(null);
  const [selected, setSelected] = useState<Vessel | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/fleet`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const vessels = data?.vessels ?? [];
  const filtered = filter === "all" ? vessels : vessels.filter(v => v.status === filter);

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Fleet Dashboard</h1>
        <p className="text-gray-400">Live PSC risk status for 50 vessels across global shipping lanes.</p>
      </div>

      {/* Summary tiles */}
      {data && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          {[
            { label: "Total Fleet", value: data.summary.total, color: "text-white" },
            { label: "Compliant", value: data.summary.green, color: "text-green-400" },
            { label: "Monitor", value: data.summary.yellow, color: "text-yellow-400" },
            { label: "At Risk", value: data.summary.red, color: "text-red-400" },
          ].map(s => (
            <div key={s.label} className="card text-center">
              <p className={`text-3xl font-bold font-mono ${s.color}`}>{s.value}</p>
              <p className="text-xs text-gray-400 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2">
          <div className="card p-0 overflow-hidden h-96 lg:h-[520px]">
            {loading ? (
              <div className="h-full flex items-center justify-center text-gray-500">Loading fleet data...</div>
            ) : (
              <FleetMap vessels={vessels} selected={selected} onSelect={setSelected} />
            )}
          </div>
        </div>

        {/* Vessel list */}
        <div className="card p-0 overflow-hidden">
          {/* Filter tabs */}
          <div className="flex border-b border-navy-700">
            {["all", "red", "yellow", "green"].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`flex-1 py-2.5 text-xs font-semibold capitalize transition-colors ${
                  filter === f
                    ? "border-b-2 border-teal-500 text-teal-400"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {f === "all" ? `All (${vessels.length})` : f === "red" ? `Risk (${data?.summary.red ?? 0})` : f === "yellow" ? `Monitor (${data?.summary.yellow ?? 0})` : `OK (${data?.summary.green ?? 0})`}
              </button>
            ))}
          </div>

          {/* Vessel list */}
          <div className="overflow-y-auto h-80 lg:h-[476px]">
            {filtered.map(v => (
              <button
                key={v.id}
                onClick={() => setSelected(v)}
                className={`w-full text-left px-4 py-3 border-b border-navy-700 hover:bg-navy-700 transition-colors ${
                  selected?.id === v.id ? "bg-navy-700" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full flex-shrink-0 ${STATUS_DOT[v.status]}`} />
                    <span className="text-sm font-semibold text-white truncate max-w-[140px]">{v.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{v.flag}</span>
                </div>
                <div className="flex items-center gap-2 mt-0.5 ml-4">
                  <span className="text-xs text-gray-500">{v.type}</span>
                  {v.defects.length > 0 && (
                    <span className="text-xs text-red-400">{v.defects.join(", ")}</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Selected vessel detail */}
      {selected && (
        <div className="mt-6 card">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold text-white">{selected.name}</h2>
              <p className="text-gray-400 text-sm">{selected.imo} · {selected.flag} · {selected.type}</p>
            </div>
            <button onClick={() => setSelected(null)} className="text-gray-500 hover:text-white">✕</button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
            <div>
              <p className="text-xs text-gray-500">PSC Risk</p>
              <p className={`font-bold capitalize ${RISK_COLOR[selected.risk_level]}`}>{selected.risk_level}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Defects</p>
              <p className="font-semibold text-white capitalize">
                {selected.defects.length === 0 ? "None" : selected.defects.join(", ")}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Last Inspection</p>
              <p className="font-semibold text-white">{selected.last_inspection}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Next Port</p>
              <p className="font-semibold text-white">{selected.next_port}</p>
            </div>
          </div>
          {selected.defects.length > 0 && (
            <div className="mt-3 flex gap-2">
              <a
                href={`/risk?defects=${selected.defects.join(",")}`}
                className="btn-secondary text-sm py-2"
              >
                Simulate Risk
              </a>
              <a
                href={`/roi?defects=${selected.defects.join(",")}`}
                className="btn-secondary text-sm py-2"
              >
                Calculate Cost
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
