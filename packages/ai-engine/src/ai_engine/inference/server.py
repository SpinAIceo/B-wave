from __future__ import annotations

import os
import sys
import time
from concurrent import futures
from pathlib import Path

import grpc

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "shared" / "gen" / "python"))

from bwave.v1 import common_pb2, inference_pb2, inference_pb2_grpc  # noqa: E402

from .engine import InferenceEngine  # noqa: E402
from .psc_mapper import PSCCodeMapper  # noqa: E402

_DEFECT_TYPE_MAP = {
    "rust": common_pb2.DEFECT_TYPE_RUST,
    "damage": common_pb2.DEFECT_TYPE_DAMAGE,
    "leak": common_pb2.DEFECT_TYPE_LEAK,
    "missing_label": common_pb2.DEFECT_TYPE_MISSING_LABEL,
    "cargo_lashing": common_pb2.DEFECT_TYPE_CARGO_LASHING,
}


class EdgeInferenceServiceServicer(inference_pb2_grpc.EdgeInferenceServiceServicer):
    def __init__(self, engine: InferenceEngine, mapper: PSCCodeMapper):
        self._engine = engine
        self._mapper = mapper
        self._start_time = time.monotonic()

    def DetectDefects(self, request, context):
        if not self._engine.is_loaded:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Model not loaded")
            return inference_pb2.DetectResponse()

        start = time.perf_counter()
        detections = self._engine.predict(request.image_data)
        elapsed_ms = (time.perf_counter() - start) * 1000

        defects = []
        for det in detections:
            mapping = self._mapper.map_defect(det.class_name, det.confidence)
            defects.append(common_pb2.Defect(
                bbox=common_pb2.BoundingBox(
                    x_min=det.x_min,
                    y_min=det.y_min,
                    x_max=det.x_max,
                    y_max=det.y_max,
                ),
                defect_type=_DEFECT_TYPE_MAP.get(
                    det.class_name, common_pb2.DEFECT_TYPE_UNSPECIFIED
                ),
                confidence=det.confidence,
                psc_code=mapping.psc_code,
                severity=int(mapping.severity),
            ))

        return inference_pb2.DetectResponse(
            defects=defects,
            inference_time_ms=elapsed_ms,
            model_version=self._engine.model_version,
        )

    def GetModelInfo(self, request, context):
        return inference_pb2.ModelInfo(
            model_name="bwave-yolov8-defect",
            model_version=self._engine.model_version,
            supported_defect_types=list(self._engine.class_names),
            input_width=self._engine._image_size,
            input_height=self._engine._image_size,
            runtime=self._engine.runtime,
        )

    def HealthCheck(self, request, context):
        return common_pb2.HealthStatus(
            healthy=self._engine.is_loaded,
            version=self._engine.model_version,
            uptime_seconds=time.monotonic() - self._start_time,
        )


def _load_tls_credentials() -> grpc.ServerCredentials | None:
    cert_path = os.environ.get("BWAVE_TLS_CERT")
    key_path = os.environ.get("BWAVE_TLS_KEY")
    ca_path = os.environ.get("BWAVE_TLS_CA")

    if not (cert_path and key_path):
        return None

    cert = Path(cert_path).read_bytes()
    key = Path(key_path).read_bytes()
    ca = Path(ca_path).read_bytes() if ca_path else None

    return grpc.ssl_server_credentials(
        [(key, cert)],
        root_certificates=ca,
        require_client_auth=ca is not None,
    )


def serve(port: int = 50051, model_path: str | None = None):
    if model_path is None:
        model_path = os.environ.get("BWAVE_MODEL_PATH", "models/bwave-defect.onnx")

    engine = InferenceEngine(model_path)
    mapper = PSCCodeMapper()

    max_workers = int(os.environ.get("BWAVE_GRPC_WORKERS", "4"))
    max_concurrent = int(os.environ.get("BWAVE_GRPC_MAX_CONCURRENT", "10"))

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        maximum_concurrent_rpcs=max_concurrent,
        options=[
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),  # 10MB
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
        ],
    )
    inference_pb2_grpc.add_EdgeInferenceServiceServicer_to_server(
        EdgeInferenceServiceServicer(engine, mapper), server
    )

    creds = _load_tls_credentials()
    if creds:
        server.add_secure_port(f"[::]:{port}", creds)
        tls_status = "mTLS" if os.environ.get("BWAVE_TLS_CA") else "TLS"
    else:
        server.add_insecure_port(f"[::]:{port}")
        tls_status = "INSECURE (set BWAVE_TLS_CERT/KEY to enable TLS)"

    server.start()

    model_status = "ready" if engine.is_loaded else "no model"
    print(f"EdgeInferenceService on port {port} — {model_status} — {tls_status}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
