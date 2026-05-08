/**
 * LNG / Gas Carrier — visible spherical Moss-type tanks on deck.
 * viewBox 800x300.
 */
export default function GasShip() {
  const tanks = [220, 350, 480, 590];
  const tankR = 50;
  const tankCY = 70;

  return (
    <g>
      {/* Sea band */}
      <rect x="0" y="220" width="800" height="80" fill="#0a1628" opacity="0.4" />

      {/* Hull */}
      <path
        d="M 50 220
           L 50 145
           Q 75 110 130 105
           L 700 105
           L 760 135
           L 760 220 Z"
        fill="#1e3a5f"
      />

      {/* Deck */}
      <rect x="135" y="100" width="565" height="8" fill="#2c5278" />

      {/* Spherical Moss-type tanks (clipped to top half) */}
      {tanks.map(cx => (
        <g key={cx}>
          {/* Tank skirt support */}
          <rect x={cx - tankR + 6} y="100" width={(tankR - 6) * 2} height="8" fill="#3d6b9a" />
          {/* Sphere (using clip path effect via half-sphere with arc) */}
          <path
            d={`M ${cx - tankR} 100
                A ${tankR} ${tankR} 0 0 1 ${cx + tankR} 100 Z`}
            fill="#90a4ae"
            stroke="#6ba3d8"
            strokeWidth="1"
          />
          {/* Highlight */}
          <ellipse cx={cx - 14} cy={tankCY - 6} rx="14" ry="8" fill="#c5d4dc" opacity="0.5" />
        </g>
      ))}

      {/* Bridge (forward of stern, between tanks and stern) */}
      <rect x="635" y="50" width="65" height="55" fill="#2c5278" />
      <rect x="645" y="62" width="12" height="16" fill="#1e3a5f" />
      <rect x="667" y="62" width="12" height="16" fill="#1e3a5f" />

      {/* Funnel */}
      <rect x="655" y="22" width="22" height="28" fill="#4a7ab0" />

      {/* Bow castle */}
      <rect x="100" y="85" width="40" height="20" fill="#2c5278" />

      {/* Waterline */}
      <line
        x1="50" y1="195" x2="760" y2="195"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
