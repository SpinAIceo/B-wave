import 'defect.dart';

class DetectionResult {
  final List<Defect> defects;
  final double inferenceTimeMs;
  final String modelVersion;

  const DetectionResult({
    required this.defects,
    required this.inferenceTimeMs,
    required this.modelVersion,
  });

  static const empty = DetectionResult(
    defects: [],
    inferenceTimeMs: 0,
    modelVersion: 'unknown',
  );

  int get defectCount => defects.length;
  bool get hasDefects => defects.isNotEmpty;

  int get criticalCount =>
      defects.where((d) => d.severity == Severity.critical).length;
}
