"""Estimators for the identified population and the reject-margin bounds."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

from .config import Costs, OutcomeModel
from .policies import fraud_loss, realized_cost


@dataclass
class Estimate:
    value: float
    se: float
    n_used: int
    ess: float
    max_weight: float


@dataclass
class Bounds:
    lower: float
    upper: float
    width: float
    n_rejected: int


def effective_sample_size(w: np.ndarray) -> float:
    sw = float(w.sum())
    sw2 = float((w * w).sum())
    return sw * sw / sw2 if sw2 > 0 else 0.0


def _weights(observed: np.ndarray, propensity: np.ndarray) -> np.ndarray:
    w = np.zeros(len(propensity), dtype=float)
    np.divide(
        1.0,
        propensity,
        out=w,
        where=observed & (propensity > 0),
    )
    return w


def naive(cost: np.ndarray, observed: np.ndarray) -> Estimate:
    c = cost[observed]
    n = len(c)
    if n == 0:
        return Estimate(float("nan"), float("nan"), 0, 0.0, float("nan"))
    se = float(c.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return Estimate(float(c.mean()), se, n, float(n), 1.0)


def ipw_ht(
    cost: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
) -> Estimate:
    n_pop = int(in_pop.sum())
    w = _weights(observed, propensity)
    if n_pop == 0:
        return Estimate(
            float("nan"), float("nan"), int(observed.sum()), 0.0, float("nan")
        )
    value = float((w * cost).sum() / n_pop)
    psi = np.where(in_pop, w * cost - value, 0.0)
    se = float(psi[in_pop].std(ddof=1) / np.sqrt(n_pop)) if n_pop > 1 else float("nan")
    max_w = float(w[observed].max()) if observed.any() else float("nan")
    return Estimate(value, se, int(observed.sum()), effective_sample_size(w), max_w)


def ipw_hajek(
    cost: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
) -> Estimate:
    n_pop = int(in_pop.sum())
    w = _weights(observed, propensity)
    sw = float(w.sum())
    if n_pop == 0 or sw <= 0:
        return Estimate(
            float("nan"), float("nan"), int(observed.sum()), 0.0, float("nan")
        )
    value = float((w * cost).sum() / sw)
    mean_w = sw / n_pop
    psi = np.where(in_pop, w * (cost - value) / mean_w, 0.0)
    se = float(psi[in_pop].std(ddof=1) / np.sqrt(n_pop)) if n_pop > 1 else float("nan")
    max_w = float(w[observed].max()) if observed.any() else float("nan")
    return Estimate(value, se, int(observed.sum()), effective_sample_size(w), max_w)


def fit_outcome_model(
    X: np.ndarray,
    y: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    cfg: OutcomeModel,
    seed: int,
) -> np.ndarray:
    """Cross-fitted P(fraud | X) on observed rows, weighted by 1/e."""
    n = len(y)
    idx = np.where(observed)[0]
    if len(idx) < 20 or len(np.unique(y[idx])) < 2:
        base = float(y[idx].mean()) if len(idx) else float(y.mean())
        return np.full(n, np.clip(base, 1e-6, 1 - 1e-6))

    n_splits = min(cfg.n_splits, max(2, len(idx) // 10))
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    preds = np.zeros((n_splits, n), dtype=float)
    phat = np.zeros(n, dtype=float)

    for k, (tr, te) in enumerate(kf.split(idx)):
        tr_idx, te_idx = idx[tr], idx[te]
        w = 1.0 / propensity[tr_idx]
        model = LogisticRegression(C=cfg.C, max_iter=cfg.max_iter, solver="lbfgs")
        model.fit(X[tr_idx], y[tr_idx], sample_weight=w)
        preds[k] = model.predict_proba(X)[:, 1]
        phat[te_idx] = preds[k, te_idx]

    other = np.setdiff1d(np.arange(n), idx)
    if len(other):
        phat[other] = preds[:, other].mean(axis=0)
    return np.clip(phat, 1e-6, 1 - 1e-6)


def expected_cost(
    phat: np.ndarray,
    actions: np.ndarray,
    amount: np.ndarray,
    costs: Costs,
) -> np.ndarray:
    fl = fraud_loss(amount, costs)
    return np.where(
        actions == "approve",
        phat * fl,
        np.where(
            actions == "review",
            float(costs.review_cost) + phat * float(costs.residual_fraud_loss),
            (1.0 - phat) * float(costs.false_reject_cost),
        ),
    )


def dr(
    cost: np.ndarray,
    actions: np.ndarray,
    amount: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
    phat: np.ndarray,
    costs: Costs,
) -> Estimate:
    n_pop = int(in_pop.sum())
    if n_pop == 0:
        return Estimate(
            float("nan"), float("nan"), int(observed.sum()), 0.0, float("nan")
        )
    mu = expected_cost(phat, actions, amount, costs)
    w = _weights(observed, propensity)
    value = float(mu[in_pop].mean() + (w * (cost - mu))[in_pop].mean())
    psi = np.where(in_pop, mu + w * (cost - mu) - value, 0.0)
    se = float(psi[in_pop].std(ddof=1) / np.sqrt(n_pop)) if n_pop > 1 else float("nan")
    max_w = float(w[observed].max()) if observed.any() else float("nan")
    return Estimate(value, se, int(observed.sum()), effective_sample_size(w), max_w)


def audit_only(
    cost: np.ndarray,
    audit: np.ndarray,
    resolved_approve: np.ndarray,
    p_resolved_approve: np.ndarray,
) -> Estimate:
    """Unbiased estimate for the approved population from the audit sample."""
    mask = audit & resolved_approve
    n = int(mask.sum())
    if n == 0:
        return Estimate(float("nan"), float("nan"), 0, 0.0, float("nan"))
    w = np.zeros(len(cost), dtype=float)
    w[mask] = 1.0 / p_resolved_approve[mask]
    value = float((w * cost).sum() / w.sum())
    mean_w = float(w[mask].mean())
    psi = np.where(mask, w * (cost - value) / mean_w, 0.0)
    se = float(psi[mask].std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return Estimate(value, se, n, effective_sample_size(w), float(w[mask].max()))


def policy_bounds(
    actions: np.ndarray,
    amount: np.ndarray,
    costs: Costs,
    in_pop: np.ndarray,
    rejected: np.ndarray,
    v_pop: float,
) -> Bounds:
    """Partial-identification bounds for the full-population value.

    The unobserved logging-rejected rows are bounded by the min/max cost of the
    candidate action; the identified population uses the supplied estimate.
    """
    n = len(actions)
    n_pop = int(in_pop.sum())
    n_rej = int(rejected.sum())
    if n_rej == 0 or n == 0:
        return Bounds(v_pop, v_pop, 0.0, n_rej)
    if not np.isfinite(v_pop):
        return Bounds(float("nan"), float("nan"), float("nan"), n_rej)

    fl = fraud_loss(amount, costs)
    min_cost = np.zeros(n, dtype=float)
    max_cost = np.zeros(n, dtype=float)
    app = actions == "approve"
    rev = actions == "review"
    rej = actions == "reject"
    min_cost[app] = 0.0
    max_cost[app] = fl[app]
    min_cost[rev] = float(costs.review_cost)
    max_cost[rev] = float(costs.review_cost) + float(costs.residual_fraud_loss)
    min_cost[rej] = 0.0
    max_cost[rej] = float(costs.false_reject_cost)

    lower = (n_pop / n) * v_pop + (n_rej / n) * float(min_cost[rejected].mean())
    upper = (n_pop / n) * v_pop + (n_rej / n) * float(max_cost[rejected].mean())
    return Bounds(lower, upper, upper - lower, n_rej)


def coverage(estimate: Estimate, truth: float) -> float:
    if not np.isfinite(estimate.value) or not np.isfinite(estimate.se):
        return float("nan")
    return float(abs(estimate.value - truth) <= 1.96 * estimate.se)
