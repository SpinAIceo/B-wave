"use client";
import { useEffect, useRef } from "react";

interface BBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  class_name: string;
  confidence: number;
  psc_code: string;
  severity: string;
}

interface Props {
  imageUrl: string;
  detections: BBox[];
  imageWidth: number;
  imageHeight: number;
}

const CLASS_COLORS: Record<string, string> = {
  rust: "#f97316",    // orange
  damage: "#ef4444",  // red
  leak: "#a855f7",    // purple
};

export default function BboxCanvas({ imageUrl, detections, imageWidth, imageHeight }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new window.Image();
    img.onload = () => {
      const displayW = canvas.parentElement?.clientWidth ?? 640;
      const scale = displayW / imageWidth;
      const displayH = imageHeight * scale;

      canvas.width = displayW;
      canvas.height = displayH;

      ctx.drawImage(img, 0, 0, displayW, displayH);

      for (const det of detections) {
        const x = det.x_min * scale;
        const y = det.y_min * scale;
        const w = (det.x_max - det.x_min) * scale;
        const h = (det.y_max - det.y_min) * scale;
        const color = CLASS_COLORS[det.class_name] ?? "#14b8a6";

        // Box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.strokeRect(x, y, w, h);

        // Label background
        const label = `${det.class_name.toUpperCase()} ${(det.confidence * 100).toFixed(0)}% · PSC ${det.psc_code}`;
        ctx.font = "bold 12px monospace";
        const textW = ctx.measureText(label).width + 8;
        const textH = 20;
        const labelY = y > textH + 4 ? y - textH - 2 : y + 2;

        ctx.fillStyle = color + "dd";
        ctx.fillRect(x - 1, labelY, textW, textH);

        ctx.fillStyle = "#fff";
        ctx.fillText(label, x + 3, labelY + 14);
      }
    };
    img.src = imageUrl;
  }, [imageUrl, detections, imageWidth, imageHeight]);

  return <canvas ref={canvasRef} className="w-full rounded-lg" />;
}
