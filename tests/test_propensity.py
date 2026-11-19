import numpy as np
from types import SimpleNamespace

from onboarding_audit.propensity import estimate_from_draw, noisy_copy


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
