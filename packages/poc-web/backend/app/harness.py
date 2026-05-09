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


# Drop-reason taxonomy — one of these on every dropped detection.
# Lets the caller log a precise WHY for each filtered-out box.
DROP_BELOW_THRESHOLD = "below_threshold"
DROP_NOT_ALLOWED_IN_ZONE = "not_allowed_in_zone"  # informational; always combined with DROP_BELOW_THRESHOLD


@dataclass
class HarnessTrace:
    """Per-detection trace returned by adjust_with_trace().
    Lets callers reconstruct WHY a detection was kept/dropped, step by step."""
    raw_confidence: float
    calibrated_confidence: float          # after temperature_scale
    allowed_in_zone: bool                 # zone allowlist check
    allowlist_factor: float               # 1.0 if allowed (or no allowlist), `disallowed_penalty` otherwise
    zone_prior_factor: float              # multiplicative; 1.0 if no prior
    vessel_type_factor: float             # multiplicative; 1.0 if no modifier
    final_confidence: float               # calibrated × allowlist × prior × vessel_type, clamped to [0, 1]
    threshold_applied: float              # the (zone, class) cutoff
    threshold_zone_key: str               # which zone bucket was used ("default" if zone unknown)
    kept: bool
    drop_reason: str | None               # None when kept


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
        Returns (adjusted_confidence, kept) — `kept=False` means drop.
        For step-by-step diagnostics, use `adjust_with_trace`."""
        adj, kept, _ = self.adjust_with_trace(class_name, raw_confidence, context)
        return adj, kept

    def adjust_with_trace(
        self,
        class_name: str,
        raw_confidence: float,
        context: HarnessContext | None = None,
    ) -> tuple[float, bool, HarnessTrace]:
        """Same as adjust(), but also returns a HarnessTrace describing every
        multiplicative factor and the threshold decision. The trace is intended
        for human-readable logging at WARN/INFO/DEBUG levels."""
        ctx = context or HarnessContext()

        calibrated = temperature_scale(raw_confidence, self.config.calibration_T)

        allowed_in_zone, allowlist_factor = self._allowlist_factor(class_name, ctx)
        zone_prior_factor = self._zone_prior_factor(class_name, ctx)
        vessel_type_factor = self._vessel_type_factor(class_name, ctx)

        final = calibrated * allowlist_factor * zone_prior_factor * vessel_type_factor
        final = max(0.0, min(1.0, final))

        zone_key = ctx.zone if (ctx.zone and ctx.zone in self.config.zone_thresholds) else "default"
        threshold = self._threshold_for(class_name, ctx.zone)
        kept = final >= threshold
        drop_reason = None if kept else DROP_BELOW_THRESHOLD

        trace = HarnessTrace(
            raw_confidence=raw_confidence,
            calibrated_confidence=calibrated,
            allowed_in_zone=allowed_in_zone,
            allowlist_factor=allowlist_factor,
            zone_prior_factor=zone_prior_factor,
            vessel_type_factor=vessel_type_factor,
            final_confidence=final,
            threshold_applied=threshold,
            threshold_zone_key=zone_key,
            kept=kept,
            drop_reason=drop_reason,
        )
        return final, kept, trace

    # ── Introspection helpers (for startup logging) ──────────────────────────

    def describe(self) -> dict:
        """Return a small snapshot of the loaded configuration — handy to
        log at startup so operators can verify what's actually live."""
        return {
            "calibration_T": self.config.calibration_T,
            "default_threshold": self.config.default_threshold,
            "zones_with_thresholds": sorted(self.config.zone_thresholds.keys()),
            "zones_with_allowlist": sorted(self.config.zone_allowed.keys()),
            "vessel_types": sorted(self.config.vessel_type_modifiers.keys()),
            "disallowed_penalty": self.config.disallowed_penalty,
        }

    # Internals -----------------------------------------------------------------

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
            return True, 1.0  # no allowlist defined for this zone
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
    "HarnessDetection",
    "HarnessContext",
    "HarnessConfig",
    "HarnessTrace",
    "InferenceHarness",
    "temperature_scale",
    "DROP_BELOW_THRESHOLD",
    "DROP_NOT_ALLOWED_IN_ZONE",
]
