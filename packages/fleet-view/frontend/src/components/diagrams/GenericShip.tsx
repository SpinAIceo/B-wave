/**
 * Generic vessel — flat filled silhouette.
 * viewBox 800x300, bow on left, stern on right.
 * Pure decorative SVG; zone overlay is added by <VesselDiagram>.
 */
export default function GenericShip() {
  return (
    <g>
      {/* Sea band */}
      <rect x="0" y="220" width="800" height="80" fill="#0a1628" opacity="0.4" />

      {/* Hull (main body) */}
      <path
        d="M 50 220
           L 50 140
           Q 75 105 130 100
           L 700 100
           L 760 130
           L 760 220 Z"
        fill="#1e3a5f"
      />

      {/* Deck line accent */}
      <line x1="130" y1="100" x2="700" y2="100" stroke="#3d6b9a" strokeWidth="2" />

      {/* Bridge / superstructure */}
      <rect x="600" y="50" width="100" height="50" fill="#2c5278" />
      <rect x="615" y="62" width="18" height="20" fill="#1e3a5f" />
      <rect x="645" y="62" width="18" height="20" fill="#1e3a5f" />
      <rect x="675" y="62" width="18" height="20" fill="#1e3a5f" />

      {/* Funnel */}
      <rect x="635" y="20" width="22" height="30" fill="#4a7ab0" />
      <rect x="638" y="20" width="16" height="6" fill="#2c5278" />

      {/* Bow accent (anchor area) */}
      <circle cx="80" cy="160" r="4" fill="#3d6b9a" />

      {/* Waterline */}
      <line
        x1="50" y1="195" x2="760" y2="195"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
