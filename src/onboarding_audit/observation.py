"""Observation model: review labels, post-approval labels, audit, delay."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from .config import Observation


def p_resolved(
    day: np.ndarray,
    median: float,
    sigma: float,
    cutoff: float,
) -> np.ndarray:
    """P(label delay <= cutoff - decision day) for a lognormal delay."""
    day = np.asarray(day, dtype=float)
    remaining = cutoff - day
    out = np.zeros(len(day), dtype=float)
    valid = remaining > 0
    if median <= 0:
        out[valid] = 1.0
        return out
    z = (np.log(np.maximum(remaining[valid], 1e-12)) - np.log(median)) / sigma
    out[valid] = norm.cdf(z)
    return out


@dataclass
class ObservationModel:
    cfg: Observation
    decision_day: np.ndarray
    logging_actions: np.ndarray
    review_mask: np.ndarray
    approve_mask: np.ndarray
    reject_mask: np.ndarray
    in_pop: np.ndarray
    p_resolved_review: np.ndarray
    p_resolved_approve: np.ndarray
    propensity: np.ndarray
    e_review: float
    e_approve: float


@dataclass
class ObservationDraw:
    observed: np.ndarray
    audit: np.ndarray
    resolved_review: np.ndarray
    resolved_approve: np.ndarray
    observed_review: np.ndarray
    observed_approve: np.ndarray
    label_source: np.ndarray


def build_observation_model(
    logging_actions: np.ndarray,
    decision_day: np.ndarray,
    cfg: Observation,
) -> ObservationModel:
    actions = np.asarray(logging_actions)
    review_mask = actions == "review"
    approve_mask = actions == "approve"
    reject_mask = actions == "reject"
    in_pop = ~reject_mask

    p_rev = p_resolved(
        decision_day,
        cfg.review_delay_median,
        cfg.review_delay_sigma,
        cfg.cutoff_day,
    )
    p_app = p_resolved(
        decision_day,
        cfg.approve_delay_median,
        cfg.approve_delay_sigma,
        cfg.cutoff_day,
    )

    e_review = p_rev * float(cfg.kappa_review)
    e_approve = p_app * (
        1.0 - (1.0 - float(cfg.e_approve)) * (1.0 - float(cfg.audit_rate))
    )

    propensity = np.zeros(len(actions), dtype=float)
    propensity[review_mask] = e_review[review_mask]
    propensity[approve_mask] = e_approve[approve_mask]
    if (propensity[in_pop] <= 0).any():
        raise ValueError(
            "positivity failure: a non-rejected row has zero observation "
            "probability. Increase kappa_review, e_approve, or audit_rate."
        )
    return ObservationModel(
        cfg=cfg,
        decision_day=np.asarray(decision_day, dtype=float),
        logging_actions=actions,
        review_mask=review_mask,
        approve_mask=approve_mask,
        reject_mask=reject_mask,
        in_pop=in_pop,
        p_resolved_review=p_rev,
        p_resolved_approve=p_app,
        propensity=propensity,
        e_review=float(cfg.kappa_review),
        e_approve=float(cfg.e_approve),
    )


def draw_observation(
    model: ObservationModel,
    rng: np.random.Generator,
    *,
    y: np.ndarray | None = None,
    outcome_dependent: bool = False,
    e_approve_fraud: float = 0.30,
) -> ObservationDraw:
    """Draw resolved, observed labels for one replication.

    Resolution is a random lognormal delay draw. The main mechanism is
    action-dependent: review labels with kappa_review, approved labels with
    e_approve plus the random post-hoc audit. In the outcome-dependent stress
    scenario, approved fraud is labeled with e_approve_fraud while approved
    legitimate applications are labeled only by the audit.
    """
    n = len(model.logging_actions)
    cfg = model.cfg

    delay_rev = rng.lognormal(
        mean=np.log(cfg.review_delay_median),
        sigma=cfg.review_delay_sigma,
        size=n,
    )
    delay_app = rng.lognormal(
        mean=np.log(cfg.approve_delay_median),
        sigma=cfg.approve_delay_sigma,
        size=n,
    )
    resolved_review = (model.decision_day + delay_rev) <= cfg.cutoff_day
    resolved_approve = (model.decision_day + delay_app) <= cfg.cutoff_day

    audit = (rng.random(n) < float(cfg.audit_rate)) & model.approve_mask
    review_channel = model.review_mask & (rng.random(n) < float(cfg.kappa_review))
    if outcome_dependent:
        if y is None:
            raise ValueError("outcome_dependent draws require y")
        fraud = np.asarray(y, dtype=int) == 1
        approve_channel = (
            model.approve_mask & fraud & (rng.random(n) < float(e_approve_fraud))
        )
    else:
        approve_channel = model.approve_mask & (rng.random(n) < float(cfg.e_approve))

    observed_review = review_channel & resolved_review
    observed_approve = model.approve_mask & (approve_channel | audit) & resolved_approve
    observed = observed_review | observed_approve

    label_source = np.full(n, "none", dtype=object)
    label_source[observed_review] = "review"
    label_source[observed_approve & audit] = "audit"
    label_source[observed_approve & ~audit & approve_channel] = "post_approval_report"

    return ObservationDraw(
        observed=observed,
        audit=audit,
        resolved_review=resolved_review,
        resolved_approve=resolved_approve,
        observed_review=observed_review,
        observed_approve=observed_approve,
        label_source=label_source,
    )
