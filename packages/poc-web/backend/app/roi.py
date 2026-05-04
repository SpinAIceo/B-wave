from __future__ import annotations

from app.models import RoiResponse
from app.risk import PORT_DB, DEFECT_RISK, _risk_level

# Daily cost of vessel detention by type (USD)
VESSEL_DAILY_COST: dict[str, float] = {
    "bulk_carrier": 15_000,
    "container": 50_000,
    "tanker": 35_000,
    "ro_ro": 25_000,
    "gas_carrier": 45_000,
    "passenger": 80_000,
    "general_cargo": 12_000,
}

# Cargo delay cost multiplier ($ per day per 1000 DWT)
CARGO_COST_PER_1000DWT = 200

# PSC deficiency rectification costs
DEFECT_REPAIR_COST: dict[str, float] = {
    "rust": 5_000,
    "damage": 15_000,
    "leak": 8_000,
}

# B-Wave system pricing
BWAVE_ANNUAL_COST = 20_000  # USD/year per vessel


def calculate_roi(
    defects: list[str],
    port_code: str,
    vessel_type: str,
    vessel_dwt: int,
) -> RoiResponse:
    port_info = PORT_DB.get(port_code)
    base_rate = port_info[2] if port_info else 3.0
    defect_contrib = sum(DEFECT_RISK.get(d, 1.0) for d in defects)
    adjusted_rate = min(base_rate + defect_contrib, 99.0)
    risk_level = _risk_level(adjusted_rate)

    # Expected detention probability and duration
    detention_prob = adjusted_rate / 100
    avg_days_map = {"LOW": 1.5, "MEDIUM": 2.0, "HIGH": 2.5, "CRITICAL": 3.5}
    avg_days = avg_days_map.get(risk_level, 2.0)
    expected_detention_days = detention_prob * avg_days

    # Vessel operating cost
    daily_cost = VESSEL_DAILY_COST.get(vessel_type, 20_000)
    detention_cost = expected_detention_days * daily_cost

    # Cargo delay cost (DWT * rate * days)
    cargo_delay_cost = (vessel_dwt / 1000) * CARGO_COST_PER_1000DWT * expected_detention_days

    # Reputational / administrative (fixed 20% of direct costs)
    reputational_cost = (detention_cost + cargo_delay_cost) * 0.20

    total_risk = detention_cost + cargo_delay_cost + reputational_cost

    # ROI calculation
    roi_ratio = total_risk / BWAVE_ANNUAL_COST if total_risk > 0 else 0
    payback_months = (BWAVE_ANNUAL_COST / total_risk * 12) if total_risk > 0 else 999

    breakdown = {
        "detention_probability": f"{adjusted_rate:.1f}%",
        "expected_detention_days": round(expected_detention_days, 2),
        "vessel_daily_cost_usd": daily_cost,
        "defects_detected": defects,
        "repair_cost_estimate_usd": sum(DEFECT_REPAIR_COST.get(d, 5_000) for d in defects),
        "annual_voyages_protected": 12,
    }

    return RoiResponse(
        expected_detention_days=round(expected_detention_days, 2),
        detention_cost_usd=round(detention_cost, 0),
        cargo_delay_cost_usd=round(cargo_delay_cost, 0),
        reputational_cost_usd=round(reputational_cost, 0),
        total_risk_usd=round(total_risk, 0),
        bwave_annual_cost_usd=BWAVE_ANNUAL_COST,
        roi_ratio=round(roi_ratio, 2),
        payback_months=round(min(payback_months, 99.0), 1),
        breakdown=breakdown,
    )
