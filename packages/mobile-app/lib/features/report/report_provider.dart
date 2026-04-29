import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/defect.dart';
import '../../data/models/detection_result.dart';

class ReportState {
  final List<DetectionResult> results;
  final String inspectorId;
  final String vesselName;
  final String portName;
  final DateTime inspectionDate;

  ReportState({
    this.results = const [],
    this.inspectorId = 'CREW-001',
    this.vesselName = 'MV Pacific Star',
    this.portName = 'Busan',
    DateTime? inspectionDate,
  }) : inspectionDate = inspectionDate ?? DateTime.now();

  int get totalDefects =>
      results.fold(0, (sum, r) => sum + r.defectCount);

  int get criticalCount =>
      results.fold(0, (sum, r) => sum + r.criticalCount);

  List<Defect> get allDefects =>
      results.expand((r) => r.defects).toList();

  double get avgInferenceTime {
    if (results.isEmpty) return 0;
    return results.fold(0.0, (sum, r) => sum + r.inferenceTimeMs) /
        results.length;
  }
}

class ReportNotifier extends StateNotifier<ReportState> {
  ReportNotifier() : super(_mockReport());

  void addResult(DetectionResult result) {
    state = ReportState(
      results: [...state.results, result],
      inspectorId: state.inspectorId,
      vesselName: state.vesselName,
      portName: state.portName,
      inspectionDate: state.inspectionDate,
    );
  }

  void clear() {
    state = ReportState();
  }

  static ReportState _mockReport() {
    return ReportState(
      inspectorId: 'CREW-001',
      vesselName: 'MV Pacific Star',
      portName: 'Busan',
      inspectionDate: DateTime.now(),
      results: [
        const DetectionResult(
          defects: [
            Defect(
              bbox: BoundingBox(xMin: 0.1, yMin: 0.2, xMax: 0.4, yMax: 0.5),
              defectType: DefectType.rust,
              confidence: 0.87,
              pscCode: '0615',
              severity: Severity.high,
            ),
            Defect(
              bbox: BoundingBox(xMin: 0.5, yMin: 0.1, xMax: 0.8, yMax: 0.35),
              defectType: DefectType.damage,
              confidence: 0.92,
              pscCode: '0630',
              severity: Severity.critical,
            ),
          ],
          inferenceTimeMs: 145.3,
          modelVersion: '0.1.0',
        ),
        const DetectionResult(
          defects: [
            Defect(
              bbox: BoundingBox(xMin: 0.3, yMin: 0.6, xMax: 0.6, yMax: 0.85),
              defectType: DefectType.cargoLashing,
              confidence: 0.81,
              pscCode: '0725',
              severity: Severity.high,
            ),
          ],
          inferenceTimeMs: 132.7,
          modelVersion: '0.1.0',
        ),
      ],
    );
  }
}

final reportProvider =
    StateNotifierProvider<ReportNotifier, ReportState>((ref) {
  return ReportNotifier();
});
