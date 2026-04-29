import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/models/inspection.dart';
import 'checklist_provider.dart';

class ChecklistScreen extends ConsumerStatefulWidget {
  const ChecklistScreen({super.key});

  @override
  ConsumerState<ChecklistScreen> createState() => _ChecklistScreenState();
}

class _ChecklistScreenState extends ConsumerState<ChecklistScreen> {
  String? _selectedCategory;

  @override
  Widget build(BuildContext context) {
    final items = ref.watch(checklistProvider);
    final notifier = ref.read(checklistProvider.notifier);

    final categories = notifier.categories;
    final filtered = _selectedCategory == null
        ? items
        : items.where((i) => i.category == _selectedCategory).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inspection Checklist'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          _ProgressHeader(
            completion: notifier.completionPercent,
            passed: notifier.passedCount,
            failed: notifier.failedCount,
            total: items.length,
          ),
          _CategoryFilter(
            categories: categories,
            selected: _selectedCategory,
            onSelected: (cat) => setState(() {
              _selectedCategory = _selectedCategory == cat ? null : cat;
            }),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.only(bottom: 16),
              itemCount: filtered.length,
              itemBuilder: (context, index) {
                final item = filtered[index];
                return _ChecklistTile(
                  item: item,
                  onStatusChanged: (status) {
                    notifier.updateItemStatus(item.itemId, status);
                  },
                  onScanTap: () => context.go('/scan'),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _ProgressHeader extends StatelessWidget {
  final double completion;
  final int passed;
  final int failed;
  final int total;

  const _ProgressHeader({
    required this.completion,
    required this.passed,
    required this.failed,
    required this.total,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${(completion * 100).toStringAsFixed(0)}% Complete',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              Text(
                '$passed pass / $failed fail / $total total',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: completion,
              minHeight: 8,
              backgroundColor: Colors.grey.shade700,
            ),
          ),
        ],
      ),
    );
  }
}

class _CategoryFilter extends StatelessWidget {
  final List<String> categories;
  final String? selected;
  final ValueChanged<String> onSelected;

  const _CategoryFilter({
    required this.categories,
    required this.selected,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        itemCount: categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final cat = categories[index];
          final isSelected = cat == selected;
          return FilterChip(
            label: Text(cat),
            selected: isSelected,
            onSelected: (_) => onSelected(cat),
          );
        },
      ),
    );
  }
}

class _ChecklistTile extends StatelessWidget {
  final ChecklistItem item;
  final ValueChanged<ChecklistItemStatus> onStatusChanged;
  final VoidCallback onScanTap;

  const _ChecklistTile({
    required this.item,
    required this.onStatusChanged,
    required this.onScanTap,
  });

  IconData get _categoryIcon {
    switch (item.category) {
      case 'Hull & Structure':
        return Icons.directions_boat;
      case 'Safety Equipment':
        return Icons.health_and_safety;
      case 'Fire Safety':
        return Icons.local_fire_department;
      case 'Cargo Securing':
        return Icons.inventory_2;
      case 'Pollution Prevention':
        return Icons.water_drop;
      case 'Navigation':
        return Icons.explore;
      case 'Living Conditions':
        return Icons.people;
      default:
        return Icons.checklist;
    }
  }

  Color get _statusColor {
    switch (item.status) {
      case ChecklistItemStatus.pass:
        return Colors.green;
      case ChecklistItemStatus.fail:
        return Colors.red;
      case ChecklistItemStatus.notChecked:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isCic = item.category == 'Cargo Securing';

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: InkWell(
        onTap: onScanTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(_categoryIcon, color: _statusColor, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            item.description,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ),
                        if (isCic) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.orange,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Text(
                              'CIC',
                              style: TextStyle(
                                  fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      item.category,
                      style: Theme.of(context)
                          .textTheme
                          .bodySmall
                          ?.copyWith(color: Colors.grey),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              PopupMenuButton<ChecklistItemStatus>(
                icon: Icon(Icons.circle, color: _statusColor, size: 20),
                onSelected: onStatusChanged,
                itemBuilder: (_) => [
                  const PopupMenuItem(
                    value: ChecklistItemStatus.pass,
                    child: Text('Pass'),
                  ),
                  const PopupMenuItem(
                    value: ChecklistItemStatus.fail,
                    child: Text('Fail'),
                  ),
                  const PopupMenuItem(
                    value: ChecklistItemStatus.notChecked,
                    child: Text('Not Checked'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
