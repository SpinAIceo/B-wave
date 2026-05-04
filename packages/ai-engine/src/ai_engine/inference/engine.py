from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

CLASS_NAMES = ["rust", "damage", "leak"]


@dataclass
class Detection:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    class_id: int
    class_name: str
    confidence: float


class InferenceEngine:
    """Unified inference engine supporting ONNX, TensorRT, and PyTorch YOLO models."""

    def __init__(self, model_path: str | Path, device: str = "cpu"):
        self.model_path = Path(model_path)
        self.device = device
        self.class_names = list(CLASS_NAMES)
        self._session = None
        self._pt_model = None
        self._image_size = 640
        self._model_version = "unknown"
        self._loaded = False
        self._is_end2end = False

        if self.model_path.exists():
            self._load_model()

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def runtime(self) -> str:
        if self._session is not None:
            return "onnxruntime"
        if self._pt_model is not None:
            return "pytorch"
        return "none"

    def _load_model(self) -> None:
        suffix = self.model_path.suffix.lower()
        if suffix == ".onnx":
            self._load_onnx()
        elif suffix == ".engine":
            self._load_tensorrt()
        else:
            self._load_pytorch()

    def _load_onnx(self) -> None:
        import onnxruntime as ort

        available = ort.get_available_providers()
        providers = ["CPUExecutionProvider"]
        if self.device != "cpu" and "CUDAExecutionProvider" in available:
            providers.insert(0, "CUDAExecutionProvider")
        elif self.device != "cpu" and "TensorrtExecutionProvider" in available:
            providers.insert(0, "TensorrtExecutionProvider")

        self._session = ort.InferenceSession(str(self.model_path), providers=providers)
        input_shape = self._session.get_inputs()[0].shape
        if isinstance(input_shape[2], int):
            self._image_size = input_shape[2]

        outputs = self._session.get_outputs()
        if len(outputs) > 0:
            out_shape = outputs[0].shape
            if (out_shape and len(out_shape) == 3
                    and isinstance(out_shape[-1], int) and out_shape[-1] == 6):
                self._is_end2end = True

        self._model_version = self.model_path.stem
        self._loaded = True

    def _load_tensorrt(self) -> None:
        from ultralytics import YOLO

        self._pt_model = YOLO(str(self.model_path), task="detect")
        self._model_version = self.model_path.stem
        self._loaded = True

    def _load_pytorch(self) -> None:
        from ultralytics import YOLO

        self._pt_model = YOLO(str(self.model_path))
        self._model_version = self.model_path.stem
        self._loaded = True

    def predict(self, image_bytes: bytes, conf_threshold: float = 0.25) -> list[Detection]:
        if not self._loaded:
            return []

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        orig_w, orig_h = image.size

        if self._session is not None:
            return self._predict_onnx(image, orig_w, orig_h, conf_threshold)
        if self._pt_model is not None:
            return self._predict_pytorch(image, orig_w, orig_h, conf_threshold)
        return []

    def _predict_onnx(
        self, image: Image.Image, orig_w: int, orig_h: int, conf_threshold: float
    ) -> list[Detection]:
        resized = image.resize((self._image_size, self._image_size))
        arr = np.array(resized, dtype=np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)[np.newaxis]

        input_name = self._session.get_inputs()[0].name
        outputs = self._session.run(None, {input_name: arr})

        if self._is_end2end:
            return self._parse_end2end_output(outputs[0], orig_w, orig_h, conf_threshold)
        return self._parse_yolo_output(outputs[0], orig_w, orig_h, conf_threshold)

    def _predict_pytorch(
        self, image: Image.Image, orig_w: int, orig_h: int, conf_threshold: float
    ) -> list[Detection]:
        results = self._pt_model.predict(
            np.array(image),
            conf=conf_threshold,
            verbose=False,
            device=self.device,
        )

        detections: list[Detection] = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())

                if cls_id < len(self.class_names):
                    class_name = self.class_names[cls_id]
                else:
                    class_name = "unknown"

                detections.append(Detection(
                    x_min=float(xyxy[0]) / orig_w,
                    y_min=float(xyxy[1]) / orig_h,
                    x_max=float(xyxy[2]) / orig_w,
                    y_max=float(xyxy[3]) / orig_h,
                    class_id=cls_id,
                    class_name=class_name,
                    confidence=conf,
                ))
        return detections

    def _parse_end2end_output(
        self,
        output: np.ndarray,
        orig_w: int,
        orig_h: int,
        conf_threshold: float,
    ) -> list[Detection]:
        """Parse YOLO26 NMS-free end2end output: [batch, num_dets, 6] = [x1,y1,x2,y2,conf,cls]."""
        if output.ndim == 3:
            output = output[0]

        detections: list[Detection] = []
        for row in output:
            x1, y1, x2, y2, conf, cls_id = row[:6]
            if conf < conf_threshold:
                continue
            cls_id = int(cls_id)
            class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else "unknown"
            detections.append(Detection(
                x_min=max(0.0, float(x1) / self._image_size),
                y_min=max(0.0, float(y1) / self._image_size),
                x_max=min(1.0, float(x2) / self._image_size),
                y_max=min(1.0, float(y2) / self._image_size),
                class_id=cls_id,
                class_name=class_name,
                confidence=float(conf),
            ))
        return detections

    def _parse_yolo_output(
        self,
        output: np.ndarray,
        orig_w: int,
        orig_h: int,
        conf_threshold: float,
    ) -> list[Detection]:
        # YOLOv8 output shape: [1, num_classes+4, num_detections]
        if output.ndim == 3:
            output = output[0]

        # Transpose if needed: [num_classes+4, N] → [N, num_classes+4]
        if output.shape[0] < output.shape[1]:
            output = output.T

        detections: list[Detection] = []
        num_classes = output.shape[1] - 4

        for row in output:
            x_center, y_center, w, h = row[:4]
            class_scores = row[4 : 4 + num_classes]
            cls_id = int(np.argmax(class_scores))
            conf = float(class_scores[cls_id])

            if conf < conf_threshold:
                continue

            x_min = (x_center - w / 2) / self._image_size
            y_min = (y_center - h / 2) / self._image_size
            x_max = (x_center + w / 2) / self._image_size
            y_max = (y_center + h / 2) / self._image_size

            class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else "unknown"

            detections.append(Detection(
                x_min=max(0.0, x_min),
                y_min=max(0.0, y_min),
                x_max=min(1.0, x_max),
                y_max=min(1.0, y_max),
                class_id=cls_id,
                class_name=class_name,
                confidence=conf,
            ))

        return _nms(detections, iou_threshold=0.45)


def _nms(detections: list[Detection], iou_threshold: float = 0.45) -> list[Detection]:
    """Simple greedy NMS."""
    if not detections:
        return []

    detections.sort(key=lambda d: d.confidence, reverse=True)
    keep: list[Detection] = []

    for det in detections:
        should_keep = True
        for kept in keep:
            if det.class_id == kept.class_id and _iou(det, kept) > iou_threshold:
                should_keep = False
                break
        if should_keep:
            keep.append(det)

    return keep


def _iou(a: Detection, b: Detection) -> float:
    x1 = max(a.x_min, b.x_min)
    y1 = max(a.y_min, b.y_min)
    x2 = min(a.x_max, b.x_max)
    y2 = min(a.y_max, b.y_max)

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a.x_max - a.x_min) * (a.y_max - a.y_min)
    area_b = (b.x_max - b.x_min) * (b.y_max - b.y_min)
    union = area_a + area_b - inter

    return inter / union if union > 0 else 0.0
