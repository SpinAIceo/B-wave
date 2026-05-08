import { createContext, useContext, useEffect, useState } from 'react';
import ko from '../locales/ko';

// Only `ko` is statically imported (default + fallback).
// Other locales are code-split into separate chunks loaded on demand.
type Dict = Record<string, string>;

export const LOCALES = {
  ko: { name: '한국어',           flag: '🇰🇷' },
  en: { name: 'English',          flag: '🇬🇧' },
  zh: { name: '简体中文',          flag: '🇨🇳' },
  tl: { name: 'Filipino',         flag: '🇵🇭' },
  id: { name: 'Bahasa Indonesia', flag: '🇮🇩' },
  ru: { name: 'Русский',          flag: '🇷🇺' },
  vi: { name: 'Tiếng Việt',       flag: '🇻🇳' },
} as const;

const loaders: Record<Locale, () => Promise<Dict>> = {
  ko: () => Promise.resolve(ko as Dict),
  en: () => import('../locales/en').then(m => m.default as Dict),
  zh: () => import('../locales/zh').then(m => m.default as Dict),
  tl: () => import('../locales/tl').then(m => m.default as Dict),
  id: () => import('../locales/id').then(m => m.default as Dict),
  ru: () => import('../locales/ru').then(m => m.default as Dict),
  vi: () => import('../locales/vi').then(m => m.default as Dict),
};

const dictCache: Partial<Record<Locale, Dict>> = { ko: ko as Dict };

export async function loadLocaleDict(locale: Locale): Promise<Dict> {
  if (!dictCache[locale]) {
    dictCache[locale] = await loaders[locale]();
  }
  return dictCache[locale]!;
}

export type Locale = keyof typeof LOCALES;
export type TranslationKey = keyof typeof ko;

const STORAGE_KEY = 'bwave-locale';
const DEFAULT_LOCALE: Locale = 'ko';

function readStoredLocale(): Locale | null {
  if (typeof window === 'undefined') return null;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored && stored in LOCALES ? (stored as Locale) : null;
  } catch {
    return null;
  }
}

function writeStoredLocale(locale: Locale): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    /* ignore unavailable storage */
  }
}

export function detectInitialLocale(): Locale {
  const stored = readStoredLocale();
  if (stored) return stored;
  if (typeof navigator !== 'undefined') {
    const browser = navigator.language.split('-')[0].toLowerCase();
    if (browser in LOCALES) return browser as Locale;
  }
  return DEFAULT_LOCALE;
}

interface LocaleContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  dict: Dict;
}

export const LocaleContext = createContext<LocaleContextValue | null>(null);

export function useLocaleState(): LocaleContextValue {
  const [locale, setLocaleState] = useState<Locale>(detectInitialLocale);
  const [dict, setDict] = useState<Dict>(ko as Dict);

  useEffect(() => {
    let cancelled = false;
    loadLocaleDict(locale).then(d => {
      if (!cancelled) setDict(d);
    });
    writeStoredLocale(locale);
    document.documentElement.lang = locale;
    return () => { cancelled = true; };
  }, [locale]);

  return { locale, setLocale: setLocaleState, dict };
}

export function useLocale() {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error('useLocale must be used within a LocaleProvider');
  }
  return ctx;
}

function format(template: string, params?: Record<string, string | number>): string {
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (_, k) => String(params[k] ?? `{${k}}`));
}

export function useT() {
  const { dict } = useLocale();
  return (key: TranslationKey, params?: Record<string, string | number>) =>
    format(dict[key] ?? (ko as Dict)[key] ?? key, params);
}
