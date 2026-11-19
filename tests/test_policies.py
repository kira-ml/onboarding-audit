import numpy as np
import pandas as pd
import pytest

from onboarding_audit.config import Costs, PolicySpec
from onboarding_audit.policies import (
    apply_capacity,
    build_policy,
    choose_actions,
    realized_cost,
)


@pytest.fixture
def costs():
    return Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
        amount_scaled=True,
    )


@pytest.fixture
def frame():
    n = 200
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "p_fraud": rng.uniform(0, 1, n),
            "p_fraud_lgbm": rng.uniform(0, 1, n),
            "amount": rng.uniform(100, 1000, n),
        }
    )


def test_actions_are_valid_and_capacity_is_respected(frame, costs):
    spec = PolicySpec("incumbent", "p_fraud", 0.10)
    policy = build_policy(frame, spec, costs, frame["amount"].to_numpy())
    assert set(policy.actions) <= {"approve", "review", "reject"}
    assert policy.review_count <= policy.review_budget
    assert policy.review_budget == int(np.ceil(0.10 * len(frame)))


def test_review_capacity_never_exceeded(frame, costs):
    spec = PolicySpec("incumbent", "p_fraud", 0.01)
    policy = build_policy(frame, spec, costs, frame["amount"].to_numpy())
    assert policy.review_count <= int(np.ceil(0.01 * len(frame)))


def test_realized_cost_identities(costs):
    y = np.array([1, 1, 0, 0])
    amount = np.array([100.0, 100.0, 100.0, 100.0])
    actions = np.array(["approve", "review", "review", "reject"], dtype=object)
    c = realized_cost(actions, y, amount, costs)
    assert c[0] == pytest.approx(100.0 * 0.01)
    assert c[1] == pytest.approx(0.02 + 0.30)
    assert c[2] == pytest.approx(0.02)
    assert c[3] == pytest.approx(0.10)


def test_rejecting_fraud_costs_zero(costs):
    y = np.array([1])
    amount = np.array([1000.0])
    actions = np.array(["reject"], dtype=object)
    assert realized_cost(actions, y, amount, costs)[0] == 0.0


def test_choose_actions_extremes(costs):
    amount = np.array([100.0, 100.0, 100.0])
    p = np.array([0.0, 0.5, 1.0])
    actions, _ = choose_actions(p, costs, amount)
    assert actions[0] == "approve"
    assert actions[2] == "reject"
    assert actions[1] in {"review", "reject"}


def test_apply_capacity_overflow_is_rerouted(costs):
    n = 10
    c_app = np.full(n, 0.5)
    c_rev = np.full(n, 0.05)
    c_rej = np.full(n, 0.1)
    actions = apply_capacity(c_app, c_rev, c_rej, k=3)
    assert (actions == "review").sum() == 3
    assert set(actions[actions != "review"]) <= {"approve", "reject"}


def test_negative_amount_rejected(frame, costs):
    frame = frame.copy()
    frame.loc[0, "amount"] = -1.0
    with pytest.raises(ValueError):
        build_policy(
            frame,
            PolicySpec("incumbent", "p_fraud", 0.1),
            costs,
            frame["amount"].to_numpy(),
        )
