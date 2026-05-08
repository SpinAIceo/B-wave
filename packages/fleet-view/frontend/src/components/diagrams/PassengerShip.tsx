/**
 * Passenger / Cruise ship — multi-deck silhouette with windows.
 * viewBox 800x300.
 */
export default function PassengerShip() {
  return (
    <g>
      {/* Sea band */}
      <rect x="0" y="220" width="800" height="80" fill="#0a1628" opacity="0.4" />

      {/* Hull */}
      <path
        d="M 50 220
           L 50 150
           Q 75 130 110 130
           L 720 130
           L 760 155
           L 760 220 Z"
        fill="#1e3a5f"
      />

      {/* Multi-deck superstructure (4 levels) */}
      <rect x="110" y="100" width="610" height="30" fill="#2c5278" />
      <rect x="125" y="75"  width="585" height="25" fill="#3d6b9a" />
      <rect x="145" y="55"  width="555" height="20" fill="#4a7ab0" />
      <rect x="170" y="38"  width="510" height="17" fill="#5a8ec0" />

      {/* Window rows (small bright dots) */}
      {[112, 87, 65, 47].map((y, lvlIdx) => {
        const startX = [120, 135, 155, 180][lvlIdx];
        const endX = [720, 705, 695, 680][lvlIdx];
        const cells = [];
        for (let x = startX; x < endX; x += 14) {
          cells.push(
            <rect key={`${y}-${x}`} x={x} y={y} width="8" height="6" fill="#fff8a8" opacity="0.8" />,
          );
        }
        return <g key={y}>{cells}</g>;
      })}

      {/* Funnels (2) */}
      <rect x="520" y="14" width="26" height="24" fill="#c44" />
      <rect x="555" y="14" width="26" height="24" fill="#c44" />

      {/* Bridge wing extending forward */}
      <rect x="170" y="30" width="60" height="10" fill="#5a8ec0" />

      {/* Lifeboats along middle deck */}
      {[180, 240, 300, 360, 420, 480].map(x => (
        <rect key={x} x={x} y="105" width="40" height="6" fill="#ff9800" />
      ))}

      {/* Waterline */}
      <line
        x1="50" y1="200" x2="760" y2="200"
        stroke="#6ba3d8" strokeWidth="2"
        strokeDasharray="6,3" opacity="0.4"
      />
    </g>
  );
}
