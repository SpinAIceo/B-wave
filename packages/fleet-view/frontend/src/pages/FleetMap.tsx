import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useEffect, useRef, useState } from 'react';
import { fetchVessels } from '../api';
import { useT } from '../lib/i18n';
import type { Vessel } from '../types';

// Set via VITE_MAPBOX_TOKEN env var; falls back to placeholder so the map
// initialises without crashing (tiles will be watermarked / blocked by Mapbox).
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN ?? '';
mapboxgl.accessToken = MAPBOX_TOKEN;

const STATUS_COLOR: Record<string, string> = {
  SAILING: '#4caf50',
  PORT: '#2196f3',
  ANCHOR: '#ff9800',
};

function vesselColor(v: Vessel): string {
  if (v.criticalDefects > 0) return '#f44336';
  if (v.detentionRisk > 30) return '#ff9800';
  return STATUS_COLOR[v.status?.toUpperCase()] ?? '#4caf50';
}

export default function FleetMap() {
  const t = useT();
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markers = useRef<mapboxgl.Marker[]>([]);
  const [vessels, setVessels] = useState<Vessel[]>([]);
  const [noToken] = useState(!MAPBOX_TOKEN);

  // Load vessels
  useEffect(() => { fetchVessels().then(setVessels); }, []);

  // Init map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [100, 20],
      zoom: 2,
      projection: 'mercator',
    });
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Place vessel markers whenever vessels or map change
  useEffect(() => {
    if (!map.current) return;
    // Remove old markers
    markers.current.forEach(m => m.remove());
    markers.current = [];

    vessels.forEach(v => {
      const el = document.createElement('div');
      el.style.cssText = `
        width: 16px; height: 16px; border-radius: 50%;
        background: ${vesselColor(v)};
        border: 2px solid rgba(255,255,255,0.6);
        cursor: pointer;
        box-shadow: 0 0 8px ${vesselColor(v)}88;
      `;

      const popup = new mapboxgl.Popup({ offset: 12, closeButton: false })
        .setHTML(`
          <div style="font-family:monospace;font-size:12px;min-width:160px;">
            <strong>${v.name}</strong><br/>
            ${v.type} · ${v.flag}<br/>
            ${t('status')}: <span style="color:${vesselColor(v)};font-weight:700">
              ${v.status?.toUpperCase() ?? '-'}
            </span><br/>
            ${t('lastInspection')}: ${v.lastInspection ?? '-'}<br/>
            ${t('criticalDefectsLabel')}:
            <span style="color:${v.criticalDefects > 0 ? '#f44336' : '#4caf50'}">
              ${v.criticalDefects}
            </span>
          </div>
        `);

      const marker = new mapboxgl.Marker(el)
        .setLngLat([v.lng, v.lat])
        .setPopup(popup)
        .addTo(map.current!);

      markers.current.push(marker);
    });
  }, [vessels, t]);

  if (noToken) {
    return (
      <div style={{ position: 'relative', width: '100%', height: '100%' }}>
        <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
        <div style={{
          position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          background: 'rgba(10,20,40,0.85)', color: '#90a4ae', gap: 12,
        }}>
          <span style={{ fontSize: 40 }}>🗺️</span>
          <p style={{ margin: 0, fontSize: 14 }}>
            Mapbox token not set. Add{' '}
            <code style={{ background: '#1e3a5f', padding: '2px 6px', borderRadius: 4 }}>
              VITE_MAPBOX_TOKEN
            </code>{' '}
            to <code>.env</code> to enable the live map.
          </p>
          <p style={{ margin: 0, fontSize: 12, color: '#546e7a' }}>
            Vessels are still loaded — token required only for tile rendering.
          </p>
          <div style={{ display: 'flex', gap: 12, marginTop: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
            {vessels.map(v => (
              <div key={v.id} style={{
                background: '#111d33', border: `1px solid ${vesselColor(v)}`,
                borderRadius: 6, padding: '6px 12px', fontSize: 12,
              }}>
                <span style={{ color: vesselColor(v), fontWeight: 700 }}>●</span>{' '}
                {v.name} ({v.flag})
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
      {/* Legend */}
      <div style={{
        position: 'absolute', bottom: 30, right: 10,
        background: 'rgba(17,29,51,0.92)', border: '1px solid #1e3a5f',
        borderRadius: 6, padding: '10px 14px', fontSize: 12, zIndex: 1,
      }}>
        <div style={{ fontWeight: 600, marginBottom: 6, color: '#90a4ae' }}>{t('status')}</div>
        {[
          ['#4caf50', t('legendNoIssues')],
          ['#ff9800', t('legendWarnings')],
          ['#f44336', t('legendCritical')],
        ].map(([color, label]) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: color, display: 'inline-block' }} />
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}
