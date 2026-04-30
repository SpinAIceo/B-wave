import 'dart:async';
import 'dart:math';
import 'dart:typed_data';

import '../models/defect.dart';
import '../models/detection_result.dart';

class EdgeClient {
  final String host;
  final int port;
  bool _connected = false;
  bool _useMock = true;

  EdgeClient({
    this.host = '192.168.1.1',
    this.port = 50051,
  });

  bool get isConnected => _connected;

  Future<void> connect() async {
    try {
      _connected = false;
      _useMock = const bool.fromEnvironment('BWAVE_USE_MOCKS', defaultValue: true);
      if (!_useMock) {
        // TODO: Replace with real gRPC channel when Dart proto stubs are generated
        // final channel = ClientChannel(host, port: port, ...);
        _connected = false;
      } else {
        _connected = true;
      }
    } catch (_) {
      _connected = false;
      _useMock = true;
    }
  }

  Future<DetectionResult> detectDefects(
    Uint8List imageData,
    int width,
    int height,
    String inspectionId,
  ) async {
    try {
      if (_useMock) {
        return _mockDetectDefects();
      }
      // TODO: Real gRPC call
      // final request = DetectRequest()
      //   ..imageData = imageData
      //   ..imageWidth = width
      //   ..imageHeight = height
      //   ..inspectionId = inspectionId;
      // final response = await _stub.detectDefects(request);
      // return _parseResponse(response);
      return DetectionResult.empty;
    } catch (_) {
      return DetectionResult.empty;
    }
  }

  Future<bool> healthCheck() async {
    try {
      if (_useMock) {
        await Future.delayed(const Duration(milliseconds: 50));
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>> getModelInfo() async {
    try {
      if (_useMock) {
        return {
          'modelName': 'bwave-yolov8-defect',
          'modelVersion': '0.1.0',
          'supportedDefectTypes': [
            'rust',
            'damage',
            'leak',
            'missing_label',
            'cargo_lashing',
          ],
          'inputWidth': 1280,
          'inputHeight': 720,
          'runtime': 'onnxruntime',
        };
      }
      return {};
    } catch (_) {
      return {};
    }
  }

  void dispose() {
    _connected = false;
  }

  DetectionResult _mockDetectDefects() {
    final random = Random();
    final defectCount = random.nextInt(4);
    final defects = <Defect>[];

    final mockDefects = [
      Defect(
        bbox: const BoundingBox(xMin: 0.1, yMin: 0.2, xMax: 0.4, yMax: 0.5),
        defectType: DefectType.rust,
        confidence: 0.87,
        pscCode: '0615',
        severity: Severity.high,
      ),
      Defect(
        bbox: const BoundingBox(xMin: 0.5, yMin: 0.1, xMax: 0.8, yMax: 0.35),
        defectType: DefectType.damage,
        confidence: 0.92,
        pscCode: '0630',
        severity: Severity.critical,
      ),
      Defect(
        bbox: const BoundingBox(xMin: 0.3, yMin: 0.6, xMax: 0.6, yMax: 0.85),
        defectType: DefectType.leak,
        confidence: 0.74,
        pscCode: '0950',
        severity: Severity.medium,
      ),
      Defect(
        bbox: const BoundingBox(xMin: 0.6, yMin: 0.5, xMax: 0.9, yMax: 0.75),
        defectType: DefectType.cargoLashing,
        confidence: 0.81,
        pscCode: '0725',
        severity: Severity.high,
      ),
    ];

    for (var i = 0; i < defectCount && i < mockDefects.length; i++) {
      defects.add(mockDefects[i]);
    }

    return DetectionResult(
      defects: defects,
      inferenceTimeMs: 120 + random.nextDouble() * 200,
      modelVersion: '0.1.0-mock',
    );
  }
}
