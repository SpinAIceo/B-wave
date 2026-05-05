"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useT } from "@/lib/i18n";
import { logger } from "@/lib/logger";

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
  low:    "text-green-400",
  medium: "text-yellow-400",
  high:   "text-red-400",
};
const STATUS_DOT: Record<string, string> = {
  green:  "bg-green-400",
  yellow: "bg-yellow-400",
  red:    "bg-red-400",
};

export default function FleetPage() {
  const t = useT();
  const [data, setData]         = useState<FleetData | null>(null);
  const [selected, setSelected] = useState<Vessel | null>(null);
  const [filter, setFilter]     = useState<string>("all");
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    const timer = logger.time("fleet", "GET /api/fleet");
    logger.info("fleet", `fetching fleet data from ${API}`);
    fetch(`${API}/api/fleet`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: FleetData) => {
        timer.end(`vessels=${d.vessels.length} red=${d.summary.red} yellow=${d.summary.yellow}`);
        logger.info("fleet", "fleet data loaded", d.summary);
        setData(d);
        setLoading(false);
      })
      .catch((e: unknown) => {
        logger.error("fleet", `fleet fetch failed: ${e instanceof Error ? e.message : e}`);
        setLoading(false);
      });
  }, []);

  const vessels  = data?.vessels ?? [];
  const filtered = filter === "all" ? vessels : vessels.filter(v => v.status === filter);

  /** 결함 배열 → 한국어 표시 */
  const defectKo: Record<string, string> = {
    rust:   t("risk_defect_rust"),
    damage: t("risk_defect_damage"),
    leak:   t("risk_defect_leak"),
  };
  const defectsText = (defs: string[]) =>
    defs.length === 0
      ? t("fleet_no_defects")
      : defs.map(d => defectKo[d] ?? d).join(", ");

  /** 필터 탭 레이블 */
  const filterLabel = (f: string): string => {
    if (f === "all")    return `${t("fleet_filter_all")} (${vessels.length})`;
    if (f === "red")    return `${t("fleet_filter_risk")} (${data?.summary.red ?? 0})`;
    if (f === "yellow") return `${t("fleet_filter_monitor")} (${data?.summary.yellow ?? 0})`;
    return `${t("fleet_filter_ok")} (${data?.summary.green ?? 0})`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">{t("fleet_title")}</h1>
        <p className="text-gray-400">{t("fleet_desc")}</p>
      </div>

      {/* Summary tiles */}
      {data && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          {[
            { labelKey: "fleet_tile_total",     value: data.summary.total,  color: "text-white" },
            { labelKey: "fleet_tile_compliant", value: data.summary.green,  color: "text-green-400" },
            { labelKey: "fleet_tile_monitor",   value: data.summary.yellow, color: "text-yellow-400" },
            { labelKey: "fleet_tile_at_risk",   value: data.summary.red,    color: "text-red-400" },
          ].map(s => (
            <div key={s.labelKey} className="card text-center">
              <p className={`text-3xl font-bold font-mono ${s.color}`}>{s.value}</p>
              <p className="text-xs text-gray-400 mt-1">{t(s.labelKey as Parameters<typeof t>[0])}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2">
          <div className="card p-0 overflow-hidden h-96 lg:h-[520px]">
            {loading ? (
              <div className="h-full flex items-center justify-center text-gray-500">{t("fleet_loading")}</div>
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
                className={`flex-1 py-2.5 text-xs font-semibold transition-colors ${
                  filter === f
                    ? "border-b-2 border-teal-500 text-teal-400"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {filterLabel(f)}
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
                    <span className="text-xs text-red-400">
                      {v.defects.map(d => defectKo[d] ?? d).join(", ")}
                    </span>
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
              <p className="text-xs text-gray-500">{t("fleet_detail_risk")}</p>
              <p className={`font-bold capitalize ${RISK_COLOR[selected.risk_level]}`}>{selected.risk_level}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">{t("fleet_detail_defects")}</p>
              <p className="font-semibold text-white">{defectsText(selected.defects)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">{t("fleet_detail_inspection")}</p>
              <p className="font-semibold text-white">{selected.last_inspection}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">{t("fleet_detail_next_port")}</p>
              <p className="font-semibold text-white">{selected.next_port}</p>
            </div>
          </div>
          {selected.defects.length > 0 && (
            <div className="mt-3 flex gap-2">
              <a
                href={`/risk?defects=${selected.defects.join(",")}`}
                className="btn-secondary text-sm py-2"
              >
                {t("fleet_btn_risk")}
              </a>
              <a
                href={`/roi?defects=${selected.defects.join(",")}`}
                className="btn-secondary text-sm py-2"
              >
                {t("fleet_btn_cost")}
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
