import { useEffect, useState } from 'react';
import { fetchVessels } from '../api';
import type { Vessel } from '../types';

export default function FleetMap() {
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [tooltip, setTooltip] = useState<{ vessel: Vessel; x: number; y: number } | null>(null);

  useEffect(() => { fetchVessels().then(setVessels); }, []);

  const toX = (lng: number) => ((lng + 180) / 360) * 900;
  const toY = (lat: number) => ((90 - lat) / 180) * 450;

  const statusColor = (v: Vessel) => {
    if (v.criticalDefects > 0) return '#f44336';
    if (v.detentionRisk > 30) return '#ff9800';
    return '#4caf50';
  };

  return (
    <div className="fleet-map-container">
      <svg width="100%" height="100%" viewBox="0 0 900 450" style={{ background: '#0d1f3c' }}>
        {/* Simplified continent outlines */}
        <rect x={0} y={0} width={900} height={450} fill="#0d1f3c" />
        {/* Grid lines */}
        {[0, 90, 180, 270, 360, 450, 540, 630, 720, 810, 900].map(x => (
          <line key={`vl${x}`} x1={x} y1={0} x2={x} y2={450} stroke="#1a2d4a" strokeWidth={0.5} />
        ))}
        {[0, 75, 150, 225, 300, 375, 450].map(y => (
          <line key={`hl${y}`} x1={0} y1={y} x2={900} y2={y} stroke="#1a2d4a" strokeWidth={0.5} />
        ))}
        {/* Simplified land masses */}
        <ellipse cx={250} cy={140} rx={90} ry={50} fill="#162744" opacity={0.6} /> {/* Europe */}
        <ellipse cx={250} cy={260} rx={60} ry={80} fill="#162744" opacity={0.6} /> {/* Africa */}
        <ellipse cx={500} cy={170} rx={150} ry={80} fill="#162744" opacity={0.6} /> {/* Asia */}
        <ellipse cx={700} cy={350} rx={50} ry={30} fill="#162744" opacity={0.6} /> {/* Australia */}
        <ellipse cx={130} cy={180} rx={60} ry={100} fill="#162744" opacity={0.6} /> {/* Americas */}

        {/* Vessel markers */}
        {vessels.map(v => {
          const cx = toX(v.lng);
          const cy = toY(v.lat);
          return (
            <g key={v.id}
              onMouseEnter={(e) => setTooltip({ vessel: v, x: e.clientX, y: e.clientY })}
              onMouseLeave={() => setTooltip(null)}
              style={{ cursor: 'pointer' }}
            >
              <circle cx={cx} cy={cy} r={12} fill={statusColor(v)} opacity={0.3} />
              <circle cx={cx} cy={cy} r={6} fill={statusColor(v)} />
              <text x={cx} y={cy - 16} textAnchor="middle" fill="#90a4ae" fontSize={9}>{v.name}</text>
            </g>
          );
        })}
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div style={{
          position: 'fixed', left: tooltip.x + 12, top: tooltip.y + 12,
          background: '#111d33', border: '1px solid #1e3a5f', borderRadius: 6,
          padding: '10px 14px', fontSize: 13, zIndex: 100, pointerEvents: 'none',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
        }}>
          <div style={{ fontWeight: 700, marginBottom: 4 }}>{tooltip.vessel.name}</div>
          <div style={{ color: '#90a4ae' }}>
            {tooltip.vessel.type} · {tooltip.vessel.flag}<br />
            Status: <span style={{ color: statusColor(tooltip.vessel), fontWeight: 600 }}>{tooltip.vessel.status}</span><br />
            Last Inspection: {tooltip.vessel.lastInspection}<br />
            Critical Defects: <span style={{ color: tooltip.vessel.criticalDefects > 0 ? '#f44336' : '#4caf50' }}>
              {tooltip.vessel.criticalDefects}
            </span>
          </div>
        </div>
      )}

      {/* Legend */}
      <div style={{
        position: 'absolute', bottom: 20, right: 20,
        background: 'rgba(17,29,51,0.9)', border: '1px solid #1e3a5f',
        borderRadius: 6, padding: 12, fontSize: 12,
      }}>
        <div style={{ fontWeight: 600, marginBottom: 6, color: '#90a4ae' }}>Status</div>
        {([['#4caf50', 'No Issues'], ['#ff9800', 'Warnings'], ['#f44336', 'Critical']] as const).map(([color, label]) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: color, display: 'inline-block' }} />
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}
