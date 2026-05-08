import 'package:flutter/material.dart';

import '../data/models/defect.dart';

/// Lightweight side-view ship diagram with 6 clickable zones.
/// Used in:
///   - Scan screen (zone picker before capture)
///   - Report screen (zone summary visualization)
///
/// Layout (matches fleet-view's React VesselDiagram):
///
///   ┌────────┬─────────────┬────────┐
///   │        │    Deck     │ Stern  │
///   │        ├─────────────┤        │
///   │  Bow   │   Midship   ├────────┤
///   │        ├─────────────┤ Engine │
///   │        │    Hull     │  Room  │
///   └────────┴─────────────┴────────┘
class VesselDiagram extends StatelessWidget {
  final Zone? selectedZone;
  final ValueChanged<Zone>? onZoneTap;
  final Map<Zone, int> zoneCounts;
  final double aspectRatio;

  const VesselDiagram({
    super.key,
    this.selectedZone,
    this.onZoneTap,
    this.zoneCounts = const {},
    this.aspectRatio = 800 / 300,
  });

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: aspectRatio,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // SVG-style virtual coordinates: 800×300
          const vbW = 800.0;
          const vbH = 300.0;
          final scale = constraints.maxWidth / vbW;

          return Stack(
            children: [
              // Decorative ship silhouette
              CustomPaint(
                size: Size(constraints.maxWidth, constraints.maxHeight),
                painter: _ShipSilhouettePainter(),
              ),

              // Clickable zone overlays
              for (final zone in _zoneLayout)
                Positioned(
                  left: zone.x * scale,
                  top: zone.y * scale,
                  width: zone.w * scale,
                  height: zone.h * scale,
                  child: _ZoneOverlay(
                    zone: zone.id,
                    isSelected: selectedZone == zone.id,
                    count: zoneCounts[zone.id] ?? 0,
                    onTap: () => onZoneTap?.call(zone.id),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class _ZoneRegion {
  final Zone id;
  final double x, y, w, h;
  const _ZoneRegion(this.id, this.x, this.y, this.w, this.h);
}

const _zoneLayout = <_ZoneRegion>[
  _ZoneRegion(Zone.bow,        0,   0,   150, 300),
  _ZoneRegion(Zone.deck,       150, 0,   500, 100),
  _ZoneRegion(Zone.midship,    150, 100, 500, 100),
  _ZoneRegion(Zone.hull,       150, 200, 500, 100),
  _ZoneRegion(Zone.stern,      650, 0,   150, 150),
  _ZoneRegion(Zone.engineRoom, 650, 150, 150, 150),
];

class _ZoneOverlay extends StatelessWidget {
  final Zone zone;
  final bool isSelected;
  final int count;
  final VoidCallback? onTap;

  const _ZoneOverlay({
    required this.zone,
    required this.isSelected,
    required this.count,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: isSelected
              ? Colors.teal.withValues(alpha: 0.28)
              : Colors.transparent,
          border: Border.all(
            color: isSelected ? Colors.tealAccent : Colors.white24,
            width: isSelected ? 2 : 0.5,
          ),
        ),
        child: Stack(
          children: [
            // Zone label (always visible — small)
            Center(
              child: Text(
                zone.displayName,
                style: TextStyle(
                  color: isSelected ? Colors.white : Colors.white70,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  shadows: const [
                    Shadow(color: Colors.black, blurRadius: 4),
                  ],
                ),
              ),
            ),
            // Defect count badge
            if (count > 0)
              Positioned(
                top: 4,
                right: 4,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    '$count',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// Decorative side-view ship silhouette painted via CustomPainter.
/// Matches the GenericShip React SVG styling (flat-fill navy palette).
class _ShipSilhouettePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final scaleX = size.width / 800.0;
    final scaleY = size.height / 300.0;

    final hullPaint = Paint()..color = const Color(0xFF1E3A5F);
    final superstructurePaint = Paint()..color = const Color(0xFF2C5278);
    final accentPaint = Paint()..color = const Color(0xFF3D6B9A);
    final waterlinePaint = Paint()
      ..color = const Color(0xFF6BA3D8).withValues(alpha: 0.4)
      ..strokeWidth = 2 * scaleY
      ..style = PaintingStyle.stroke;

    // Sea band
    final seaPaint = Paint()
      ..color = const Color(0xFF0A1628).withValues(alpha: 0.4);
    canvas.drawRect(
      Rect.fromLTWH(0, 220 * scaleY, 800 * scaleX, 80 * scaleY),
      seaPaint,
    );

    // Hull silhouette
    final hullPath = Path()
      ..moveTo(50 * scaleX, 220 * scaleY)
      ..lineTo(50 * scaleX, 140 * scaleY)
      ..quadraticBezierTo(
        75 * scaleX, 105 * scaleY,
        130 * scaleX, 100 * scaleY,
      )
      ..lineTo(700 * scaleX, 100 * scaleY)
      ..lineTo(760 * scaleX, 130 * scaleY)
      ..lineTo(760 * scaleX, 220 * scaleY)
      ..close();
    canvas.drawPath(hullPath, hullPaint);

    // Bridge / superstructure
    canvas.drawRect(
      Rect.fromLTWH(600 * scaleX, 50 * scaleY, 100 * scaleX, 50 * scaleY),
      superstructurePaint,
    );

    // Bridge windows
    for (final wx in [615.0, 645.0, 675.0]) {
      canvas.drawRect(
        Rect.fromLTWH(wx * scaleX, 62 * scaleY, 18 * scaleX, 20 * scaleY),
        hullPaint,
      );
    }

    // Funnel
    canvas.drawRect(
      Rect.fromLTWH(635 * scaleX, 20 * scaleY, 22 * scaleX, 30 * scaleY),
      accentPaint,
    );

    // Waterline (dashed via short segments)
    final dashWidth = 6 * scaleX;
    final gap = 3 * scaleX;
    var x = 50 * scaleX;
    final endX = 760 * scaleX;
    final y = 195 * scaleY;
    while (x < endX) {
      canvas.drawLine(
        Offset(x, y),
        Offset((x + dashWidth).clamp(0, endX), y),
        waterlinePaint,
      );
      x += dashWidth + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _ShipSilhouettePainter oldDelegate) => false;
}
