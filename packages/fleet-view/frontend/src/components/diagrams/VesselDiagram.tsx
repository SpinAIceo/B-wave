import { useState, type ComponentType } from 'react';
import { useT, type TranslationKey } from '../../lib/i18n';
import { type Zone } from '../../types';
import GenericShip from './GenericShip';
import ContainerShip from './ContainerShip';
import BulkShip from './BulkShip';
import TankerShip from './TankerShip';
import RoRoShip from './RoRoShip';
import GasShip from './GasShip';
import PassengerShip from './PassengerShip';
import GeneralShip from './GeneralShip';

/**
 * Maps a vessel.type string (case-insensitive) to a decorative SVG art.
 * Falls back to GenericShip for unknown types.
 *
 * Synonyms (mapped to canonical key):
 *   "bulk carrier" → bulk, "tanker" → tanker, "ro-ro" → roro,
 *   "gas carrier" / "lng" → gas, "passenger" → passenger,
 *   "general cargo" → general.
 */
const VESSEL_ART: Record<string, ComponentType> = {
  generic: GenericShip,
  container: ContainerShip,
  bulk: BulkShip,
  tanker: TankerShip,
  roro: RoRoShip,
  gas: GasShip,
  passenger: PassengerShip,
  general: GeneralShip,
};

const TYPE_ALIASES: Record<string, keyof typeof VESSEL_ART> = {
  'bulk carrier': 'bulk',
  bulkcarrier: 'bulk',
  'ro-ro': 'roro',
  'roro': 'roro',
  car: 'roro',
  'gas carrier': 'gas',
  lng: 'gas',
  lpg: 'gas',
  'general cargo': 'general',
  cargo: 'general',
  cruise: 'passenger',
  ferry: 'passenger',
};

interface ZoneRegion {
  id: Zone;
  /** SVG-coordinate hit-box in the 800×300 viewBox. */
  x: number; y: number; w: number; h: number;
  /** Label position (defaults to region center). */
  labelX?: number; labelY?: number;
}

/**
 * Six non-overlapping rectangular hit zones tiling the 800×300 viewBox.
 *
 *   ┌────────┬─────────────┬────────┐
 *   │        │    Deck     │ Stern  │
 *   │        ├─────────────┤        │
 *   │  Bow   │   Midship   ├────────┤
 *   │        ├─────────────┤ Engine │
 *   │        │    Hull     │  Room  │
 *   └────────┴─────────────┴────────┘
 */
const ZONE_LAYOUT: readonly ZoneRegion[] = [
  { id: 'bow',         x: 0,   y: 0,   w: 150, h: 300 },
  { id: 'deck',        x: 150, y: 0,   w: 500, h: 100 },
  { id: 'midship',     x: 150, y: 100, w: 500, h: 100 },
  { id: 'hull',        x: 150, y: 200, w: 500, h: 100 },
  { id: 'stern',       x: 650, y: 0,   w: 150, h: 150 },
  { id: 'engine_room', x: 650, y: 150, w: 150, h: 150 },
] as const;

function zoneI18nKey(zone: Zone): TranslationKey {
  return `zone_${zone}` as TranslationKey;
}

function vesselArtKey(vesselType: string | undefined): keyof typeof VESSEL_ART {
  if (!vesselType) return 'generic';
  const k = vesselType.toLowerCase().trim();
  if (k in VESSEL_ART) return k as keyof typeof VESSEL_ART;
  if (k in TYPE_ALIASES) return TYPE_ALIASES[k];
  return 'generic';
}

interface VesselDiagramProps {
  /** Vessel type string from the vessel record (e.g. 'CONTAINER', 'BULK'). */
  vesselType?: string;
  /** Currently selected zone (highlighted). */
  selectedZone?: Zone | null;
  /** Click handler — null to clear selection. */
  onZoneClick?: (zone: Zone | null) => void;
  /** Number of items per zone (e.g. defect counts) — rendered as a badge. */
  zoneCounts?: Partial<Record<Zone, number>>;
  /** Optional CSS class (sized by parent). */
  className?: string;
  /** Disable interactivity (read-only mode). */
  readOnly?: boolean;
}

export default function VesselDiagram({
  vesselType,
  selectedZone = null,
  onZoneClick,
  zoneCounts = {},
  className,
  readOnly = false,
}: VesselDiagramProps) {
  const t = useT();
  const [hoveredZone, setHoveredZone] = useState<Zone | null>(null);

  const ArtComponent = VESSEL_ART[vesselArtKey(vesselType)];

  const handleClick = (zone: Zone) => {
    if (readOnly || !onZoneClick) return;
    onZoneClick(selectedZone === zone ? null : zone);
  };

  return (
    <svg
      viewBox="0 0 800 300"
      className={className}
      style={{ width: '100%', height: 'auto', userSelect: 'none' }}
    >
      <ArtComponent />

      {/* Clickable zone overlay */}
      {ZONE_LAYOUT.map(({ id, x, y, w, h, labelX, labelY }) => {
        const isSelected = selectedZone === id;
        const isHovered = hoveredZone === id;
        const count = zoneCounts[id] ?? 0;
        const cx = labelX ?? x + w / 2;
        const cy = labelY ?? y + h / 2;
        const showLabel = isHovered || isSelected;

        return (
          <g key={id}>
            <rect
              x={x}
              y={y}
              width={w}
              height={h}
              fill={
                isSelected
                  ? 'rgba(20, 184, 166, 0.28)'
                  : isHovered
                  ? 'rgba(255, 255, 255, 0.08)'
                  : 'transparent'
              }
              stroke={isSelected ? '#14b8a6' : isHovered ? '#90a4ae' : 'transparent'}
              strokeWidth="2"
              style={{ cursor: readOnly ? 'default' : 'pointer', transition: 'fill .15s' }}
              onMouseEnter={() => !readOnly && setHoveredZone(id)}
              onMouseLeave={() => !readOnly && setHoveredZone(null)}
              onClick={() => handleClick(id)}
            />
            {showLabel && (
              <text
                x={cx}
                y={cy}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="#ffffff"
                fontSize="14"
                fontWeight="600"
                style={{ pointerEvents: 'none', textShadow: '0 1px 3px rgba(0,0,0,0.6)' }}
              >
                {t(zoneI18nKey(id))}
              </text>
            )}
            {count > 0 && (
              <g
                transform={`translate(${x + w - 22}, ${y + 22})`}
                style={{ pointerEvents: 'none' }}
              >
                <circle r="13" fill="#f44336" />
                <text
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="#ffffff"
                  fontSize="12"
                  fontWeight="700"
                >
                  {count}
                </text>
              </g>
            )}
          </g>
        );
      })}
    </svg>
  );
}
