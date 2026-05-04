"use client";
import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface RoiResult {
  expected_detention_days: number;
  detention_cost_usd: number;
  cargo_delay_cost_usd: number;
  reputational_cost_usd: number;
  total_risk_usd: number;
  bwave_annual_cost_usd: number;
  roi_ratio: number;
  payback_months: number;
  breakdown: Record<string, unknown>;
}

const VESSEL_TYPES = [
  { value: "bulk_carrier", label: "Bulk Carrier" },
  { value: "container", label: "Container Ship" },
  { value: "tanker", label: "Tanker" },
  { value: "ro_ro", label: "Ro-Ro" },
  { value: "gas_carrier", label: "Gas Carrier" },
  { value: "passenger", label: "Passenger" },
  { value: "general_cargo", label: "General Cargo" },
];

const PORT_OPTIONS = [
  { code: "CNSHA", label: "Shanghai" },
  { code: "USNYC", label: "New York" },
  { code: "NLRTM", label: "Rotterdam" },
  { code: "SGSIN", label: "Singapore" },
  { code: "KRPUS", label: "Busan" },
  { code: "AUSYD", label: "Sydney" },
  { code: "DEHAM", label: "Hamburg" },
  { code: "JPTYO", label: "Tokyo" },
];

const DEFECT_OPTIONS = ["rust", "damage", "leak"];

function usd(n: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);
}

function RoiContent() {
  const params = useSearchParams();
  const initDefects = (params.get("defects") ?? "").split(",").filter(Boolean);

  const [defects, setDefects] = useState<string[]>(initDefects.length ? initDefects : ["rust"]);
  const [portCode, setPortCode] = useState(params.get("port") ?? "CNSHA");
  const [vesselType, setVesselType] = useState("bulk_carrier");
  const [dwt, setDwt] = useState(50000);
  const [result, setResult] = useState<RoiResult | null>(null);
  const [loading, setLoading] = useState(false);

  const toggleDefect = (d: string) =>
    setDefects(prev => prev.includes(d) ? prev.filter(x => x !== d) : [...prev, d]);

  const run = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/roi`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ defects, port_code: portCode, vessel_type: vesselType, vessel_dwt: dwt }),
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Detention Cost Calculator</h1>
        <p className="text-gray-400">Translate defects into dollar exposure and see your ROI from preventing a single detention.</p>
      </div>

      <div className="grid lg:grid-cols-5 gap-8">
        {/* Form */}
        <div className="lg:col-span-2 space-y-5">
          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-3">Defects Present</label>
            <div className="flex flex-wrap gap-2">
              {DEFECT_OPTIONS.map(d => (
                <button
                  key={d}
                  onClick={() => toggleDefect(d)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors capitalize ${
                    defects.includes(d)
                      ? "bg-red-500/20 border-red-500 text-red-300"
                      : "border-navy-600 text-gray-400 hover:border-navy-500"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-2">Port of Call</label>
            <select
              value={portCode}
              onChange={e => setPortCode(e.target.value)}
              className="w-full bg-navy-900 border border-navy-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-teal-500"
            >
              {PORT_OPTIONS.map(p => <option key={p.code} value={p.code}>{p.label}</option>)}
            </select>
          </div>

          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-2">Vessel Type</label>
            <select
              value={vesselType}
              onChange={e => setVesselType(e.target.value)}
              className="w-full bg-navy-900 border border-navy-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-teal-500"
            >
              {VESSEL_TYPES.map(v => <option key={v.value} value={v.value}>{v.label}</option>)}
            </select>
          </div>

          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Vessel DWT: <span className="text-teal-400 font-mono">{dwt.toLocaleString()}</span>
            </label>
            <input
              type="range" min={5000} max={300000} step={5000}
              value={dwt}
              onChange={e => setDwt(Number(e.target.value))}
              className="w-full accent-teal-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>5k</span><span>300k DWT</span>
            </div>
          </div>

          <button onClick={run} disabled={loading || defects.length === 0} className="btn-primary w-full">
            {loading ? "Calculating..." : "Calculate Exposure"}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          {!result ? (
            <div className="card h-full flex flex-col items-center justify-center min-h-80 text-gray-500">
              <p>Select defects and vessel parameters to see cost exposure</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Total risk */}
              <div className="card border-2 border-red-700 bg-red-900/10">
                <p className="text-sm text-gray-400 mb-1">Total Financial Exposure (per voyage)</p>
                <p className="text-5xl font-bold font-mono text-red-400">{usd(result.total_risk_usd)}</p>
                <p className="text-sm text-gray-400 mt-1">
                  {result.expected_detention_days.toFixed(1)} expected detention days
                </p>
              </div>

              {/* Cost breakdown */}
              <div className="card">
                <h3 className="font-semibold text-white mb-3">Cost Breakdown</h3>
                {[
                  { label: "Vessel detention costs", value: result.detention_cost_usd, color: "bg-red-500" },
                  { label: "Cargo delay costs", value: result.cargo_delay_cost_usd, color: "bg-orange-500" },
                  { label: "Reputational / admin costs", value: result.reputational_cost_usd, color: "bg-yellow-500" },
                ].map((item) => (
                  <div key={item.label} className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300">{item.label}</span>
                      <span className="text-white font-mono">{usd(item.value)}</span>
                    </div>
                    <div className="w-full bg-navy-900 rounded-full h-1.5">
                      <div
                        className={`${item.color} h-1.5 rounded-full`}
                        style={{ width: `${(item.value / result.total_risk_usd) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* ROI */}
              <div className="card border-teal-700 bg-teal-900/10">
                <h3 className="font-semibold text-white mb-3">B-Wave ROI</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-teal-400 font-mono">{result.roi_ratio}x</p>
                    <p className="text-xs text-gray-400 mt-1">ROI ratio</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-teal-400 font-mono">
                      {result.payback_months < 99 ? `${result.payback_months}mo` : "—"}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">Payback period</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-teal-400 font-mono">{usd(result.bwave_annual_cost_usd)}</p>
                    <p className="text-xs text-gray-400 mt-1">Annual cost</p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-teal-900 text-sm text-gray-300">
                  Preventing <strong className="text-white">one detention</strong> pays for B-Wave for <strong className="text-teal-400">{Math.ceil(result.total_risk_usd / result.bwave_annual_cost_usd)} years</strong>.
                </div>
              </div>

              <a href="mailto:spinaiceo@gmail.com" className="block btn-primary text-center">
                Get a Formal Quote →
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function RoiPage() {
  return (
    <Suspense>
      <RoiContent />
    </Suspense>
  );
}
