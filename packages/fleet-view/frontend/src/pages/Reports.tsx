import { useEffect, useState } from 'react';
import { fetchVessels, triggerReport } from '../api';
import type { Vessel } from '../types';

const REPORT_TYPES = [
  { id: 'psc_readiness', label: 'PSC Readiness Report' },
  { id: 'class_survey', label: 'Class Survey Report' },
  { id: 'security_audit', label: 'Security Audit (UR E26/E27)' },
  { id: 'cic_compliance', label: 'CIC 2026 Compliance (Cargo Securing)' },
];

interface GeneratedReport {
  reportId: string;
  vesselName: string;
  type: string;
  generatedAt: string;
  status: 'ready' | 'generating';
}

export default function Reports() {
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [selectedVessel, setSelectedVessel] = useState('');
  const [selectedType, setSelectedType] = useState(REPORT_TYPES[0].id);
  const [reports, setReports] = useState<GeneratedReport[]>([
    { reportId: 'RPT-001', vesselName: 'MV Pacific Star', type: 'PSC Readiness Report', generatedAt: '2026-04-28 14:30', status: 'ready' },
    { reportId: 'RPT-002', vesselName: 'MV Blue Horizon', type: 'CIC 2026 Compliance', generatedAt: '2026-04-27 09:15', status: 'ready' },
    { reportId: 'RPT-003', vesselName: 'MV Ocean Harmony', type: 'Security Audit', generatedAt: '2026-04-25 16:00', status: 'ready' },
  ]);

  useEffect(() => { fetchVessels().then(setVessels); }, []);

  const handleGenerate = async () => {
    if (!selectedVessel) { alert('Select a vessel'); return; }
    const vessel = vessels.find(v => v.id === selectedVessel);
    const typeName = REPORT_TYPES.find(t => t.id === selectedType)?.label ?? selectedType;

    const result = await triggerReport(selectedVessel, selectedType);
    setReports(prev => [{
      reportId: result.reportId,
      vesselName: vessel?.name ?? selectedVessel,
      type: typeName,
      generatedAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
      status: 'ready',
    }, ...prev]);
  };

  return (
    <div>
      {/* Generate Report */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="chart-title">Generate Report</div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap', marginTop: 8 }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Vessel</label>
            <select value={selectedVessel} onChange={e => setSelectedVessel(e.target.value)} style={{ minWidth: 200 }}>
              <option value="">Select vessel...</option>
              {vessels.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Report Type</label>
            <select value={selectedType} onChange={e => setSelectedType(e.target.value)} style={{ minWidth: 240 }}>
              {REPORT_TYPES.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate}>Generate</button>
        </div>
      </div>

      {/* Reports List */}
      <div className="card">
        <div className="chart-title">Generated Reports</div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Report ID</th>
              <th>Vessel</th>
              <th>Type</th>
              <th>Generated</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(r => (
              <tr key={r.reportId}>
                <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{r.reportId}</td>
                <td>{r.vesselName}</td>
                <td>{r.type}</td>
                <td>{r.generatedAt}</td>
                <td>
                  <span className={`badge ${r.status === 'ready' ? 'badge-success' : 'badge-warning'}`}>
                    {r.status}
                  </span>
                </td>
                <td>
                  <button className="btn btn-accent" style={{ padding: '4px 10px', fontSize: 12 }}
                    onClick={() => alert(`Downloading ${r.reportId}...`)}>
                    Download PDF
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
