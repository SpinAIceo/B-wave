"use client";
import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useT } from "@/lib/i18n";
import { logger } from "@/lib/logger";

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

const DEFECT_OPTIONS = ["rust", "damage", "leak"] as const;

function usd(n: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);
}

function RoiContent() {
  const t = useT();
  const params = useSearchParams();
  const initDefects = (params.get("defects") ?? "").split(",").filter(Boolean);

  const [defects, setDefects]       = useState<string[]>(initDefects.length ? initDefects : ["rust"]);
  const [portCode, setPortCode]     = useState(params.get("port") ?? "CNSHA");
  const [vesselType, setVesselType] = useState("bulk_carrier");
  const [dwt, setDwt]               = useState(50000);
  const [result, setResult]         = useState<RoiResult | null>(null);
  const [loading, setLoading]       = useState(false);

  /** 결함 키 → 한국어 라벨 */
  const defectLabel: Record<string, string> = {
    rust:   t("risk_defect_rust"),
    damage: t("risk_defect_damage"),
    leak:   t("risk_defect_leak"),
  };

  const VESSEL_TYPES = [
    { value: "bulk_carrier",   label: t("roi_vessel_bulk") },
    { value: "container",      label: t("roi_vessel_container") },
    { value: "tanker",         label: t("roi_vessel_tanker") },
    { value: "ro_ro",          label: t("roi_vessel_roro") },
    { value: "gas_carrier",    label: t("roi_vessel_gas") },
    { value: "passenger",      label: t("roi_vessel_passenger") },
    { value: "general_cargo",  label: t("roi_vessel_general") },
  ];

  const toggleDefect = (d: string) =>
    setDefects(prev => prev.includes(d) ? prev.filter(x => x !== d) : [...prev, d]);

  const run = async () => {
    setLoading(true);
    const timer = logger.time("roi", "POST /api/roi");
    logger.info("roi", `calc start port=${portCode} type=${vesselType} dwt=${dwt} defects=[${defects.join(",")}]`);
    try {
      const res = await fetch(`${API}/api/roi`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ defects, port_code: portCode, vessel_type: vesselType, vessel_dwt: dwt }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: RoiResult = await res.json();
      timer.end(`total=${data.total_risk_usd} roi=${data.roi_ratio}x payback=${data.payback_months}mo`);
      logger.info("roi", "calc result", {
        totalRisk: data.total_risk_usd,
        roiRatio: data.roi_ratio,
        paybackMonths: data.payback_months,
      });
      setResult(data);
    } catch (e) {
      logger.error("roi", `roi calc failed: ${e instanceof Error ? e.message : e}`, e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">{t("roi_title")}</h1>
        <p className="text-gray-400">{t("roi_desc")}</p>
      </div>

      <div className="grid lg:grid-cols-5 gap-8">
        {/* Form */}
        <div className="lg:col-span-2 space-y-5">
          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-3">{t("roi_label_defects")}</label>
            <div className="flex flex-wrap gap-2">
              {DEFECT_OPTIONS.map(d => (
                <button
                  key={d}
                  onClick={() => toggleDefect(d)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                    defects.includes(d)
                      ? "bg-red-500/20 border-red-500 text-red-300"
                      : "border-navy-600 text-gray-400 hover:border-navy-500"
                  }`}
                >
                  {defectLabel[d]}
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-2">{t("roi_label_port")}</label>
            <select
              value={portCode}
              onChange={e => setPortCode(e.target.value)}
              className="w-full bg-navy-900 border border-navy-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-teal-500"
            >
              {PORT_OPTIONS.map(p => <option key={p.code} value={p.code}>{p.label}</option>)}
            </select>
          </div>

          <div className="card">
            <label className="block text-sm font-semibold text-gray-300 mb-2">{t("roi_label_vessel_type")}</label>
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
              {t("roi_label_dwt")}: <span className="text-teal-400 font-mono">{dwt.toLocaleString()}</span>
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
            {loading ? t("roi_calculating") : t("roi_calc_btn")}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          {!result ? (
            <div className="card h-full flex flex-col items-center justify-center min-h-80 text-gray-500">
              <p>{t("roi_placeholder")}</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Total risk */}
              <div className="card border-2 border-red-700 bg-red-900/10">
                <p className="text-sm text-gray-400 mb-1">{t("roi_total_exposure")}</p>
                <p className="text-5xl font-bold font-mono text-red-400">{usd(result.total_risk_usd)}</p>
                <p className="text-sm text-gray-400 mt-1">
                  {t("roi_detention_days").replace("{n}", result.expected_detention_days.toFixed(1))}
                </p>
              </div>

              {/* Cost breakdown */}
              <div className="card">
                <h3 className="font-semibold text-white mb-3">{t("roi_breakdown_title")}</h3>
                {[
                  { label: t("roi_cost_detention"), value: result.detention_cost_usd,    color: "bg-red-500" },
                  { label: t("roi_cost_cargo"),     value: result.cargo_delay_cost_usd,  color: "bg-orange-500" },
                  { label: t("roi_cost_repute"),    value: result.reputational_cost_usd, color: "bg-yellow-500" },
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
                <h3 className="font-semibold text-white mb-3">{t("roi_section_title")}</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-teal-400 font-mono">{result.roi_ratio}x</p>
                    <p className="text-xs text-gray-400 mt-1">{t("roi_ratio_label")}</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-teal-400 font-mono">
                      {result.payback_months < 99 ? `${result.payback_months}mo` : "—"}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">{t("roi_payback_label")}</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-teal-400 font-mono">{usd(result.bwave_annual_cost_usd)}</p>
                    <p className="text-xs text-gray-400 mt-1">{t("roi_annual_label")}</p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-teal-900 text-sm text-gray-300">
                  {t("roi_payback_text").replace("{n}", String(Math.ceil(result.total_risk_usd / result.bwave_annual_cost_usd)))}
                </div>
              </div>

              <a href="mailto:spinaiceo@gmail.com" className="block btn-primary text-center">
                {t("roi_link_quote")}
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
