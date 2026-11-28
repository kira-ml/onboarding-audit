from types import SimpleNamespace

import numpy as np
import pytest

from onboarding_audit.propensity import (
    estimate_from_draw,
    fit_covariate_propensity,
    noisy_copy,
)


def _model(actions):
    return SimpleNamespace(logging_actions=np.asarray(actions))


def _draw(observed, audit):
    return SimpleNamespace(
        observed=np.asarray(observed, dtype=bool),
        audit=np.asarray(audit, dtype=bool),
    )


def test_estimate_review_rate():
    model = _model(["review"] * 4)
    draw = _draw([True, True, False, False], [False] * 4)
    e = estimate_from_draw(model, draw)
    assert np.allclose(e, 0.5)


def test_estimate_approve_with_audit():
    # 4 approved: 1 audited+observed, 3 non-audited with 1 observed.
    model = _model(["approve"] * 4)
    draw = _draw([True, True, False, False], [True, False, False, False])
    e = estimate_from_draw(model, draw)
    # audit rate 0.25; base rate 1/3; e = 0.25 + 0.75*(1/3) = 0.5
    assert np.allclose(e, 0.5)


def test_estimate_zero_for_reject():
    model = _model(["reject", "reject"])
    draw = _draw([False, False], [False, False])
    e = estimate_from_draw(model, draw)
    assert np.allclose(e, 0.0)


def test_noisy_copy_has_mean_near_one_and_preserves_zeros():
    rng = np.random.default_rng(0)
    e = np.full(100_000, 0.2)
    e[:10] = 0.0
    out = noisy_copy(e, 0.10, rng)
    assert np.allclose(out[:10], 0.0)
    assert abs(out[10:].mean() - 0.2) < 0.005
    assert (out >= 0).all() and (out <= 1).all()


def test_noisy_copy_zero_sigma_is_identity():
    rng = np.random.default_rng(0)
    e = np.array([0.1, 0.2, 0.0])
    assert np.allclose(noisy_copy(e, 0.0, rng), e)


def test_fit_covariate_propensity_recovers_a_logistic_gradient():
    rng = np.random.default_rng(0)
    n = 50_000
    z = rng.normal(size=n)
    X = np.column_stack([z, rng.normal(size=n)])
    p = 1.0 / (1.0 + np.exp(-(-2.0 + 1.0 * z)))
    observed = rng.random(n) < p
    actions = np.full(n, "approve")
    e = fit_covariate_propensity(X, actions, observed, n_splits=3)
    assert np.corrcoef(e, p)[0, 1] > 0.8
    assert e.mean() == pytest.approx(observed.mean(), abs=0.01)
    assert (e > 0).all() and (e < 1).all()


def test_fit_covariate_propensity_keeps_rejects_at_zero():
    rng = np.random.default_rng(0)
    n = 1_000
    X = rng.normal(size=(n, 2))
    actions = np.array(["approve"] * 500 + ["review"] * 300 + ["reject"] * 200)
    observed = rng.random(n) < 0.2
    e = fit_covariate_propensity(X, actions, observed, n_splits=2)
    assert (e[actions == "reject"] == 0).all()
    assert (e[actions == "approve"] > 0).all()
    assert (e[actions == "review"] > 0).all()
