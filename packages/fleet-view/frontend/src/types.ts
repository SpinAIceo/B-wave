export type VesselStatus = 'sailing' | 'port' | 'anchor' | 'maintenance';
export type DefectType = 'rust' | 'damage' | 'leak' | 'missing_label' | 'cargo_lashing';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type MoURegion = 'Tokyo' | 'Paris' | 'Indian Ocean' | 'Abuja' | 'USCG';

export const ZONES = ['bow', 'midship', 'stern', 'deck', 'hull', 'engine_room'] as const;
export type Zone = typeof ZONES[number];
export const DEFAULT_ZONE: Zone = 'midship';

export interface Vessel {
  id: string;
  name: string;
  type: string;
  flag: string;
  managementCompany: string;
  /** Backend exposes `latitude` (snake → camel). `lat` kept for legacy mock compat. */
  latitude?: number;
  longitude?: number;
  /** Legacy mock fields — populated when displaying mock data. */
  lat?: number;
  lng?: number;
  status: VesselStatus | string;  // backend returns "PORT"/"SAILING" uppercase enum
  /** Backend: `last_psc_inspection`. */
  lastPscInspection?: string;
  /** Computed (mock-only). */
  lastInspection?: string;
  /** Mock/computed display fields — backend may not expose these directly. */
  criticalDefects?: number;
  detentionRisk?: number;
  edgeServerId?: string;
  detentionHistory?: unknown[];
  subscriptionTier?: string;
}

export interface Inspection {
  id: string;
  vesselId: string;
  /** Mock-only display field; computed from vessels list when backend doesn't expose it. */
  vesselName?: string;
  /** Backend: `port_of_inspection`. */
  portOfInspection: string;
  mouRegion: MoURegion | string;
  startedAt: string;
  completedAt?: string;
  totalItems: number;
  passed: number;
  failed: number;
  criticalDefects: number;
  inspectorId?: string;
  synced?: boolean;
  syncedAt?: string;
}

export interface Detection {
  id: string;
  defectType: DefectType;
  confidence: number;
  pscCode: string;
  severity: Severity;
  bbox: { xMin: number; yMin: number; xMax: number; yMax: number };
  zone: Zone;
}

export interface DashboardOverview {
  totalVessels: number;
  activeInspections: number;
  criticalDefects: number;
  detentionRiskScore: number;
  vesselsByStatus: Record<VesselStatus, number>;
  defectDistribution: Record<DefectType, number>;
}

export interface SyncEvent {
  id: string;
  vesselId: string;
  recordsReceived: number;
  syncedAt: string;
  status: 'success' | 'partial' | 'failed';
}

export const DEFECT_COLORS: Record<DefectType, string> = {
  rust: '#ff9800',
  damage: '#f44336',
  leak: '#2196f3',
  missing_label: '#ffeb3b',
  cargo_lashing: '#9c27b0',
};

export const DEFECT_LABELS: Record<DefectType, string> = {
  rust: '부식',
  damage: '손상',
  leak: '누수',
  missing_label: '라벨 누락',
  cargo_lashing: '화물 결박',
};

export const STATUS_COLORS: Record<VesselStatus, string> = {
  sailing: '#4caf50',
  port: '#2196f3',
  anchor: '#ff9800',
  maintenance: '#f44336',
};
