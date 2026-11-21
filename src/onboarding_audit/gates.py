"""Identification gates for the arbitrary-log report.

The report must not print a point estimate when the log does not identify it.
These checks are deliberately conservative: a false "not identified" is cheaper
than a confident memo on an unidentified quantity.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class IdentificationReport:
    passed: bool
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "metrics": {k: float(v) for k, v in self.metrics.items()},
        }


def _ess(w: np.ndarray) -> float:
    sw = float(w.sum())
    sw2 = float((w * w).sum())
    return sw * sw / sw2 if sw2 > 0 else 0.0


def check_identification(
    *,
    actions: np.ndarray,
    candidate_actions: np.ndarray,
    observed: np.ndarray,
    propensity: np.ndarray,
    cost: np.ndarray,
    positivity_ok: bool,
    propensity_source: str,
    has_audit: bool,
    min_observed_total: int = 100,
    min_observed_per_action: int = 30,
    min_ess: float = 100.0,
    max_weight: float = 100.0,
    max_candidate_outside_p0_share: float = 0.10,
) -> IdentificationReport:
    """Check whether the log supports a point estimate for the P0 population."""
    actions = np.asarray(actions)
    candidate_actions = np.asarray(candidate_actions)
    observed = np.asarray(observed, dtype=bool)
    e = np.asarray(propensity, dtype=float)
    cost = np.asarray(cost, dtype=float)

    in_pop = actions != "reject"
    rejected = ~in_pop
    n = len(actions)
    n_pop = int(in_pop.sum())
    n_rejected = int(rejected.sum())
    n_obs = int(observed.sum())

    reasons: list[str] = []
    warnings: list[str] = []

    # Positivity: every P0 row must have a positive chance of observation.
    # A provided propensity column is only required on observed rows; an
    # estimated propensity is populated for every P0 row. With a provided
    # column, a structural zero on an unobserved row cannot be detected; the
    # memo states that the check covers observed P0 rows only.
    if not positivity_ok:
        reasons.append("positivity failure: a P0 row has zero observation probability")
    elif propensity_source == "provided":
        if (observed & in_pop).any() and (e[observed & in_pop] <= 0).any():
            reasons.append("positivity failure: an observed P0 row has zero propensity")
    elif n_pop and (e[in_pop] <= 0).any():
        reasons.append("positivity failure: a P0 row has zero observation probability")

    # Cost support: negative costs are not a valid decision input.
    if (cost < 0).any():
        reasons.append("cost support failure: at least one candidate cost is negative")

    # Sample size.
    if n_obs < min_observed_total:
        reasons.append(f"observed sample too small: {n_obs} < {min_observed_total}")
    per_action = {}
    for action in ("approve", "review"):
        mask = actions == action
        if mask.any():
            per_action[action] = int((observed & mask).sum())
    for action, count in per_action.items():
        if count < min_observed_per_action:
            reasons.append(
                f"observed {action} sample too small: {count} < "
                f"{min_observed_per_action}"
            )

    # Weights and ESS on the observed P0 rows.
    w = np.zeros(n, dtype=float)
    np.divide(1.0, e, out=w, where=observed & in_pop & (e > 0))
    ess = _ess(w)
    max_w = float(w[observed & in_pop].max()) if (observed & in_pop).any() else 0.0
    if ess < min_ess:
        reasons.append(f"effective sample size too small: {ess:.1f} < {min_ess:.1f}")
    if max_w > max_weight:
        reasons.append(f"max weight too high: {max_w:.1f} > {max_weight:.1f}")

    # Candidate actions outside the logging P0 population.
    outside = rejected & (candidate_actions != "reject")
    outside_share = float(outside.sum() / n) if n else 0.0
    if outside_share > max_candidate_outside_p0_share:
        warnings.append(
            f"candidate actions outside P0: {outside.sum():,} rows "
            f"({outside_share:.1%}); the point estimate is P0-only, so report "
            "the bounds for the full-policy value"
        )

    # Soft diagnostics.
    if n_obs < 500:
        warnings.append(f"small observed sample: {n_obs} labels")
    if ess < 500:
        warnings.append(f"low effective sample size: {ess:.0f}")
    if max_w > 50:
        warnings.append(f"heavy max weight: {max_w:.1f}")
    for action, count in per_action.items():
        if 30 <= count < 100:
            warnings.append(f"moderate {action} sample: {count} labels")
    e_mask = observed & in_pop if propensity_source == "provided" else in_pop
    e_min = float(e[e_mask].min()) if e_mask.any() else 0.0
    e_max = float(e[e_mask].max()) if e_mask.any() else 0.0
    if e_min < 0.01:
        warnings.append(f"small propensity: e_min={e_min:.4f}")
    if propensity_source == "estimated" and not has_audit:
        warnings.append(
            "action-level propensities estimated without an audit; consider "
            "`--propensity-model covariate` or an audit"
        )
    if propensity_source == "estimated_covariate":
        warnings.append(
            "covariate propensities are a logistic approximation; check the "
            "weight tail and ESS"
        )

    metrics = {
        "n": float(n),
        "n_p0": float(n_pop),
        "n_rejected": float(n_rejected),
        "n_observed": float(n_obs),
        "ess": float(ess),
        "max_weight": float(max_w),
        "e_min": float(e_min),
        "e_max": float(e_max),
        "candidate_outside_p0": float(outside.sum()),
        "candidate_outside_p0_share": float(outside_share),
        "cost_min": float(cost.min()) if n else 0.0,
        "min_observed_action": float(min(per_action.values())) if per_action else 0.0,
    }
    return IdentificationReport(
        passed=not reasons,
        reasons=reasons,
        warnings=warnings,
        metrics=metrics,
    )
