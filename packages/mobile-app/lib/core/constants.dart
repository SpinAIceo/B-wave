import 'package:flutter/material.dart';

class AppConstants {
  AppConstants._();

  static const String defaultEdgeHost = '192.168.1.1';
  static const int defaultEdgePort = 50051;
  static const Duration scanThrottleInterval = Duration(milliseconds: 500);
  static const double minTouchTarget = 48.0;
  static const String appVersion = '0.1.0';

  static const Map<String, Color> defectColors = {
    'rust': Colors.orange,
    'damage': Colors.red,
    'leak': Colors.blue,
    'missing_label': Colors.yellow,
    'cargo_lashing': Colors.purple,
  };

  static const List<String> supportedLocales = ['ko', 'en', 'zh', 'tl'];
}
