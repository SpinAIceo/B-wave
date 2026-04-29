from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PSCMapping:
    psc_code: str
    severity: Severity
    description: str


# PSC deficiency code mapping per defect type
_DEFECT_TO_PSC: dict[str, str] = {
    "rust": "0615",
    "damage": "0630",
    "leak": "0950",
    "missing_label": "1320",
    "cargo_lashing": "0725",
}

_PSC_DESCRIPTIONS: dict[str, str] = {
    "0615": "Hull corrosion / wastage",
    "0630": "Structural deficiency",
    "0950": "Oil / water leakage",
    "1320": "Safety signs / labels missing",
    "0725": "Cargo securing deficiency",
}


class PSCCodeMapper:
    """Maps AI-detected defect types and confidence to PSC violation codes."""

    def __init__(
        self,
        critical_threshold: float = 0.8,
        high_threshold: float = 0.6,
        medium_threshold: float = 0.4,
    ):
        self.critical_threshold = critical_threshold
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def map_defect(self, defect_type: str, confidence: float) -> PSCMapping:
        psc_code = _DEFECT_TO_PSC.get(defect_type, "9999")
        severity = self._classify_severity(confidence)
        description = _PSC_DESCRIPTIONS.get(psc_code, "Unknown deficiency")

        return PSCMapping(
            psc_code=psc_code,
            severity=severity,
            description=description,
        )

    def _classify_severity(self, confidence: float) -> Severity:
        if confidence >= self.critical_threshold:
            return Severity.CRITICAL
        if confidence >= self.high_threshold:
            return Severity.HIGH
        if confidence >= self.medium_threshold:
            return Severity.MEDIUM
        return Severity.LOW

    @staticmethod
    def get_psc_code(defect_type: str) -> str:
        return _DEFECT_TO_PSC.get(defect_type, "9999")

    @staticmethod
    def get_all_mappings() -> dict[str, str]:
        return dict(_DEFECT_TO_PSC)
