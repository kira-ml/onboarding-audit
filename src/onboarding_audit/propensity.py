"""Propensity helpers for the sensitivity analysis.

The pilot's main result uses oracle propensities to isolate estimator behavior.
This module adds the realistic modes:

- `estimated`: action-level propensities estimated from the observed draw;
- `noisy`: the oracle propensity multiplied by lognormal noise;
- `covariate`: a per-action logistic model P(observed | action, X), fit with
  cross-fitting so the propensities are not evaluated in-sample.

These are used only to test whether the correction survives the loss of the
oracle. They are not a substitute for a real propensity-estimation study on a
bank's log.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

from .observation import ObservationDraw, ObservationModel


def estimate_from_draw(
    model: ObservationModel,
    draw: ObservationDraw,
) -> np.ndarray:
    """Estimate action-level observation propensities from one draw."""
    actions = model.logging_actions
    observed = draw.observed
    review = actions == "review"
    approve = actions == "approve"
    e = np.zeros(len(actions), dtype=float)

    if review.any():
        e[review] = float(observed[review].mean())
    if approve.any():
        # The marginal observation rate is the propensity. The earlier
        # decomposition (audit_rate + (1-audit_rate) * base) omitted the
        # resolution factor on the audit channel and overstated e.
        e[approve] = float(observed[approve].mean())
    return e


def noisy_copy(
    e: np.ndarray,
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Lognormal multiplicative noise with mean 1, clipped to (0, 1]."""
    if sigma <= 0:
        return e.copy()
    z = rng.normal(size=len(e))
    out = e * np.exp(sigma * z - 0.5 * sigma * sigma)
    out = np.clip(out, 1e-6, 1.0)
    out[e <= 0] = 0.0
    return out


def fit_covariate_propensity(
    X: np.ndarray,
    actions: np.ndarray,
    observed: np.ndarray,
    *,
    C: float = 0.5,
    max_iter: int = 300,
    n_splits: int = 3,
    random_state: int = 0,
) -> np.ndarray:
    """Per-action logistic propensity model P(observed | action, X).

    The target `observed` is known for every row, so the model can be fit on all
    rows of an action, not only on the labeled rows. Reject rows have e=0
    (outside the primary estimand). The model is cross-fitted: each row's
    propensity comes from a model that did not see that row, which prevents
    in-sample overfitting from flattering the correction. If an action has too
    few rows, one class, or a fold with one class, the action/fold mean is used.
    """
    X = np.asarray(X, dtype=float)
    actions = np.asarray(actions)
    observed = np.asarray(observed).astype(int)
    if X.shape[0] != len(actions):
        raise ValueError("X and actions must have the same number of rows")
    e = np.zeros(len(actions), dtype=float)
    for action in ("review", "approve"):
        mask = actions == action
        if not mask.any():
            continue
        Xa = X[mask]
        ya = observed[mask]
        if len(ya) < 20 or len(np.unique(ya)) < 2:
            e[mask] = float(ya.mean())
            continue
        k = min(n_splits, len(ya))
        if k < 2:
            e[mask] = float(ya.mean())
            continue
        folds = KFold(n_splits=k, shuffle=True, random_state=random_state)
        pred = np.empty(len(ya), dtype=float)
        for train, test in folds.split(Xa):
            y_train = ya[train]
            if len(np.unique(y_train)) < 2:
                pred[test] = float(y_train.mean())
                continue
            model = LogisticRegression(C=C, max_iter=max_iter, solver="lbfgs")
            model.fit(Xa[train], y_train)
            pred[test] = model.predict_proba(Xa[test])[:, 1]
        e[mask] = pred
    e = np.clip(e, 1e-6, 1.0 - 1e-6)
    e[actions == "reject"] = 0.0
    return e
