from __future__ import annotations

from app.models import RiskFactor, RiskResponse

# MOU port database: code → (name, region, base_detention_rate%)
PORT_DB: dict[str, tuple[str, str, float]] = {
    "CNSHA": ("Shanghai", "Tokyo MOU", 4.5),
    "CNTAO": ("Qingdao", "Tokyo MOU", 4.2),
    "CNNGB": ("Ningbo", "Tokyo MOU", 4.8),
    "JPTYO": ("Tokyo", "Tokyo MOU", 1.2),
    "JPOSA": ("Osaka", "Tokyo MOU", 1.1),
    "KRPUS": ("Busan", "Tokyo MOU", 2.3),
    "SGSIN": ("Singapore", "Indian Ocean MOU", 1.8),
    "AUMEL": ("Melbourne", "Indian Ocean MOU", 3.2),
    "AUSYD": ("Sydney", "Indian Ocean MOU", 3.4),
    "AUPAK": ("Port Adelaide", "Indian Ocean MOU", 3.1),
    "NLRTM": ("Rotterdam", "Paris MOU", 2.1),
    "BEANR": ("Antwerp", "Paris MOU", 2.4),
    "DEHAM": ("Hamburg", "Paris MOU", 2.0),
    "GBSOU": ("Southampton", "Paris MOU", 2.2),
    "ESBCN": ("Barcelona", "Paris MOU", 3.0),
    "USNYC": ("New York", "USCG", 5.2),
    "USLAX": ("Los Angeles", "USCG", 4.8),
    "USHOU": ("Houston", "USCG", 5.0),
    "AEDXB": ("Dubai", "Indian Ocean MOU", 2.8),
    "INBOM": ("Mumbai", "Indian Ocean MOU", 3.6),
    "BRSSZ": ("Santos", "Acuerdo de Viña del Mar", 3.9),
    "ZACPT": ("Cape Town", "Abuja MOU", 4.1),
    "EGPSD": ("Port Said", "Mediterranean MOU", 3.3),
}

# Defect risk contribution in percentage points
DEFECT_RISK: dict[str, float] = {
    "rust": 2.0,
    "damage": 3.5,
    "leak": 5.0,
}

# Vessel age factor
def _age_factor(age_years: int) -> float:
    if age_years < 5:
        return 0.0
    if age_years < 10:
        return 0.5
    if age_years < 15:
        return 1.5
    return 3.0


def _risk_level(rate: float) -> str:
    if rate < 2.0:
        return "LOW"
    if rate < 4.0:
        return "MEDIUM"
    if rate < 6.0:
        return "HIGH"
    return "CRITICAL"


def _recommendation(risk_level: str, defects: list[str]) -> str:
    if not defects:
        if risk_level in ("LOW", "MEDIUM"):
            return "No critical defects detected. Maintain regular inspection schedule."
        return "High-risk port. Conduct thorough pre-arrival inspection."
    defect_str = ", ".join(defects)
    if risk_level == "CRITICAL":
        return f"URGENT: {defect_str} detected in critical-risk port. Immediate rectification required before port call."
    if risk_level == "HIGH":
        return f"HIGH RISK: {defect_str} defects significantly increase detention probability. Rectify before arrival."
    return f"Moderate risk: {defect_str} detected. Schedule rectification to reduce detention probability."


def calculate_risk(port_code: str, defects: list[str], vessel_age_years: int) -> RiskResponse:
    port_info = PORT_DB.get(port_code)
    if port_info is None:
        port_name, mou_region, base_rate = "Unknown Port", "Unknown MOU", 3.0
    else:
        port_name, mou_region, base_rate = port_info

    factors: list[RiskFactor] = [
        RiskFactor(label=f"{port_name} base rate", contribution=base_rate)
    ]

    defect_contrib = sum(DEFECT_RISK.get(d, 1.0) for d in defects)
    if defect_contrib > 0:
        factors.append(RiskFactor(label=f"Detected defects ({', '.join(defects)})", contribution=defect_contrib))

    age_contrib = _age_factor(vessel_age_years)
    if age_contrib > 0:
        factors.append(RiskFactor(label=f"Vessel age ({vessel_age_years} years)", contribution=age_contrib))

    adjusted = min(base_rate + defect_contrib + age_contrib, 99.0)
    risk_level = _risk_level(adjusted)

    # Historical average detention: longer in stricter regions
    avg_days_map = {"Paris MOU": 2.0, "Tokyo MOU": 1.8, "USCG": 2.5, "Indian Ocean MOU": 1.5}
    avg_days = avg_days_map.get(mou_region, 2.0)

    return RiskResponse(
        port_code=port_code,
        port_name=port_name,
        mou_region=mou_region,
        base_detention_rate=round(base_rate, 1),
        adjusted_detention_rate=round(adjusted, 1),
        risk_level=risk_level,
        risk_factors=factors,
        historical_average_days=avg_days,
        recommendation=_recommendation(risk_level, defects),
    )
