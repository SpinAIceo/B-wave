import 'package:flutter_riverpod/flutter_riverpod.dart';

class PortAlert {
  final String portName;
  final String countryCode;
  final String mouRegion;
  final List<String> cicFocusAreas;
  final String priority;
  final DateTime estimatedArrival;

  const PortAlert({
    required this.portName,
    required this.countryCode,
    required this.mouRegion,
    required this.cicFocusAreas,
    required this.priority,
    required this.estimatedArrival,
  });
}

final alertProvider = Provider<List<PortAlert>>((ref) {
  final now = DateTime.now();
  return [
    PortAlert(
      portName: 'Busan',
      countryCode: 'KR',
      mouRegion: 'Tokyo MoU',
      cicFocusAreas: [
        'Cargo Securing (CIC 2026)',
        'SOLAS Safety Equipment',
        'Fire Safety Systems',
      ],
      priority: 'high',
      estimatedArrival: now.add(const Duration(days: 3)),
    ),
    PortAlert(
      portName: 'Singapore',
      countryCode: 'SG',
      mouRegion: 'Tokyo MoU',
      cicFocusAreas: [
        'Cargo Securing (CIC 2026)',
        'MARPOL Pollution Prevention',
        'ISM Code Compliance',
      ],
      priority: 'high',
      estimatedArrival: now.add(const Duration(days: 10)),
    ),
    PortAlert(
      portName: 'Rotterdam',
      countryCode: 'NL',
      mouRegion: 'Paris MoU',
      cicFocusAreas: [
        'Cargo Securing (CIC 2026)',
        'MLC Living Conditions',
        'Cyber Security (UR E26/E27)',
      ],
      priority: 'medium',
      estimatedArrival: now.add(const Duration(days: 21)),
    ),
    PortAlert(
      portName: 'Shanghai',
      countryCode: 'CN',
      mouRegion: 'Tokyo MoU',
      cicFocusAreas: [
        'Cargo Securing (CIC 2026)',
        'Hull & Structure',
      ],
      priority: 'low',
      estimatedArrival: now.add(const Duration(days: 35)),
    ),
  ];
});
