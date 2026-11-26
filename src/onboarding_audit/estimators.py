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


def action_weighted(
    cost: np.ndarray,
    observed: np.ndarray,
    actions: np.ndarray,
    in_pop: np.ndarray,
) -> Estimate:
    """Hajek estimate with action-level observation rates estimated from the log.

    This is the natural "incumbent backtest with action weights" comparator to
    the unweighted labeled mean. It is not the oracle IPW: the observation rate
    is estimated within each logged action from the same draw.
    """
    e = np.zeros(len(cost), dtype=float)
    for action in ("approve", "review"):
        mask = actions == action
        if mask.any():
            e[mask] = float(observed[mask].mean())
    return ipw_hajek(cost, observed, e, in_pop)


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


def labels_for_power(
    se: float,
    delta: float,
    n_observed: int,
    *,
    power: float = 0.80,
    alpha: float = 0.05,
) -> int:
    """Labels needed to detect `delta` at the given power.

    Approximate: assumes the comparison standard error scales as
    1/sqrt(n_labels) and that the label noise dominates. Planning only.
    """
    if not np.isfinite(se) or se <= 0 or delta <= 0 or n_observed <= 0:
        return 0
    z = float(norm.ppf(1 - alpha / 2) + norm.ppf(power))
    return int(np.ceil(n_observed * (z * se / delta) ** 2))


def full_policy_difference(
    actions_candidate: np.ndarray,
    actions_incumbent: np.ndarray,
    amount: np.ndarray,
    costs: Costs,
    in_pop: np.ndarray,
    p0_difference: float,
    p0_difference_se: float,
    *,
    z: float = 1.96,
) -> dict:
    """Bound the full-policy difference and report its reject-margin sensitivity.

    The `P0` difference is identified (up to its standard error). The reject
    margin is not. For each logging-rejected application, the candidate and
    incumbent costs are evaluated at ``Y=0`` and ``Y=1``; the per-row difference
    therefore has two possible values, and the mean difference is bounded by the
    means of the per-row minima and maxima. That bound is sharp when the
    unobserved outcomes can vary freely across rejected rows.

    The break-even fraud rate assumes a **common** fraud rate ``p`` among
    logging-rejected rows. It is a sensitivity threshold, not an estimate: if
    the full-policy difference changes sign inside ``[0, 1]``, the decision
    depends on an unobserved quantity, and the memo should say so.
    """
    n = len(actions_candidate)
    in_pop = np.asarray(in_pop, dtype=bool)
    rejected = ~in_pop
    n_pop = int(in_pop.sum())
    n_rej = int(rejected.sum())
    out = {
        "p0_difference": p0_difference,
        "p0_difference_se": p0_difference_se,
        "p0_share": float(n_pop / n) if n else float("nan"),
        "reject_share": float(n_rej / n) if n else float("nan"),
        "n_rejected": n_rej,
        "reject_difference_if_legit": float("nan"),
        "reject_difference_if_fraud": float("nan"),
        "reject_min_mean": float("nan"),
        "reject_max_mean": float("nan"),
        "full_difference_lower": float("nan"),
        "full_difference_upper": float("nan"),
        "breakeven_reject_fraud_rate": float("nan"),
        "breakeven_low": float("nan"),
        "breakeven_high": float("nan"),
        "decision": "not identified",
        "basis": "",
    }
    if n == 0:
        out["basis"] = "empty population"
        return out

    se = 0.0 if not np.isfinite(p0_difference_se) else max(float(p0_difference_se), 0.0)

    if n_rej == 0:
        if not np.isfinite(p0_difference):
            out["basis"] = "P0 difference not identified"
            return out
        if not np.isfinite(p0_difference_se):
            out["basis"] = (
                "P0 standard error is not available; the full-policy interval is "
                "not identified"
            )
            return out
        lower = p0_difference - z * se
        upper = p0_difference + z * se
        if se > 0:
            p_better = float(norm.cdf(-p0_difference / se))
            if p_better >= 0.95:
                decision = "candidate cheaper"
            elif p_better <= 0.05:
                decision = "incumbent cheaper"
            else:
                decision = "inconclusive"
        else:
            if p0_difference < 0:
                decision = "candidate cheaper"
            elif p0_difference > 0:
                decision = "incumbent cheaper"
            else:
                decision = "inconclusive"
        out.update(
            {
                "full_difference_lower": lower,
                "full_difference_upper": upper,
                "decision": decision,
                "basis": "no logging-rejected rows; the full population equals P0",
            }
        )
        return out

    y0 = np.zeros(n, dtype=int)
    y1 = np.ones(n, dtype=int)
    c0 = realized_cost(actions_candidate, y0, amount, costs)
    c1 = realized_cost(actions_candidate, y1, amount, costs)
    i0 = realized_cost(actions_incumbent, y0, amount, costs)
    i1 = realized_cost(actions_incumbent, y1, amount, costs)
    d0 = (c0 - i0)[rejected]
    d1 = (c1 - i1)[rejected]
    reject_d0 = float(d0.mean())
    reject_d1 = float(d1.mean())
    reject_min = float(np.minimum(d0, d1).mean())
    reject_max = float(np.maximum(d0, d1).mean())
    out.update(
        {
            "reject_difference_if_legit": reject_d0,
            "reject_difference_if_fraud": reject_d1,
            "reject_min_mean": reject_min,
            "reject_max_mean": reject_max,
        }
    )
    if n_pop == 0:
        if reject_max < 0:
            decision = "candidate cheaper for any reject outcome"
        elif reject_min > 0:
            decision = "incumbent cheaper for any reject outcome"
        else:
            decision = "depends on the reject margin"
        out.update(
            {
                "full_difference_lower": reject_min,
                "full_difference_upper": reject_max,
                "decision": decision,
                "basis": (
                    "no P0 rows; the full population is the logging-rejected "
                    "population, bounded by its per-row min/max"
                ),
            }
        )
        return out
    if not np.isfinite(p0_difference):
        out["basis"] = (
            "P0 difference not identified; reject margin reported for diagnostics"
        )
        return out
    if not np.isfinite(p0_difference_se):
        out["basis"] = (
            "P0 standard error is not available; the full-policy interval is not "
            "identified"
        )
        return out

    p0_share = n_pop / n
    rej_share = n_rej / n
    full_lower = p0_share * (p0_difference - z * se) + rej_share * reject_min
    full_upper = p0_share * (p0_difference + z * se) + rej_share * reject_max
    # Does the reject margin have leverage on the *decision*? A nonzero range
    # that only moves the magnitude is not enough; it must be able to flip the
    # sign at the P0 point estimate. Otherwise a zero-crossing is P0
    # uncertainty, not reject-margin dependence.
    point_lo = p0_share * p0_difference + rej_share * reject_min
    point_hi = p0_share * p0_difference + rej_share * reject_max
    reject_can_flip = (point_lo < 0 < point_hi) or (point_hi < 0 < point_lo)
    reject_moves_magnitude = (reject_max - reject_min) > 1e-12
    if full_upper < 0:
        decision = "candidate cheaper for any reject outcome"
    elif full_lower > 0:
        decision = "incumbent cheaper for any reject outcome"
    elif reject_can_flip:
        decision = "depends on the reject margin"
    else:
        decision = "P0 inconclusive"

    basis = ""
    if decision == "P0 inconclusive":
        if reject_moves_magnitude:
            basis = (
                "the combined interval includes zero because the P0 estimate is "
                "uncertain; the reject margin moves the magnitude but does not "
                "flip the sign at the P0 point estimate"
            )
        else:
            basis = (
                "the combined interval includes zero because the P0 estimate is "
                "uncertain; the reject margin cannot change the difference"
            )
    elif decision != "depends on the reject margin":
        basis = "the sharp bounds exclude zero; no reject-margin assumption is needed"
    else:
        # Homogeneous-p sensitivity. The full difference is linear in p:
        #   D(p) = p0_share * D_P0 + reject_share * [d0 + p * (d1 - d0)].
        intercept = p0_share * p0_difference + rej_share * reject_d0
        slope = rej_share * (reject_d1 - reject_d0)
        if abs(slope) > 1e-12:
            p_star = -intercept / slope
            intercept_lo = p0_share * (p0_difference - z * se) + rej_share * reject_d0
            intercept_hi = p0_share * (p0_difference + z * se) + rej_share * reject_d0
            p_lo = -intercept_lo / slope
            p_hi = -intercept_hi / slope
            out.update(
                {
                    "breakeven_reject_fraud_rate": p_star,
                    "breakeven_low": min(p_lo, p_hi),
                    "breakeven_high": max(p_lo, p_hi),
                }
            )
            if 0.0 < p_star < 1.0:
                if intercept < 0 < intercept + slope:
                    basis = (
                        "under a common rejected fraud rate p, the candidate is "
                        f"cheaper for p < {p_star:.3f} and the incumbent is "
                        f"cheaper for p > {p_star:.3f}; the sharp bounds still "
                        "include zero"
                    )
                elif intercept + slope < 0 < intercept:
                    basis = (
                        "under a common rejected fraud rate p, the candidate is "
                        f"cheaper for p > {p_star:.3f} and the incumbent is "
                        f"cheaper for p < {p_star:.3f}; the sharp bounds still "
                        "include zero"
                    )
                else:
                    basis = "the homogeneous-p sensitivity has no sign change in [0, 1]"
            else:
                basis = (
                    "the homogeneous-p break-even lies outside [0, 1]; "
                    "the sharp bounds still include zero"
                )
        else:
            basis = (
                "the average reject-margin slope is zero; the sharp bounds still "
                "include zero because the per-row differences can differ"
            )

    out.update(
        {
            "full_difference_lower": full_lower,
            "full_difference_upper": full_upper,
            "decision": decision,
            "basis": basis,
        }
    )
    return out


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
        out["full_policy"] = full_policy_difference(
            actions_candidate,
            actions_incumbent,
            amount,
            costs,
            in_pop,
            out["difference"],
            out["difference_se"],
        )
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
        out["full_policy"] = full_policy_difference(
            actions_candidate,
            actions_incumbent,
            amount,
            costs,
            in_pop,
            diff,
            se,
        )
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
    power_targets = {}
    for rel in (0.05, 0.10):
        delta = rel * abs(v_i)
        needed = labels_for_power(se, delta, int(observed.sum()))
        power_targets[f"delta_{int(rel * 100)}pct"] = {
            "delta": delta,
            "labels_needed": needed,
            "additional_labels": max(0, needed - int(observed.sum())),
        }
    out["power"] = power_targets
    out["full_policy"] = full_policy_difference(
        actions_candidate,
        actions_incumbent,
        amount,
        costs,
        in_pop,
        diff,
        se,
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
