"""
Deterministic risk-scoring engine.

R = w1(Internal Risk) + w2(External Risk) + w3(Time Pressure) + w4(Historical Risk)
"""

from dataclasses import dataclass, field
from typing import Dict

from models import OperationPriority, RiskLevel

DEFAULT_WEIGHTS: Dict[str, float] = {
    "internal": 0.35,
    "external": 0.30,
    "time_pressure": 0.20,
    "historical": 0.15,
}

RISK_LEVEL_THRESHOLDS = (
    (0.25, RiskLevel.LOW),
    (0.50, RiskLevel.MEDIUM),
    (0.75, RiskLevel.HIGH),
    (1.01, RiskLevel.CRITICAL),
)

PRIORITY_TO_INTERNAL_RISK: Dict[OperationPriority, float] = {
    OperationPriority.LOW: 0.15,
    OperationPriority.MEDIUM: 0.40,
    OperationPriority.HIGH: 0.70,
    OperationPriority.URGENT: 0.90,
}


class RiskEngineError(ValueError):
    """Raised when risk inputs are out of the valid [0.0, 1.0] range."""


@dataclass
class RiskResult:
    risk_score: float
    risk_level: RiskLevel
    breakdown: Dict[str, float] = field(default_factory=dict)


def _clamp01(value: float, name: str) -> float:
    if not isinstance(value, (int, float)):
        raise RiskEngineError(f"{name} must be numeric, got {type(value).__name__}")
    if value < 0.0 or value > 1.0:
        raise RiskEngineError(f"{name} must be within [0.0, 1.0], got {value}")
    return float(value)


def derive_internal_risk_from_priority(priority: OperationPriority) -> float:
    try:
        return PRIORITY_TO_INTERNAL_RISK[priority]
    except KeyError as exc:
        raise RiskEngineError(f"Unknown priority: {priority}") from exc


def derive_external_risk_from_weather(weather: dict) -> float:
    """
    Convert an Open-Meteo current-weather payload into normalised [0,1]
    external risk. Deterministic thresholds only.
    """
    precipitation = float(weather.get("precipitation", 0.0) or 0.0)
    wind_speed = float(weather.get("wind_speed_10m", 0.0) or 0.0)

    precipitation_component = min(precipitation / 20.0, 1.0)
    wind_component = min(wind_speed / 80.0, 1.0)

    return round(max(precipitation_component, wind_component), 4)


def score_to_level(score: float) -> RiskLevel:
    for upper_bound, level in RISK_LEVEL_THRESHOLDS:
        if score <= upper_bound:
            return level
    return RiskLevel.CRITICAL


def compute_risk_score(
    internal_risk: float,
    external_risk: float,
    time_pressure: float,
    historical_risk: float,
    weights: Dict[str, float] = None,
) -> RiskResult:
    weights = weights or DEFAULT_WEIGHTS

    internal_risk = _clamp01(internal_risk, "internal_risk")
    external_risk = _clamp01(external_risk, "external_risk")
    time_pressure = _clamp01(time_pressure, "time_pressure")
    historical_risk = _clamp01(historical_risk, "historical_risk")

    weighted = {
        "internal": internal_risk * weights["internal"],
        "external": external_risk * weights["external"],
        "time_pressure": time_pressure * weights["time_pressure"],
        "historical": historical_risk * weights["historical"],
    }

    raw_score = round(sum(weighted.values()), 4)
    raw_score = min(raw_score, 1.0)

    level = score_to_level(raw_score)

    return RiskResult(risk_score=raw_score, risk_level=level, breakdown=weighted)
