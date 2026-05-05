import type {
  DashboardOverview,
  Detection,
  Inspection,
  Vessel,
} from './types';
import { logger } from './lib/logger';

const API_BASE = (import.meta.env.VITE_API_URL ?? '') + '/api/v1';
const USE_MOCKS = !import.meta.env.VITE_API_URL || import.meta.env.VITE_USE_MOCKS === 'true';

logger.info('api', `mode=${USE_MOCKS ? 'MOCK' : 'LIVE'} base=${API_BASE}`);

async function fetchOrMock<T>(label: string, fetcher: () => Promise<T>, mockData: T): Promise<T> {
  if (USE_MOCKS) {
    logger.debug('api', `[mock] ${label}`);
    return mockData;
  }
  const timer = logger.time('api', label);
  try {
    const result = await fetcher();
    timer.end('OK');
    return result;
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    logger.warn('api', `${label} FAILED (${msg}) — falling back to mock`);
    return mockData;
  }
}

const MOCK_VESSELS: Vessel[] = [
  {
    id: 'V001', name: 'MV Pacific Star', type: 'Bulk Carrier', flag: 'KR',
    managementCompany: 'Spinai Maritime', lat: 35.1, lng: 129.0,
    status: 'sailing', lastInspection: '2026-04-25', criticalDefects: 1, detentionRisk: 35,
  },
  {
    id: 'V002', name: 'MV Ocean Harmony', type: 'Container', flag: 'PA',
    managementCompany: 'Spinai Maritime', lat: 1.26, lng: 103.8,
    status: 'port', lastInspection: '2026-04-20', criticalDefects: 0, detentionRisk: 12,
  },
  {
    id: 'V003', name: 'MV Blue Horizon', type: 'Tanker', flag: 'LR',
    managementCompany: 'Spinai Maritime', lat: 51.9, lng: 4.5,
    status: 'anchor', lastInspection: '2026-04-15', criticalDefects: 3, detentionRisk: 78,
  },
  {
    id: 'V004', name: 'MV Northern Wind', type: 'Bulk Carrier', flag: 'MH',
    managementCompany: 'Spinai Maritime', lat: 31.2, lng: 121.5,
    status: 'sailing', lastInspection: '2026-04-22', criticalDefects: 0, detentionRisk: 8,
  },
  {
    id: 'V005', name: 'MV Coral Venture', type: 'Container', flag: 'SG',
    managementCompany: 'Spinai Maritime', lat: 22.3, lng: 114.2,
    status: 'maintenance', lastInspection: '2026-04-10', criticalDefects: 2, detentionRisk: 62,
  },
];

const MOCK_INSPECTIONS: Inspection[] = [
  { id: 'I001', vesselId: 'V001', vesselName: 'MV Pacific Star', port: 'Busan', mouRegion: 'Tokyo', startedAt: '2026-04-25T08:00', completedAt: '2026-04-25T10:30', totalItems: 15, passed: 12, failed: 3, criticalDefects: 1 },
  { id: 'I002', vesselId: 'V002', vesselName: 'MV Ocean Harmony', port: 'Singapore', mouRegion: 'Tokyo', startedAt: '2026-04-20T09:00', completedAt: '2026-04-20T11:00', totalItems: 15, passed: 15, failed: 0, criticalDefects: 0 },
  { id: 'I003', vesselId: 'V003', vesselName: 'MV Blue Horizon', port: 'Rotterdam', mouRegion: 'Paris', startedAt: '2026-04-15T07:00', completedAt: '2026-04-15T10:00', totalItems: 15, passed: 10, failed: 5, criticalDefects: 3 },
  { id: 'I004', vesselId: 'V004', vesselName: 'MV Northern Wind', port: 'Shanghai', mouRegion: 'Tokyo', startedAt: '2026-04-22T06:30', completedAt: '2026-04-22T08:00', totalItems: 15, passed: 14, failed: 1, criticalDefects: 0 },
  { id: 'I005', vesselId: 'V005', vesselName: 'MV Coral Venture', port: 'Hong Kong', mouRegion: 'Tokyo', startedAt: '2026-04-10T08:00', completedAt: '2026-04-10T11:30', totalItems: 15, passed: 11, failed: 4, criticalDefects: 2 },
  { id: 'I006', vesselId: 'V001', vesselName: 'MV Pacific Star', port: 'Yokohama', mouRegion: 'Tokyo', startedAt: '2026-04-18T09:00', completedAt: '2026-04-18T11:00', totalItems: 15, passed: 13, failed: 2, criticalDefects: 0 },
];

const MOCK_OVERVIEW: DashboardOverview = {
  totalVessels: 5,
  activeInspections: 2,
  criticalDefects: 6,
  detentionRiskScore: 39,
  vesselsByStatus: { sailing: 2, port: 1, anchor: 1, maintenance: 1 },
  defectDistribution: { rust: 12, damage: 5, leak: 8, missing_label: 3, cargo_lashing: 7 },
};

export function fetchVessels(): Promise<Vessel[]> {
  return fetchOrMock(
    'GET /api/v1/vessels',
    () => fetch(`${API_BASE}/vessels`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    MOCK_VESSELS,
  );
}

export function fetchVessel(id: string): Promise<Vessel | undefined> {
  return fetchOrMock(
    `GET /api/v1/vessels/${id}`,
    () => fetch(`${API_BASE}/vessels/${id}`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    MOCK_VESSELS.find(v => v.id === id),
  );
}

export function fetchDashboardOverview(): Promise<DashboardOverview> {
  return fetchOrMock(
    'GET /api/v1/dashboard/overview',
    () => fetch(`${API_BASE}/dashboard/overview`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    MOCK_OVERVIEW,
  );
}

export function fetchInspections(vesselId?: string): Promise<Inspection[]> {
  const filtered = vesselId
    ? MOCK_INSPECTIONS.filter(i => i.vesselId === vesselId)
    : MOCK_INSPECTIONS;
  return fetchOrMock(
    `GET /api/v1/vessels/${vesselId ?? 'all'}/inspections`,
    () => fetch(`${API_BASE}/vessels/${vesselId ?? 'all'}/inspections`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    filtered,
  );
}

export function fetchDetections(inspectionId: string): Promise<Detection[]> {
  return fetchOrMock(
    `GET /api/v1/inspections/${inspectionId}/detections`,
    () => fetch(`${API_BASE}/inspections/${inspectionId}/detections`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    [],
  );
}

export function triggerReport(vesselId: string, type: string): Promise<{ reportId: string }> {
  logger.info('api', `triggerReport vessel=${vesselId} type=${type}`);
  return fetchOrMock(
    'POST /api/v1/reports/generate',
    () => fetch(`${API_BASE}/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vessel_id: vesselId, report_type: type }),
    }).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    { reportId: `RPT-${vesselId}-${type}-${Date.now()}` },
  );
}
