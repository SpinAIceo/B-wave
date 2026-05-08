import { useEffect, useMemo, useRef, useState } from 'react';
import * as d3 from 'd3';
import { fetchDashboardOverview, fetchInspections, fetchVessels } from '../api';
import type { DashboardOverview, DefectType, Inspection, Vessel } from '../types';
import { DEFECT_COLORS } from '../types';
import { useT } from '../lib/i18n';

export default function Dashboard() {
  const t = useT();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [vessels, setVessels] = useState<Vessel[]>([]);

  useEffect(() => {
    fetchDashboardOverview().then(setOverview);
    fetchInspections().then(setInspections);
    fetchVessels().then(setVessels);
  }, []);

  const vesselNameById = useMemo(
    () => Object.fromEntries(vessels.map(v => [v.id, v.name])),
    [vessels],
  );

  const defectLabels: Record<DefectType, string> = {
    rust: t('defectRust'),
    damage: t('defectDamage'),
    leak: t('defectLeak'),
    missing_label: t('defectMissingLabel'),
    cargo_lashing: t('defectCargoLashing'),
  };
  const statusLabels: Record<string, string> = {
    sailing: t('statusSailing'),
    port: t('statusPort'),
    anchor: t('statusAnchor'),
    maintenance: t('statusMaintenance'),
  };

  if (!overview) return <div>{t('loading')}</div>;

  return (
    <div>
      <div className="stats-grid">
        <StatCard label={t('totalVessels')} value={overview.totalVessels} color="var(--primary)" trend={t('trendThisMonth')} up />
        <StatCard label={t('activeInspections')} value={overview.activeInspections} color="var(--accent)" trend={t('trendOngoing')} />
        <StatCard label={t('criticalDefects')} value={overview.criticalDefects} color="var(--danger)" trend={t('trendVsLastWeek')} up />
        <StatCard label={t('detentionRisk')} value={overview.detentionRiskScore} color="var(--warning)" trend={t('trendScoreOf100')} />
      </div>

      <div className="charts-grid">
        <div className="card">
          <div className="chart-title">{t('defectDistribution')}</div>
          <DefectBarChart data={overview.defectDistribution} labels={defectLabels} />
        </div>
        <div className="card">
          <div className="chart-title">{t('fleetStatus')}</div>
          <StatusDonut data={overview.vesselsByStatus} labels={statusLabels} />
        </div>
      </div>

      <div className="card">
        <div className="chart-title">{t('recentInspections')}</div>
        <table className="data-table">
          <thead>
            <tr>
              <th>{t('vessel')}</th>
              <th>{t('port')}</th>
              <th>{t('date')}</th>
              <th>{t('result')}</th>
              <th>{t('critical')}</th>
            </tr>
          </thead>
          <tbody>
            {inspections.slice(0, 10).map(ins => (
              <tr key={ins.id}>
                <td>{ins.vesselName ?? vesselNameById[ins.vesselId] ?? ins.vesselId}</td>
                <td>{ins.portOfInspection}</td>
                <td>{(ins.completedAt ?? ins.startedAt).slice(0, 10)}</td>
                <td>
                  <span className={`badge ${ins.failed > 0 ? 'badge-danger' : 'badge-success'}`}>
                    {ins.failed > 0 ? t('fail') : t('pass')}
                  </span>
                </td>
                <td style={{ color: ins.criticalDefects > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>
                  {ins.criticalDefects}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value, color, trend, up }: {
  label: string; value: number; color: string; trend?: string; up?: boolean;
}) {
  return (
    <div className="stat-card">
      <span className="stat-label">{label}</span>
      <span className="stat-value" style={{ color }}>{value}</span>
      {trend && <span className={`stat-trend ${up ? 'up' : ''}`}>{trend}</span>}
    </div>
  );
}

function DefectBarChart({ data, labels }: { data: Record<DefectType, number>; labels: Record<DefectType, string> }) {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();

    const width = 500, height = 200, margin = { top: 10, right: 20, bottom: 10, left: 100 };
    const entries = (Object.entries(data) as [DefectType, number][]).sort((a, b) => b[1] - a[1]);

    const x = d3.scaleLinear()
      .domain([0, d3.max(entries, d => d[1]) ?? 1])
      .range([0, width - margin.left - margin.right]);

    const y = d3.scaleBand<string>()
      .domain(entries.map(d => d[0]))
      .range([margin.top, height - margin.bottom])
      .padding(0.3);

    const g = svg.append('g').attr('transform', `translate(${margin.left},0)`);

    g.selectAll('rect')
      .data(entries)
      .join('rect')
      .attr('y', d => y(d[0]) ?? 0)
      .attr('height', y.bandwidth())
      .attr('width', d => x(d[1]))
      .attr('fill', d => DEFECT_COLORS[d[0]])
      .attr('rx', 4);

    g.selectAll('.label')
      .data(entries)
      .join('text')
      .attr('x', -8)
      .attr('y', d => (y(d[0]) ?? 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'end')
      .attr('fill', '#90a4ae')
      .attr('font-size', 12)
      .text(d => labels[d[0]]);

    g.selectAll('.count')
      .data(entries)
      .join('text')
      .attr('x', d => x(d[1]) + 6)
      .attr('y', d => (y(d[0]) ?? 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('fill', '#e0e0e0')
      .attr('font-size', 12)
      .attr('font-weight', 600)
      .text(d => d[1]);
  }, [data, labels]);

  return <svg ref={ref} width={500} height={200} />;
}

function StatusDonut({ data, labels }: { data: Record<string, number>; labels: Record<string, string> }) {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();

    const STATUS_COLORS_MAP: Record<string, string> = {
      sailing: '#4caf50',
      port: '#2196f3',
      anchor: '#ff9800',
      maintenance: '#f44336',
    };

    const size = 200, radius = size / 2 - 10;
    const entries = Object.entries(data) as [string, number][];

    const pieGen = d3.pie<[string, number]>().value(d => d[1]).sort(null);
    const arcGen = d3.arc<d3.PieArcDatum<[string, number]>>()
      .innerRadius(radius * 0.55)
      .outerRadius(radius);

    const g = svg.append('g').attr('transform', `translate(${size / 2},${size / 2})`);

    g.selectAll('path')
      .data(pieGen(entries))
      .join('path')
      .attr('d', arcGen)
      .attr('fill', d => STATUS_COLORS_MAP[d.data[0]] ?? '#666');

    g.selectAll('text')
      .data(pieGen(entries))
      .join('text')
      .attr('transform', d => `translate(${arcGen.centroid(d)})`)
      .attr('text-anchor', 'middle')
      .attr('fill', 'white')
      .attr('font-size', 10)
      .attr('font-weight', 600)
      .text(d => labels[d.data[0]] ?? d.data[0]);
  }, [data, labels]);

  return <svg ref={ref} width={200} height={200} />;
}
