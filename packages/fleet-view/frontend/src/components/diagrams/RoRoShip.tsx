/**
 * Ro-Ro / Car carrier — boxy high-freeboard silhouette.
 * viewBox 800x300.
 */
export default function RoRoShip() {
  return (
    <g>
      {/* Sea band */}
      <rect x="0" y="220" width="800" height="80" fill="#0a1628" opacity="0.4" />

      {/* Lower hull */}
      <path
        d="M 50 220
           L 50 150
           Q 75 130 110 130
           L 740 130
           L 760 150
           L 760 220 Z"
        fill="#1e3a5f"
      />

      {/* Boxy car-deck superstructure (full length, high freeboard) */}
      <rect x="110" y="40" width="630" height="90" fill="#2c5278" />

      {/* Window strip rows (3 levels) */}
      {[55, 75, 95].map(y => (
        <g key={y}>
          {Array.from({ length: 22 }, (_, i) => (
            <rect
              key={i}
              x={130 + i * 27}
              y={y}
              width="20"
              height="8"
              fill="#0a1628"
            />
          ))}
        </g>
      ))}

      {/* Stern ramp suggestion */}
      <path d="M 740 130 L 760 130 L 760 165 L 740 165 Z" fill="#3d6b9a" />

      {/* Bow ramp / breakwater hint */}
      <path d="M 90 130 L 110 130 L 110 165 L 90 145 Z" fill="#3d6b9a" />

      {/* Bridge on top */}
      <rect x="600" y="20" width="100" height="20" fill="#3d6b9a" />
      <rect x="610" y="25" width="80" height="10" fill="#0a1628" />

      {/* Waterline */}
      <line
        x1="50" y1="200" x2="760" y2="200"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
