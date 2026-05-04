"use client";
import { useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface Vessel {
  id: string;
  name: string;
  flag: string;
  type: string;
  imo: string;
  lat: number;
  lon: number;
  status: string;
  risk_level: string;
  defects: string[];
  last_inspection: string;
  next_port: string;
}

interface Props {
  vessels: Vessel[];
  selected: Vessel | null;
  onSelect: (v: Vessel) => void;
}

const STATUS_COLOR: Record<string, string> = {
  green: "#4ade80",
  yellow: "#facc15",
  red: "#f87171",
};

function FlyTo({ vessel }: { vessel: Vessel | null }) {
  const map = useMap();
  useEffect(() => {
    if (vessel) {
      map.flyTo([vessel.lat, vessel.lon], 6, { duration: 1 });
    }
  }, [vessel, map]);
  return null;
}

export default function FleetMap({ vessels, selected, onSelect }: Props) {
  return (
    <MapContainer
      center={[20, 10]}
      zoom={2}
      style={{ height: "100%", width: "100%", background: "#0a1628" }}
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org">OpenStreetMap</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      <FlyTo vessel={selected} />
      {vessels.map(v => (
        <CircleMarker
          key={v.id}
          center={[v.lat, v.lon]}
          radius={selected?.id === v.id ? 9 : 6}
          pathOptions={{
            color: STATUS_COLOR[v.status],
            fillColor: STATUS_COLOR[v.status],
            fillOpacity: selected?.id === v.id ? 1.0 : 0.75,
            weight: selected?.id === v.id ? 2 : 1,
          }}
          eventHandlers={{ click: () => onSelect(v) }}
        >
          <Popup>
            <div style={{ fontFamily: "monospace", fontSize: 12, minWidth: 160 }}>
              <strong>{v.name}</strong><br />
              {v.flag} · {v.type}<br />
              Risk: <span style={{ color: STATUS_COLOR[v.status], fontWeight: "bold" }}>{v.risk_level.toUpperCase()}</span><br />
              {v.defects.length > 0 && <>Defects: {v.defects.join(", ")}<br /></>}
              Next: {v.next_port}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
