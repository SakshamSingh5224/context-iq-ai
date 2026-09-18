import pytest

from models import OperationPriority, RiskLevel
from services.risk_engine import (
    RiskEngineError,
    compute_risk_score,
    derive_external_risk_from_weather,
    derive_internal_risk_from_priority,
)


def test_compute_risk_score_low():
    result = compute_risk_score(0.1, 0.1, 0.1, 0.1)
    assert result.risk_level == RiskLevel.LOW
    assert 0.0 <= result.risk_score <= 0.25


def test_compute_risk_score_critical():
    result = compute_risk_score(1.0, 1.0, 1.0, 1.0)
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.risk_score == 1.0


def test_compute_risk_score_breakdown_sums_to_score():
    result = compute_risk_score(0.5, 0.5, 0.5, 0.5)
    assert round(sum(result.breakdown.values()), 4) == result.risk_score


def test_out_of_range_raises():
    with pytest.raises(RiskEngineError):
        compute_risk_score(1.5, 0.1, 0.1, 0.1)


def test_negative_value_raises():
    with pytest.raises(RiskEngineError):
        compute_risk_score(0.1, -0.2, 0.1, 0.1)


def test_non_numeric_raises():
    with pytest.raises(RiskEngineError):
        compute_risk_score("high", 0.1, 0.1, 0.1)


def test_derive_internal_risk_from_priority():
    assert derive_internal_risk_from_priority(OperationPriority.URGENT) == 0.90
    assert derive_internal_risk_from_priority(OperationPriority.LOW) == 0.15


def test_derive_external_risk_from_weather_severe_rain():
    score = derive_external_risk_from_weather({"precipitation": 40, "wind_speed_10m": 5})
    assert score == 1.0


def test_derive_external_risk_from_weather_missing_keys_defaults_zero():
    score = derive_external_risk_from_weather({})
    assert score == 0.0
