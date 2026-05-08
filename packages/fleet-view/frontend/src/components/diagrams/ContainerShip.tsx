/**
 * Container ship — flat filled silhouette with stacked containers on deck.
 * viewBox 800x300.
 */
const CONTAINER_COLORS = ['#c44', '#4a8', '#48b', '#c84', '#5a5', '#a44'];

function ContainerStack({ x, y, cols, rows }: { x: number; y: number; cols: number; rows: number }) {
  const w = 36, h = 18;
  const cells = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      cells.push(
        <rect
          key={`${r}-${c}`}
          x={x + c * (w + 1)}
          y={y - (r + 1) * (h + 1)}
          width={w}
          height={h}
          fill={CONTAINER_COLORS[(c + r * 3) % CONTAINER_COLORS.length]}
          stroke="#0a1628"
          strokeWidth="0.5"
        />,
      );
    }
  }
  return <>{cells}</>;
}

export default function ContainerShip() {
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

      {/* Deck line */}
      <line x1="130" y1="100" x2="700" y2="100" stroke="#3d6b9a" strokeWidth="2" />

      {/* Container stacks (bow → midship area) */}
      <ContainerStack x={150} y={100} cols={4} rows={3} />
      <ContainerStack x={310} y={100} cols={4} rows={4} />
      <ContainerStack x={470} y={100} cols={4} rows={3} />

      {/* Bridge */}
      <rect x="615" y="60" width="80" height="40" fill="#2c5278" />
      <rect x="625" y="70" width="14" height="14" fill="#1e3a5f" />
      <rect x="650" y="70" width="14" height="14" fill="#1e3a5f" />
      <rect x="675" y="70" width="14" height="14" fill="#1e3a5f" />

      {/* Funnel */}
      <rect x="640" y="30" width="22" height="30" fill="#4a7ab0" />

      {/* Waterline */}
      <line
        x1="50" y1="195" x2="760" y2="195"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
