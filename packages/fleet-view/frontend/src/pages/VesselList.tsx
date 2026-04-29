import { useEffect, useState } from 'react';
import { fetchVessels } from '../api';
import type { Vessel } from '../types';
import VesselDetail from './VesselDetail';

type SortKey = keyof Pick<Vessel, 'name' | 'type' | 'flag' | 'status' | 'lastInspection' | 'criticalDefects' | 'detentionRisk'>;

export default function VesselList() {
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('name');
  const [sortAsc, setSortAsc] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => { fetchVessels().then(setVessels); }, []);

  const filtered = vessels
    .filter(v => v.name.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      const av = a[sortKey], bv = b[sortKey];
      const cmp = typeof av === 'number' ? av - (bv as number) : String(av).localeCompare(String(bv));
      return sortAsc ? cmp : -cmp;
    });

  const handleSort = (key: SortKey) => {
    if (sortKey === key) { setSortAsc(!sortAsc); }
    else { setSortKey(key); setSortAsc(true); }
  };

  const arrow = (key: SortKey) => sortKey === key ? (sortAsc ? ' ▲' : ' ▼') : '';

  const statusBadge = (status: string) => {
    const cls = status === 'sailing' ? 'badge-success' : status === 'port' ? 'badge-info' :
      status === 'anchor' ? 'badge-warning' : 'badge-danger';
    return <span className={`badge ${cls}`}>{status}</span>;
  };

  const riskBadge = (risk: number) => {
    const cls = risk >= 60 ? 'badge-danger' : risk >= 30 ? 'badge-warning' : 'badge-success';
    return <span className={`badge ${cls}`}>{risk}%</span>;
  };

  if (selectedId) {
    const vessel = vessels.find(v => v.id === selectedId);
    if (vessel) return <VesselDetail vessel={vessel} onBack={() => setSelectedId(null)} />;
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <input
          type="text" className="search-input" placeholder="Search vessels..."
          value={search} onChange={e => setSearch(e.target.value)}
        />
        <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{filtered.length} vessels</span>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('name')}>Name{arrow('name')}</th>
              <th onClick={() => handleSort('type')}>Type{arrow('type')}</th>
              <th onClick={() => handleSort('flag')}>Flag{arrow('flag')}</th>
              <th onClick={() => handleSort('status')}>Status{arrow('status')}</th>
              <th onClick={() => handleSort('lastInspection')}>Last Inspection{arrow('lastInspection')}</th>
              <th onClick={() => handleSort('criticalDefects')}>Critical{arrow('criticalDefects')}</th>
              <th onClick={() => handleSort('detentionRisk')}>Detention Risk{arrow('detentionRisk')}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(v => (
              <tr key={v.id} onClick={() => setSelectedId(v.id)} style={{ cursor: 'pointer' }}>
                <td style={{ fontWeight: 600 }}>{v.name}</td>
                <td>{v.type}</td>
                <td>{v.flag}</td>
                <td>{statusBadge(v.status)}</td>
                <td>{v.lastInspection}</td>
                <td style={{ color: v.criticalDefects > 0 ? 'var(--danger)' : 'var(--text-muted)', fontWeight: 600 }}>
                  {v.criticalDefects}
                </td>
                <td>{riskBadge(v.detentionRisk)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
