import 'dart:async';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/defect.dart';
import '../../data/models/detection_result.dart';
import '../../data/services/edge_client.dart';
import '../../data/services/inspection_session.dart';
import '../../data/services/local_storage.dart';

enum ScanState { idle, scanning, paused, error }

class ScanStatus {
  final ScanState state;
  final List<Defect> detections;
  final bool isConnected;
  final double inferenceTimeMs;
  final String modelVersion;
  final String? errorMessage;
  final CameraController? cameraController;

  const ScanStatus({
    this.state = ScanState.idle,
    this.detections = const [],
    this.isConnected = false,
    this.inferenceTimeMs = 0,
    this.modelVersion = 'unknown',
    this.errorMessage,
    this.cameraController,
  });

  bool get isCameraReady =>
      cameraController != null && cameraController!.value.isInitialized;

  ScanStatus copyWith({
    ScanState? state,
    List<Defect>? detections,
    bool? isConnected,
    double? inferenceTimeMs,
    String? modelVersion,
    String? errorMessage,
    CameraController? cameraController,
  }) {
    return ScanStatus(
      state: state ?? this.state,
      detections: detections ?? this.detections,
      isConnected: isConnected ?? this.isConnected,
      inferenceTimeMs: inferenceTimeMs ?? this.inferenceTimeMs,
      modelVersion: modelVersion ?? this.modelVersion,
      errorMessage: errorMessage ?? this.errorMessage,
      cameraController: cameraController ?? this.cameraController,
    );
  }
}

class ScanController extends StateNotifier<ScanStatus> {
  final EdgeClient _client;
  /// Optional sink for completed detection results — used to push results
  /// into the shared InspectionSession so they get zone-tagged and visible
  /// in the report screen.
  final void Function(DetectionResult)? onDetectionComplete;
  CameraController? _camera;
  Timer? _captureTimer;
  bool _isProcessing = false;

  // Capture interval: send a frame every 2 seconds while scanning
  static const _captureInterval = Duration(seconds: 2);

  ScanController(this._client, {this.onDetectionComplete})
      : super(const ScanStatus());

  Future<void> initialize() async {
    // Connect to edge server
    await _client.connect();
    final healthy = await _client.healthCheck();
    final info = await _client.getModelInfo();

    // Initialize camera
    final cameras = await availableCameras();
    if (cameras.isEmpty) {
      state = state.copyWith(
        isConnected: healthy,
        modelVersion: info['modelVersion'] as String? ?? 'unknown',
        state: ScanState.error,
        errorMessage: 'No camera available',
      );
      return;
    }

    // Prefer back camera
    final camera = cameras.firstWhere(
      (c) => c.lensDirection == CameraLensDirection.back,
      orElse: () => cameras.first,
    );

    _camera = CameraController(
      camera,
      ResolutionPreset.medium, // 640×480 range — matches edge server expectation
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.jpeg,
    );

    try {
      await _camera!.initialize();
      state = state.copyWith(
        isConnected: healthy,
        modelVersion: info['modelVersion'] as String? ?? 'unknown',
        cameraController: _camera,
      );
    } catch (e) {
      state = state.copyWith(
        isConnected: healthy,
        modelVersion: info['modelVersion'] as String? ?? 'unknown',
        state: ScanState.error,
        errorMessage: 'Camera init failed: $e',
      );
    }
  }

  void startScan() {
    if (state.state == ScanState.scanning) return;
    state = state.copyWith(state: ScanState.scanning, detections: []);
    _captureTimer = Timer.periodic(_captureInterval, (_) => _captureAndInfer());
  }

  void stopScan() {
    _captureTimer?.cancel();
    _captureTimer = null;
    state = state.copyWith(state: ScanState.idle, detections: []);
  }

  void pauseScan() {
    _captureTimer?.cancel();
    _captureTimer = null;
    state = state.copyWith(state: ScanState.paused);
  }

  Future<void> _captureAndInfer() async {
    if (state.state != ScanState.scanning) return;
    if (_isProcessing) return;
    if (_camera == null || !_camera!.value.isInitialized) return;

    _isProcessing = true;
    try {
      final xFile = await _camera!.takePicture();
      final bytes = await xFile.readAsBytes();
      await processFrame(
        bytes,
        _camera!.value.previewSize?.width.toInt() ?? 640,
        _camera!.value.previewSize?.height.toInt() ?? 480,
      );
    } catch (e) {
      // Non-fatal: log and continue; do not stop the scan loop
    } finally {
      _isProcessing = false;
    }
  }

  Future<void> processFrame(Uint8List frameBytes, int width, int height) async {
    if (state.state != ScanState.scanning) return;

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
        // Push to shared session — zone tagging happens there.
        onDetectionComplete?.call(result);
        // Persist result to local Hive cache
        await LocalStorage.instance.saveScanResult(
          inspectionId: 'inspection-${DateTime.now().millisecondsSinceEpoch}',
          result: result,
        );
      }
    } catch (e) {
      state = state.copyWith(
        state: ScanState.error,
        errorMessage: e.toString(),
        isConnected: false,
      );
    }
  }

  @override
  void dispose() {
    _captureTimer?.cancel();
    _camera?.dispose();
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
  return ScanController(
    client,
    onDetectionComplete: (result) {
      ref.read(inspectionSessionProvider.notifier).addScanResult(result);
    },
  );
});
