"""Propensity helpers for the sensitivity analysis.

The pilot's main result uses oracle propensities to isolate estimator behavior.
This module adds the two realistic modes:

- `estimated`: action-level propensities estimated from the observed draw;
- `noisy`: the oracle propensity multiplied by lognormal noise.

Both are used only to test whether the correction survives the loss of the
oracle. They are not a substitute for a real propensity-estimation study on a
bank's log.
"""

from __future__ import annotations

import numpy as np

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
        audit = draw.audit
        audit_rate = float(audit[approve].mean())
        non_audit = approve & ~audit
        base = float(observed[non_audit].mean()) if non_audit.any() else 0.0
        e[approve] = audit_rate + (1.0 - audit_rate) * base
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
