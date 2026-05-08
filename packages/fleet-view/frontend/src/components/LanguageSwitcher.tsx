import { useState, useRef, useEffect } from 'react';
import { LOCALES, useLocale, type Locale } from '../lib/i18n';

export default function LanguageSwitcher() {
  const { locale, setLocale } = useLocale();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  const current = LOCALES[locale];

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          display: 'flex', alignItems: 'center', gap: 6,
          background: 'transparent', border: '1px solid var(--border)',
          color: 'var(--text-primary)', padding: '6px 12px',
          borderRadius: 6, cursor: 'pointer', fontSize: 13,
        }}
        aria-label="Language"
      >
        <span style={{ fontSize: 16 }}>{current.flag}</span>
        <span>{current.name}</span>
        <span style={{ fontSize: 10, opacity: 0.6 }}>▼</span>
      </button>

      {open && (
        <div
          style={{
            position: 'absolute', top: 'calc(100% + 4px)', right: 0,
            background: 'var(--bg-secondary)', border: '1px solid var(--border)',
            borderRadius: 6, minWidth: 160, zIndex: 1000,
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
          }}
        >
          {(Object.keys(LOCALES) as Locale[]).map(code => {
            const l = LOCALES[code];
            const active = code === locale;
            return (
              <button
                key={code}
                onClick={() => { setLocale(code); setOpen(false); }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  width: '100%', padding: '8px 12px',
                  background: active ? 'var(--bg-primary)' : 'transparent',
                  border: 'none', color: 'var(--text-primary)',
                  cursor: 'pointer', fontSize: 13, textAlign: 'left',
                }}
              >
                <span style={{ fontSize: 16 }}>{l.flag}</span>
                <span style={{ flex: 1 }}>{l.name}</span>
                {active && <span style={{ color: 'var(--primary)' }}>✓</span>}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
