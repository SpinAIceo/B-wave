import 'dart:typed_data';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/defect.dart';
import '../../data/models/detection_result.dart';
import '../../data/services/edge_client.dart';

enum ScanState { idle, scanning, paused, error }

class ScanStatus {
  final ScanState state;
  final List<Defect> detections;
  final bool isConnected;
  final double inferenceTimeMs;
  final String modelVersion;
  final String? errorMessage;

  const ScanStatus({
    this.state = ScanState.idle,
    this.detections = const [],
    this.isConnected = false,
    this.inferenceTimeMs = 0,
    this.modelVersion = 'unknown',
    this.errorMessage,
  });

  ScanStatus copyWith({
    ScanState? state,
    List<Defect>? detections,
    bool? isConnected,
    double? inferenceTimeMs,
    String? modelVersion,
    String? errorMessage,
  }) {
    return ScanStatus(
      state: state ?? this.state,
      detections: detections ?? this.detections,
      isConnected: isConnected ?? this.isConnected,
      inferenceTimeMs: inferenceTimeMs ?? this.inferenceTimeMs,
      modelVersion: modelVersion ?? this.modelVersion,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class ScanController extends StateNotifier<ScanStatus> {
  final EdgeClient _client;
  bool _isProcessing = false;

  ScanController(this._client) : super(const ScanStatus());

  Future<void> initialize() async {
    await _client.connect();
    final healthy = await _client.healthCheck();
    final info = await _client.getModelInfo();
    state = state.copyWith(
      isConnected: healthy,
      modelVersion: info['modelVersion'] as String? ?? 'unknown',
    );
  }

  void startScan() {
    if (state.state == ScanState.scanning) return;
    state = state.copyWith(state: ScanState.scanning);
  }

  void stopScan() {
    state = state.copyWith(
      state: ScanState.idle,
      detections: [],
    );
  }

  void pauseScan() {
    state = state.copyWith(state: ScanState.paused);
  }

  Future<void> processFrame(Uint8List frameBytes, int width, int height) async {
    if (state.state != ScanState.scanning) return;
    if (_isProcessing) return;

    _isProcessing = true;
    try {
      final result = await _client.detectDefects(
        frameBytes,
        width,
        height,
        'inspection-${DateTime.now().millisecondsSinceEpoch}',
      );

      if (result != DetectionResult.empty) {
        state = state.copyWith(
          detections: result.defects,
          inferenceTimeMs: result.inferenceTimeMs,
          modelVersion: result.modelVersion,
          isConnected: true,
        );
      }
    } catch (e) {
      state = state.copyWith(
        state: ScanState.error,
        errorMessage: e.toString(),
        isConnected: false,
      );
    } finally {
      _isProcessing = false;
    }
  }

  @override
  void dispose() {
    _client.dispose();
    super.dispose();
  }
}

final edgeClientProvider = Provider<EdgeClient>((ref) {
  final client = EdgeClient();
  ref.onDispose(() => client.dispose());
  return client;
});

final scanControllerProvider =
    StateNotifierProvider<ScanController, ScanStatus>((ref) {
  final client = ref.watch(edgeClientProvider);
  return ScanController(client);
});
