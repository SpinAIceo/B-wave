import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/models/defect.dart';
import '../../data/services/inspection_session.dart';
import '../../widgets/vessel_diagram.dart';
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

  void _openZonePicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        final session = ref.watch(inspectionSessionProvider);
        return Container(
          decoration: const BoxDecoration(
            color: Color(0xFF1a1a2e),
            borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
          ),
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('점검 구역 선택',
                      style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w700)),
                  IconButton(icon: const Icon(Icons.close, color: Colors.white70),
                      onPressed: () => Navigator.pop(ctx)),
                ],
              ),
              const SizedBox(height: 4),
              const Text(
                '구역을 선택하면 다음 촬영부터 자동으로 태깅됩니다',
                style: TextStyle(color: Colors.white60, fontSize: 12),
              ),
              const SizedBox(height: 12),
              VesselDiagram(
                selectedZone: session.currentZone,
                zoneCounts: session.defectsByZone,
                onZoneTap: (zone) {
                  ref.read(inspectionSessionProvider.notifier).setCurrentZone(zone);
                  Navigator.pop(ctx);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final status = ref.watch(scanControllerProvider);
    final session = ref.watch(inspectionSessionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('B-Wave Scanner'),
        actions: [
          ActionChip(
            avatar: const Icon(Icons.location_on, size: 16, color: Colors.tealAccent),
            label: Text(session.currentZone.displayName,
                style: const TextStyle(fontSize: 12)),
            onPressed: () => _openZonePicker(context),
            backgroundColor: Colors.teal.withValues(alpha: 0.18),
          ),
          const SizedBox(width: 6),
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
          _CameraView(status: status),
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

class _CameraView extends StatelessWidget {
  final ScanStatus status;

  const _CameraView({required this.status});

  @override
  Widget build(BuildContext context) {
    if (status.isCameraReady) {
      return CameraPreview(status.cameraController!);
    }

    // Fallback while camera is initializing or unavailable
    return Container(
      color: Colors.black87,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              status.state == ScanState.error ? Icons.videocam_off : Icons.videocam,
              size: 64,
              color: status.state == ScanState.error ? Colors.red : Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              status.state == ScanState.error
                  ? (status.errorMessage ?? 'Camera error')
                  : 'Initializing camera...',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(color: Colors.white70),
              textAlign: TextAlign.center,
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
