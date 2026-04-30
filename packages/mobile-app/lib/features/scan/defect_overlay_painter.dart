import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import '../../data/models/defect.dart';

class DefectOverlayPainter extends CustomPainter {
  final List<Defect> defects;
  final double animationValue;

  DefectOverlayPainter({
    required this.defects,
    this.animationValue = 1.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (final defect in defects) {
      _drawDefectBox(canvas, size, defect);
    }
  }

  void _drawDefectBox(Canvas canvas, Size size, Defect defect) {
    final rect = Rect.fromLTRB(
      defect.bbox.xMin * size.width,
      defect.bbox.yMin * size.height,
      defect.bbox.xMax * size.width,
      defect.bbox.yMax * size.height,
    );

    final isCritical = defect.severity == Severity.critical;
    final opacity = isCritical ? (0.6 + 0.4 * animationValue) : 1.0;
    final strokeWidth = isCritical ? 5.0 : 3.0;

    final boxPaint = Paint()
      ..color = defect.defectType.color.withValues(alpha: opacity)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;

    canvas.drawRect(rect, boxPaint);

    final fillPaint = Paint()
      ..color = defect.defectType.color.withValues(alpha: 0.1)
      ..style = PaintingStyle.fill;
    canvas.drawRect(rect, fillPaint);

    _drawLabel(canvas, size, rect, defect);
  }

  void _drawLabel(Canvas canvas, Size size, Rect boxRect, Defect defect) {
    final label = defect.label;

    final textStyle = ui.TextStyle(
      color: Colors.white,
      fontSize: 14,
      fontWeight: ui.FontWeight.bold,
    );

    final paragraphBuilder = ui.ParagraphBuilder(ui.ParagraphStyle(
      textAlign: TextAlign.left,
      maxLines: 1,
    ))
      ..pushStyle(textStyle)
      ..addText(label);

    final paragraph = paragraphBuilder.build()
      ..layout(const ui.ParagraphConstraints(width: 300));

    final labelWidth = paragraph.longestLine + 12;
    final labelHeight = paragraph.height + 8;

    final labelTop = (boxRect.top - labelHeight - 2).clamp(0.0, size.height - labelHeight);
    final labelLeft = boxRect.left.clamp(0.0, (size.width - labelWidth).clamp(0.0, size.width));

    final labelRect = Rect.fromLTWH(
      labelLeft,
      labelTop,
      labelWidth,
      labelHeight,
    );

    final bgPaint = Paint()
      ..color = defect.defectType.color.withValues(alpha: 0.8)
      ..style = PaintingStyle.fill;

    canvas.drawRRect(
      RRect.fromRectAndRadius(labelRect, const Radius.circular(4)),
      bgPaint,
    );

    canvas.drawParagraph(
      paragraph,
      Offset(labelRect.left + 6, labelRect.top + 4),
    );
  }

  @override
  bool shouldRepaint(covariant DefectOverlayPainter oldDelegate) {
    return oldDelegate.defects != defects ||
        oldDelegate.animationValue != animationValue;
  }
}
