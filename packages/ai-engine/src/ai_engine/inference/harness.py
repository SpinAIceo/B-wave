"""
Inference Harness — post-processing pipeline that lifts a mediocre YOLO model
toward production-quality output without retraining.

Three layers, applied in order:

  1. **Confidence calibration** (temperature scaling)
     A single learned scalar T (fit offline on a validation set) reshapes raw
     softmax scores so that "0.8 confidence" actually means ~80% probability.
     Critical when downstream code (e.g. PSCCodeMapper) maps confidence to
     severity buckets.

  2. **Context-aware filtering**
     Domain priors per (vessel_zone, vessel_type) demote unlikely class /
     zone combinations and boost likely ones — e.g. cargo_lashing on a deck
     of a container ship is plausible; the same on a tanker hull is not.

  3. **Zone-specific thresholding**
     Drops detections whose calibrated, context-adjusted confidence falls
     below a per-(zone, class) cutoff. Recall-vs-precision is tuned per
     deployment environment without touching the model.

Wire-up:

    engine = InferenceEngine(model_path)
    harness = InferenceHarness.load_default()

    raw = engine.predict(image_bytes, conf_threshold=0.05)  # collect liberally
    refined = harness.process(raw, HarnessContext(zone="hull", vessel_type="bulk"))

Calibration data is fit by `scripts/fit_calibration.py`; if no calibration
file exists the harness uses T=1.0 (identity), so the pipeline is safe to
ship before fitting.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Re-import the Detection dataclass so callers can use harness alone
from .engine import Detection

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "harness.yaml"


# ── Configuration objects ────────────────────────────────────────────────────


@dataclass
class HarnessContext:
    """Optional per-request context. All fields default to None — when absent
    the harness falls back to the `default` zone bucket and skips context priors."""
    zone: str | None = None
    vessel_type: str | None = None
    inspection_mode: str | None = None


DROP_BELOW_THRESHOLD = "below_threshold"
DROP_NOT_ALLOWED_IN_ZONE = "not_allowed_in_zone"


@dataclass
class HarnessTrace:
    """Per-detection trace returned by adjust_with_trace().
    Lets callers reconstruct WHY a detection was kept/dropped, step by step."""
    raw_confidence: float
    calibrated_confidence: float
    allowed_in_zone: bool
    allowlist_factor: float
    zone_prior_factor: float
    vessel_type_factor: float
    final_confidence: float
    threshold_applied: float
    threshold_zone_key: str
    kept: bool
    drop_reason: str | None


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


# ── Calibration helpers ──────────────────────────────────────────────────────


def _logit(p: float, eps: float = 1e-6) -> float:
    p = max(eps, min(1.0 - eps, p))
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def temperature_scale(prob: float, T: float) -> float:
    """Apply temperature T to a Bernoulli probability:
       calibrated = sigmoid(logit(p) / T)
    T > 1 softens (overconfident → cooled), T < 1 sharpens.
    T == 1 is the identity."""
    if T == 1.0:
        return prob
    return _sigmoid(_logit(prob) / T)


# ── Main harness ─────────────────────────────────────────────────────────────


class InferenceHarness:
    """Stateless post-processor; safe to share across threads/requests."""

    def __init__(self, config: HarnessConfig):
        self.config = config

    # Convenience constructors --------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InferenceHarness":
        return cls(HarnessConfig.from_dict(data))

    @classmethod
    def from_yaml(cls, path: str | Path) -> "InferenceHarness":
        import yaml  # lazy import — yaml is optional at runtime

        with Path(path).open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)

    @classmethod
    def load_default(cls) -> "InferenceHarness":
        """Try the bundled config; fall back to a no-op harness so the
        pipeline never crashes from a missing file."""
        if DEFAULT_CONFIG_PATH.exists():
            try:
                return cls.from_yaml(DEFAULT_CONFIG_PATH)
            except Exception:
                pass
        return cls(HarnessConfig())

    # Pipeline ------------------------------------------------------------------

    def process(
        self,
        detections: list[Detection],
        context: HarnessContext | None = None,
    ) -> list[Detection]:
        """Apply calibration → context filter → zone threshold; return new list."""
        out: list[Detection] = []
        for det in detections:
            kept, new_conf, _ = self._evaluate(det.class_name, det.confidence, context)
            if not kept:
                continue
            out.append(Detection(
                x_min=det.x_min, y_min=det.y_min,
                x_max=det.x_max, y_max=det.y_max,
                class_id=det.class_id, class_name=det.class_name,
                confidence=new_conf,
            ))
        return out

    def process_with_traces(
        self,
        detections: list[Detection],
        context: HarnessContext | None = None,
    ) -> list[tuple[Detection, HarnessTrace, bool]]:
        """Same as process(), but returns (Detection, HarnessTrace, kept) for
        every input — including dropped ones — so callers can log the chain.
        The Detection's confidence is the final adjusted value."""
        out: list[tuple[Detection, HarnessTrace, bool]] = []
        for det in detections:
            kept, new_conf, trace = self._evaluate(det.class_name, det.confidence, context)
            adjusted = Detection(
                x_min=det.x_min, y_min=det.y_min,
                x_max=det.x_max, y_max=det.y_max,
                class_id=det.class_id, class_name=det.class_name,
                confidence=new_conf,
            )
            out.append((adjusted, trace, kept))
        return out

    def describe(self) -> dict:
        """Snapshot of the loaded configuration — useful at startup."""
        return {
            "calibration_T": self.config.calibration_T,
            "default_threshold": self.config.default_threshold,
            "zones_with_thresholds": sorted(self.config.zone_thresholds.keys()),
            "zones_with_allowlist": sorted(self.config.zone_allowed.keys()),
            "vessel_types": sorted(self.config.vessel_type_modifiers.keys()),
            "disallowed_penalty": self.config.disallowed_penalty,
        }

    # Internals -----------------------------------------------------------------

    def _evaluate(
        self, class_name: str, raw_conf: float, context: HarnessContext | None
    ) -> tuple[bool, float, HarnessTrace]:
        """Single-detection pipeline. Returns (kept, final_conf, trace)."""
        ctx = context or HarnessContext()
        calibrated = temperature_scale(raw_conf, self.config.calibration_T)

        allowed_in_zone, allowlist_f = self._allowlist_factor(class_name, ctx)
        zone_prior_f = self._zone_prior_factor(class_name, ctx)
        vessel_type_f = self._vessel_type_factor(class_name, ctx)

        final = calibrated * allowlist_f * zone_prior_f * vessel_type_f
        final = max(0.0, min(1.0, final))

        zone_key = ctx.zone if (ctx.zone and ctx.zone in self.config.zone_thresholds) else "default"
        threshold = self._threshold_for(class_name, ctx.zone)
        kept = final >= threshold

        trace = HarnessTrace(
            raw_confidence=raw_conf,
            calibrated_confidence=calibrated,
            allowed_in_zone=allowed_in_zone,
            allowlist_factor=allowlist_f,
            zone_prior_factor=zone_prior_f,
            vessel_type_factor=vessel_type_f,
            final_confidence=final,
            threshold_applied=threshold,
            threshold_zone_key=zone_key,
            kept=kept,
            drop_reason=None if kept else DROP_BELOW_THRESHOLD,
        )
        return kept, final, trace

    def _threshold_for(self, class_name: str, zone: str | None) -> float:
        zone_key = zone if (zone and zone in self.config.zone_thresholds) else "default"
        zone_map = self.config.zone_thresholds.get(zone_key, {})
        return zone_map.get(class_name, self.config.default_threshold)

    def _allowlist_factor(
        self, class_name: str, ctx: HarnessContext
    ) -> tuple[bool, float]:
        if not ctx.zone:
            return True, 1.0
        allowed = self.config.zone_allowed.get(ctx.zone)
        if allowed is None:
            return True, 1.0
        if class_name in allowed:
            return True, 1.0
        return False, self.config.disallowed_penalty

    def _zone_prior_factor(self, class_name: str, ctx: HarnessContext) -> float:
        if not ctx.zone:
            return 1.0
        return self.config.zone_priors.get(ctx.zone, {}).get(class_name, 1.0)

    def _vessel_type_factor(self, class_name: str, ctx: HarnessContext) -> float:
        if not ctx.vessel_type:
            return 1.0
        vt_mods = self.config.vessel_type_modifiers.get(ctx.vessel_type.lower(), {})
        return vt_mods.get(class_name, 1.0)


__all__ = [
    "Detection",
    "HarnessContext",
    "HarnessConfig",
    "HarnessTrace",
    "InferenceHarness",
    "temperature_scale",
    "DROP_BELOW_THRESHOLD",
    "DROP_NOT_ALLOWED_IN_ZONE",
]
