"""Approve/review/reject policy construction and cost accounting."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import Costs, PolicySpec

ACTIONS = ("approve", "review", "reject")


@dataclass
class PolicyActions:
    spec: PolicySpec
    actions: np.ndarray
    c_approve: np.ndarray
    c_review: np.ndarray
    c_reject: np.ndarray
    review_budget: int

    @property
    def review_count(self) -> int:
        return int((self.actions == "review").sum())


def fraud_loss(amount: np.ndarray, costs: Costs) -> np.ndarray:
    if costs.amount_scaled:
        return amount * float(costs.fraud_loss_rate)
    return np.full(len(amount), float(costs.fraud_loss_rate))


def choose_actions(
    p: np.ndarray,
    costs: Costs,
    amounts: np.ndarray,
    *,
    false_reject_cost: float | None = None,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Argmin of expected cost over approve/review/reject."""
    p = np.asarray(p, dtype=float)
    fl = fraud_loss(amounts, costs)
    fr = float(
        costs.false_reject_cost if false_reject_cost is None else false_reject_cost
    )
    c_approve = p * fl
    c_review = float(costs.review_cost) + p * float(costs.residual_fraud_loss)
    c_reject = (1.0 - p) * fr
    matrix = np.column_stack([c_approve, c_review, c_reject])
    idx = np.argmin(matrix, axis=1)
    actions = np.asarray(ACTIONS, dtype=object)[idx]
    return actions, (c_approve, c_review, c_reject)


def apply_capacity(
    c_approve: np.ndarray,
    c_review: np.ndarray,
    c_reject: np.ndarray,
    k: int,
) -> np.ndarray:
    """Cap review at K; reroute overflow by the approve-vs-reject argmin."""
    n = len(c_approve)
    matrix = np.column_stack([c_approve, c_review, c_reject])
    idx = np.argmin(matrix, axis=1)
    actions = np.empty(n, dtype=object)
    actions[idx == 0] = "approve"
    actions[idx == 2] = "reject"

    review_idx = np.where(idx == 1)[0]
    if len(review_idx) == 0:
        return actions
    if len(review_idx) <= k:
        actions[review_idx] = "review"
        return actions

    savings = np.minimum(c_approve, c_reject) - c_review
    order = review_idx[np.argsort(-savings[review_idx], kind="stable")]
    keep = order[:k]
    overflow = order[k:]
    actions[keep] = "review"
    actions[overflow] = np.where(
        c_approve[overflow] <= c_reject[overflow], "approve", "reject"
    )
    return actions


def build_policy(
    df: pd.DataFrame,
    spec: PolicySpec,
    base_costs: Costs,
    amount: np.ndarray,
    *,
    review_capacity: float | None = None,
) -> PolicyActions:
    """Build a policy's actions under its own decision cost assumptions."""
    if spec.score_col not in df.columns:
        raise ValueError(f"missing score column {spec.score_col!r}")
    amount = np.asarray(amount, dtype=float)
    if not np.isfinite(amount).all() or (amount < 0).any():
        raise ValueError("amount must be finite and non-negative")
    p = df[spec.score_col].to_numpy(dtype=float)
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError(f"score {spec.score_col!r} must be finite and in [0, 1]")

    _actions_unconstrained, (c_app, c_rev, c_rej) = choose_actions(
        p,
        base_costs,
        amount,
        false_reject_cost=spec.decision_false_reject_cost,
    )
    capacity = spec.review_capacity if review_capacity is None else review_capacity
    if not 0.0 < capacity <= 1.0:
        raise ValueError("review_capacity must be in (0, 1]")
    k = int(np.ceil(capacity * len(df)))
    actions = apply_capacity(c_app, c_rev, c_rej, k)
    if int((actions == "review").sum()) > k:
        raise AssertionError("review capacity violated")
    return PolicyActions(
        spec=spec,
        actions=actions,
        c_approve=c_app,
        c_review=c_rev,
        c_reject=c_rej,
        review_budget=k,
    )


def realized_cost(
    actions: np.ndarray,
    y: np.ndarray,
    amount: np.ndarray,
    costs: Costs,
) -> np.ndarray:
    """Realized cost per application under the evaluation cost matrix."""
    actions = np.asarray(actions)
    y = np.asarray(y, dtype=int)
    fraud = y == 1
    legit = ~fraud
    fl = fraud_loss(amount, costs)
    cost = np.zeros(len(actions), dtype=float)

    cost[fraud & (actions == "approve")] = fl[fraud & (actions == "approve")]
    cost[fraud & (actions == "review")] = float(costs.review_cost) + float(
        costs.residual_fraud_loss
    )
    cost[fraud & (actions == "reject")] = 0.0

    cost[legit & (actions == "approve")] = 0.0
    cost[legit & (actions == "review")] = float(costs.review_cost)
    cost[legit & (actions == "reject")] = float(costs.false_reject_cost)
    return cost


def mean_cost(
    actions: np.ndarray,
    y: np.ndarray,
    amount: np.ndarray,
    costs: Costs,
    mask: np.ndarray | None = None,
) -> float:
    c = realized_cost(actions, y, amount, costs)
    if mask is not None:
        c = c[mask]
    return float(c.mean())
