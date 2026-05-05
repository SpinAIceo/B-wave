"use client";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import dynamic from "next/dynamic";
import { useT } from "@/lib/i18n";
import { logger } from "@/lib/logger";

const BboxCanvas = dynamic(() => import("@/components/BboxCanvas"), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface BBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  class_name: string;
  confidence: number;
  psc_code: string;
  psc_description: string;
  severity: string;
}

interface DetectResult {
  detections: BBox[];
  image_width: number;
  image_height: number;
  inference_ms: number;
  model_version: string;
}

const SEVERITY_CLASS: Record<string, string> = {
  CRITICAL: "badge-critical",
  HIGH:     "badge-high",
  MEDIUM:   "badge-medium",
  LOW:      "badge-low",
};

const CLASS_COLOR: Record<string, string> = {
  rust:   "text-orange-400",
  damage: "text-red-400",
  leak:   "text-purple-400",
};

// ── 언어별 라벨 테이블 (Bilingual label tables) ──────────────────────────────

/** 결함 class_name → 한국어 표시명 */
const CLASS_KO: Record<string, string> = {
  rust:   "부식",
  damage: "손상",
  leak:   "누수",
};

/** 결함 class_name → 영어 전체 명칭 */
const CLASS_EN: Record<string, string> = {
  rust:   "Rust / Corrosion",
  damage: "Structural Damage",
  leak:   "Oil / Water Leak",
};

/** PSC 코드 → 영어 설명 */
const PSC_DESC_EN: Record<string, string> = {
  "0615": "Hull corrosion / wastage",
  "0630": "Structural deficiency",
  "0950": "Oil / water leakage",
};

/** PSC 코드 → 한국어 설명 */
const PSC_DESC_KO: Record<string, string> = {
  "0615": "선체 부식/낭비",
  "0630": "구조적 결함",
  "0950": "오일/수분 누출",
};

/** 심각도 → 한국어 */
const SEVERITY_KO: Record<string, string> = {
  CRITICAL: "심각",
  HIGH:     "높음",
  MEDIUM:   "중간",
  LOW:      "낮음",
};

const VESSELS = [
  { id: "V001", name: "MV Pacific Star" },
  { id: "V002", name: "MV Ocean Harmony" },
  { id: "V003", name: "MV Blue Horizon" },
  { id: "V004", name: "MV Northern Wind" },
  { id: "V005", name: "MV Coral Venture" },
];

export default function SandboxPage() {
  const t = useT();
  const [imageUrl, setImageUrl]   = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [result, setResult]       = useState<DetectResult | null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const [vesselId, setVesselId]   = useState("V001");

  const onDrop = useCallback((accepted: File[]) => {
    const file = accepted[0];
    if (!file) return;
    logger.info("sandbox", "━━━ 파일 선택됨 | File selected ━━━");
    logger.info("sandbox", `  이름(name)   : ${file.name}`);
    logger.info("sandbox", `  크기(size)   : ${(file.size / 1024).toFixed(0)} KB`);
    logger.info("sandbox", `  형식(type)   : ${file.type}`);
    logger.info("sandbox", `  수정일(lastModified): ${new Date(file.lastModified).toISOString()}`);
    setImageFile(file);
    setImageUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    maxSize: 20 * 1024 * 1024,
    multiple: false,
  });

  const runDetect = async () => {
    if (!imageFile) return;
    setLoading(true);
    setError(null);

    const totalSteps = 5;
    logger.info("sandbox", `\n${"═".repeat(60)}`);
    logger.info("sandbox", `🔍 PSC 분석 파이프라인 시작 | Analysis pipeline started`);
    logger.info("sandbox", `${"═".repeat(60)}`);

    // ── STEP 1/5: 파일 검증 (File validation) ──────────────────────────────
    logger.info("sandbox", `[STEP 1/${totalSteps}] 파일 검증 | File validation`);
    logger.info("sandbox", `  파일명(filename) : ${imageFile.name}`);
    logger.info("sandbox", `  파일크기(size)   : ${(imageFile.size / 1024).toFixed(1)} KB`);
    logger.info("sandbox", `  MIME 형식(type)  : ${imageFile.type}`);
    logger.info("sandbox", `  선박(vessel)     : ${vesselId}`);
    if (imageFile.size > 20 * 1024 * 1024) {
      logger.error("sandbox", `  ✗ 파일 크기 초과 | File too large (max 20MB)`);
      setError("파일 크기 20MB 초과");
      setLoading(false);
      return;
    }
    logger.info("sandbox", `  ✓ 검증 통과 | Validation passed`);

    // ── STEP 2/5: FormData 생성 (FormData build) ───────────────────────────
    logger.info("sandbox", `[STEP 2/${totalSteps}] FormData 생성 | FormData build`);
    const form = new FormData();
    form.append("file", imageFile);
    const url = `${API}/api/detect?vessel_id=${vesselId}`;
    logger.info("sandbox", `  엔드포인트(endpoint) : POST ${url}`);
    logger.info("sandbox", `  요청 바디(body)      : multipart/form-data (file=${imageFile.name})`);

    // ── STEP 3/5: API 요청 전송 (API request) ──────────────────────────────
    logger.info("sandbox", `[STEP 3/${totalSteps}] API 요청 전송 | Sending API request`);
    const timer = logger.time("sandbox", "API round-trip");
    try {
      const res = await fetch(url, { method: "POST", body: form });

      // ── STEP 4/5: 응답 파싱 (Response parse) ─────────────────────────────
      logger.info("sandbox", `[STEP 4/${totalSteps}] 응답 파싱 | Response parse`);
      logger.info("sandbox", `  HTTP 상태(status)  : ${res.status} ${res.statusText}`);
      logger.info("sandbox", `  Content-Type       : ${res.headers.get("content-type") ?? "unknown"}`);
      // ── request-ID 상관 (trace correlation) ─────────────────────────────
      const serverReqId = res.headers.get("x-request-id");
      if (serverReqId) {
        logger.info("sandbox", `  X-Request-ID       : ${serverReqId}  ← 백엔드 로그와 이 ID로 연결 | correlate backend logs with this ID`);
      } else {
        logger.warn("sandbox", `  X-Request-ID       : 없음 (헤더 미노출) | header not exposed`);
      }
      if (!res.ok) {
        logger.error("sandbox", `  ✗ HTTP 오류 | HTTP error — status=${res.status} req_id=${serverReqId ?? "?"}`);;
        throw new Error(`Server error: ${res.status}`);
      }
      const data: DetectResult = await res.json();
      timer.end(`status=${res.status}`);
      logger.info("sandbox", `  모델 버전(model)       : ${data.model_version}`);
      logger.info("sandbox", `  추론 시간(inference)   : ${data.inference_ms} ms`);
      logger.info("sandbox", `  이미지 크기(img size)  : ${data.image_width}×${data.image_height}px`);
      logger.info("sandbox", `  탐지 건수(detections)  : ${data.detections.length}건`);

      // ── STEP 5/5: 탐지 결과 처리 (Detection result processing) ──────────
      logger.info("sandbox", `[STEP 5/${totalSteps}] 탐지 결과 처리 | Detection result processing`);
      if (data.detections.length === 0) {
        logger.info("sandbox", `  ✓ 결함 없음 (PSC 적합) | No defects found — PSC compliant`);
      } else {
        logger.info("sandbox", `  탐지된 결함 목록 | Detected defects:`);
        data.detections.forEach((det, i) => {
          const koClass  = CLASS_KO[det.class_name]  ?? det.class_name;
          const enClass  = CLASS_EN[det.class_name]  ?? det.class_name;
          const koDesc   = PSC_DESC_KO[det.psc_code] ?? "알 수 없음";
          const enDesc   = PSC_DESC_EN[det.psc_code] ?? "Unknown";
          const koSev    = SEVERITY_KO[det.severity] ?? det.severity;
          const confPct  = (det.confidence * 100).toFixed(1);
          logger.info("sandbox", `  ┌─ [결과 ${i + 1}/${data.detections.length}] ─────────────────────────────`);
          logger.info("sandbox", `  │  클래스(class)  KO: ${koClass}  /  EN: ${enClass}`);
          logger.info("sandbox", `  │  신뢰도(conf)   : ${confPct}%`);
          logger.info("sandbox", `  │  심각도(severity) KO: ${koSev}  /  EN: ${det.severity}`);
          logger.info("sandbox", `  │  PSC 코드       : ${det.psc_code}`);
          logger.info("sandbox", `  │  PSC 설명 KO    : ${koDesc}`);
          logger.info("sandbox", `  │  PSC 설명 EN    : ${enDesc}`);
          logger.info("sandbox", `  │  바운딩박스(bbox): [${det.x_min.toFixed(0)}, ${det.y_min.toFixed(0)}] → [${det.x_max.toFixed(0)}, ${det.y_max.toFixed(0)}]`);
          logger.info("sandbox", `  └────────────────────────────────────────────`);
        });

        // 심각도별 집계 로그 (Severity summary)
        const sevCount: Record<string, number> = {};
        data.detections.forEach(d => { sevCount[d.severity] = (sevCount[d.severity] ?? 0) + 1; });
        const sevSummaryKo = Object.entries(sevCount).map(([s, c]) => `${SEVERITY_KO[s] ?? s}:${c}건`).join(", ");
        const sevSummaryEn = Object.entries(sevCount).map(([s, c]) => `${s}:${c}`).join(", ");
        logger.info("sandbox", `  📊 심각도 집계 KO | ${sevSummaryKo}`);
        logger.info("sandbox", `  📊 severity summary EN | ${sevSummaryEn}`);
      }

      logger.info("sandbox", `${"─".repeat(60)}`);
      logger.info("sandbox", `✅ 분석 완료 | Pipeline complete — ${data.detections.length}건 탐지 / ${data.inference_ms}ms`);
      logger.info("sandbox", `${"═".repeat(60)}\n`);
      setResult(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Request failed";
      // ── 오류 유형 분류 (Error category classification) ─────────────────
      let errCategory = "UNKNOWN";
      if (e instanceof TypeError && msg.includes("fetch")) {
        errCategory = "NETWORK_FAIL";        // CORS, 서버 다운, DNS 오류
      } else if (e instanceof SyntaxError) {
        errCategory = "JSON_PARSE_FAIL";     // 응답이 JSON 아님
      } else if (msg.startsWith("Server error:")) {
        errCategory = `HTTP_${msg.split(":")[1]?.trim() ?? "ERR"}`;
      } else if (msg.toLowerCase().includes("timeout")) {
        errCategory = "TIMEOUT";
      }
      logger.error("sandbox", `${"─".repeat(60)}`);
      logger.error("sandbox", `✗ 파이프라인 오류 | Pipeline error`);
      logger.error("sandbox", `  오류 분류(category) : ${errCategory}`);
      logger.error("sandbox", `  오류 유형(type)     : ${e instanceof Error ? e.constructor.name : typeof e}`);
      logger.error("sandbox", `  메시지(message)     : ${msg}`);
      logger.error("sandbox", `  API 주소(url)       : ${url}`);
      logger.error("sandbox", `  → 백엔드 로그 검색: X-Request-ID로 추적하세요`);
      logger.error("sandbox", `${"═".repeat(60)}\n`, e);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const defectCountText = (n: number) =>
    n === 0 ? t("sandbox_no_defects") : t("sandbox_defects_found_plural").replace("{n}", String(n));

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">{t("sandbox_title")}</h1>
        <p className="text-gray-400">{t("sandbox_desc")}</p>
        <div className="mt-4 flex items-center gap-3">
          <label className="text-sm text-gray-400 whitespace-nowrap">{t("sandbox_vessel_label")}</label>
          <select
            value={vesselId}
            onChange={e => setVesselId(e.target.value)}
            className="bg-navy-800 border border-navy-600 text-white text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-teal-500"
          >
            {VESSELS.map(v => (
              <option key={v.id} value={v.id}>{v.name}</option>
            ))}
          </select>
          <span className="text-xs text-gray-500">{t("sandbox_sync_hint")}</span>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Upload + Image */}
        <div>
          {!imageUrl ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
                isDragActive ? "border-teal-400 bg-teal-400/5" : "border-navy-600 hover:border-teal-600"
              }`}
            >
              <input {...getInputProps()} />
              <div className="text-5xl mb-4">📷</div>
              <p className="text-lg font-semibold text-white mb-2">{t("sandbox_dropzone_title")}</p>
              <p className="text-sm text-gray-400">{t("sandbox_dropzone_hint")}</p>
            </div>
          ) : (
            <div>
              <div className="relative rounded-xl overflow-hidden bg-navy-900">
                {result ? (
                  <BboxCanvas
                    imageUrl={imageUrl}
                    detections={result.detections}
                    imageWidth={result.image_width}
                    imageHeight={result.image_height}
                  />
                ) : (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={imageUrl} alt="Uploaded" className="w-full rounded-xl" />
                )}
              </div>
              <div className="flex gap-3 mt-4">
                <button onClick={runDetect} disabled={loading} className="btn-primary flex-1">
                  {loading ? t("sandbox_analyzing") : t("sandbox_run_btn")}
                </button>
                <button
                  onClick={() => { setImageUrl(null); setImageFile(null); setResult(null); }}
                  className="btn-secondary px-4 py-3"
                >
                  {t("sandbox_reset")}
                </button>
              </div>
              {result && (
                <p className="text-xs text-gray-500 mt-2 text-center">
                  {result.model_version} · {result.inference_ms > 0 ? `${result.inference_ms}ms inference` : t("sandbox_demo_mode")}
                </p>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 card border-red-700 bg-red-900/20 text-red-300 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        <div>
          {!result ? (
            <div className="card h-full flex flex-col items-center justify-center text-center min-h-64">
              <div className="text-4xl mb-3 opacity-30">◈</div>
              <p className="text-gray-500">{t("sandbox_upload_hint")}</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="card">
                <div className="flex justify-between items-center mb-1">
                  <h3 className="font-semibold text-white">{t("sandbox_result_header")}</h3>
                  <span className="text-xs text-gray-500">{result.image_width}×{result.image_height}px</span>
                </div>
                <p className="text-2xl font-bold text-teal-400">
                  {defectCountText(result.detections.length)}
                </p>
              </div>

              {result.detections.length === 0 && (
                <div className="card border-green-700 bg-green-900/20">
                  <p className="text-green-300 font-semibold">{t("sandbox_compliant")}</p>
                  <p className="text-sm text-gray-400 mt-1">{t("sandbox_compliant_desc")}</p>
                </div>
              )}

              {result.detections.map((det, i) => (
                <div key={i} className="card">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`font-bold text-lg ${CLASS_COLOR[det.class_name] ?? "text-white"}`}>
                        {CLASS_KO[det.class_name] ?? det.class_name}
                      </span>
                      <span className={SEVERITY_CLASS[det.severity] ?? "badge-medium"}>
                        {det.severity}
                      </span>
                    </div>
                    <span className="text-lg font-mono font-bold text-white">
                      {(det.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="psc-tag">PSC {det.psc_code}</span>
                    <span className="text-sm text-gray-400">{det.psc_description}</span>
                  </div>
                  <div className="mt-2 text-xs text-gray-500 font-mono">
                    [{det.x_min.toFixed(0)}, {det.y_min.toFixed(0)}] → [{det.x_max.toFixed(0)}, {det.y_max.toFixed(0)}]
                  </div>
                </div>
              ))}

              {result.detections.length > 0 && (
                <a
                  href={`/risk?defects=${result.detections.map(d => d.class_name).join(",")}`}
                  className="block btn-secondary text-center"
                >
                  {t("sandbox_link_risk")}
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
