from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..inference.engine import Detection, InferenceEngine


class CargoSubtype(StrEnum):
    LASHING_LOOSE = "LASHING_LOOSE"
    TURNBUCKLE_BROKEN = "TURNBUCKLE_BROKEN"
    WIRE_CUT = "WIRE_CUT"
    SECURING_MISSING = "SECURING_MISSING"


@dataclass
class CargoDefect:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    defect_subtype: CargoSubtype
    confidence: float
    psc_code: str = "0725"


class CargoSecuringDetector:
    """Specialized detector for 2026 CIC cargo securing defects.

    Wraps an InferenceEngine and filters to cargo_lashing detections,
    then classifies sub-types via bbox heuristics.
    """

    CARGO_CLASS_NAME = "cargo_lashing"

    def __init__(self, engine: InferenceEngine):
        self._engine = engine

    def detect(self, image_bytes: bytes, conf_threshold: float = 0.25) -> list[CargoDefect]:
        all_detections = self._engine.predict(image_bytes, conf_threshold=conf_threshold)
        cargo_detections = [d for d in all_detections if d.class_name == self.CARGO_CLASS_NAME]
        return [self._classify_subtype(d) for d in cargo_detections]

    def _classify_subtype(self, det: Detection) -> CargoDefect:
        subtype = self._infer_subtype(det)
        return CargoDefect(
            x_min=det.x_min,
            y_min=det.y_min,
            x_max=det.x_max,
            y_max=det.y_max,
            defect_subtype=subtype,
            confidence=det.confidence,
        )

    @staticmethod
    def _infer_subtype(det: Detection) -> CargoSubtype:
        """Heuristic subtype classification based on bbox geometry.

        This is placeholder logic — will be replaced by a dedicated
        classifier once labeled cargo-securing training data is available.
        """
        width = det.x_max - det.x_min
        height = det.y_max - det.y_min

        if height < 0.001 or width < 0.001:
            return CargoSubtype.SECURING_MISSING

        aspect_ratio = width / height

        # Tall narrow → lashing rod / turnbuckle
        if aspect_ratio < 0.4:
            if det.confidence > 0.7:
                return CargoSubtype.TURNBUCKLE_BROKEN
            return CargoSubtype.LASHING_LOOSE

        # Wide short → wire / strap
        if aspect_ratio > 2.5:
            return CargoSubtype.WIRE_CUT

        # Square-ish or large area → missing securing element
        if (width * height) > 0.05:
            return CargoSubtype.SECURING_MISSING
        return CargoSubtype.LASHING_LOOSE
