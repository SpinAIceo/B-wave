"""
Inference Harness — lightweight standalone copy for poc-web backend.

This is a self-contained version of `ai_engine.inference.harness` that
poc-web/backend can use without depending on the ai-engine package
(Railway deploys this folder in isolation).

Three-stage pipeline applied to raw YOLO detections:
  1. Confidence calibration  (temperature scaling, single scalar T)
  2. Context-aware filtering  (zone allowlist + per-class priors + vessel-type modifiers)
  3. Zone-specific thresholds (per (zone, class) cutoff)

Configured via `harness.yaml` next to this file. Falls back to a no-op
harness if YAML is missing/invalid so the pipeline never crashes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent / "harness.yaml"


@dataclass
class HarnessDetection:
    """Minimal detection record passed through the harness."""
    class_name: str
    confidence: float


@dataclass
class HarnessContext:
    zone: str | None = None
    vessel_type: str | None = None
    inspection_mode: str | None = None


@dataclass
class HarnessConfig:
    calibration_T: float = 1.0
    default_threshold: float = 0.25
    zone_thresholds: dict[str, dict[str, float]] = field(default_factory=dict)
    zone_allowed: dict[str, list[str]] = field(default_factory=dict)
    zone_priors: dict[str, dict[str, float]] = field(default_factory=dict)
    vessel_type_modifiers: dict[str, dict[str, float]] = field(default_factory=dict)
    disallowed_penalty: float = 0.4

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HarnessConfig":
        cal = (data.get("calibration") or {}).get("temperature", 1.0)
        ctx = data.get("context_rules") or {}
        return cls(
            calibration_T=float(cal),
            default_threshold=float(data.get("default_threshold", 0.25)),
            zone_thresholds={
                z: {k: float(v) for k, v in vals.items()}
                for z, vals in (data.get("zone_thresholds") or {}).items()
            },
            zone_allowed={
                z: list(rules.get("allowed", []))
                for z, rules in (ctx.get("zones") or {}).items()
            },
            zone_priors={
                z: {k: float(v) for k, v in (rules.get("priors") or {}).items()}
                for z, rules in (ctx.get("zones") or {}).items()
            },
            vessel_type_modifiers={
                t: {k: float(v) for k, v in mods.items()}
                for t, mods in (ctx.get("vessel_types") or {}).items()
            },
            disallowed_penalty=float(ctx.get("disallowed_penalty", 0.4)),
        )


def _logit(p: float, eps: float = 1e-6) -> float:
    p = max(eps, min(1.0 - eps, p))
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def temperature_scale(prob: float, T: float) -> float:
    if T == 1.0:
        return prob
    return _sigmoid(_logit(prob) / T)


class InferenceHarness:
    """Stateless post-processor; safe to share across requests."""

    def __init__(self, config: HarnessConfig):
        self.config = config

    @classmethod
    def load_default(cls) -> "InferenceHarness":
        if CONFIG_PATH.exists():
            try:
                import yaml

                with CONFIG_PATH.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                return cls(HarnessConfig.from_dict(data))
            except Exception:
                pass
        return cls(HarnessConfig())

    def adjust(
        self,
        class_name: str,
        raw_confidence: float,
        context: HarnessContext | None = None,
    ) -> tuple[float, bool]:
        """Apply pipeline to a single detection.
        Returns (adjusted_confidence, kept) — `kept=False` means drop."""
        ctx = context or HarnessContext()

        conf = temperature_scale(raw_confidence, self.config.calibration_T)
        conf *= self._context_factor(class_name, ctx)
        conf = max(0.0, min(1.0, conf))

        threshold = self._threshold_for(class_name, ctx.zone)
        return conf, conf >= threshold

    # Internals -----------------------------------------------------------------

    def _threshold_for(self, class_name: str, zone: str | None) -> float:
        zone_key = zone if (zone and zone in self.config.zone_thresholds) else "default"
        zone_map = self.config.zone_thresholds.get(zone_key, {})
        return zone_map.get(class_name, self.config.default_threshold)

    def _context_factor(self, class_name: str, ctx: HarnessContext) -> float:
        factor = 1.0

        if ctx.zone:
            allowed = self.config.zone_allowed.get(ctx.zone)
            if allowed and class_name not in allowed:
                factor *= self.config.disallowed_penalty
            zone_prior = self.config.zone_priors.get(ctx.zone, {}).get(class_name)
            if zone_prior is not None:
                factor *= zone_prior

        if ctx.vessel_type:
            vt_mods = self.config.vessel_type_modifiers.get(ctx.vessel_type.lower(), {})
            mod = vt_mods.get(class_name)
            if mod is not None:
                factor *= mod

        return factor


__all__ = [
    "HarnessDetection",
    "HarnessContext",
    "HarnessConfig",
    "InferenceHarness",
    "temperature_scale",
]
