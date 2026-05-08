"use client";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import ko from "@/locales/ko";
import {
  DEFAULT_LOCALE,
  LOCALES,
  STORAGE_KEY,
  format,
  loadLocaleDict,
  type Locale,
  type TKey,
} from "./i18n";

type Dict = Record<string, string>;

function readStoredLocale(): Locale | null {
  if (typeof window === "undefined") return null;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored && stored in LOCALES ? (stored as Locale) : null;
  } catch {
    return null;
  }
}

function writeStoredLocale(locale: Locale): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    /* ignore unavailable storage */
  }
  // Persist as cookie too so the server can read it on the next request
  // and emit the correct <html lang> attribute (avoids hydration mismatch).
  if (typeof document !== "undefined") {
    const oneYear = 60 * 60 * 24 * 365;
    document.cookie = `${STORAGE_KEY}=${locale}; path=/; max-age=${oneYear}; SameSite=Lax`;
  }
}

function detectInitialLocale(): Locale {
  const stored = readStoredLocale();
  if (stored) return stored;
  if (typeof navigator !== "undefined") {
    const browser = navigator.language.split("-")[0].toLowerCase();
    if (browser in LOCALES) return browser as Locale;
  }
  return DEFAULT_LOCALE;
}

interface LocaleContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  dict: Dict;
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

interface LocaleProviderProps {
  children: ReactNode;
  initialLocale?: Locale;
}

export function LocaleProvider({ children, initialLocale }: LocaleProviderProps) {
  const [locale, setLocaleState] = useState<Locale>(initialLocale ?? DEFAULT_LOCALE);
  const [dict, setDict] = useState<Dict>(ko as Dict);

  // Hydrate from client-side storage / browser after mount
  useEffect(() => {
    setLocaleState(detectInitialLocale());
  }, []);

  useEffect(() => {
    let cancelled = false;
    loadLocaleDict(locale).then(d => {
      if (!cancelled) setDict(d);
    });
    writeStoredLocale(locale);
    if (typeof document !== "undefined") {
      document.documentElement.lang = locale;
    }
    return () => { cancelled = true; };
  }, [locale]);

  return (
    <LocaleContext.Provider value={{ locale, setLocale: setLocaleState, dict }}>
      {children}
    </LocaleContext.Provider>
  );
}

export function useLocale() {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error("useLocale must be used within a LocaleProvider");
  }
  return ctx;
}

export function useT() {
  const { dict } = useLocale();
  return (key: TKey, params?: Record<string, string | number>) =>
    format(dict[key] ?? (ko as Dict)[key] ?? key, params);
}
