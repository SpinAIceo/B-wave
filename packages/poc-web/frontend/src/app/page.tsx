"use client";
import Link from "next/link";
import { useT } from "@/lib/i18n";

const FEATURES = [
  {
    href: "/sandbox",
    icon: "🔍",
    titleKey: "feat_sandbox_title",
    descKey: "feat_sandbox_desc",
    ctaKey: "feat_sandbox_cta",
  },
  {
    href: "/risk",
    icon: "⚠️",
    titleKey: "feat_risk_title",
    descKey: "feat_risk_desc",
    ctaKey: "feat_risk_cta",
  },
  {
    href: "/roi",
    icon: "💰",
    titleKey: "feat_roi_title",
    descKey: "feat_roi_desc",
    ctaKey: "feat_roi_cta",
  },
  {
    href: "/fleet",
    icon: "🗺️",
    titleKey: "feat_fleet_title",
    descKey: "feat_fleet_desc",
    ctaKey: "feat_fleet_cta",
  },
] as const;

const STATS = [
  { value: "9.3ms",    labelKey: "stat_latency_label" },
  { value: "0.323",   labelKey: "stat_map_label" },
  { value: "11,367",  labelKey: "stat_images_label" },
  { value: "<500ms",  labelKey: "stat_sla_label" },
] as const;

export default function HomePage() {
  const t = useT();
  return (
    <div className="max-w-7xl mx-auto px-4 py-16">
      {/* Hero */}
      <div className="text-center mb-20">
        <div className="inline-flex items-center gap-2 bg-teal-500/10 border border-teal-500/30 text-teal-400 text-sm px-4 py-1.5 rounded-full mb-6">
          <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
          {t("home_badge")}
        </div>
        <h1 className="text-5xl sm:text-6xl font-bold text-white mb-6 leading-tight">
          {t("home_hero_title1")}
          <br />
          <span className="text-teal-400">{t("home_hero_title2")}</span>
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          {t("home_hero_desc")}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/sandbox" className="btn-primary text-base px-8 py-4">
            {t("home_cta_primary")}
          </Link>
          <Link href="/roi" className="btn-secondary text-base px-8 py-4">
            {t("home_cta_secondary")}
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-20">
        {STATS.map((s) => (
          <div key={s.labelKey} className="card text-center">
            <div className="text-3xl font-bold text-teal-400 font-mono">{s.value}</div>
            <div className="text-sm text-gray-400 mt-1">{t(s.labelKey)}</div>
          </div>
        ))}
      </div>

      {/* Feature cards */}
      <div className="grid sm:grid-cols-2 gap-6 mb-20">
        {FEATURES.map((f) => (
          <div key={f.href} className="card group hover:border-teal-700 transition-colors">
            <div className="text-3xl mb-3">{f.icon}</div>
            <h2 className="text-xl font-bold text-white mb-2">{t(f.titleKey)}</h2>
            <p className="text-gray-400 text-sm leading-relaxed mb-4">{t(f.descKey)}</p>
            <Link href={f.href} className="text-teal-400 text-sm font-semibold hover:text-teal-300 transition-colors">
              {t(f.ctaKey)}
            </Link>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="card text-center border-teal-700 bg-gradient-to-br from-navy-800 to-navy-700">
        <h2 className="text-2xl font-bold text-white mb-2">{t("home_demo_title")}</h2>
        <p className="text-gray-400 mb-6">{t("home_demo_desc")}</p>
        <a href="mailto:spinaiceo@gmail.com" className="btn-primary inline-block">
          {t("home_demo_cta")}
        </a>
      </div>
    </div>
  );
}
