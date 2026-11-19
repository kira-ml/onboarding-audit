"""Validate a decision log against the onboarding-audit schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

REQUIRED = ["application_id", "decision_time", "action", "score", "amount"]
OPTIONAL = [
    "application_time",
    "reviewed",
    "review_outcome",
    "review_time",
    "audit_flag",
    "audit_time",
    "propensity",
    "label",
    "label_time",
    "label_source",
    "censoring_reason",
    "model_version",
    "threshold_version",
    "segment",
    "channel",
    "amount",
]
FEATURE_HINTS = [
    "customer_age",
    "credit_risk_score",
    "velocity_6h",
    "velocity_24h",
    "velocity_4w",
    "bank_months_count",
    "zip_count_4w",
    "session_length_in_minutes",
    "p_fraud",
    "p_fraud_lgbm",
]
PII_HINTS = ["name", "email", "phone", "address", "account_number", "ssn"]


@dataclass
class SchemaReport:
    ok: bool
    n_rows: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    estimator_readiness: dict[str, bool] = field(default_factory=dict)
    missing_by_estimator: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "n_rows": self.n_rows,
            "errors": self.errors,
            "warnings": self.warnings,
            "estimator_readiness": self.estimator_readiness,
            "missing_by_estimator": self.missing_by_estimator,
        }


def _has(df: pd.DataFrame, cols: list[str]) -> bool:
    return all(c in df.columns for c in cols)


def validate_log(df: pd.DataFrame) -> SchemaReport:
    errors: list[str] = []
    warnings: list[str] = []
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        errors.append(f"missing required columns: {missing}")
        return SchemaReport(
            ok=False,
            n_rows=len(df),
            errors=errors,
            warnings=warnings,
            estimator_readiness={},
            missing_by_estimator={},
        )

    if len(df) == 0:
        errors.append("log is empty")
    if df["application_id"].isna().any():
        errors.append("application_id contains nulls")
    if df["decision_time"].isna().any():
        errors.append("decision_time contains nulls")

    actions = df["action"].astype(str)
    bad = ~actions.isin({"approve", "review", "reject"})
    if bad.any():
        errors.append(f"invalid action values: {sorted(actions[bad].unique())}")

    score = pd.to_numeric(df["score"], errors="coerce")
    if score.isna().any() or ((score < 0) | (score > 1)).any():
        errors.append("score must be numeric in [0, 1]")
    amount = pd.to_numeric(df["amount"], errors="coerce")
    if amount.isna().any() or (amount < 0).any():
        errors.append("amount must be numeric and non-negative")

    if "reviewed" in df.columns:
        vals = df["reviewed"].dropna()
        if not set(vals.unique()).issubset({0, 1}):
            errors.append("reviewed must be 0/1")
        if ((df["reviewed"] == 1) & (actions != "review")).any():
            errors.append("reviewed=1 requires action='review'")
    if "audit_flag" in df.columns:
        vals = df["audit_flag"].dropna()
        if not set(vals.unique()).issubset({0, 1}):
            errors.append("audit_flag must be 0/1")
        if ((df["audit_flag"] == 1) & (actions != "approve")).any():
            errors.append("audit_flag=1 requires action='approve'")
    if "propensity" in df.columns:
        p = pd.to_numeric(df["propensity"], errors="coerce").dropna()
        if ((p <= 0) | (p > 1)).any():
            errors.append("propensity must be in (0, 1]")
    if "label" in df.columns:
        vals = df["label"].dropna()
        if not set(vals.unique()).issubset({0, 1}):
            errors.append("label must be 0/1 or null")
        if "label_time" not in df.columns:
            errors.append("label_time is required when label is present")
        else:
            has_label = df["label"].notna()
            if df.loc[has_label, "label_time"].isna().any():
                errors.append("label_time missing for some labeled rows")
    if "application_time" in df.columns and "decision_time" in df.columns:
        app = pd.to_datetime(df["application_time"], errors="coerce")
        dec = pd.to_datetime(df["decision_time"], errors="coerce")
        if (dec < app).any():
            errors.append("decision_time precedes application_time")

    if "propensity" not in df.columns:
        warnings.append(
            "propensity is absent; IPW/DR will rely on the audit design or "
            "known observation probabilities."
        )
    if "label_source" not in df.columns:
        warnings.append(
            "label_source is absent; the label-source mix diagnostic cannot be "
            "computed. Add review / post_approval_report / chargeback / "
            "mule_investigation / audit."
        )
    if "label_time" not in df.columns:
        warnings.append(
            "label_time is absent; label-maturity and delay diagnostics cannot "
            "be computed."
        )
    for col in df.columns:
        low = col.lower()
        if any(h in low for h in PII_HINTS) and not low.endswith(("_hash", "_id")):
            warnings.append(
                f"column {col!r} may contain PII; use a hashed/pseudonymized "
                "evaluation extract."
            )

    readiness: dict[str, bool] = {}
    missing_by: dict[str, list[str]] = {}

    def check(name: str, cols: list[str]) -> None:
        miss = [c for c in cols if c not in df.columns]
        readiness[name] = len(miss) == 0
        missing_by[name] = miss

    check("naive", ["action", "label"])
    ipw_ok = _has(df, ["action", "label"]) and (
        "propensity" in df.columns or "audit_flag" in df.columns
    )
    readiness["ipw"] = ipw_ok
    missing_by["ipw"] = [] if ipw_ok else ["propensity or audit_flag"]
    dr_ok = ipw_ok and any(c in df.columns for c in FEATURE_HINTS)
    readiness["dr"] = dr_ok
    missing_by["dr"] = (
        [] if dr_ok else ["propensity/audit_flag + pre-decision features"]
    )
    check("audit_only", ["audit_flag", "label", "label_time"])
    check("bounds", ["action", "amount", "label"])

    return SchemaReport(
        ok=len(errors) == 0,
        n_rows=len(df),
        errors=errors,
        warnings=warnings,
        estimator_readiness=readiness,
        missing_by_estimator=missing_by,
    )
