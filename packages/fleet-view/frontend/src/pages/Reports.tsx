import { useEffect, useState } from 'react';
import { fetchVessels, triggerReport } from '../api';
import type { Vessel } from '../types';
import { useT } from '../lib/i18n';

interface GeneratedReport {
  reportId: string;
  vesselName: string;
  typeKey: 'reportPscReadiness' | 'reportClassSurvey' | 'reportSecurityAudit' | 'reportCicCompliance';
  generatedAt: string;
  status: 'ready' | 'generating';
}

export default function Reports() {
  const t = useT();
  const REPORT_TYPES = [
    { id: 'psc_readiness',  labelKey: 'reportPscReadiness'  as const },
    { id: 'class_survey',   labelKey: 'reportClassSurvey'   as const },
    { id: 'security_audit', labelKey: 'reportSecurityAudit' as const },
    { id: 'cic_compliance', labelKey: 'reportCicCompliance' as const },
  ];
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [selectedVessel, setSelectedVessel] = useState('');
  const [selectedType, setSelectedType] = useState(REPORT_TYPES[0].id);
  const [reports, setReports] = useState<GeneratedReport[]>([
    { reportId: 'RPT-001', vesselName: 'MV Pacific Star',  typeKey: 'reportPscReadiness',  generatedAt: '2026-04-28 14:30', status: 'ready' },
    { reportId: 'RPT-002', vesselName: 'MV Blue Horizon',  typeKey: 'reportCicCompliance', generatedAt: '2026-04-27 09:15', status: 'ready' },
    { reportId: 'RPT-003', vesselName: 'MV Ocean Harmony', typeKey: 'reportSecurityAudit', generatedAt: '2026-04-25 16:00', status: 'ready' },
  ]);

  useEffect(() => { fetchVessels().then(setVessels); }, []);

  const handleGenerate = async () => {
    if (!selectedVessel) { alert(t('selectVesselAlert')); return; }
    const vessel = vessels.find(v => v.id === selectedVessel);
    const typeEntry = REPORT_TYPES.find(rt => rt.id === selectedType);

    const result = await triggerReport(selectedVessel, selectedType);
    setReports(prev => [{
      reportId: result.reportId,
      vesselName: vessel?.name ?? selectedVessel,
      typeKey: typeEntry?.labelKey ?? 'reportPscReadiness',
      generatedAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
      status: 'ready',
    }, ...prev]);
  };

  return (
    <div>
      {/* Generate Report */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="chart-title">{t('generateReport')}</div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap', marginTop: 8 }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>{t('vesselLabel')}</label>
            <select value={selectedVessel} onChange={e => setSelectedVessel(e.target.value)} style={{ minWidth: 200 }}>
              <option value="">{t('selectVessel')}</option>
              {vessels.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>{t('reportTypeLabel')}</label>
            <select value={selectedType} onChange={e => setSelectedType(e.target.value)} style={{ minWidth: 240 }}>
              {REPORT_TYPES.map(rt => <option key={rt.id} value={rt.id}>{t(rt.labelKey)}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate}>{t('generateBtn')}</button>
        </div>
      </div>

      {/* Reports List */}
      <div className="card">
        <div className="chart-title">{t('generatedReports')}</div>
        <table className="data-table">
          <thead>
            <tr>
              <th>{t('colReportId')}</th>
              <th>{t('colVessel')}</th>
              <th>{t('rptColType')}</th>
              <th>{t('colGenerated')}</th>
              <th>{t('rptColStatus')}</th>
              <th>{t('colAction')}</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(r => (
              <tr key={r.reportId}>
                <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{r.reportId}</td>
                <td>{r.vesselName}</td>
                <td>{t(r.typeKey)}</td>
                <td>{r.generatedAt}</td>
                <td>
                  <span className={`badge ${r.status === 'ready' ? 'badge-success' : 'badge-warning'}`}>
                    {r.status === 'ready' ? t('statusReady') : t('statusGenerating')}
                  </span>
                </td>
                <td>
                  <button className="btn btn-accent" style={{ padding: '4px 10px', fontSize: 12 }}
                    onClick={() => alert(t('downloading', { id: r.reportId }))}>
                    {t('downloadPdf')}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
