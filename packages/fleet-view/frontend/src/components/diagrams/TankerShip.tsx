/**
 * Tanker — flat silhouette with smooth deck and visible manifolds/pipes.
 * viewBox 800x300.
 */
export default function TankerShip() {
  return (
    <g>
      {/* Sea band */}
      <rect x="0" y="220" width="800" height="80" fill="#0a1628" opacity="0.4" />

      {/* Hull (lower waterline — laden tanker) */}
      <path
        d="M 50 220
           L 50 145
           Q 75 110 135 105
           L 705 105
           L 760 135
           L 760 220 Z"
        fill="#1e3a5f"
      />

      {/* Smooth deck */}
      <rect x="135" y="100" width="570" height="6" fill="#2c5278" />

      {/* Center catwalk (full length) */}
      <rect x="160" y="88" width="500" height="6" fill="#3d6b9a" />
      <rect x="160" y="80" width="3" height="14" fill="#3d6b9a" />
      <rect x="660" y="80" width="3" height="14" fill="#3d6b9a" />

      {/* Manifold cluster (midship) */}
      <g transform="translate(380, 70)">
        <rect x="0" y="0" width="40" height="22" fill="#4a7ab0" />
        <circle cx="8" cy="11" r="3" fill="#1e3a5f" />
        <circle cx="20" cy="11" r="3" fill="#1e3a5f" />
        <circle cx="32" cy="11" r="3" fill="#1e3a5f" />
      </g>

      {/* Cargo tank vents (small dots along catwalk) */}
      {[200, 260, 320, 460, 520, 580].map(x => (
        <circle key={x} cx={x} cy="88" r="3" fill="#4a7ab0" />
      ))}

      {/* Bridge */}
      <rect x="615" y="48" width="85" height="55" fill="#2c5278" />
      <rect x="625" y="60" width="14" height="14" fill="#1e3a5f" />
      <rect x="648" y="60" width="14" height="14" fill="#1e3a5f" />
      <rect x="671" y="60" width="14" height="14" fill="#1e3a5f" />

      {/* Funnel */}
      <rect x="640" y="18" width="22" height="30" fill="#4a7ab0" />

      {/* Bow castle (small) */}
      <path d="M 80 105 L 80 92 L 130 92 L 130 105 Z" fill="#2c5278" />

      {/* Waterline */}
      <line
        x1="50" y1="200" x2="760" y2="200"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
