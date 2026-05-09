"""Unit tests for the inference harness post-processor."""
from __future__ import annotations

import math

import pytest

from ai_engine.inference.engine import Detection
from ai_engine.inference.harness import (
    DROP_BELOW_THRESHOLD,
    HarnessConfig,
    HarnessContext,
    HarnessTrace,
    InferenceHarness,
    temperature_scale,
)


def _det(class_name: str, conf: float, cls_id: int = 0) -> Detection:
    return Detection(
        x_min=0.1, y_min=0.1, x_max=0.4, y_max=0.4,
        class_id=cls_id, class_name=class_name, confidence=conf,
    )


# ── temperature_scale ────────────────────────────────────────────────────────


def test_temperature_T1_is_identity():
    for p in (0.05, 0.4, 0.5, 0.6, 0.95):
        assert temperature_scale(p, 1.0) == p


def test_temperature_T_high_pulls_toward_half():
    # T > 1 cools overconfident values toward 0.5
    assert temperature_scale(0.95, 3.0) < 0.95
    assert temperature_scale(0.95, 3.0) > 0.5
    assert temperature_scale(0.05, 3.0) > 0.05
    assert temperature_scale(0.05, 3.0) < 0.5


def test_temperature_T_low_sharpens():
    # T < 1 sharpens — pushes away from 0.5 toward extremes
    assert temperature_scale(0.6, 0.5) > 0.6
    assert temperature_scale(0.4, 0.5) < 0.4


def test_temperature_handles_extremes():
    # T=1 is the identity — pass-through (no eps clamping in this fast path)
    assert temperature_scale(0.0, 1.0) == 0.0
    assert temperature_scale(1.0, 1.0) == 1.0
    # T != 1 routes through logit/sigmoid, which clamps via eps to avoid inf
    assert 0.0 < temperature_scale(0.0, 2.0) < 1.0
    assert 0.0 < temperature_scale(1.0, 2.0) < 1.0
    # symmetric around 0.5
    assert math.isclose(
        temperature_scale(0.7, 2.0) - 0.5,
        0.5 - temperature_scale(0.3, 2.0),
        abs_tol=1e-9,
    )


# ── HarnessConfig.from_dict ──────────────────────────────────────────────────


def test_config_from_empty_dict_has_defaults():
    cfg = HarnessConfig.from_dict({})
    assert cfg.calibration_T == 1.0
    assert cfg.default_threshold == 0.25
    assert cfg.zone_thresholds == {}
    assert cfg.disallowed_penalty == 0.4


def test_config_from_full_dict():
    cfg = HarnessConfig.from_dict({
        "calibration": {"temperature": 1.7},
        "default_threshold": 0.3,
        "zone_thresholds": {"hull": {"rust": 0.18}},
        "context_rules": {
            "disallowed_penalty": 0.2,
            "zones": {
                "hull": {"allowed": ["rust"], "priors": {"rust": 1.2}},
            },
            "vessel_types": {"bulk": {"cargo_lashing": 0.5}},
        },
    })
    assert cfg.calibration_T == 1.7
    assert cfg.zone_thresholds["hull"]["rust"] == 0.18
    assert cfg.zone_allowed["hull"] == ["rust"]
    assert cfg.zone_priors["hull"]["rust"] == 1.2
    assert cfg.vessel_type_modifiers["bulk"]["cargo_lashing"] == 0.5
    assert cfg.disallowed_penalty == 0.2


# ── InferenceHarness.process — integration scenarios ────────────────────────


def test_noop_harness_keeps_above_default_threshold():
    h = InferenceHarness(HarnessConfig())  # all defaults: T=1, thr=0.25
    out = h.process([_det("rust", 0.30), _det("rust", 0.20)])
    assert len(out) == 1
    assert out[0].confidence == 0.30


def test_zone_threshold_lookup_overrides_default():
    h = InferenceHarness(HarnessConfig(
        default_threshold=0.50,
        zone_thresholds={"hull": {"rust": 0.10}},
    ))
    # rust @ 0.15 — would be dropped at default 0.50, but hull threshold is 0.10
    out = h.process([_det("rust", 0.15)], HarnessContext(zone="hull"))
    assert len(out) == 1


def test_disallowed_class_in_zone_gets_demoted():
    h = InferenceHarness(HarnessConfig(
        default_threshold=0.30,
        zone_thresholds={"hull": {"rust": 0.30, "cargo_lashing": 0.30}},
        zone_allowed={"hull": ["rust"]},  # cargo_lashing not allowed
        disallowed_penalty=0.4,
    ))
    # cargo_lashing at 0.5 → 0.5 * 0.4 = 0.2 → below threshold → dropped
    out = h.process(
        [_det("cargo_lashing", 0.5), _det("rust", 0.5)],
        HarnessContext(zone="hull"),
    )
    assert len(out) == 1
    assert out[0].class_name == "rust"


def test_zone_prior_boosts_class():
    h = InferenceHarness(HarnessConfig(
        default_threshold=0.30,
        zone_thresholds={"engine_room": {"leak": 0.30}},
        zone_priors={"engine_room": {"leak": 1.5}},
    ))
    # leak at 0.22 * 1.5 = 0.33 → kept
    out = h.process([_det("leak", 0.22)], HarnessContext(zone="engine_room"))
    assert len(out) == 1
    assert out[0].confidence == pytest.approx(0.33, abs=0.001)


def test_vessel_type_modifier_demotes():
    h = InferenceHarness(HarnessConfig(
        default_threshold=0.30,
        zone_thresholds={"deck": {"cargo_lashing": 0.30}},
        vessel_type_modifiers={"tanker": {"cargo_lashing": 0.4}},
    ))
    # cargo_lashing at 0.6 * 0.4 = 0.24 → dropped on tanker
    out = h.process(
        [_det("cargo_lashing", 0.6)],
        HarnessContext(zone="deck", vessel_type="tanker"),
    )
    assert out == []


def test_calibration_then_threshold():
    h = InferenceHarness(HarnessConfig(
        calibration_T=2.0,  # cools confidence toward 0.5
        default_threshold=0.50,
    ))
    # raw 0.95 → calibrated ~0.74 → above 0.5 → kept
    out = h.process([_det("rust", 0.95)])
    assert len(out) == 1
    assert out[0].confidence < 0.95
    assert out[0].confidence > 0.5


def test_pipeline_combination():
    """Calibration → context (boost) → zone threshold all chained."""
    h = InferenceHarness(HarnessConfig(
        calibration_T=1.5,
        default_threshold=0.25,
        zone_thresholds={"hull": {"rust": 0.20}},
        zone_priors={"hull": {"rust": 1.10}},
    ))
    # raw 0.4 → calibrated (T=1.5) ≈ 0.435 → × 1.10 ≈ 0.479 → above 0.20 ✓
    out = h.process([_det("rust", 0.4)], HarnessContext(zone="hull"))
    assert len(out) == 1
    assert out[0].confidence > 0.4  # boosted


def test_load_default_falls_back_when_no_config():
    """If config file is missing, returns no-op harness (T=1, default=0.25)."""
    h = InferenceHarness.load_default()
    # Whether config exists or not, this must succeed and act sanely
    out = h.process([_det("rust", 0.30)])
    assert isinstance(out, list)


def test_unknown_zone_uses_default_thresholds():
    h = InferenceHarness(HarnessConfig(
        default_threshold=0.40,
        zone_thresholds={
            "hull": {"rust": 0.15},
            "default": {"rust": 0.40},
        },
    ))
    # zone="cabin" not in config → uses default → 0.30 dropped
    out = h.process([_det("rust", 0.30)], HarnessContext(zone="cabin"))
    assert out == []


# ── trace API ────────────────────────────────────────────────────────────────


def test_process_with_traces_returns_per_detection_trace():
    h = InferenceHarness(HarnessConfig(
        calibration_T=2.0,
        default_threshold=0.30,
        zone_thresholds={"hull": {"rust": 0.20, "leak": 0.50}},
        zone_allowed={"hull": ["rust"]},
        zone_priors={"hull": {"rust": 1.10}},
        disallowed_penalty=0.4,
    ))
    out = h.process_with_traces(
        [_det("rust", 0.40), _det("leak", 0.50)],
        HarnessContext(zone="hull", vessel_type="bulk"),
    )
    assert len(out) == 2

    rust_det, rust_trace, rust_kept = out[0]
    leak_det, leak_trace, leak_kept = out[1]

    # rust: allowed, gets boosted, kept
    assert isinstance(rust_trace, HarnessTrace)
    assert rust_trace.allowed_in_zone is True
    assert rust_trace.allowlist_factor == 1.0
    assert rust_trace.zone_prior_factor == 1.10
    assert rust_trace.kept is True
    assert rust_trace.drop_reason is None
    assert rust_kept is True
    assert rust_det.confidence == rust_trace.final_confidence

    # leak: NOT in hull allowlist, gets demoted by 0.4, dropped
    assert leak_trace.allowed_in_zone is False
    assert leak_trace.allowlist_factor == 0.4
    assert leak_trace.kept is False
    assert leak_trace.drop_reason == DROP_BELOW_THRESHOLD
    assert leak_kept is False


def test_describe_returns_config_snapshot():
    h = InferenceHarness(HarnessConfig(
        calibration_T=1.5,
        default_threshold=0.3,
        zone_thresholds={"hull": {}, "deck": {}},
        zone_allowed={"hull": ["rust"]},
        vessel_type_modifiers={"bulk": {}, "tanker": {}},
    ))
    info = h.describe()
    assert info["calibration_T"] == 1.5
    assert info["default_threshold"] == 0.3
    assert info["zones_with_thresholds"] == ["deck", "hull"]
    assert info["zones_with_allowlist"] == ["hull"]
    assert info["vessel_types"] == ["bulk", "tanker"]


def test_trace_threshold_zone_key_falls_back_to_default():
    h = InferenceHarness(HarnessConfig(
        zone_thresholds={"hull": {"rust": 0.10}, "default": {"rust": 0.40}},
    ))
    # Unknown zone → trace must reflect 'default' bucket
    out = h.process_with_traces(
        [_det("rust", 0.50)],
        HarnessContext(zone="unknown_zone"),
    )
    _, trace, _ = out[0]
    assert trace.threshold_zone_key == "default"
    assert trace.threshold_applied == 0.40
