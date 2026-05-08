import ko from "@/locales/ko";

// Only `ko` is statically imported (default + fallback).
// Other locales are code-split into separate chunks loaded on demand.
type Dict = Record<string, string>;

export const LOCALES = {
  ko: { name: "한국어",            flag: "🇰🇷" },
  en: { name: "English",           flag: "🇬🇧" },
  zh: { name: "简体中文",           flag: "🇨🇳" },
  tl: { name: "Filipino",          flag: "🇵🇭" },
  id: { name: "Bahasa Indonesia",  flag: "🇮🇩" },
  ru: { name: "Русский",           flag: "🇷🇺" },
  vi: { name: "Tiếng Việt",        flag: "🇻🇳" },
} as const;

export type Locale = keyof typeof LOCALES;
export type TKey = keyof typeof ko;

export const STORAGE_KEY = "bwave-locale";
export const DEFAULT_LOCALE: Locale = "ko";

const loaders: Record<Locale, () => Promise<Dict>> = {
  ko: () => Promise.resolve(ko as Dict),
  en: () => import("@/locales/en").then(m => m.default as Dict),
  zh: () => import("@/locales/zh").then(m => m.default as Dict),
  tl: () => import("@/locales/tl").then(m => m.default as Dict),
  id: () => import("@/locales/id").then(m => m.default as Dict),
  ru: () => import("@/locales/ru").then(m => m.default as Dict),
  vi: () => import("@/locales/vi").then(m => m.default as Dict),
};

const dictCache: Partial<Record<Locale, Dict>> = { ko: ko as Dict };

export async function loadLocaleDict(locale: Locale): Promise<Dict> {
  if (!dictCache[locale]) {
    dictCache[locale] = await loaders[locale]();
  }
  return dictCache[locale]!;
}

export function format(template: string, params?: Record<string, string | number>): string {
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (_, k) => String(params[k] ?? `{${k}}`));
}

/**
 * Server-safe translation. Returns the default locale (ko) translation.
 * Use only in Server Components where dynamic locale switching is not needed.
 */
export function t(key: TKey, params?: Record<string, string | number>): string {
  return format((ko as Dict)[key] ?? key, params);
}

// Re-export the client hook for convenient `import { useT } from "@/lib/i18n"`
export { useT, useLocale } from "./LocaleProvider";
