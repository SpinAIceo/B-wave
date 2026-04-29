import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'alert_provider.dart';

class AlertScreen extends ConsumerWidget {
  const AlertScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Port Inspection Alerts'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: alerts.length,
        itemBuilder: (context, index) => _AlertCard(alert: alerts[index]),
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final PortAlert alert;

  const _AlertCard({required this.alert});

  Color get _priorityColor {
    switch (alert.priority) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  String get _countryFlag {
    switch (alert.countryCode) {
      case 'KR':
        return '🇰🇷';
      case 'SG':
        return '🇸🇬';
      case 'NL':
        return '🇳🇱';
      case 'CN':
        return '🇨🇳';
      default:
        return '🏳';
    }
  }

  String get _daysUntil {
    final days = alert.estimatedArrival.difference(DateTime.now()).inDays;
    if (days <= 0) return 'Today';
    if (days == 1) return 'Tomorrow';
    return 'In $days days';
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: Text(_countryFlag, style: const TextStyle(fontSize: 32)),
        title: Row(
          children: [
            Text(alert.portName),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: _priorityColor.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: _priorityColor),
              ),
              child: Text(
                alert.priority.toUpperCase(),
                style: TextStyle(
                  color: _priorityColor,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        subtitle: Text('$_daysUntil · ${alert.mouRegion}'),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Divider(),
                Text(
                  'CIC Focus Areas:',
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                ...alert.cicFocusAreas.map(
                  (area) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      children: [
                        Icon(
                          area.contains('CIC')
                              ? Icons.priority_high
                              : Icons.check_circle_outline,
                          size: 16,
                          color:
                              area.contains('CIC') ? Colors.orange : Colors.grey,
                        ),
                        const SizedBox(width: 8),
                        Flexible(child: Text(area)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'ETA: ${alert.estimatedArrival.toString().substring(0, 10)}',
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
