import { useState, type FormEvent } from 'react';
import { useAuth } from '../lib/AuthProvider';
import { LoginError } from '../lib/auth';
import { useT } from '../lib/i18n';
import LanguageSwitcher from '../components/LanguageSwitcher';

export default function Login() {
  const t = useT();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError(t('loginRequired'));
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await login(username.trim(), password);
    } catch (err) {
      const msg = err instanceof LoginError && err.status === 401
        ? t('loginInvalidCredentials')
        : err instanceof Error ? err.message : t('loginGenericError');
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-primary)',
    }}>
      <div style={{ position: 'absolute', top: 16, right: 24 }}>
        <LanguageSwitcher />
      </div>
      <div style={{
        background: 'var(--bg-secondary)', padding: '36px 32px',
        borderRadius: 10, border: '1px solid var(--border)',
        width: '100%', maxWidth: 400, boxShadow: '0 8px 30px rgba(0,0,0,0.3)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h1 style={{ fontSize: 28, marginBottom: 4, color: 'var(--text-primary)' }}>B-Wave</h1>
          <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{t('appSubtitle')}</span>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>
              {t('loginUsername')}
            </label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoFocus
              autoComplete="username"
              disabled={submitting}
              style={{
                width: '100%', padding: '10px 12px',
                background: 'var(--bg-primary)', color: 'var(--text-primary)',
                border: '1px solid var(--border)', borderRadius: 6,
                fontSize: 14, boxSizing: 'border-box',
              }}
            />
          </div>

          <div style={{ marginBottom: 18 }}>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>
              {t('loginPassword')}
            </label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
              disabled={submitting}
              style={{
                width: '100%', padding: '10px 12px',
                background: 'var(--bg-primary)', color: 'var(--text-primary)',
                border: '1px solid var(--border)', borderRadius: 6,
                fontSize: 14, boxSizing: 'border-box',
              }}
            />
          </div>

          {error && (
            <div style={{
              marginBottom: 14, padding: '8px 12px',
              background: 'rgba(244, 67, 54, 0.12)', border: '1px solid var(--danger)',
              borderRadius: 6, color: 'var(--danger)', fontSize: 13,
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
            style={{ width: '100%', padding: '10px', fontSize: 14 }}
          >
            {submitting ? t('loginSubmitting') : t('loginSubmit')}
          </button>
        </form>

        <div style={{
          marginTop: 18, paddingTop: 14, borderTop: '1px solid var(--border)',
          fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.6,
        }}>
          {t('loginRolesHint')}
        </div>
      </div>
    </div>
  );
}
