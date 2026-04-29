import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/inspection.dart';

class ChecklistNotifier extends StateNotifier<List<ChecklistItem>> {
  ChecklistNotifier() : super(_mockChecklist());

  void updateItemStatus(String itemId, ChecklistItemStatus status) {
    state = [
      for (final item in state)
        if (item.itemId == itemId) ...[
          ChecklistItem(
            itemId: item.itemId,
            category: item.category,
            description: item.description,
            status: status,
            detectionIds: item.detectionIds,
            notes: item.notes,
          ),
        ] else
          item,
    ];
  }

  List<ChecklistItem> getByCategory(String category) {
    return state.where((item) => item.category == category).toList();
  }

  double get completionPercent {
    if (state.isEmpty) return 0;
    final checked =
        state.where((i) => i.status != ChecklistItemStatus.notChecked).length;
    return checked / state.length;
  }

  int get passedCount =>
      state.where((i) => i.status == ChecklistItemStatus.pass).length;

  int get failedCount =>
      state.where((i) => i.status == ChecklistItemStatus.fail).length;

  List<String> get categories =>
      state.map((i) => i.category).toSet().toList()..sort();

  static List<ChecklistItem> _mockChecklist() => [
        ChecklistItem(
          itemId: 'CL-001',
          category: 'Hull & Structure',
          description: 'Hull plating condition — check for corrosion, cracks, dents',
        ),
        ChecklistItem(
          itemId: 'CL-002',
          category: 'Hull & Structure',
          description: 'Deck plating and coaming — verify structural integrity',
        ),
        ChecklistItem(
          itemId: 'CL-003',
          category: 'Safety Equipment',
          description: 'Lifeboat davit and winch — operational test',
        ),
        ChecklistItem(
          itemId: 'CL-004',
          category: 'Safety Equipment',
          description: 'Life raft hydrostatic release — expiry date check',
        ),
        ChecklistItem(
          itemId: 'CL-005',
          category: 'Safety Equipment',
          description: 'Fire extinguisher pressure and inspection tags',
        ),
        ChecklistItem(
          itemId: 'CL-006',
          category: 'Fire Safety',
          description: 'Fire main and hydrants — pressure test',
        ),
        ChecklistItem(
          itemId: 'CL-007',
          category: 'Fire Safety',
          description: 'Emergency fire pump — operational verification',
        ),
        ChecklistItem(
          itemId: 'CL-008',
          category: 'Cargo Securing',
          description: 'Lashing rods tension — check for loosening (CIC 2026)',
        ),
        ChecklistItem(
          itemId: 'CL-009',
          category: 'Cargo Securing',
          description: 'Turnbuckles condition — check for damage or corrosion (CIC 2026)',
        ),
        ChecklistItem(
          itemId: 'CL-010',
          category: 'Cargo Securing',
          description: 'Securing wires and chains — check for cuts and wear (CIC 2026)',
        ),
        ChecklistItem(
          itemId: 'CL-011',
          category: 'Pollution Prevention',
          description: 'Oil water separator — operation and 15ppm alarm test',
        ),
        ChecklistItem(
          itemId: 'CL-012',
          category: 'Pollution Prevention',
          description: 'Bilge area — check for oil leaks and containment',
        ),
        ChecklistItem(
          itemId: 'CL-013',
          category: 'Navigation',
          description: 'Navigation lights — operational check all positions',
        ),
        ChecklistItem(
          itemId: 'CL-014',
          category: 'Living Conditions',
          description: 'Safety signage and labels — verify completeness',
        ),
        ChecklistItem(
          itemId: 'CL-015',
          category: 'Living Conditions',
          description: 'Emergency escape routes — markings and accessibility',
        ),
      ];
}

final checklistProvider =
    StateNotifierProvider<ChecklistNotifier, List<ChecklistItem>>((ref) {
  return ChecklistNotifier();
});
