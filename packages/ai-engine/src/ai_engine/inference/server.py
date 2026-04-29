from __future__ import annotations

import sys
from concurrent import futures
from pathlib import Path

import grpc

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "shared" / "gen" / "python"))

from bwave.v1 import common_pb2, inference_pb2, inference_pb2_grpc  # noqa: E402


class EdgeInferenceServiceServicer(inference_pb2_grpc.EdgeInferenceServiceServicer):
    def DetectDefects(self, request, context):
        return inference_pb2.DetectResponse(
            defects=[],
            inference_time_ms=0.0,
            model_version="0.1.0-stub",
        )

    def GetModelInfo(self, request, context):
        return inference_pb2.ModelInfo(
            model_name="bwave-yolov8-stub",
            model_version="0.1.0-stub",
            supported_defect_types=["RUST", "DAMAGE", "LEAK", "MISSING_LABEL", "CARGO_LASHING"],
            input_width=1280,
            input_height=720,
            runtime="onnxruntime",
        )

    def HealthCheck(self, request, context):
        return common_pb2.HealthStatus(
            healthy=True,
            version="0.1.0",
            uptime_seconds=0.0,
        )


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    inference_pb2_grpc.add_EdgeInferenceServiceServicer_to_server(
        EdgeInferenceServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"EdgeInferenceService listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
