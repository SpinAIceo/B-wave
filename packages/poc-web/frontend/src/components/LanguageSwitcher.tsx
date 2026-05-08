"use client";
import { useState, useRef, useEffect } from "react";
import { LOCALES, type Locale } from "@/lib/i18n";
import { useLocale } from "@/lib/LocaleProvider";

export default function LanguageSwitcher() {
  const { locale, setLocale } = useLocale();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const current = LOCALES[locale];

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-sm text-gray-300 hover:text-white hover:bg-navy-700 transition-colors"
        aria-label="Language"
      >
        <span className="text-base">{current.flag}</span>
        <span className="hidden sm:inline">{current.name}</span>
        <span className="text-[10px] opacity-60">▼</span>
      </button>

      {open && (
        <div className="absolute top-full right-0 mt-1 min-w-[160px] bg-navy-800 border border-navy-600 rounded-lg shadow-lg z-50 overflow-hidden">
          {(Object.keys(LOCALES) as Locale[]).map(code => {
            const l = LOCALES[code];
            const active = code === locale;
            return (
              <button
                key={code}
                onClick={() => { setLocale(code); setOpen(false); }}
                className={`flex items-center gap-2 w-full px-3 py-2 text-sm text-left transition-colors ${
                  active ? "bg-navy-700 text-teal-400" : "text-gray-300 hover:bg-navy-700 hover:text-white"
                }`}
              >
                <span className="text-base">{l.flag}</span>
                <span className="flex-1">{l.name}</span>
                {active && <span>✓</span>}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
