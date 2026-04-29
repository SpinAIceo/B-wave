import { useEffect, useState } from 'react';
import { fetchInspections, triggerReport } from '../api';
import type { Inspection, Vessel } from '../types';

interface Props {
  vessel: Vessel;
  onBack: () => void;
}

export default function VesselDetail({ vessel, onBack }: Props) {
  const [inspections, setInspections] = useState<Inspection[]>([]);

  useEffect(() => { fetchInspections(vessel.id).then(setInspections); }, [vessel.id]);

  const handleGenerateReport = async () => {
    const result = await triggerReport(vessel.id, 'psc_readiness');
    alert(`Report generated: ${result.reportId}`);
  };

  const statusColor = vessel.criticalDefects > 0 ? 'var(--danger)' :
    vessel.detentionRisk > 30 ? 'var(--warning)' : 'var(--success)';

  return (
    <div>
      <button className="btn btn-primary" onClick={onBack} style={{ marginBottom: 16 }}>
        ← Back to Fleet
      </button>

      {/* Header */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ fontSize: 24, marginBottom: 4 }}>{vessel.name}</h2>
            <div style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
              {vessel.type} · Flag: {vessel.flag} · {vessel.managementCompany}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className={`badge ${vessel.status === 'sailing' ? 'badge-success' : vessel.status === 'port' ? 'badge-info' : 'badge-warning'}`} style={{ fontSize: 14, padding: '4px 12px' }}>
              {vessel.status.toUpperCase()}
            </span>
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-muted)' }}>
              Detention Risk: <span style={{ color: statusColor, fontWeight: 700 }}>{vessel.detentionRisk}%</span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Inspection History */}
        <div className="card">
          <div className="chart-title">Inspection History</div>
          <div className="timeline">
            {inspections.map(ins => (
              <div key={ins.id} className={`timeline-item ${ins.criticalDefects > 0 ? 'critical' : ''}`}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{ins.port}</div>
                <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                  {ins.completedAt.slice(0, 10)} · {ins.mouRegion} MoU
                </div>
                <div style={{ fontSize: 13, marginTop: 4 }}>
                  <span style={{ color: 'var(--success)' }}>{ins.passed} pass</span>
                  {' / '}
                  <span style={{ color: ins.failed > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>{ins.failed} fail</span>
                  {ins.criticalDefects > 0 && (
                    <span style={{ color: 'var(--danger)', fontWeight: 700, marginLeft: 8 }}>
                      {ins.criticalDefects} critical
                    </span>
                  )}
                </div>
              </div>
            ))}
            {inspections.length === 0 && (
              <div style={{ color: 'var(--text-muted)', padding: 16 }}>No inspections recorded</div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="chart-title">Quick Actions</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 8 }}>
            <button className="btn btn-primary" onClick={handleGenerateReport}>
              📋 Generate PSC Readiness Report
            </button>
            <button className="btn btn-accent" onClick={() => alert('Opening last inspection...')}>
              🔍 View Last Inspection
            </button>
            <button className="btn" style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
              onClick={() => alert('Scheduling next inspection...')}>
              📅 Schedule Inspection
            </button>
          </div>

          <div style={{ marginTop: 24 }}>
            <div className="chart-title">Vessel Info</div>
            <table style={{ fontSize: 13 }}>
              <tbody>
                {[
                  ['Position', `${vessel.lat.toFixed(2)}°N, ${vessel.lng.toFixed(2)}°E`],
                  ['Last Inspection', vessel.lastInspection],
                  ['Critical Defects', `${vessel.criticalDefects}`],
                  ['Detention Risk', `${vessel.detentionRisk}%`],
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
