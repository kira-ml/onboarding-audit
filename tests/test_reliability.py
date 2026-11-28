import numpy as np
import pytest

from onboarding_audit.config import Costs
from onboarding_audit.gates import IdentificationReport
from onboarding_audit.reliability import (
    bootstrap_decision,
    build_reliability_profile,
    calibration_metrics,
    cost_stress,
)


def _costs():
    return Costs(
        fraud_loss_rate=0.0019187869,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )


def test_bootstrap_decision_clear_winner():
    n = 100
    cost_c = np.zeros(n)
    cost_i = np.ones(n)
    actions = np.array(["approve"] * n, dtype=object)
    amount = np.full(n, 100.0)
    observed = np.ones(n, dtype=bool)
    e = np.ones(n)
    in_pop = np.ones(n, dtype=bool)
    phat = np.zeros(n)
    out = bootstrap_decision(
        cost_c,
        actions,
        cost_i,
        actions,
        amount,
        observed,
        e,
        in_pop,
        phat,
        _costs(),
        n_boot=200,
        seed=0,
    )
    assert out["available"]
    assert out["point_difference"] == pytest.approx(-1.0)
    assert out["p_candidate_better_boot"] == pytest.approx(1.0)
    assert out["same_direction_share"] == pytest.approx(1.0)
    assert out["ci_low"] == pytest.approx(-1.0)
    assert out["ci_high"] == pytest.approx(-1.0)
    assert out["decision_boot"] == "prefer candidate"


def test_calibration_metrics_perfect():
    y = np.array([0] * 10 + [1] * 10)
    phat = np.array([0.0] * 10 + [1.0] * 10)
    observed = np.ones(20, dtype=bool)
    out = calibration_metrics(y, phat, observed)
    assert out["available"]
    assert out["brier"] < 1e-9
    assert out["ece"] < 1e-5
    assert out["log_loss"] < 1e-4


def test_calibration_metrics_missing_model():
    out = calibration_metrics(np.zeros(10), None, np.ones(10, dtype=bool))
    assert not out["available"]


def test_cost_stress_stable_when_candidate_dominates():
    n = 100
    y = np.zeros(n, dtype=int)
    actions = np.array(["review"] * n, dtype=object)
    candidate = np.array(["approve"] * n, dtype=object)
    amount = np.full(n, 100.0)
    observed = np.ones(n, dtype=bool)
    e = np.ones(n)
    in_pop = np.ones(n, dtype=bool)
    phat = np.zeros(n)
    out = cost_stress(
        y,
        actions,
        candidate,
        amount,
        observed,
        e,
        in_pop,
        phat,
        _costs(),
        "prefer candidate",
    )
    assert out["available"]
    assert out["n_cells"] == 9
    assert out["same_decision_share"] == pytest.approx(1.0)
    assert out["stable_at_80pct"] is True


def test_profile_gate_failure_is_grade_d():
    ident = IdentificationReport(passed=False, reasons=["positivity failure"])
    profile = build_reliability_profile(
        identification=ident,
        comparison={"decision": "not identified", "full_policy": {}},
        bootstrap={"available": False, "reason": "not identified"},
        calibration={"available": False, "reason": "not identified"},
        prop_calibration={"available": False, "reason": "not identified"},
        stress={"available": False, "reason": "not identified"},
    )
    assert profile["grade"].startswith("D")
    assert profile["dimensions"]["identification"]["status"] == "fail"


def _strong_inputs():
    ident = IdentificationReport(
        passed=True,
        metrics={"n_observed": 1000, "ess": 900, "n_rejected": 100},
    )
    return {
        "identification": ident,
        "comparison": {
            "decision": "prefer candidate",
            "full_policy": {"decision": "candidate cheaper for any reject outcome"},
        },
        "bootstrap": {
            "available": True,
            "p_candidate_better_boot": 0.99,
            "same_direction_share": 0.99,
        },
        "calibration": {"available": True, "ece": 0.02, "brier": 0.10},
        "prop_calibration": {
            "available": True,
            "observed_expected_ratio": 1.0,
        },
        "stress": {"available": True, "same_decision_share": 1.0, "n_cells": 9},
    }


def test_profile_all_strong_is_grade_a():
    profile = build_reliability_profile(**_strong_inputs())
    assert profile["grade"].startswith("A")


def test_profile_weak_calibration_blocks_release():
    inputs = _strong_inputs()
    inputs["calibration"] = {"available": True, "ece": 0.25, "brier": 0.30}
    profile = build_reliability_profile(**inputs)
    assert profile["grade"].startswith("C")
    assert profile["dimensions"]["model_calibration"]["status"] == "weak"


def test_profile_weak_operational_readiness_blocks_release():
    inputs = _strong_inputs()
    inputs["identification"] = IdentificationReport(
        passed=True, metrics={"n_observed": 40, "ess": 30, "n_rejected": 5}
    )
    profile = build_reliability_profile(**inputs)
    assert profile["grade"].startswith("C")
    assert profile["dimensions"]["operational_readiness"]["status"] == "weak"


def test_profile_structural_unavailable_blocks_release():
    inputs = _strong_inputs()
    inputs["comparison"] = {
        "decision": "prefer candidate",
        "full_policy": {"decision": "P0 inconclusive"},
    }
    profile = build_reliability_profile(**inputs)
    assert profile["grade"].startswith("C")
    assert profile["dimensions"]["structural_reject_margin"]["status"] == "unavailable"


def test_profile_conflicting_full_policy_blocks_release():
    inputs = _strong_inputs()
    inputs["comparison"] = {
        "decision": "prefer candidate",
        "full_policy": {"decision": "incumbent cheaper for any reject outcome"},
    }
    profile = build_reliability_profile(**inputs)
    assert profile["grade"].startswith("C")
    assert profile["dimensions"]["structural_reject_margin"]["status"] == "unavailable"
    assert "conflicts" in profile["dimensions"]["structural_reject_margin"]["evidence"]


def test_profile_structural_not_applicable_without_rejects():
    inputs = _strong_inputs()
    inputs["identification"] = IdentificationReport(
        passed=True, metrics={"n_observed": 1000, "ess": 900, "n_rejected": 0}
    )
    inputs["comparison"] = {
        "decision": "prefer candidate",
        "full_policy": {"decision": "P0 inconclusive"},
    }
    profile = build_reliability_profile(**inputs)
    assert profile["grade"].startswith("A")
    assert (
        profile["dimensions"]["structural_reject_margin"]["status"] == "not_applicable"
    )
