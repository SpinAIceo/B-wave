import { useEffect, useState } from 'react';
import {
  fetchInspections,
  fetchVesselDetections,
  fetchVesselZoneSummary,
  triggerReport,
} from '../api';
import type { Detection, Inspection, Vessel, Zone } from '../types';
import { useT } from '../lib/i18n';
import VesselDiagram from '../components/diagrams/VesselDiagram';

interface Props {
  vessel: Vessel;
  onBack: () => void;
}

export default function VesselDetail({ vessel, onBack }: Props) {
  const t = useT();
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [zoneCounts, setZoneCounts] = useState<Record<Zone, number>>({
    bow: 0, midship: 0, stern: 0, deck: 0, hull: 0, engine_room: 0,
  });
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null);
  const STATUS_LABELS: Record<string, string> = {
    sailing: t('statusSailing'),
    port: t('statusPort'),
    anchor: t('statusAnchor'),
    maintenance: t('statusMaintenance'),
  };

  useEffect(() => {
    fetchInspections(vessel.id).then(setInspections);
    fetchVesselDetections(vessel.id).then(setDetections);
    fetchVesselZoneSummary(vessel.id).then(setZoneCounts);
  }, [vessel.id]);

  const filteredDetections = selectedZone
    ? detections.filter(d => d.zone === selectedZone)
    : detections;

  const handleGenerateReport = async () => {
    const result = await triggerReport(vessel.id, 'psc_readiness');
    alert(`${t('reportGenerated')}: ${result.reportId}`);
  };

  const critCnt = vessel.criticalDefects ?? 0;
  const detRisk = vessel.detentionRisk ?? 0;
  const statusColor = critCnt > 0 ? 'var(--danger)' :
    detRisk > 30 ? 'var(--warning)' : 'var(--success)';

  return (
    <div>
      <button className="btn btn-primary" onClick={onBack} style={{ marginBottom: 16 }}>
        {t('backToFleet')}
      </button>

      {/* Header */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ fontSize: 24, marginBottom: 4 }}>{vessel.name}</h2>
            <div style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
              {vessel.type} · {t('flagLabel')}: {vessel.flag} · {vessel.managementCompany}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className={`badge ${vessel.status === 'sailing' ? 'badge-success' : vessel.status === 'port' ? 'badge-info' : 'badge-warning'}`} style={{ fontSize: 14, padding: '4px 12px' }}>
              {(STATUS_LABELS[vessel.status] ?? vessel.status).toUpperCase()}
            </span>
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-muted)' }}>
              {t('detentionRiskLabel')}: <span style={{ color: statusColor, fontWeight: 700 }}>{detRisk}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Defect Map by Zone */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="chart-title">{t('defectMap')}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 12 }}>
          {t('clickZoneToFilter')}
        </div>
        <div style={{ background: '#0a1628', borderRadius: 8, padding: 16 }}>
          <VesselDiagram
            vesselType={vessel.type}
            selectedZone={selectedZone}
            onZoneClick={setSelectedZone}
            zoneCounts={zoneCounts}
          />
        </div>
        {selectedZone && (
          <div style={{
            marginTop: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '8px 12px', background: 'var(--bg-primary)', borderRadius: 6,
          }}>
            <span style={{ fontSize: 13 }}>
              <strong>{t('defectsInZone', { zone: t(`zone_${selectedZone}` as never) })}</strong>
              {' · '}
              {filteredDetections.length > 0
                ? `${filteredDetections.length}`
                : t('noDefectsInZone')}
            </span>
            <button
              className="btn"
              style={{ padding: '4px 10px', fontSize: 12, background: 'transparent',
                       color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
              onClick={() => setSelectedZone(null)}
            >
              {t('clearFilter')}
            </button>
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Inspection History */}
        <div className="card">
          <div className="chart-title">{t('inspectionHistory')}</div>
          <div className="timeline">
            {inspections.map(ins => (
              <div key={ins.id} className={`timeline-item ${ins.criticalDefects > 0 ? 'critical' : ''}`}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{ins.portOfInspection}</div>
                <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                  {(ins.completedAt ?? ins.startedAt).slice(0, 10)} · {ins.mouRegion} {t('mouSuffix')}
                </div>
                <div style={{ fontSize: 13, marginTop: 4 }}>
                  <span style={{ color: 'var(--success)' }}>{ins.passed} {t('passLabel')}</span>
                  {' / '}
                  <span style={{ color: ins.failed > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>{ins.failed} {t('failLabel')}</span>
                  {ins.criticalDefects > 0 && (
                    <span style={{ color: 'var(--danger)', fontWeight: 700, marginLeft: 8 }}>
                      {ins.criticalDefects} {t('criticalLabel')}
                    </span>
                  )}
                </div>
              </div>
            ))}
            {inspections.length === 0 && (
              <div style={{ color: 'var(--text-muted)', padding: 16 }}>{t('noInspectionsRecorded')}</div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="chart-title">{t('quickActions')}</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 8 }}>
            <button className="btn btn-primary" onClick={handleGenerateReport}>
              {t('generatePscReport')}
            </button>
            <button className="btn btn-accent" onClick={() => alert(t('openingLastInspection'))}>
              {t('viewLastInspection')}
            </button>
            <button className="btn" style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
              onClick={() => alert(t('schedulingInspection'))}>
              {t('scheduleInspection')}
            </button>
          </div>

          <div style={{ marginTop: 24 }}>
            <div className="chart-title">{t('vesselInfo')}</div>
            <table style={{ fontSize: 13 }}>
              <tbody>
                {[
                  [t('infoPosition'),
                    vessel.lat != null && vessel.lng != null
                      ? `${vessel.lat.toFixed(2)}°N, ${vessel.lng.toFixed(2)}°E`
                      : '-'],
                  [t('infoLastInspection'), vessel.lastInspection ?? '-'],
                  [t('infoCriticalDefects'), `${vessel.criticalDefects ?? 0}`],
                  [t('infoDetentionRisk'), `${vessel.detentionRisk ?? 0}%`],
                ].map(([label, value]) => (
                  <tr key={label}>
                    <td style={{ color: 'var(--text-muted)', padding: '4px 16px 4px 0' }}>{label}</td>
                    <td style={{ fontWeight: 600 }}>{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
