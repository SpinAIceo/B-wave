import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/constants.dart';

enum AppThemeMode { light, dark, highContrast }

final themeProvider = StateProvider<AppThemeMode>((ref) => AppThemeMode.dark);
final localeProvider = StateProvider<String>((ref) => 'en');
final edgeHostProvider =
    StateProvider<String>((ref) => AppConstants.defaultEdgeHost);
final edgePortProvider =
    StateProvider<int>((ref) => AppConstants.defaultEdgePort);

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = ref.watch(themeProvider);
    final locale = ref.watch(localeProvider);
    final host = ref.watch(edgeHostProvider);
    final port = ref.watch(edgePortProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          _SectionHeader(title: 'Edge Server Connection'),
          ListTile(
            leading: const Icon(Icons.dns),
            title: const Text('Server Host'),
            subtitle: Text(host),
            onTap: () => _editTextField(
              context,
              title: 'Edge Server Host',
              initialValue: host,
              onSave: (v) => ref.read(edgeHostProvider.notifier).state = v,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.numbers),
            title: const Text('Server Port'),
            subtitle: Text('$port'),
            onTap: () => _editTextField(
              context,
              title: 'Edge Server Port',
              initialValue: '$port',
              onSave: (v) {
                final p = int.tryParse(v);
                if (p != null) ref.read(edgePortProvider.notifier).state = p;
              },
            ),
          ),
          ListTile(
            leading: const Icon(Icons.wifi_find),
            title: const Text('Test Connection'),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Connection test: mock OK')),
              );
            },
          ),
          const Divider(),
          _SectionHeader(title: 'Appearance'),
          ListTile(
            leading: const Icon(Icons.palette),
            title: const Text('Theme'),
            subtitle: Text(theme.name),
            trailing: SegmentedButton<AppThemeMode>(
              segments: const [
                ButtonSegment(value: AppThemeMode.light, label: Text('Light')),
                ButtonSegment(value: AppThemeMode.dark, label: Text('Dark')),
                ButtonSegment(
                    value: AppThemeMode.highContrast, label: Text('Hi-Con')),
              ],
              selected: {theme},
              onSelectionChanged: (v) =>
                  ref.read(themeProvider.notifier).state = v.first,
            ),
          ),
          const Divider(),
          _SectionHeader(title: 'Language'),
          ...['en', 'ko', 'zh', 'tl'].map(
            (code) => RadioListTile<String>(
              title: Text(_localeName(code)),
              value: code,
              groupValue: locale,
              onChanged: (v) =>
                  ref.read(localeProvider.notifier).state = v ?? 'en',
            ),
          ),
          const Divider(),
          _SectionHeader(title: 'About'),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('App Version'),
            subtitle: Text(AppConstants.appVersion),
          ),
        ],
      ),
    );
  }

  String _localeName(String code) {
    switch (code) {
      case 'ko':
        return '한국어';
      case 'en':
        return 'English';
      case 'zh':
        return '中文';
      case 'tl':
        return 'Tagalog';
      default:
        return code;
    }
  }

  void _editTextField(
    BuildContext context, {
    required String title,
    required String initialValue,
    required ValueChanged<String> onSave,
  }) {
    final controller = TextEditingController(text: initialValue);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () {
              onSave(controller.text);
              Navigator.pop(ctx);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;

  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      child: Text(
        title,
        style: Theme.of(context)
            .textTheme
            .titleSmall
            ?.copyWith(color: Theme.of(context).colorScheme.primary),
      ),
    );
  }
}
