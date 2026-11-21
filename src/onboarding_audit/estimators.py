"""Estimators for the identified population and the reject-margin bounds."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm
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
    lower_unconditional: float = float("nan")
    upper_unconditional: float = float("nan")
    width_unconditional: float = float("nan")


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
    if n_pop == 0 or w.sum() <= 0:
        return Estimate(
            float("nan"), float("nan"), int(observed.sum()), 0.0, float("nan")
        )
    value = float((w * cost).sum() / n_pop)
    # Standard HT variance for the finite-population mean. The previous form
    # centred on `value`, which adds Var_pop(c)/n_pop and is conservative; this
    # form is zero under a census (e=1) and matches the design variance.
    e = np.where(observed, propensity, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(
            observed & (e > 0),
            (1.0 - e) * cost * cost / (e * e),
            0.0,
        )
    se = float(np.sqrt(terms.sum()) / n_pop) if n_pop > 1 else float("nan")
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
    """Cross-fitted P(fraud | X) on observed rows, weighted by 1/e.

    A row with zero propensity cannot inform the model; it is dropped rather
    than divided by zero. If no usable row remains, the prediction is NaN so the
    caller withholds the estimate instead of trusting a constant.
    """
    n = len(y)
    idx = np.where(observed & (propensity > 0))[0]
    if len(idx) == 0:
        return np.full(n, np.nan)
    if len(idx) < 20 or len(np.unique(y[idx])) < 2:
        base = float(y[idx].mean())
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
    if not np.isfinite(mu[in_pop]).all() or w.sum() <= 0:
        return Estimate(
            float("nan"), float("nan"), int(observed.sum()), 0.0, float("nan")
        )
    value = float(mu[in_pop].mean() + (w * (cost - mu))[in_pop].mean())
    psi = np.where(in_pop, mu + w * (cost - mu) - value, 0.0)
    se = float(psi[in_pop].std(ddof=1) / np.sqrt(n_pop)) if n_pop > 1 else float("nan")
    max_w = float(w[observed].max()) if observed.any() else float("nan")
    return Estimate(value, se, int(observed.sum()), effective_sample_size(w), max_w)


def _dr_parts(
    cost: np.ndarray,
    actions: np.ndarray,
    amount: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
    phat: np.ndarray,
    costs: Costs,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return the DR value, its per-row influence term, and the weights."""
    mu = expected_cost(phat, actions, amount, costs)
    w = _weights(observed, propensity)
    if not np.isfinite(mu[in_pop]).all() or w.sum() <= 0:
        return float("nan"), np.zeros(len(cost)), w
    value = float(mu[in_pop].mean() + (w * (cost - mu))[in_pop].mean())
    psi = np.where(in_pop, mu + w * (cost - mu) - value, 0.0)
    return value, psi, w


def compare_policies(
    cost_candidate: np.ndarray,
    actions_candidate: np.ndarray,
    cost_incumbent: np.ndarray,
    actions_incumbent: np.ndarray,
    amount: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    in_pop: np.ndarray,
    phat: np.ndarray,
    costs: Costs,
) -> dict:
    """Paired DR comparison of the candidate and the logged policy on P0.

    The difference uses the paired influence terms, so the shared outcome model
    and propensity cancel in the variance. Nuisance-estimation uncertainty is
    not included; the interval is a first-order approximation.

    ``p_better`` is the normal-approximation probability that the candidate has
    the lower P0 cost. ``regret_*`` are E[max(0, wrong-way difference)] in cost
    units per application.
    """
    n_pop = int(in_pop.sum())
    c_cost = np.where(observed, cost_candidate, 0.0)
    i_cost = np.where(observed, cost_incumbent, 0.0)
    v_c, psi_c, w = _dr_parts(
        c_cost, actions_candidate, amount, observed, propensity, in_pop, phat, costs
    )
    v_i, psi_i, _ = _dr_parts(
        i_cost, actions_incumbent, amount, observed, propensity, in_pop, phat, costs
    )
    out = {
        "candidate_value": v_c,
        "incumbent_value": v_i,
        "difference": float("nan"),
        "difference_se": float("nan"),
        "difference_ci_low": float("nan"),
        "difference_ci_high": float("nan"),
        "p_candidate_better": float("nan"),
        "regret_candidate": float("nan"),
        "regret_incumbent": float("nan"),
        "decision": "not identified",
        "n_pop": n_pop,
        "n_observed": int(observed.sum()),
        "max_weight": float(w[observed].max()) if observed.any() else float("nan"),
    }
    if not (np.isfinite(v_c) and np.isfinite(v_i)) or n_pop <= 1:
        return out
    diff = v_c - v_i
    psi_d = psi_c - psi_i
    se = float(psi_d[in_pop].std(ddof=1) / np.sqrt(n_pop))
    out.update(
        {
            "difference": diff,
            "difference_se": se,
            "difference_ci_low": diff - 1.96 * se,
            "difference_ci_high": diff + 1.96 * se,
        }
    )
    if not np.isfinite(se) or se <= 0:
        out["p_candidate_better"] = 1.0 if diff < 0 else 0.0
        out["decision"] = "prefer candidate" if diff < 0 else "keep incumbent"
        out["regret_candidate"] = float(max(diff, 0.0))
        out["regret_incumbent"] = float(max(-diff, 0.0))
        return out
    z = diff / se
    p_better = float(norm.cdf(-z))  # P(D < 0): candidate is cheaper
    phi = float(norm.pdf(z))
    cdf = float(norm.cdf(z))
    # Regret of choosing the candidate is E[max(0, D)]; choosing the incumbent is
    # E[max(0, -D)]. The labels were reversed in the first implementation.
    regret_candidate = se * phi + diff * cdf
    regret_incumbent = se * phi - diff * (1.0 - cdf)
    if p_better >= 0.95:
        decision = "prefer candidate"
    elif p_better <= 0.05:
        decision = "keep incumbent"
    else:
        decision = "inconclusive"
    out.update(
        {
            "p_candidate_better": p_better,
            "regret_candidate": float(max(regret_candidate, 0.0)),
            "regret_incumbent": float(max(regret_incumbent, 0.0)),
            "decision": decision,
        }
    )
    return out


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
    v_pop_se: float = 0.0,
) -> Bounds:
    """Partial-identification bounds for the full-population value.

    The unobserved logging-rejected rows are bounded by the min/max cost of the
    candidate action; the identified population uses the supplied estimate. The
    unconditional interval widens the bounds by the `P0` estimate's standard
    error, scaled by the `P0` share. Because the bounds are monotone in `v_pop`,
    that widened interval is a valid (conservative) 95% confidence interval for
    the full-population value under the bounds assumptions; the narrow interval
    is not.
    """
    n = len(actions)
    n_pop = int(in_pop.sum())
    n_rej = int(rejected.sum())
    se = 0.0 if not np.isfinite(v_pop_se) else max(float(v_pop_se), 0.0)
    se_term = 1.96 * (n_pop / max(n, 1)) * se
    if n_rej == 0 or n == 0:
        return Bounds(
            v_pop,
            v_pop,
            0.0,
            n_rej,
            v_pop - se_term,
            v_pop + se_term,
            2.0 * se_term,
        )
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
    lower_u = lower - se_term
    upper_u = upper + se_term
    return Bounds(
        lower,
        upper,
        upper - lower,
        n_rej,
        lower_u,
        upper_u,
        upper_u - lower_u,
    )


def coverage(estimate: Estimate, truth: float) -> float:
    if not np.isfinite(estimate.value) or not np.isfinite(estimate.se):
        return float("nan")
    return float(abs(estimate.value - truth) <= 1.96 * estimate.se)
