import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/models/defect.dart';
import 'report_provider.dart';

class ReportScreen extends ConsumerWidget {
  const ReportScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final report = ref.watch(reportProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inspection Report'),
        actions: [
          IconButton(
            icon: const Icon(Icons.picture_as_pdf),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('PDF export coming soon')),
              );
            },
            tooltip: 'Export PDF',
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _InspectionHeader(report: report),
          const SizedBox(height: 16),
          _SummaryCard(report: report),
          const SizedBox(height: 16),
          Text(
            'Detected Defects',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          if (report.allDefects.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: Text('No defects detected')),
              ),
            )
          else
            ...report.allDefects.map((d) => _DefectTile(defect: d)),
        ],
      ),
    );
  }
}

class _InspectionHeader extends StatelessWidget {
  final ReportState report;

  const _InspectionHeader({required this.report});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  report.vesselName,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Chip(label: Text(report.portName)),
              ],
            ),
            const SizedBox(height: 8),
            Text('Inspector: ${report.inspectorId}'),
            Text(
              'Date: ${report.inspectionDate.toString().substring(0, 16)}',
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final ReportState report;

  const _SummaryCard({required this.report});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: report.criticalCount > 0
          ? Colors.red.shade900.withValues(alpha: 0.3)
          : Colors.green.shade900.withValues(alpha: 0.3),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _SummaryItem(
              label: 'Defects',
              value: '${report.totalDefects}',
              color: report.totalDefects > 0 ? Colors.orange : Colors.green,
            ),
            _SummaryItem(
              label: 'Critical',
              value: '${report.criticalCount}',
              color: report.criticalCount > 0 ? Colors.red : Colors.green,
            ),
            _SummaryItem(
              label: 'Scans',
              value: '${report.results.length}',
              color: Colors.cyan,
            ),
            _SummaryItem(
              label: 'Avg Time',
              value: '${report.avgInferenceTime.toStringAsFixed(0)}ms',
              color: Colors.grey,
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryItem extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _SummaryItem({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _DefectTile extends StatelessWidget {
  final Defect defect;

  const _DefectTile({required this.defect});

  String get _recommendedAction {
    switch (defect.defectType) {
      case DefectType.rust:
        return 'Inspect hull plating, prepare for spot blasting and recoating';
      case DefectType.damage:
        return 'Assess structural integrity, consult class surveyor if needed';
      case DefectType.leak:
        return 'Identify source, contain spill, repair fitting or gasket';
      case DefectType.missingLabel:
        return 'Replace safety signage per SOLAS requirements';
      case DefectType.cargoLashing:
        return 'Re-tension or replace lashing equipment before departure';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ExpansionTile(
        leading: Icon(Icons.warning, color: defect.defectType.color, size: 28),
        title: Text(defect.defectType.displayName),
        subtitle: Text('PSC ${defect.pscCode} · ${defect.confidencePercent}'),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: defect.severity.color.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: defect.severity.color),
          ),
          child: Text(
            defect.severity.label,
            style: TextStyle(
              color: defect.severity.color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Divider(),
                Text(
                  'Description: ${defect.defectType.description}',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Recommended Action:',
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                Text(
                  _recommendedAction,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 8),
                Text(
                  'Location: (${defect.bbox.xMin.toStringAsFixed(2)}, '
                  '${defect.bbox.yMin.toStringAsFixed(2)}) — '
                  '(${defect.bbox.xMax.toStringAsFixed(2)}, '
                  '${defect.bbox.yMax.toStringAsFixed(2)})',
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(color: Colors.grey),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
