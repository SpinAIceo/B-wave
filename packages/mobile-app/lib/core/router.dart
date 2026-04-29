import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../features/alert/alert_screen.dart';
import '../features/checklist/checklist_screen.dart';
import '../features/report/report_screen.dart';
import '../features/scan/scan_screen.dart';
import '../features/settings/settings_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/scan',
  routes: [
    ShellRoute(
      builder: (context, state, child) => ScaffoldWithNavBar(child: child),
      routes: [
        GoRoute(
          path: '/scan',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ScanScreen(),
          ),
        ),
        GoRoute(
          path: '/checklist',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ChecklistScreen(),
          ),
        ),
        GoRoute(
          path: '/report',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ReportScreen(),
          ),
        ),
        GoRoute(
          path: '/alert',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: AlertScreen(),
          ),
        ),
      ],
    ),
    GoRoute(
      path: '/settings',
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
);

class ScaffoldWithNavBar extends StatelessWidget {
  final Widget child;

  const ScaffoldWithNavBar({super.key, required this.child});

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    if (location.startsWith('/checklist')) return 1;
    if (location.startsWith('/report')) return 2;
    if (location.startsWith('/alert')) return 3;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex(context),
        onDestinationSelected: (index) {
          switch (index) {
            case 0:
              context.go('/scan');
            case 1:
              context.go('/checklist');
            case 2:
              context.go('/report');
            case 3:
              context.go('/alert');
          }
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.camera_alt_outlined),
            selectedIcon: Icon(Icons.camera_alt),
            label: 'Scan',
          ),
          NavigationDestination(
            icon: Icon(Icons.checklist_outlined),
            selectedIcon: Icon(Icons.checklist),
            label: 'Checklist',
          ),
          NavigationDestination(
            icon: Icon(Icons.assessment_outlined),
            selectedIcon: Icon(Icons.assessment),
            label: 'Report',
          ),
          NavigationDestination(
            icon: Icon(Icons.notifications_outlined),
            selectedIcon: Icon(Icons.notifications),
            label: 'Alert',
          ),
        ],
      ),
    );
  }
}
