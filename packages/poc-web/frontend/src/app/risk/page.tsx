"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useT } from "@/lib/i18n";
import { logger } from "@/lib/logger";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Port { code: string; name: string; region: string }
interface RiskFactor { label: string; contribution: number }
interface RiskResult {
  port_code: string;
  port_name: string;
  mou_region: string;
  base_detention_rate: number;
  adjusted_detention_rate: number;
  risk_level: string;
  risk_factors: RiskFactor[];
  historical_average_days: number;
  recommendation: string;
}

const RISK_COLOR: Record<string, string> = {
  LOW:      "text-green-400",
  MEDIUM:   "text-yellow-400",
  HIGH:     "text-orange-400",
  CRITICAL: "text-red-400",
};
const RISK_BG: Record<string, string> = {
  LOW:      "border-green-700 bg-green-900/10",
  MEDIUM:   "border-yellow-700 bg-yellow-900/10",
  HIGH:     "border-orange-700 bg-orange-900/10",
  CRITICAL: "border-red-700 bg-red-900/20",
};

const DEFECT_OPTIONS = ["rust", "damage", "leak"] as const;
const AGE_OPTIONS    = [1, 5, 10, 15, 20, 25];

function RiskContent() {
  const t = useT();
  const params = useSearchParams();

  const [ports, setPorts]       = useState<Port[]>([]);
  const [portCode, setPortCode] = useState("CNSHA");
  const [defects, setDefects]   = useState<string[]>([]);
  const [age, setAge]           = useState(10);
  const [result, setResult]     = useState<RiskResult | null>(null);
  const [loading, setLoading]   = useState(false);

  /** 결함 키 → 한국어 라벨 */
  const defectLabel: Record<string, string> = {
    rust:   t("risk_defect_rust"),
    damage: t("risk_defect_damage"),
    leak:   t("risk_defect_leak"),
  };

  useEffect(() => {
    logger.info("risk", "loading ports list");
    fetch(`${API}/api/ports`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then((data: Port[]) => { logger.info("risk", `ports loaded count=${data.length}`); setPorts(data); })
      .catch((e: unknown) => logger.error("risk", `ports fetch failed: ${e instanceof Error ? e.message : e}`));
    const d = params.get("defects");
    if (d) {
      const parsed = d.split(",").filter(Boolean);
      logger.info("risk", `pre-filled defects from URL: ${parsed.join(", ")}`);
      setDefects(parsed);
    }
  }, [params]);

  const toggleDefect = (d: string) =>
    setDefects(prev => prev.includes(d) ? prev.filter(x => x !== d) : [...prev, d]);

  const run = async () => {
    setLoading(true);
    const timer = logger.time("risk", "POST /api/risk");
    logger.info("risk", `calc start port=${portCode} defects=[${defects.join(",")}] age=${age}yr`);
    try {
      const res = await fetch(`${API}/api/risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ port_code: portCode, defects, vessel_age_years: age }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: RiskResult = await res.json();
      timer.end(`level=${data.risk_level} rate=${data.adjusted_detention_rate}%`);
      logger.info("risk", "calc result", { level: data.risk_level, rate: data.adjusted_detention_rate });
      setResult(data);
    } catch (e) {
      logger.error("risk", `risk calc failed: ${e instanceof Error ? e.message : e}`, e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">{t("risk_title")}</h1>
        <p className="text-gray-400">{t("risk_desc")}</p>
      </div>

      <div className="grid lg:grid-cols-5 gap-8">
        {/* Form */}
        <div className="lg:col-span-2 space-y-5">
          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-2">{t("risk_label_port")}</label>
            <select
              value={portCode}
              onChange={e => setPortCode(e.target.value)}
              className="w-full bg-navy-900 border border-navy-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-teal-500"
            >
              {ports.length === 0 ? (
                <option value="CNSHA">Shanghai (CNSHA)</option>
              ) : (
                ports.map(p => (
                  <option key={p.code} value={p.code}>{p.name} ({p.code})</option>
                ))
              )}
            </select>
          </div>

          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-3">{t("risk_label_defects")}</label>
            <div className="flex flex-wrap gap-2">
              {DEFECT_OPTIONS.map(d => (
                <button
                  key={d}
                  onClick={() => toggleDefect(d)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                    defects.includes(d)
                      ? "bg-teal-500/20 border-teal-500 text-teal-300"
                      : "border-navy-600 text-gray-400 hover:border-navy-500"
                  }`}
                >
                  {defectLabel[d]}
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-2">{t("risk_label_age")}</label>
            <select
              value={age}
              onChange={e => setAge(Number(e.target.value))}
              className="w-full bg-navy-900 border border-navy-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-teal-500"
            >
              {AGE_OPTIONS.map(y => (
                <option key={y} value={y}>{t("risk_age_years").replace("{n}", String(y))}</option>
              ))}
            </select>
          </div>

          <button onClick={run} disabled={loading} className="btn-primary w-full">
            {loading ? t("risk_calculating") : t("risk_calc_btn")}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          {!result ? (
            <div className="card h-full flex items-center justify-center min-h-80 text-gray-500">
              {t("risk_placeholder")}
            </div>
          ) : (
            <div className="space-y-4">
              {/* Main risk card */}
              <div className={`card border-2 ${RISK_BG[result.risk_level]}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-gray-400">{result.port_name} · {result.mou_region}</p>
                    <p className={`text-5xl font-bold font-mono mt-1 ${RISK_COLOR[result.risk_level]}`}>
                      {result.adjusted_detention_rate}%
                    </p>
                    <p className="text-sm text-gray-400 mt-1">{t("risk_detention_prob")}</p>
                  </div>
                  <span className={`font-bold text-lg px-3 py-1 rounded border ${RISK_BG[result.risk_level]} ${RISK_COLOR[result.risk_level]}`}>
                    {result.risk_level}
                  </span>
                </div>
                <div className="mt-3 pt-3 border-t border-navy-700">
                  <p className="text-sm text-gray-300">{result.recommendation}</p>
                </div>
              </div>

              {/* Risk breakdown */}
              <div className="card">
                <h3 className="font-semibold text-white mb-3">{t("risk_breakdown_title")}</h3>
                <div className="space-y-2">
                  {result.risk_factors.map((f, i) => (
                    <div key={i}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">{f.label}</span>
                        <span className="text-teal-400 font-mono">+{f.contribution.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-navy-900 rounded-full h-1.5">
                        <div
                          className="bg-teal-500 h-1.5 rounded-full"
                          style={{ width: `${Math.min((f.contribution / result.adjusted_detention_rate) * 100, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="card text-center">
                  <p className="text-2xl font-bold text-white font-mono">{result.base_detention_rate}%</p>
                  <p className="text-xs text-gray-400 mt-1">{t("risk_base_rate")}</p>
                </div>
                <div className="card text-center">
                  <p className="text-2xl font-bold text-white font-mono">{result.historical_average_days}d</p>
                  <p className="text-xs text-gray-400 mt-1">{t("risk_avg_duration")}</p>
                </div>
              </div>

              <a
                href={`/roi?defects=${result.risk_factors.flatMap(f => f.label.includes("defect") ? [] : []).join(",")}&port=${result.port_code}`}
                className="block btn-secondary text-center"
              >
                {t("risk_link_roi")}
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function RiskPage() {
  return (
    <Suspense>
      <RiskContent />
    </Suspense>
  );
}
