"use client";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import dynamic from "next/dynamic";

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
  HIGH: "badge-high",
  MEDIUM: "badge-medium",
  LOW: "badge-low",
};

const CLASS_COLOR: Record<string, string> = {
  rust: "text-orange-400",
  damage: "text-red-400",
  leak: "text-purple-400",
};

export default function SandboxPage() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [result, setResult] = useState<DetectResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    const file = accepted[0];
    if (!file) return;
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
    try {
      const form = new FormData();
      form.append("file", imageFile);
      const res = await fetch(`${API}/api/detect`, { method: "POST", body: form });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: DetectResult = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">AI Defect Detector</h1>
        <p className="text-gray-400">Upload any ship equipment photo — hull, pipes, deck structures — to get instant PSC defect analysis.</p>
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
              <p className="text-lg font-semibold text-white mb-2">Drop a ship photo here</p>
              <p className="text-sm text-gray-400">JPG, PNG, WebP · max 20MB</p>
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
                  {loading ? "Analyzing..." : "Run PSC Analysis"}
                </button>
                <button
                  onClick={() => { setImageUrl(null); setImageFile(null); setResult(null); }}
                  className="btn-secondary px-4 py-3"
                >
                  Reset
                </button>
              </div>
              {result && (
                <p className="text-xs text-gray-500 mt-2 text-center">
                  {result.model_version} · {result.inference_ms > 0 ? `${result.inference_ms}ms inference` : "demo mode"}
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
              <p className="text-gray-500">Upload an image and run analysis to see PSC defect results</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="card">
                <div className="flex justify-between items-center mb-1">
                  <h3 className="font-semibold text-white">Analysis Complete</h3>
                  <span className="text-xs text-gray-500">{result.image_width}×{result.image_height}px</span>
                </div>
                <p className="text-2xl font-bold text-teal-400">
                  {result.detections.length === 0 ? "No defects detected" : `${result.detections.length} defect${result.detections.length > 1 ? "s" : ""} found`}
                </p>
              </div>

              {result.detections.length === 0 && (
                <div className="card border-green-700 bg-green-900/20">
                  <p className="text-green-300 font-semibold">✓ PSC Compliant</p>
                  <p className="text-sm text-gray-400 mt-1">No deficiencies detected. Vessel appears compliant for this inspection area.</p>
                </div>
              )}

              {result.detections.map((det, i) => (
                <div key={i} className="card">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`font-bold text-lg capitalize ${CLASS_COLOR[det.class_name] ?? "text-white"}`}>
                        {det.class_name}
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
                  Simulate Port Risk →
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
