import 'package:flutter/material.dart';

class BoundingBox {
  final double xMin;
  final double yMin;
  final double xMax;
  final double yMax;

  const BoundingBox({
    required this.xMin,
    required this.yMin,
    required this.xMax,
    required this.yMax,
  });

  double get width => xMax - xMin;
  double get height => yMax - yMin;
  Offset get center => Offset((xMin + xMax) / 2, (yMin + yMax) / 2);
}

enum DefectType {
  rust(1, 'Rust', 'Corrosion', Colors.orange),
  damage(2, 'Damage', 'Structural Damage', Colors.red),
  leak(3, 'Leak', 'Oil/Water Leak', Colors.blue),
  missingLabel(4, 'Missing Label', 'Safety Sign Missing', Colors.yellow),
  cargoLashing(5, 'Cargo Lashing', 'Cargo Securing Defect', Colors.purple);

  const DefectType(this.value, this.displayName, this.description, this.color);

  final int value;
  final String displayName;
  final String description;
  final Color color;

  static DefectType fromValue(int value) {
    return DefectType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => DefectType.rust,
    );
  }
}

enum Zone {
  bow('bow', 'Bow', '선수'),
  midship('midship', 'Midship', '중앙'),
  stern('stern', 'Stern', '선미'),
  deck('deck', 'Deck', '갑판'),
  hull('hull', 'Hull', '선체'),
  engineRoom('engine_room', 'Engine Room', '기관실');

  const Zone(this.code, this.displayNameEn, this.displayNameKo);

  final String code;
  final String displayNameEn;
  final String displayNameKo;

  String get displayName => displayNameKo;

  static Zone fromCode(String code) {
    return Zone.values.firstWhere(
      (e) => e.code == code,
      orElse: () => Zone.midship,
    );
  }
}

const Zone defaultZone = Zone.midship;

enum Severity {
  low(1, 'LOW'),
  medium(2, 'MEDIUM'),
  high(3, 'HIGH'),
  critical(4, 'CRITICAL');

  const Severity(this.value, this.label);

  final int value;
  final String label;

  static Severity fromValue(int value) {
    return Severity.values.firstWhere(
      (e) => e.value == value,
      orElse: () => Severity.low,
    );
  }

  Color get color {
    switch (this) {
      case Severity.low:
        return Colors.green;
      case Severity.medium:
        return Colors.yellow;
      case Severity.high:
        return Colors.orange;
      case Severity.critical:
        return Colors.red;
    }
  }
}

class Defect {
  final BoundingBox bbox;
  final DefectType defectType;
  final double confidence;
  final String pscCode;
  final Severity severity;
  final Zone zone;

  const Defect({
    required this.bbox,
    required this.defectType,
    required this.confidence,
    required this.pscCode,
    required this.severity,
    this.zone = defaultZone,
  });

  String get confidencePercent => '${(confidence * 100).toStringAsFixed(0)}%';
  String get label => '${defectType.displayName} $confidencePercent $pscCode';

  Defect copyWith({Zone? zone}) {
    return Defect(
      bbox: bbox,
      defectType: defectType,
      confidence: confidence,
      pscCode: pscCode,
      severity: severity,
      zone: zone ?? this.zone,
    );
  }
}
