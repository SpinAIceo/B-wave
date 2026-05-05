import { useEffect, useState, useCallback } from 'react';
import { useT } from '../lib/i18n';
import { logger } from '../lib/logger';

const API_BASE = (import.meta.env.VITE_API_URL ?? '') + '/api/v1';
const IS_LIVE   = !!import.meta.env.VITE_API_URL;

interface ErrorLog {
  id: number;
  ts: string;
  level: string;
  req_id: string;
  module: string;
  message: string;
}

interface LogsResponse {
  count: number;
  filters: { level: string | null; req_id: string | null; limit: number };
  logs: ErrorLog[];
}

const LEVEL_STYLE: Record<string, string> = {
  ERROR:   'background:#ff3b3b22;color:#ff3b3b;border:1px solid #ff3b3b44',
  WARNING: 'background:#ff950022;color:#ff9500;border:1px solid #ff950044',
};

export default function LogViewer() {
  const t = useT();
  const [logs, setLogs]         = useState<ErrorLog[]>([]);
  const [total, setTotal]       = useState(0);
  const [loading, setLoading]   = useState(false);
  const [level, setLevel]       = useState<string>('');
  const [reqId, setReqId]       = useState('');
  const [expanded, setExpanded] = useState<number | null>(null);

  const fetchLogs = useCallback(async () => {
    if (!IS_LIVE) {
      logger.warn('LogViewer', 'API_URL 미설정 — 로그 조회 불가 (VITE_API_URL 필요)');
      return;
    }
    setLoading(true);
    const params = new URLSearchParams({ limit: '200' });
    if (level)  params.set('level', level);
    if (reqId.trim()) params.set('req_id', reqId.trim());
    const url = `${API_BASE}/logs?${params}`;
    logger.info('LogViewer', `[STEP 1/2] GET ${url}`);
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: LogsResponse = await res.json();
      logger.info('LogViewer', `[STEP 2/2] 수신 count=${data.count} level=${level || 'ALL'} req_id=${reqId || 'ALL'}`);
      setLogs(data.logs);
      setTotal(data.count);
    } catch (e) {
      logger.error('LogViewer', `로그 조회 실패: ${e instanceof Error ? e.message : e}`);
    } finally {
      setLoading(false);
    }
  }, [level, reqId]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const clearLogs = async () => {
    if (!confirm(t('logsClearConfirm'))) return;
    logger.info('LogViewer', 'DELETE /api/v1/logs — 전체 삭제 요청');
    try {
      await fetch(`${API_BASE}/logs`, { method: 'DELETE' });
      setLogs([]); setTotal(0);
      logger.info('LogViewer', '전체 삭제 완료');
    } catch (e) {
      logger.error('LogViewer', `삭제 실패: ${e instanceof Error ? e.message : e}`);
    }
  };

  const fmtTs = (ts: string) => {
    try { return new Date(ts).toLocaleString('ko-KR', { hour12: false }); }
    catch { return ts; }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'monospace' }}>
      <h2 style={{ color: '#e2e8f0', marginBottom: 4 }}>{t('logsTitle')}</h2>
      <p style={{ color: '#94a3b8', marginBottom: 20, fontSize: 13 }}>{t('logsDesc')}</p>

      {!IS_LIVE && (
        <div style={{ background: '#ff950022', border: '1px solid #ff9500', borderRadius: 8, padding: '12px 16px', marginBottom: 16, color: '#ff9500', fontSize: 13 }}>
          ⚠ VITE_API_URL 미설정 — 로그 조회는 실제 백엔드 연결 시 작동합니다.
        </div>
      )}

      {/* ── 필터 바 ─────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <select
          value={level}
          onChange={e => setLevel(e.target.value)}
          style={{ background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: '6px 10px', fontSize: 13 }}
        >
          <option value="">{t('logsFilterAll')}</option>
          <option value="ERROR">ERROR만</option>
          <option value="WARNING">WARNING만</option>
        </select>

        <input
          placeholder="Request-ID (예: AB12CD34)"
          value={reqId}
          onChange={e => setReqId(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && fetchLogs()}
          style={{ background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: '6px 12px', fontSize: 13, width: 220 }}
        />

        <button
          onClick={fetchLogs}
          style={{ background: '#0d9488', color: '#fff', border: 'none', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', fontSize: 13 }}
        >
          {t('logsBtnRefresh')}
        </button>

        <button
          onClick={clearLogs}
          style={{ background: '#7f1d1d', color: '#fca5a5', border: '1px solid #991b1b', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', fontSize: 13 }}
        >
          {t('logsBtnClear')}
        </button>

        <span style={{ color: '#64748b', fontSize: 12, marginLeft: 'auto' }}>
          {loading ? t('logsLoading') : `총 ${total}건`}
        </span>
      </div>

      {/* ── 로그 테이블 ──────────────────────────────────────────────────── */}
      {logs.length === 0 && !loading ? (
        <div style={{ color: '#64748b', textAlign: 'center', padding: '40px 0', fontSize: 14 }}>
          {t('logsEmpty')}
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ background: '#0f172a', color: '#94a3b8' }}>
                {[t('logsColTs'), t('logsColLevel'), t('logsColReqId'), t('logsColModule'), t('logsColMessage')].map(h => (
                  <th key={h} style={{ padding: '8px 10px', textAlign: 'left', borderBottom: '1px solid #1e293b', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map(row => (
                <>
                  <tr
                    key={row.id}
                    onClick={() => setExpanded(expanded === row.id ? null : row.id)}
                    style={{ borderBottom: '1px solid #1e293b', cursor: 'pointer', background: expanded === row.id ? '#1e293b' : 'transparent' }}
                  >
                    <td style={{ padding: '7px 10px', color: '#94a3b8', whiteSpace: 'nowrap' }}>{fmtTs(row.ts)}</td>
                    <td style={{ padding: '7px 10px' }}>
                      <span style={{ borderRadius: 4, padding: '2px 7px', fontSize: 11, fontWeight: 700, ...(LEVEL_STYLE[row.level] ? Object.fromEntries(LEVEL_STYLE[row.level].split(';').map(s => { const [k,v] = s.split(':'); return [k?.trim().replace(/-([a-z])/g, (_,c) => c.toUpperCase()), v?.trim()]; }).filter(([k]) => k)) : {}) }}>
                        {row.level}
                      </span>
                    </td>
                    <td style={{ padding: '7px 10px', color: '#7dd3fc', fontFamily: 'monospace' }}>{row.req_id || '-'}</td>
                    <td style={{ padding: '7px 10px', color: '#a78bfa' }}>{row.module}</td>
                    <td style={{ padding: '7px 10px', color: '#e2e8f0', maxWidth: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{row.message}</td>
                  </tr>
                  {expanded === row.id && (
                    <tr key={`${row.id}-exp`} style={{ background: '#0f172a' }}>
                      <td colSpan={5} style={{ padding: '12px 16px' }}>
                        <pre style={{ margin: 0, color: '#e2e8f0', fontSize: 12, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                          {JSON.stringify(row, null, 2)}
                        </pre>
                        <button
                          onClick={() => { setReqId(row.req_id); fetchLogs(); }}
                          style={{ marginTop: 8, background: '#1e3a5f', color: '#7dd3fc', border: '1px solid #1e40af', borderRadius: 4, padding: '4px 10px', cursor: 'pointer', fontSize: 11 }}
                        >
                          이 Request-ID로 필터
                        </button>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
