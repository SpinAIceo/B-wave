/**
 * Bulk Carrier — flat silhouette with hatch covers along deck.
 * viewBox 800x300.
 */
const HATCH_FILL = '#3d6b9a';

export default function BulkShip() {
  const hatchY = 80;
  const hatchH = 18;
  const hatches = [170, 250, 330, 410, 490, 570];

  return (
    <g>
      {/* Sea band */}
      <rect x="0" y="220" width="800" height="80" fill="#0a1628" opacity="0.4" />

      {/* Hull */}
      <path
        d="M 50 220
           L 50 140
           Q 75 105 130 100
           L 700 100
           L 760 130
           L 760 220 Z"
        fill="#1e3a5f"
      />

      {/* Deck plate (raised) */}
      <rect x="135" y="95" width="565" height="8" fill="#2c5278" />

      {/* Hatch covers */}
      {hatches.map(x => (
        <g key={x}>
          <rect x={x} y={hatchY - hatchH} width="60" height={hatchH} fill={HATCH_FILL} />
          <rect x={x + 4} y={hatchY - hatchH + 3} width="52" height="3" fill="#2c5278" />
        </g>
      ))}

      {/* Bridge / superstructure (aft) */}
      <rect x="615" y="50" width="80" height="50" fill="#2c5278" />
      <rect x="625" y="62" width="14" height="20" fill="#1e3a5f" />
      <rect x="650" y="62" width="14" height="20" fill="#1e3a5f" />
      <rect x="675" y="62" width="14" height="20" fill="#1e3a5f" />

      {/* Funnel */}
      <rect x="640" y="20" width="22" height="30" fill="#4a7ab0" />

      {/* Deck cranes */}
      {[210, 360, 510].map(x => (
        <g key={x}>
          <rect x={x - 1} y="50" width="3" height="35" fill="#90a4ae" />
          <line x1={x} y1="55" x2={x + 30} y2="80" stroke="#90a4ae" strokeWidth="2" />
        </g>
      ))}

      {/* Waterline */}
      <line
        x1="50" y1="195" x2="760" y2="195"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
