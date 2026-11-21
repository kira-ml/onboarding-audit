"""Load and prepare the BAF account-opening evaluation frame."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


@dataclass
class EvalData:
    df: pd.DataFrame
    y: np.ndarray
    amount: np.ndarray
    month: np.ndarray
    decision_day: np.ndarray
    X: np.ndarray
    feature_names: list[str]
    n: int


def _decision_day(
    month: np.ndarray,
    rng: np.random.Generator,
    months: tuple[int, ...] | list[int] | None = None,
) -> np.ndarray:
    """Uniform decision day within each evaluation month; cutoff is day 90.

    The months are mapped to consecutive 30-day windows starting at day 0, so a
    single-month run uses days 0-30 and a two-month run uses days 0-60. This
    keeps the delay/cutoff comparison meaningful when the window is split.
    """
    months = tuple(sorted(months if months is not None else (5, 6)))
    day = np.empty(len(month), dtype=float)
    present = set(np.unique(month).tolist())
    if not present <= set(months):
        raise ValueError(f"evaluation months must be a subset of {months}")
    for i, m in enumerate(months):
        mask = month == m
        if mask.any():
            day[mask] = 30.0 * i + rng.uniform(0.0, 30.0, int(mask.sum()))
    return day


def load_eval_data(
    path: Path | str,
    *,
    label_col: str,
    amount_col: str,
    month_col: str,
    outcome_features: list[str] | tuple[str, ...],
    seed: int,
    months: tuple[int, ...] | list[int] | None = None,
) -> EvalData:
    """Load a scored BAF test-window parquet and build the outcome-model matrix.

    The feature matrix is standardized on the evaluation window. The scaler uses
    features only (no labels), so this is not target leakage; it is an
    unsupervised preprocessing choice stated in the pilot spec.
    """
    df = pd.read_parquet(path)
    if months is not None:
        df = df[df[month_col].isin(tuple(months))].reset_index(drop=True)
        if df.empty:
            raise ValueError(f"no rows in months {tuple(months)}")
    required = {label_col, amount_col, month_col, *outcome_features}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")

    y = df[label_col].to_numpy(dtype=int)
    amount = df[amount_col].to_numpy(dtype=float)
    month = df[month_col].to_numpy(dtype=int)
    if not np.isin(y, [0, 1]).all():
        raise ValueError("label must be binary")
    if not np.isfinite(amount).all() or (amount < 0).any():
        raise ValueError("amount must be finite and non-negative")

    rng = np.random.default_rng(seed)
    decision_day = _decision_day(month, rng, months)

    features = list(outcome_features)
    X = df[features].to_numpy(dtype=float)
    X = np.column_stack([X, np.log1p(amount), month.astype(float)])
    feature_names = features + ["log1p_amount", "month"]
    if not np.isfinite(X).all():
        raise ValueError("outcome-model features contain non-finite values")
    X = StandardScaler().fit_transform(X)

    return EvalData(
        df=df,
        y=y,
        amount=amount,
        month=month,
        decision_day=decision_day,
        X=X,
        feature_names=feature_names,
        n=len(df),
    )
