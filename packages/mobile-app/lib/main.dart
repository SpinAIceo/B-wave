import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router.dart';
import 'core/theme.dart';
import 'features/settings/settings_screen.dart';

void main() => runApp(const ProviderScope(child: BWaveApp()));

class BWaveApp extends ConsumerWidget {
  const BWaveApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);

    final ThemeData theme;
    switch (themeMode) {
      case AppThemeMode.light:
        theme = BWaveTheme.light();
      case AppThemeMode.dark:
        theme = BWaveTheme.dark();
      case AppThemeMode.highContrast:
        theme = BWaveTheme.highContrast();
    }

    return MaterialApp.router(
      title: 'B-Wave Scanner',
      theme: theme,
      routerConfig: appRouter,
      debugShowCheckedModeBanner: false,
    );
  }
}
