import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/defect.dart';
import '../models/detection_result.dart';
import '../models/inspection.dart';

/// Shared session state that bridges the Scan, Checklist, and Report screens.
class InspectionSession {
  final String id;
  final String vesselId;
  final String inspectorId;
  final String portOfInspection;
  final String mouRegion;
  final DateTime startedAt;
  final List<DetectionResult> scanResults;
  final List<ChecklistItem> checklistItems;
  /// Currently active inspection zone — applied to defects captured next.
  /// Inspector changes this via the zone picker before walking to a new area.
  final Zone currentZone;

  const InspectionSession({
    required this.id,
    required this.vesselId,
    required this.inspectorId,
    required this.portOfInspection,
    required this.mouRegion,
    required this.startedAt,
    this.scanResults = const [],
    this.checklistItems = const [],
    this.currentZone = defaultZone,
  });

  InspectionSession copyWith({
    List<DetectionResult>? scanResults,
    List<ChecklistItem>? checklistItems,
    Zone? currentZone,
  }) {
    return InspectionSession(
      id: id,
      vesselId: vesselId,
      inspectorId: inspectorId,
      portOfInspection: portOfInspection,
      mouRegion: mouRegion,
      startedAt: startedAt,
      scanResults: scanResults ?? this.scanResults,
      checklistItems: checklistItems ?? this.checklistItems,
      currentZone: currentZone ?? this.currentZone,
    );
  }

  // ── Derived stats ─────────────────────────────────────────────────────────

  int get totalDefects =>
      scanResults.fold(0, (s, r) => s + r.defectCount);

  int get criticalCount =>
      scanResults.fold(0, (s, r) => s + r.criticalCount);

  List<Defect> get allDefects =>
      scanResults.expand((r) => r.defects).toList();

  double get avgInferenceTime {
    if (scanResults.isEmpty) return 0;
    return scanResults.fold(0.0, (s, r) => s + r.inferenceTimeMs) /
        scanResults.length;
  }

  /// Checklist items manually marked fail — shown in report alongside AI detections.
  List<ChecklistItem> get failedItems =>
      checklistItems.where((i) => i.status == ChecklistItemStatus.fail).toList();

  /// Defect counts grouped by zone — drives the diagram badges.
  Map<Zone, int> get defectsByZone {
    final counts = <Zone, int>{for (final z in Zone.values) z: 0};
    for (final d in allDefects) {
      counts[d.zone] = (counts[d.zone] ?? 0) + 1;
    }
    return counts;
  }

  /// All defects in a specific zone.
  List<Defect> defectsInZone(Zone zone) =>
      allDefects.where((d) => d.zone == zone).toList();
}

class InspectionSessionNotifier extends StateNotifier<InspectionSession> {
  InspectionSessionNotifier()
      : super(InspectionSession(
          id: 'INS-${DateTime.now().millisecondsSinceEpoch}',
          vesselId: 'V-001',
          inspectorId: 'CREW-001',
          portOfInspection: 'Busan',
          mouRegion: 'TOKYO',
          startedAt: DateTime.now(),
        ));

  void addScanResult(DetectionResult result) {
    // Tag every defect in the scan with the session's current zone.
    final zone = state.currentZone;
    final tagged = DetectionResult(
      defects: result.defects.map((d) => d.copyWith(zone: zone)).toList(),
      inferenceTimeMs: result.inferenceTimeMs,
      modelVersion: result.modelVersion,
    );
    state = state.copyWith(
      scanResults: [...state.scanResults, tagged],
    );
  }

  void updateChecklistItems(List<ChecklistItem> items) {
    state = state.copyWith(checklistItems: items);
  }

  /// Switch the active zone — defects captured next will be tagged accordingly.
  void setCurrentZone(Zone zone) {
    state = state.copyWith(currentZone: zone);
  }

  /// Re-tag a previously captured defect (post-hoc edit during review).
  /// Identifies the defect by reference equality across the flat list.
  void retagDefect(Defect target, Zone zone) {
    final updatedScans = state.scanResults.map((r) {
      final updatedDefects = r.defects.map((d) {
        return identical(d, target) ? d.copyWith(zone: zone) : d;
      }).toList();
      return DetectionResult(
        defects: updatedDefects,
        inferenceTimeMs: r.inferenceTimeMs,
        modelVersion: r.modelVersion,
      );
    }).toList();
    state = state.copyWith(scanResults: updatedScans);
  }

  void reset() {
    state = InspectionSession(
      id: 'INS-${DateTime.now().millisecondsSinceEpoch}',
      vesselId: state.vesselId,
      inspectorId: state.inspectorId,
      portOfInspection: state.portOfInspection,
      mouRegion: state.mouRegion,
      startedAt: DateTime.now(),
    );
  }
}

final inspectionSessionProvider =
    StateNotifierProvider<InspectionSessionNotifier, InspectionSession>(
  (ref) => InspectionSessionNotifier(),
);
