import numpy as np
import pytest

from onboarding_audit.config import Costs, OutcomeModel
from onboarding_audit.estimators import (
    audit_only,
    dr,
    effective_sample_size,
    expected_cost,
    fit_outcome_model,
    full_policy_difference,
    ipw_hajek,
    ipw_ht,
    naive,
    policy_bounds,
    compare_policies,
)


def _ones(n):
    return np.ones(n, dtype=float)


def test_full_observation_identity():
    rng = np.random.default_rng(0)
    n = 5_000
    cost = rng.gamma(2.0, 0.01, n)
    observed = np.ones(n, dtype=bool)
    in_pop = np.ones(n, dtype=bool)
    prop = _ones(n)
    truth = float(cost.mean())

    assert naive(cost, observed).value == pytest.approx(truth)
    assert ipw_ht(cost, observed, prop, in_pop).value == pytest.approx(truth)
    assert ipw_hajek(cost, observed, prop, in_pop).value == pytest.approx(truth)


def test_action_weighted_uses_observed_action_rates():
    from onboarding_audit.estimators import action_weighted

    actions = np.array(["approve", "approve", "review", "review"], dtype=object)
    observed = np.array([True, False, True, True])
    cost = np.array([2.0, 99.0, 1.0, 1.0])
    in_pop = np.ones(4, dtype=bool)
    est = action_weighted(cost, observed, actions, in_pop)
    # approve: 1/2 observed -> weight 2; review: 2/2 -> weight 1.
    # Hajek: (2*2 + 1*1 + 1*1) / (2 + 1 + 1) = 1.5.
    assert est.value == pytest.approx(1.5)
    assert est.max_weight == pytest.approx(2.0)


def test_ess_bounds():
    w = np.array([1.0, 1.0, 1.0, 1.0])
    assert effective_sample_size(w) == pytest.approx(4.0)
    w2 = np.array([100.0, 0.0, 0.0, 0.0])
    assert effective_sample_size(w2) == pytest.approx(1.0)


def test_bounds_contain_true_full_value():
    n = 100
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, n)
    amount = np.full(n, 100.0)
    actions = np.array(["approve"] * n, dtype=object)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    in_pop = np.zeros(n, dtype=bool)
    in_pop[:80] = True
    rejected = ~in_pop
    # True P0 value for the approve action.
    from onboarding_audit.policies import realized_cost

    c = realized_cost(actions, y, amount, costs)
    v_pop = float(c[in_pop].mean())
    true_full = float(c.mean())
    b = policy_bounds(actions, amount, costs, in_pop, rejected, v_pop)
    assert b.lower <= true_full <= b.upper


def test_unconditional_bounds_widen_with_standard_error():
    n = 100
    amount = np.full(n, 100.0)
    actions = np.array(["approve"] * n, dtype=object)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    in_pop = np.zeros(n, dtype=bool)
    in_pop[:80] = True
    rejected = ~in_pop
    base = policy_bounds(actions, amount, costs, in_pop, rejected, 0.10)
    widened = policy_bounds(
        actions, amount, costs, in_pop, rejected, 0.10, v_pop_se=0.01
    )
    assert widened.lower_unconditional < base.lower
    assert widened.upper_unconditional > base.upper
    assert widened.width_unconditional > base.width
    assert widened.lower_unconditional == pytest.approx(base.lower - 1.96 * 0.8 * 0.01)


def test_audit_only_full_audit_is_unbiased():
    n = 1000
    rng = np.random.default_rng(0)
    cost = rng.gamma(2.0, 0.01, n)
    audit = np.ones(n, dtype=bool)
    resolved = np.ones(n, dtype=bool)
    truth = float(cost.mean())
    est = audit_only(cost, audit, resolved, _ones(n))
    assert est.value == pytest.approx(truth)


def test_expected_cost_matches_realized_for_extremes():
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    amount = np.array([100.0, 100.0])
    # p=0 -> approve legit cost 0; p=1 -> reject fraud cost 0.
    actions = np.array(["approve", "reject"], dtype=object)
    phat = np.array([0.0, 1.0])
    mu = expected_cost(phat, actions, amount, costs)
    assert mu[0] == pytest.approx(0.0)
    assert mu[1] == pytest.approx(0.0)


def test_outcome_model_returns_probabilities():
    rng = np.random.default_rng(0)
    n = 500
    X = rng.normal(size=(n, 4))
    y = (X[:, 0] + rng.normal(size=n) > 0).astype(int)
    observed = np.ones(n, dtype=bool)
    prop = np.full(n, 0.5)
    phat = fit_outcome_model(X, y, observed, prop, OutcomeModel(C=0.5, n_splits=3), 0)
    assert phat.shape == (n,)
    assert (phat >= 0).all() and (phat <= 1).all()


def test_ipw_weights_large_for_low_propensity():
    n = 100
    cost = np.ones(n)
    observed = np.ones(n, dtype=bool)
    in_pop = np.ones(n, dtype=bool)
    prop = np.full(n, 0.01)
    est = ipw_ht(cost, observed, prop, in_pop)
    assert est.value == pytest.approx(100.0)
    assert est.max_weight == pytest.approx(100.0)


def test_outcome_model_drops_zero_propensity_rows():
    rng = np.random.default_rng(0)
    n = 200
    X = rng.normal(size=(n, 3))
    y = rng.integers(0, 2, n)
    observed = np.ones(n, dtype=bool)
    prop = np.full(n, 0.5)
    prop[:10] = 0.0  # labelled reject rows carry e=0
    phat = fit_outcome_model(X, y, observed, prop, OutcomeModel(C=0.5, n_splits=3), 0)
    assert phat.shape == (n,)
    assert np.isfinite(phat).all()


def test_outcome_model_with_no_usable_rows_is_nan():
    n = 10
    X = np.zeros((n, 2))
    y = np.zeros(n, dtype=int)
    observed = np.ones(n, dtype=bool)
    prop = np.zeros(n)
    phat = fit_outcome_model(X, y, observed, prop, OutcomeModel(C=0.5, n_splits=2), 0)
    assert np.isnan(phat).all()


def test_zero_observation_ipw_and_dr_are_nan():
    n = 50
    cost = np.ones(n)
    observed = np.zeros(n, dtype=bool)
    in_pop = np.ones(n, dtype=bool)
    prop = np.full(n, 0.5)
    assert not np.isfinite(ipw_ht(cost, observed, prop, in_pop).value)
    phat = np.full(n, 0.1)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    actions = np.array(["approve"] * n, dtype=object)
    amount = np.full(n, 100.0)
    assert not np.isfinite(
        dr(cost, actions, amount, observed, prop, in_pop, phat, costs).value
    )


def test_census_has_zero_design_variance():
    n = 100
    rng = np.random.default_rng(0)
    cost = rng.gamma(2.0, 0.01, n)
    observed = np.ones(n, dtype=bool)
    in_pop = np.ones(n, dtype=bool)
    prop = np.ones(n)
    est = ipw_ht(cost, observed, prop, in_pop)
    assert est.value == pytest.approx(float(cost.mean()))
    assert est.se == pytest.approx(0.0)


def test_bounds_without_rejected_rows_widen_with_p0_error():
    n = 50
    amount = np.full(n, 100.0)
    actions = np.array(["approve"] * n, dtype=object)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    in_pop = np.ones(n, dtype=bool)
    rejected = np.zeros(n, dtype=bool)
    b = policy_bounds(actions, amount, costs, in_pop, rejected, 0.10, v_pop_se=0.01)
    assert b.width == 0.0
    assert b.lower_unconditional == pytest.approx(0.10 - 1.96 * 0.01)
    assert b.upper_unconditional == pytest.approx(0.10 + 1.96 * 0.01)


def test_compare_policies_prefers_the_cheaper_policy():
    n = 500
    amount = np.full(n, 1000.0)
    actions_c = np.array(["approve"] * n, dtype=object)
    actions_i = np.array(["review"] * n, dtype=object)
    y = np.zeros(n)
    observed = np.ones(n, dtype=bool)
    e = np.ones(n)
    in_pop = np.ones(n, dtype=bool)
    phat = np.zeros(n)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    from onboarding_audit.policies import realized_cost

    cost_c = realized_cost(actions_c, y, amount, costs)
    cost_i = realized_cost(actions_i, y, amount, costs)
    comp = compare_policies(
        cost_c, actions_c, cost_i, actions_i, amount, observed, e, in_pop, phat, costs
    )
    assert comp["difference"] < 0
    assert comp["p_candidate_better"] > 0.5
    assert comp["decision"] == "prefer candidate"
    assert comp["regret_candidate"] < comp["regret_incumbent"]


def test_full_policy_difference_breakeven():
    n = 100
    amount = np.full(n, 100.0)
    actions_c = np.array(["approve"] * n, dtype=object)
    actions_i = np.array(["approve"] * 80 + ["reject"] * 20, dtype=object)
    in_pop = np.zeros(n, dtype=bool)
    in_pop[:80] = True
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    out = full_policy_difference(actions_c, actions_i, amount, costs, in_pop, 0.0, 0.0)
    assert out["reject_difference_if_legit"] == pytest.approx(-0.10)
    assert out["reject_difference_if_fraud"] == pytest.approx(1.00)
    assert out["full_difference_lower"] == pytest.approx(-0.02)
    assert out["full_difference_upper"] == pytest.approx(0.20)
    assert out["decision"] == "depends on the reject margin"
    assert out["breakeven_reject_fraud_rate"] == pytest.approx(0.10 / 1.10)
    assert "p <" in out["basis"] and "cheaper" in out["basis"]


def test_full_policy_difference_without_rejected_rows():
    n = 50
    amount = np.full(n, 100.0)
    actions = np.array(["approve"] * n, dtype=object)
    in_pop = np.ones(n, dtype=bool)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    out = full_policy_difference(actions, actions, amount, costs, in_pop, -0.01, 0.002)
    assert out["n_rejected"] == 0
    assert out["full_difference_lower"] == pytest.approx(-0.01 - 1.96 * 0.002)
    assert out["full_difference_upper"] == pytest.approx(-0.01 + 1.96 * 0.002)
    assert out["decision"] == "candidate cheaper"
    assert "full population equals P0" in out["basis"]


def test_full_policy_difference_candidate_rejects_all_rejected_rows():
    n = 100
    amount = np.full(n, 100.0)
    actions_c = np.array(["approve"] * 80 + ["reject"] * 20, dtype=object)
    actions_i = np.array(["approve"] * 80 + ["reject"] * 20, dtype=object)
    in_pop = np.zeros(n, dtype=bool)
    in_pop[:80] = True
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    out = full_policy_difference(
        actions_c, actions_i, amount, costs, in_pop, -0.01, 0.0
    )
    assert out["reject_difference_if_legit"] == pytest.approx(0.0)
    assert out["reject_difference_if_fraud"] == pytest.approx(0.0)
    assert out["full_difference_lower"] == pytest.approx(-0.8 * 0.01)
    assert out["full_difference_upper"] == pytest.approx(-0.8 * 0.01)
    assert out["decision"] == "candidate cheaper for any reject outcome"
    assert np.isnan(out["breakeven_reject_fraud_rate"])


def test_full_policy_difference_does_not_blame_reject_margin_for_p0_noise():
    n = 100
    amount = np.full(n, 100.0)
    actions_c = np.array(["approve"] * 80 + ["reject"] * 20, dtype=object)
    actions_i = np.array(["approve"] * 80 + ["reject"] * 20, dtype=object)
    in_pop = np.zeros(n, dtype=bool)
    in_pop[:80] = True
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    out = full_policy_difference(
        actions_c, actions_i, amount, costs, in_pop, -0.04, 0.03
    )
    # The reject margin is identical under both policies, so a zero-crossing is
    # P0 uncertainty, not reject-margin dependence.
    assert out["reject_min_mean"] == pytest.approx(0.0)
    assert out["reject_max_mean"] == pytest.approx(0.0)
    assert out["full_difference_lower"] < 0 < out["full_difference_upper"]
    assert out["decision"] == "P0 inconclusive"
    assert "P0 estimate is uncertain" in out["basis"]
    assert np.isnan(out["breakeven_reject_fraud_rate"])


def test_full_policy_difference_small_reject_range_does_not_flip_decision():
    n = 1000
    amount = np.full(n, 100.0)
    amount[-1] = 1.0
    actions_i = np.array(["approve"] * 900 + ["reject"] * 100, dtype=object)
    actions_c = actions_i.copy()
    actions_c[-1] = "approve"  # one rejected row changes; small exposure
    in_pop = np.zeros(n, dtype=bool)
    in_pop[:900] = True
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    out = full_policy_difference(
        actions_c, actions_i, amount, costs, in_pop, -0.01, 0.01
    )
    assert out["reject_max_mean"] > out["reject_min_mean"]  # range is nonzero
    assert out["full_difference_lower"] < 0 < out["full_difference_upper"]
    assert out["decision"] == "P0 inconclusive"
    assert "moves the magnitude" in out["basis"]


def test_full_policy_difference_all_rejected_population():
    n = 10
    amount = np.full(n, 100.0)
    actions_i = np.array(["reject"] * n, dtype=object)
    actions_c = np.array(["approve"] * n, dtype=object)
    in_pop = np.zeros(n, dtype=bool)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    out = full_policy_difference(
        actions_c, actions_i, amount, costs, in_pop, float("nan"), float("nan")
    )
    assert out["full_difference_lower"] == pytest.approx(-0.10)
    assert out["full_difference_upper"] == pytest.approx(1.00)
    assert out["decision"] == "depends on the reject margin"
    assert "no P0 rows" in out["basis"]


def test_compare_policies_includes_full_policy_check():
    n = 200
    amount = np.full(n, 100.0)
    actions_c = np.array(["approve"] * n, dtype=object)
    actions_i = np.array(["review"] * n, dtype=object)
    y = np.zeros(n)
    observed = np.ones(n, dtype=bool)
    e = np.ones(n)
    in_pop = np.ones(n, dtype=bool)
    phat = np.zeros(n)
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    from onboarding_audit.policies import realized_cost

    cost_c = realized_cost(actions_c, y, amount, costs)
    cost_i = realized_cost(actions_i, y, amount, costs)
    comp = compare_policies(
        cost_c, actions_c, cost_i, actions_i, amount, observed, e, in_pop, phat, costs
    )
    assert comp["full_policy"]["n_rejected"] == 0
    assert comp["full_policy"]["decision"] == "candidate cheaper"


def test_labels_for_power_known_value():
    from onboarding_audit.estimators import labels_for_power

    # z = 1.96 + 0.8416 = 2.8016; 1000 * (2.8016 * 0.01 / 0.01)^2 = 7849
    assert labels_for_power(0.01, 0.01, 1000) == 7849
    assert labels_for_power(0.0, 0.01, 1000) == 0
    assert labels_for_power(0.01, 0.0, 1000) == 0
