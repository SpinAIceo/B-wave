"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useT } from "@/lib/i18n";
import LanguageSwitcher from "./LanguageSwitcher";

export default function NavBar() {
  const path = usePathname();
  const t = useT();

  const NAV = [
    { href: "/sandbox", label: t("nav_ai_sandbox") },
    { href: "/risk",    label: t("nav_psc_risk") },
    { href: "/roi",     label: t("nav_roi_calculator") },
    { href: "/fleet",   label: t("nav_fleet_demo") },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-navy-900/95 backdrop-blur border-b border-navy-700">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg text-white">
          <span className="text-teal-400">◈</span>
          <span>B-Wave</span>
          <span className="text-xs font-normal text-gray-400 hidden sm:block">{t("nav_brand_subtitle")}</span>
        </Link>
        <nav className="flex items-center gap-1">
          {NAV.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                path.startsWith(href)
                  ? "bg-teal-500/20 text-teal-400"
                  : "text-gray-400 hover:text-white hover:bg-navy-700"
              }`}
            >
              {label}
            </Link>
          ))}
          <Link href="/sandbox" className="ml-3 btn-primary text-sm py-2 hidden sm:block">
            {t("nav_try_free")}
          </Link>
          <div className="ml-2">
            <LanguageSwitcher />
          </div>
        </nav>
      </div>
    </header>
  );
}
