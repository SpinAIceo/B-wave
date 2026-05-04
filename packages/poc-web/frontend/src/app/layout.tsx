import type { Metadata } from "next";
import "./globals.css";
import NavBar from "@/components/NavBar";

export const metadata: Metadata = {
  title: "B-Wave | Ship PSC Defect Scanner",
  description: "AI-powered Port State Control defect detection for maritime vessels",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <NavBar />
        <main className="min-h-screen pt-16">{children}</main>
        <footer className="border-t border-navy-700 py-8 text-center text-sm text-gray-500">
          <p>© 2026 Spinai — B-Wave Edge Vision AI · PSC Compliance Scanner</p>
          <p className="mt-1 text-xs">Model: YOLO26s-v1 · mAP50-95=0.323 · Latency p95=9.3ms (RTX4090)</p>
        </footer>
      </body>
    </html>
  );
}
