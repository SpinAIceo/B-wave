enum ChecklistItemStatus {
  pass,
  fail,
  notChecked;

  String get displayName {
    switch (this) {
      case ChecklistItemStatus.pass:
        return 'Pass';
      case ChecklistItemStatus.fail:
        return 'Fail';
      case ChecklistItemStatus.notChecked:
        return 'Not Checked';
    }
  }
}

class ChecklistItem {
  final String itemId;
  final String category;
  final String description;
  ChecklistItemStatus status;
  final List<String> detectionIds;
  String notes;

  ChecklistItem({
    required this.itemId,
    required this.category,
    required this.description,
    this.status = ChecklistItemStatus.notChecked,
    List<String>? detectionIds,
    this.notes = '',
  }) : detectionIds = detectionIds ?? [];
}

class Inspection {
  final String id;
  final String vesselId;
  final String inspectorId;
  final String portOfInspection;
  final String mouRegion;
  final DateTime startedAt;
  DateTime? completedAt;
  final List<ChecklistItem> checklistItems;
  final List<String> detectionIds;

  Inspection({
    required this.id,
    required this.vesselId,
    required this.inspectorId,
    required this.portOfInspection,
    required this.mouRegion,
    required this.startedAt,
    this.completedAt,
    List<ChecklistItem>? checklistItems,
    List<String>? detectionIds,
  })  : checklistItems = checklistItems ?? [],
        detectionIds = detectionIds ?? [];

  int get totalItems => checklistItems.length;
  int get passedItems =>
      checklistItems.where((i) => i.status == ChecklistItemStatus.pass).length;
  int get failedItems =>
      checklistItems.where((i) => i.status == ChecklistItemStatus.fail).length;
  double get completionPercent {
    if (totalItems == 0) return 0;
    final checked = checklistItems
        .where((i) => i.status != ChecklistItemStatus.notChecked)
        .length;
    return checked / totalItems;
  }
}
