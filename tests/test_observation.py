import numpy as np
import pytest

from onboarding_audit.config import Observation
from onboarding_audit.observation import (
    build_observation_model,
    draw_observation,
    p_resolved,
)


def test_p_resolved_is_monotone_in_decision_day():
    day = np.array([0.0, 30.0, 60.0, 89.0])
    p = p_resolved(day, median=45.0, sigma=0.8, cutoff=90.0)
    assert np.all(np.diff(p) <= 1e-12)
    assert (p >= 0).all() and (p <= 1).all()


def test_zero_delay_resolves_everything():
    day = np.linspace(0, 60, 100)
    p = p_resolved(day, median=0.5, sigma=0.1, cutoff=90.0)
    assert np.allclose(p, 1.0)


def test_propensity_positive_for_non_rejected():
    n = 1000
    actions = np.array(["approve", "review", "reject"] * (n // 3) + ["approve"])
    day = np.linspace(0, 60, len(actions))
    cfg = Observation(audit_rate=0.01)
    model = build_observation_model(actions, day, cfg)
    assert (model.propensity[model.in_pop] > 0).all()
    assert (model.propensity[model.reject_mask] == 0).all()
    assert model.e_review > 0
    assert model.e_approve > 0


def test_empirical_observation_frequency_matches_propensity():
    n = 200_000
    actions = np.full(n, "approve")
    day = np.zeros(n)
    cfg = Observation(
        kappa_review=1.0,
        e_approve=0.20,
        audit_rate=0.0,
        approve_delay_median=0.5,
        approve_delay_sigma=0.1,
        cutoff_day=90.0,
    )
    model = build_observation_model(actions, day, cfg)
    rng = np.random.default_rng(0)
    draw = draw_observation(model, rng)
    assert draw.observed.mean() == pytest.approx(0.20, abs=0.01)


def test_full_observation_observes_all_non_rejected():
    n = 1000
    actions = np.array(["approve", "review", "reject"] * (n // 3) + ["approve"])
    day = np.linspace(0, 60, len(actions))
    cfg = Observation(
        kappa_review=1.0,
        e_approve=1.0,
        audit_rate=1.0,
        review_delay_median=0.5,
        review_delay_sigma=0.1,
        approve_delay_median=0.5,
        approve_delay_sigma=0.1,
        cutoff_day=90.0,
    )
    model = build_observation_model(actions, day, cfg)
    draw = draw_observation(model, np.random.default_rng(0))
    assert draw.observed[model.in_pop].all()
    assert not draw.observed[model.reject_mask].any()


def test_outcome_dependent_approved_fraud_is_more_observed():
    n = 50_000
    actions = np.full(n, "approve")
    day = np.zeros(n)
    y = np.zeros(n, dtype=int)
    y[: int(0.05 * n)] = 1
    cfg = Observation(
        e_approve=0.0,
        audit_rate=0.01,
        approve_delay_median=0.5,
        approve_delay_sigma=0.1,
        cutoff_day=90.0,
    )
    model = build_observation_model(actions, day, cfg)
    draw = draw_observation(
        model,
        np.random.default_rng(0),
        y=y,
        outcome_dependent=True,
        e_approve_fraud=0.5,
    )
    fraud_obs = draw.observed[y == 1].mean()
    legit_obs = draw.observed[y == 0].mean()
    assert fraud_obs == pytest.approx(0.505, abs=0.02)
    assert legit_obs == pytest.approx(0.01, abs=0.005)
