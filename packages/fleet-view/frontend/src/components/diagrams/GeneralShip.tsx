/**
 * General Cargo — traditional silhouette with derrick cranes.
 * viewBox 800x300.
 */
export default function GeneralShip() {
  const masts = [220, 380, 540];

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

      {/* Deck plate */}
      <rect x="135" y="95" width="565" height="8" fill="#2c5278" />

      {/* Derrick masts + booms */}
      {masts.map(x => (
        <g key={x}>
          <rect x={x - 2} y="35" width="4" height="60" fill="#90a4ae" />
          {/* boom going forward */}
          <line x1={x} y1="55" x2={x - 50} y2="80" stroke="#90a4ae" strokeWidth="2.5" />
          {/* boom going aft */}
          <line x1={x} y1="55" x2={x + 50} y2="80" stroke="#90a4ae" strokeWidth="2.5" />
          {/* Top platform */}
          <rect x={x - 5} y="32" width="10" height="4" fill="#90a4ae" />
        </g>
      ))}

      {/* Hatch openings (3 cargo holds, simple) */}
      {[170, 330, 490].map(x => (
        <rect key={x} x={x} y="80" width="80" height="15" fill="#3d6b9a" />
      ))}

      {/* Bridge */}
      <rect x="615" y="50" width="80" height="50" fill="#2c5278" />
      <rect x="625" y="62" width="14" height="20" fill="#1e3a5f" />
      <rect x="650" y="62" width="14" height="20" fill="#1e3a5f" />
      <rect x="675" y="62" width="14" height="20" fill="#1e3a5f" />

      {/* Funnel */}
      <rect x="640" y="22" width="22" height="28" fill="#4a7ab0" />

      {/* Bow forecastle */}
      <rect x="80" y="85" width="50" height="15" fill="#2c5278" />

      {/* Waterline */}
      <line
        x1="50" y1="195" x2="760" y2="195"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
