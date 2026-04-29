import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/models/defect.dart';
import 'defect_overlay_painter.dart';
import 'scan_controller.dart';

class ScanScreen extends ConsumerStatefulWidget {
  const ScanScreen({super.key});

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(scanControllerProvider.notifier).initialize();
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final status = ref.watch(scanControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('B-Wave Scanner'),
        actions: [
          _ConnectionIndicator(isConnected: status.isConnected),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/settings'),
            tooltip: 'Settings',
          ),
        ],
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          _CameraPreviewPlaceholder(isScanning: status.state == ScanState.scanning),
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, _) {
              return CustomPaint(
                painter: DefectOverlayPainter(
                  defects: status.detections,
                  animationValue: _pulseController.value,
                ),
              );
            },
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: _InfoBar(status: status),
          ),
        ],
      ),
      floatingActionButton: SizedBox(
        width: 72,
        height: 72,
        child: FloatingActionButton(
          onPressed: () {
            final controller = ref.read(scanControllerProvider.notifier);
            if (status.state == ScanState.scanning) {
              controller.stopScan();
            } else {
              controller.startScan();
            }
          },
          backgroundColor: status.state == ScanState.scanning
              ? Colors.red
              : Theme.of(context).colorScheme.primary,
          child: Icon(
            status.state == ScanState.scanning ? Icons.stop : Icons.camera,
            size: 36,
          ),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }
}

class _CameraPreviewPlaceholder extends StatelessWidget {
  final bool isScanning;

  const _CameraPreviewPlaceholder({required this.isScanning});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black87,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isScanning ? Icons.videocam : Icons.videocam_off,
              size: 64,
              color: isScanning ? Colors.green : Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              isScanning ? 'Scanning...' : 'Tap to Start Scan',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.white70,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Point camera at equipment to detect defects',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.white38,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ConnectionIndicator extends StatelessWidget {
  final bool isConnected;

  const _ConnectionIndicator({required this.isConnected});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isConnected ? Colors.green : Colors.red,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            isConnected ? 'Edge' : 'Offline',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

class _InfoBar extends StatelessWidget {
  final ScanStatus status;

  const _InfoBar({required this.status});

  @override
  Widget build(BuildContext context) {
    if (status.state != ScanState.scanning && status.detections.isEmpty) {
      return const SizedBox.shrink();
    }

    final criticalCount =
        status.detections.where((d) => d.severity == Severity.critical).length;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      margin: const EdgeInsets.only(bottom: 80),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.8),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _InfoChip(
            icon: Icons.warning_amber,
            label: '${status.detections.length} defects',
            color: status.detections.isEmpty ? Colors.green : Colors.orange,
          ),
          if (criticalCount > 0)
            _InfoChip(
              icon: Icons.error,
              label: '$criticalCount critical',
              color: Colors.red,
            ),
          _InfoChip(
            icon: Icons.speed,
            label: '${status.inferenceTimeMs.toStringAsFixed(0)}ms',
            color: Colors.cyan,
          ),
          _InfoChip(
            icon: Icons.memory,
            label: status.modelVersion,
            color: Colors.grey,
          ),
        ],
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}
