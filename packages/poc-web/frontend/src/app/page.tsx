import Link from "next/link";

const FEATURES = [
  {
    href: "/sandbox",
    icon: "🔍",
    title: "AI Defect Detector",
    desc: "Upload any ship photo. Get instant PSC violation codes, bounding box overlays, and severity ratings — powered by YOLO26s trained on 11,000+ maritime images.",
    cta: "Try Sandbox →",
  },
  {
    href: "/risk",
    icon: "⚠️",
    title: "Port PSC Risk Simulator",
    desc: "Select destination port and detected defects. Predict detention probability using real MOU statistics from Tokyo, Paris, USCG, and 20+ regional authorities.",
    cta: "Simulate Risk →",
  },
  {
    href: "/roi",
    icon: "💰",
    title: "Detention Cost Calculator",
    desc: "Translate defects into dollar exposure. Model detention days, cargo delay penalties, and reputational costs versus B-Wave system investment.",
    cta: "Calculate ROI →",
  },
  {
    href: "/fleet",
    icon: "🗺️",
    title: "Fleet Dashboard Demo",
    desc: "Live-style visualization of 50 vessels across global shipping lanes. Green/yellow/red PSC risk status updated in real time.",
    cta: "View Fleet →",
  },
];

const STATS = [
  { value: "9.3ms", label: "p95 inference latency" },
  { value: "0.323", label: "mAP50-95 (3-class)" },
  { value: "11,367", label: "training images" },
  { value: "<500ms", label: "end-to-end SLA" },
];

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-16">
      {/* Hero */}
      <div className="text-center mb-20">
        <div className="inline-flex items-center gap-2 bg-teal-500/10 border border-teal-500/30 text-teal-400 text-sm px-4 py-1.5 rounded-full mb-6">
          <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
          Live Virtual PoC — No hardware required
        </div>
        <h1 className="text-5xl sm:text-6xl font-bold text-white mb-6 leading-tight">
          Ship PSC Defect Detection
          <br />
          <span className="text-teal-400">in Under 500ms</span>
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          B-Wave deploys on your edge server aboard the vessel. Crew points a tablet camera at equipment — rust, damage, and leaks are flagged with PSC violation codes before the inspector arrives.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/sandbox" className="btn-primary text-base px-8 py-4">
            Upload a Ship Photo →
          </Link>
          <Link href="/roi" className="btn-secondary text-base px-8 py-4">
            See Cost Exposure
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-20">
        {STATS.map((s) => (
          <div key={s.label} className="card text-center">
            <div className="text-3xl font-bold text-teal-400 font-mono">{s.value}</div>
            <div className="text-sm text-gray-400 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Feature cards */}
      <div className="grid sm:grid-cols-2 gap-6 mb-20">
        {FEATURES.map((f) => (
          <div key={f.href} className="card group hover:border-teal-700 transition-colors">
            <div className="text-3xl mb-3">{f.icon}</div>
            <h2 className="text-xl font-bold text-white mb-2">{f.title}</h2>
            <p className="text-gray-400 text-sm leading-relaxed mb-4">{f.desc}</p>
            <Link href={f.href} className="text-teal-400 text-sm font-semibold hover:text-teal-300 transition-colors">
              {f.cta}
            </Link>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="card text-center border-teal-700 bg-gradient-to-br from-navy-800 to-navy-700">
        <h2 className="text-2xl font-bold text-white mb-2">Ready for a Full Demo?</h2>
        <p className="text-gray-400 mb-6">
          See B-Wave running on actual edge hardware aboard your vessel. We bring the equipment, you provide the ship.
        </p>
        <a href="mailto:spinaiceo@gmail.com" className="btn-primary inline-block">
          Request Hardware Demo
        </a>
      </div>
    </div>
  );
}
