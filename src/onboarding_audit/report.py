"""Arbitrary-log report: evaluate a candidate onboarding policy from a log.

This is the v0.2 product surface. It reuses the pilot estimators but takes a
team's own decision log and a candidate score file. It does not simulate
anything: propensities come from the log (provided or estimated), labels are the
observed labels, and the reject margin is bounded.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .config import Costs, PilotConfig, load_config
from .estimators import (
    Estimate,
    compare_policies,
    dr,
    effective_sample_size,
    fit_outcome_model,
    ipw_hajek,
    ipw_ht,
    naive,
    policy_bounds,
)
from .gates import IdentificationReport, check_identification
from .policies import apply_capacity, choose_actions, realized_cost
from .propensity import fit_covariate_propensity
from .reliability import build_reliability
from .schema import validate_log

TARGET_P0 = "P0"
# The audit sample is drawn from the logging-approved population, not the
# candidate's approved population. Keep the short label for compatibility, but
# state the distinction in the memo and the docs.
TARGET_APPROVED = "approved"
TARGET_FULL = "full"


@dataclass
class PropensityEstimate:
    e: np.ndarray
    source: str
    e_review: float
    e_approve: float
    audit_rate: float
    positivity_ok: bool
    observed_rows: int
    details: dict


@dataclass
class ReportResult:
    n: int
    p0_n: int
    rejected_n: int
    observed_n: int
    action_counts: dict
    candidate_action_counts: dict
    propensity: PropensityEstimate
    identification: IdentificationReport
    estimates: dict
    diagnostics: dict
    bounds: dict
    audit: dict
    comparison: dict
    memo_path: str
    report_path: str


def _read(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_parquet(path)


def _clean(value):
    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    return value


def estimate_propensities(
    df: pd.DataFrame,
    *,
    propensity_col: str = "propensity",
    audit_col: str = "audit_flag",
    propensity_model: str = "action",
    feature_cols: list[str] | tuple[str, ...] | None = None,
    amount_col: str = "amount",
    seed: int | None = None,
) -> PropensityEstimate:
    """Use a provided propensity when complete for observed rows; else estimate.

    The default estimate is the marginal action-level rate:
      e_review  = observed / reviewed
      e_approve = observed / approved

    The marginal rate is the propensity. An earlier audit-aware decomposition
    omitted the resolution factor on the audit channel and overstated e.

    With ``propensity_model="covariate"``, a cross-fitted per-action logistic
    model P(observed | action, X) is used instead. It needs numeric feature
    columns; the design adds log amount and month when available.
    """
    actions = df["action"].astype(str).to_numpy()
    observed = df["label"].notna().to_numpy()
    approve = actions == "approve"
    review = actions == "review"
    reject = actions == "reject"

    if audit_col in df.columns:
        audit = df[audit_col].fillna(0).astype(bool).to_numpy()
    else:
        audit = np.zeros(len(df), dtype=bool)
    audit_rate = float(audit[approve].mean()) if approve.any() else 0.0
    design_names = list(feature_cols or [])

    provided = (
        propensity_col in df.columns
        and observed.any()
        and df.loc[observed, propensity_col].notna().all()
    )
    if provided:
        e = np.zeros(len(df), dtype=float)
        column = df[propensity_col].astype(float)
        provided_all = bool(column.notna().all())
        if provided_all:
            e = column.to_numpy(dtype=float)
            e_diag = np.ones(len(df), dtype=bool)
        else:
            e[observed] = column.loc[observed].to_numpy(dtype=float)
            e_diag = observed
        e_review = (
            float(e[review & e_diag].mean())
            if (review & e_diag).any()
            else float("nan")
        )
        e_approve = (
            float(e[approve & e_diag].mean())
            if (approve & e_diag).any()
            else float("nan")
        )
        source = "provided"
    elif propensity_model == "covariate":
        X, names = _features(df, list(feature_cols or []), amount_col)
        if X is None:
            raise ValueError(
                "covariate propensity model requires at least one numeric feature"
            )
        design_names = names
        e = fit_covariate_propensity(
            X,
            actions,
            observed,
            random_state=int(seed if seed is not None else 0),
        )
        e_review = float(e[review].mean()) if review.any() else 0.0
        e_approve = float(e[approve].mean()) if approve.any() else 0.0
        source = "estimated_covariate"
    else:
        e_review = float(observed[review].mean()) if review.any() else 0.0
        e_approve = float(observed[approve].mean()) if approve.any() else 0.0
        e = np.zeros(len(df), dtype=float)
        e[review] = e_review
        e[approve] = e_approve
        source = "estimated"

    if provided:
        if provided_all:
            in_pop = ~reject
            positivity_ok = bool(in_pop.any() and (e[in_pop] > 0).all())
        else:
            positivity_ok = bool(observed.any() and (e[observed] > 0).all())
    else:
        in_pop = ~reject
        positivity_ok = bool(in_pop.any() and (e[in_pop] > 0).all())

    # Propensity calibration: compare the expected number of observed P0 rows
    # under the stated e to the actual number. Only computable when e covers all
    # P0 rows. A ratio far below 1 means e is too high or the labels are heavily
    # censored; a ratio above 1 is impossible under the stated e.
    calibration_ratio = float("nan")
    expected_observed = float("nan")
    actual_observed = float("nan")
    if provided and provided_all:
        in_pop = ~reject
        expected_observed = float(e[in_pop].sum())
        actual_observed = float(observed[in_pop].sum())
        if expected_observed > 0:
            calibration_ratio = actual_observed / expected_observed
    details = {
        "n_review": int(review.sum()),
        "n_approve": int(approve.sum()),
        "n_reject": int(reject.sum()),
        "n_observed_review": int((review & observed).sum()),
        "n_observed_approve": int((approve & observed).sum()),
        "n_audit": int(audit.sum()),
        "audit_rate_among_approved": audit_rate,
        "provided_propensity": provided,
        "provided_all_rows": bool(provided and provided_all),
        "expected_observed": expected_observed,
        "actual_observed": actual_observed,
        "calibration_ratio": calibration_ratio,
        "propensity_model": propensity_model,
        "propensity_features": design_names,
    }
    return PropensityEstimate(
        e=e,
        source=source,
        e_review=e_review,
        e_approve=e_approve,
        audit_rate=audit_rate,
        positivity_ok=positivity_ok,
        observed_rows=int(observed.sum()),
        details=details,
    )


def _candidate_actions(
    df: pd.DataFrame,
    candidate: pd.DataFrame,
    costs: Costs,
    capacity: float,
) -> np.ndarray:
    if "application_id" not in candidate.columns:
        raise ValueError("candidate file must contain application_id")
    if candidate["application_id"].duplicated().any():
        raise ValueError("candidate file has duplicate application_id values")
    if "action" not in candidate.columns and "score" not in candidate.columns:
        raise ValueError("candidate file must contain action or score")

    merged = df[["application_id"]].merge(
        candidate, on="application_id", how="left", validate="one_to_one"
    )
    if "action" in merged.columns and merged["action"].notna().all():
        actions = merged["action"].astype(str).to_numpy()
        if not set(actions).issubset({"approve", "review", "reject"}):
            raise ValueError("candidate action must be approve/review/reject")
        return actions
    if "score" not in merged.columns or merged["score"].isna().any():
        missing = (
            int(merged["score"].isna().sum()) if "score" in merged else len(merged)
        )
        raise ValueError(f"candidate score missing for {missing} applications")

    score = merged["score"].astype(float).to_numpy()
    if not np.isfinite(score).all() or ((score < 0) | (score > 1)).any():
        raise ValueError("candidate score must be finite and in [0, 1]")
    _, (c_app, c_rev, c_rej) = choose_actions(
        score, costs, df["amount"].to_numpy(float)
    )
    k = int(np.ceil(capacity * len(df)))
    return apply_capacity(c_app, c_rev, c_rej, k)


def _features(
    df: pd.DataFrame,
    feature_cols: list[str] | tuple[str, ...],
    amount_col: str,
) -> tuple[np.ndarray | None, list[str]]:
    cols = [c for c in feature_cols if c in df.columns]
    if not cols:
        return None, []
    X = df[cols].to_numpy(dtype=float)
    names = list(cols)
    X = np.column_stack([X, np.log1p(df[amount_col].to_numpy(dtype=float))])
    names.append("log1p_amount")
    if "month" in df.columns:
        X = np.column_stack([X, df["month"].to_numpy(dtype=float)])
        names.append("month")
    if not np.isfinite(X).all():
        raise ValueError("outcome-model features contain non-finite values")
    return StandardScaler().fit_transform(X), names


def _audit_estimate(
    cost: np.ndarray,
    audit: np.ndarray,
    observed: np.ndarray,
    followup: np.ndarray | None = None,
    n_bins: int = 5,
) -> Estimate:
    """Audit-only mean, post-stratified by follow-up time when available.

    A complete-case mean over observed audit labels is biased toward rows with a
    short delay: late decisions have less time to resolve. Stratifying the audit
    sample by follow-up time and weighting each stratum by 1/P(observed) removes
    that cohort mix bias. Within a stratum the labels are assumed missing at
    random; that is the remaining assumption.
    """
    mask = audit & observed
    n = int(mask.sum())
    if n == 0:
        return Estimate(float("nan"), float("nan"), 0, 0.0, float("nan"))
    if followup is None:
        c = cost[mask]
        se = float(c.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
        return Estimate(float(c.mean()), se, n, float(n), 1.0)

    audit_idx = np.where(audit)[0]
    if len(audit_idx) < 2 * n_bins or not np.isfinite(followup[audit_idx]).all():
        c = cost[mask]
        se = float(c.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
        return Estimate(float(c.mean()), se, n, float(n), 1.0)

    edges = np.quantile(followup[audit_idx], np.linspace(0, 1, n_bins + 1))
    if len(np.unique(edges)) < 3:
        c = cost[mask]
        se = float(c.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
        return Estimate(float(c.mean()), se, n, float(n), 1.0)
    bins = np.clip(np.digitize(followup, edges[1:-1]), 0, n_bins - 1)

    weights = np.zeros(len(cost), dtype=float)
    for b in range(n_bins):
        idx_b = audit_idx[bins[audit_idx] == b]
        if len(idx_b) == 0:
            continue
        p_obs = float(observed[idx_b].mean())
        if p_obs <= 0:
            # A stratum with no observed label cannot be reweighted; fall back
            # to the complete-case mean rather than silently dropping it.
            c = cost[mask]
            se = float(c.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
            return Estimate(float(c.mean()), se, n, float(n), 1.0)
        weights[idx_b[observed[idx_b]]] = 1.0 / p_obs

    total = float(weights.sum())
    if total <= 0:
        return Estimate(float("nan"), float("nan"), n, 0.0, float("nan"))
    value = float((weights * cost).sum() / total)
    se = float(np.sqrt((weights**2 * (cost - value) ** 2).sum()) / total)
    return Estimate(value, se, n, effective_sample_size(weights), float(weights.max()))


def evaluate_report(
    df: pd.DataFrame,
    candidate_actions: np.ndarray,
    propensity: PropensityEstimate,
    config: PilotConfig,
    *,
    feature_cols: list[str] | tuple[str, ...],
    seed: int | None = None,
    observation_assumption: str = "unknown",
    reliability_n_boot: int = 500,
    readiness: dict | None = None,
) -> tuple[dict, dict, dict, dict, dict, IdentificationReport]:
    """Return estimates, diagnostics, bounds, audit recommendation."""
    y = df["label"].fillna(0).astype(int).to_numpy()
    observed = df["label"].notna().to_numpy()
    amount = df["amount"].to_numpy(dtype=float)
    actions = df["action"].astype(str).to_numpy()
    in_pop = actions != "reject"
    rejected = ~in_pop
    e = propensity.e
    audit = (
        df["audit_flag"].fillna(0).astype(bool).to_numpy()
        if "audit_flag" in df.columns
        else np.zeros(len(df), dtype=bool)
    )

    cost = realized_cost(candidate_actions, y, amount, config.costs)
    identification = check_identification(
        actions=actions,
        candidate_actions=candidate_actions,
        observed=observed,
        propensity=e,
        cost=cost,
        positivity_ok=propensity.positivity_ok,
        propensity_source=propensity.source,
        has_audit=bool(audit.any()),
        observation_assumption=observation_assumption,
        calibration_ratio=float(
            propensity.details.get("calibration_ratio", float("nan"))
        ),
    )
    estimates: dict[str, dict] = {}

    def add(name: str, est: Estimate, target: str) -> None:
        estimates[name] = {
            "value": est.value,
            "se": est.se,
            "n_used": est.n_used,
            "ess": est.ess,
            "max_weight": est.max_weight,
            "target": target,
        }

    add("naive", naive(cost, observed), TARGET_P0)
    add("ipw_ht", ipw_ht(cost, observed, e, in_pop), TARGET_P0)
    add("ipw_hajek", ipw_hajek(cost, observed, e, in_pop), TARGET_P0)

    phat = None
    X, names = _features(df, feature_cols, "amount")
    if X is not None:
        phat = fit_outcome_model(
            X,
            y,
            observed,
            e,
            config.outcome_model,
            seed=int(seed if seed is not None else config.seed),
        )
        add(
            "dr",
            dr(
                cost, candidate_actions, amount, observed, e, in_pop, phat, config.costs
            ),
            TARGET_P0,
        )
    else:
        estimates["dr"] = {
            "value": float("nan"),
            "se": float("nan"),
            "n_used": 0,
            "ess": 0.0,
            "max_weight": float("nan"),
            "target": TARGET_P0,
        }

    audit = (
        df["audit_flag"].fillna(0).astype(bool).to_numpy()
        if "audit_flag" in df.columns
        else np.zeros(len(df), dtype=bool)
    )
    if "decision_time" in df.columns:
        dt = pd.to_datetime(df["decision_time"], errors="coerce")
        if dt.notna().any():
            followup = (dt.max() - dt).dt.days.to_numpy(dtype=float)
        else:
            followup = None
    else:
        followup = None
    add(
        "audit_only",
        _audit_estimate(cost, audit, observed, followup=followup),
        TARGET_APPROVED,
    )

    cost_incumbent = realized_cost(actions, y, amount, config.costs)
    if X is not None:
        comparison = compare_policies(
            cost,
            candidate_actions,
            cost_incumbent,
            actions,
            amount,
            observed,
            e,
            in_pop,
            phat,
            config.costs,
        )
    else:
        comparison = {
            "candidate_value": float("nan"),
            "incumbent_value": float("nan"),
            "difference": float("nan"),
            "difference_se": float("nan"),
            "difference_ci_low": float("nan"),
            "difference_ci_high": float("nan"),
            "p_candidate_better": float("nan"),
            "regret_candidate": float("nan"),
            "regret_incumbent": float("nan"),
            "decision": "not identified",
            "n_pop": int(in_pop.sum()),
            "n_observed": int(observed.sum()),
            "max_weight": float("nan"),
        }

    v_pop = estimates["dr"]["value"]
    if not np.isfinite(v_pop):
        v_pop = estimates["ipw_ht"]["value"]
    b = policy_bounds(
        candidate_actions,
        amount,
        config.costs,
        in_pop,
        rejected,
        v_pop,
        v_pop_se=(
            estimates["dr"]["se"]
            if np.isfinite(estimates["dr"]["se"])
            else estimates["ipw_ht"]["se"]
        ),
    )
    bounds = {
        "lower": b.lower,
        "upper": b.upper,
        "width": b.width,
        "lower_unconditional": b.lower_unconditional,
        "upper_unconditional": b.upper_unconditional,
        "width_unconditional": b.width_unconditional,
        "n_rejected": b.n_rejected,
        "v_pop": v_pop,
    }

    diagnostics = {
        "n": len(df),
        "p0_n": int(in_pop.sum()),
        "rejected_n": int(rejected.sum()),
        "observed_n": int(observed.sum()),
        "observed_fraction": float(observed.mean()),
        "action_counts": {
            a: int((actions == a).sum()) for a in ("approve", "review", "reject")
        },
        "candidate_action_counts": {
            a: int((candidate_actions == a).sum())
            for a in ("approve", "review", "reject")
        },
        "candidate_review_outside_p0": int(
            ((candidate_actions == "review") & rejected).sum()
        ),
        "candidate_approve_outside_p0": int(
            ((candidate_actions == "approve") & rejected).sum()
        ),
        "review_fraud_rate_observed": (
            float(y[(actions == "review") & observed].mean())
            if ((actions == "review") & observed).any()
            else float("nan")
        ),
        "approved_fraud_rate_observed": (
            float(y[(actions == "approve") & observed].mean())
            if ((actions == "approve") & observed).any()
            else float("nan")
        ),
        "propensity_source": propensity.source,
        "propensity_model": propensity.details.get("propensity_model"),
        "propensity_features": propensity.details.get("propensity_features", []),
        "positivity_ok": propensity.positivity_ok,
        "e_review": propensity.e_review,
        "e_approve": propensity.e_approve,
        "audit_rate_among_approved": propensity.audit_rate,
        "calibration_ratio": propensity.details.get("calibration_ratio", float("nan")),
        "expected_observed": propensity.details.get("expected_observed", float("nan")),
        "actual_observed": propensity.details.get("actual_observed", float("nan")),
        "e_min_observed": float(e[observed].min()) if observed.any() else float("nan"),
        "e_max_observed": float(e[observed].max()) if observed.any() else float("nan"),
        "frac_observed_e_lt_001": float((e[observed] < 0.01).mean())
        if observed.any()
        else float("nan"),
        "ess_ipw": estimates["ipw_ht"]["ess"],
        "max_weight_ipw": estimates["ipw_ht"]["max_weight"],
        "audit_only_method": (
            "post_stratified_by_followup" if followup is not None else "complete_case"
        ),
        "feature_names": names,
    }
    if observed.any():
        w_obs = 1.0 / e[observed]
        diagnostics["weight_p50"] = float(np.quantile(w_obs, 0.5))
        diagnostics["weight_p99"] = float(np.quantile(w_obs, 0.99))
        diagnostics["weight_max"] = float(w_obs.max())
    if "label_source" in df.columns:
        diagnostics["label_source_counts"] = {
            str(k): int(v) for k, v in df["label_source"].value_counts().items()
        }
    if "amount" in df.columns and len(df) >= 10:
        quintile = pd.qcut(df["amount"], 5, labels=False, duplicates="drop")
        for action in ("approve", "review"):
            mask = actions == action
            if mask.sum() < 10:
                continue
            rates = (
                df.loc[mask]
                .assign(_quintile=quintile[mask])
                .groupby("_quintile")["label"]
                .apply(lambda s: float(s.notna().mean()))
            )
            diagnostics[f"{action}_observed_rate_by_amount_quintile"] = [
                float(v) for v in rates.to_numpy()
            ]
    if "decision_time" in df.columns and "label_time" in df.columns:
        dec = pd.to_datetime(df["decision_time"], errors="coerce")
        lab = pd.to_datetime(df["label_time"], errors="coerce")
        delay = (lab - dec).dt.total_seconds() / 86400.0
        delay = delay[np.isfinite(delay)]
        if len(delay):
            diagnostics["label_delay_days"] = {
                "median": float(delay.median()),
                "p90": float(delay.quantile(0.9)),
                "n": len(delay),
            }
    if "segment" in df.columns:
        seg_values = df["segment"].astype("string").fillna("unknown")
        segment_diagnostics: dict[str, dict] = {}
        for name in sorted(seg_values.unique()):
            mask = (seg_values == name).to_numpy()
            n_seg = int(mask.sum())
            if n_seg < 50:
                segment_diagnostics[str(name)] = {
                    "n": n_seg,
                    "suppressed": True,
                }
                continue
            seg_actions = actions[mask]
            seg_observed = observed[mask]
            seg_y = y[mask]
            seg_candidate = candidate_actions[mask]
            observed_legit = seg_observed & (seg_y == 0)
            candidate_reject = seg_candidate == "reject"
            segment_diagnostics[str(name)] = {
                "n": n_seg,
                "suppressed": False,
                "incumbent_approve": int((seg_actions == "approve").sum()),
                "incumbent_review": int((seg_actions == "review").sum()),
                "incumbent_reject": int((seg_actions == "reject").sum()),
                "candidate_reject_share": float(candidate_reject.mean()),
                "candidate_change_share": float((seg_candidate != seg_actions).mean()),
                "observed_fraud_rate": (
                    float(seg_y[seg_observed].mean()) if seg_observed.any() else None
                ),
                "observed_legit_n": int(observed_legit.sum()),
                "candidate_false_reject_share": (
                    float(
                        (candidate_reject & observed_legit).sum() / observed_legit.sum()
                    )
                    if observed_legit.any()
                    else None
                ),
            }
        diagnostics["segment_diagnostics"] = segment_diagnostics

    audit_rec = _audit_recommendation(
        df,
        cost,
        observed,
        audit,
        config.costs,
        estimates,
        identified=identification.passed,
    )
    diagnostics["reliability"] = build_reliability(
        y=y,
        cost=cost,
        actions=actions,
        candidate_actions=candidate_actions,
        amount=amount,
        observed=observed,
        propensity=e,
        in_pop=in_pop,
        phat=phat,
        costs=config.costs,
        comparison=comparison,
        identification=identification,
        seed=int(seed if seed is not None else config.seed),
        n_boot=int(reliability_n_boot),
        propensity_source=propensity.source,
        propensity_model=str(propensity.details.get("propensity_model", "action")),
        readiness=readiness,
    )
    return estimates, diagnostics, bounds, audit_rec, comparison, identification


def _audit_recommendation(
    df: pd.DataFrame,
    cost: np.ndarray,
    observed: np.ndarray,
    audit: np.ndarray,
    costs: Costs,
    estimates: dict,
    *,
    identified: bool = True,
) -> dict:
    """Size a random post-hoc verification audit to the decision's effect size."""
    y = df["label"].fillna(0).astype(int).to_numpy()
    actions = df["action"].astype(str).to_numpy()
    approved = actions == "approve"
    p = (
        float(y[approved & observed].mean())
        if (approved & observed).any()
        else float("nan")
    )
    n_current = int(audit.sum())
    current_share = float(n_current / max(approved.sum(), 1))
    out = {
        "design": "random post-hoc verification of approved applications; shadow scoring; not random approvals/rejections",
        "current_audit_count": n_current,
        "current_audit_share_of_approved": current_share,
        "approved_fraud_rate_observed": p,
        "approved_n": int(approved.sum()),
    }
    if np.isfinite(p) and 0 < p < 1:
        targets = {}
        for rel in (0.20, 0.10):
            target_abs = rel * p
            n_needed = int(np.ceil(p * (1 - p) / (target_abs**2)))
            additional = max(0, n_needed - n_current)
            targets[f"rel_{int(rel * 100)}pct"] = {
                "target_relative_se": rel,
                "labels_needed": n_needed,
                "additional_labels": additional,
                "additional_review_cost": additional * float(costs.review_cost),
            }
        out["fraud_rate_targets"] = targets

    point = estimates.get("dr", {}).get("value", float("nan"))
    if not np.isfinite(point):
        point = estimates.get("ipw_ht", {}).get("value", float("nan"))
    if identified and np.isfinite(point) and observed.any():
        sd = float(cost[observed].std(ddof=1))
        target_abs = 0.05 * abs(point)
        if target_abs > 0:
            n_needed = int(np.ceil((sd**2) / (target_abs**2)))
            additional = max(0, n_needed - n_current)
            out["policy_value_target_5pct"] = {
                "labels_needed": n_needed,
                "additional_labels": additional,
                "additional_review_cost": additional * float(costs.review_cost),
            }
    return out


def _fmt(value, digits=6):
    if value is None:
        return "n/a"
    if isinstance(value, float) and not np.isfinite(value):
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_memo(
    result: ReportResult, path: Path, *, log_path: str, candidate_path: str
) -> None:
    L: list[str] = []
    L.append("# Onboarding Policy Change Memo")
    L.append("")
    L.append(
        "_Generated by `onboarding-audit report`. This is a measurement memo, "
        "not a production approval._"
    )
    L.append("")
    L.append("## 1. Decision")
    L.append("")
    L.append(f"- **Log:** `{log_path}`")
    L.append(f"- **Candidate:** `{candidate_path}`")
    L.append(f"- **Applications:** {result.n:,}")
    L.append(
        f"- **Identified population (`P0`, logging non-rejected):** {result.p0_n:,}"
    )
    L.append(f"- **Logging-rejected (outside `P0`):** {result.rejected_n:,}")
    L.append(
        f"- **Observed labels:** {result.observed_n:,} ({result.observed_n / max(result.n, 1):.1%})"
    )
    L.append(f"- **Logging actions:** {result.action_counts}")
    L.append(f"- **Candidate actions:** {result.candidate_action_counts}")
    outside_review = result.diagnostics.get("candidate_review_outside_p0", 0)
    outside_approve = result.diagnostics.get("candidate_approve_outside_p0", 0)
    outside = int(outside_review) + int(outside_approve)
    outside_share = outside / max(result.n, 1)
    L.append(
        f"- **Candidate actions on logging-rejected rows:** {outside:,} "
        f"({outside_share:.1%}) — outside the `P0` estimate"
    )
    profile = result.diagnostics.get("reliability", {}).get("profile", {})
    if profile:
        grade = str(profile.get("grade", "not available"))
        if grade.startswith(("A", "B")):
            release = "release for review/pilot; not production"
        elif grade.startswith("C"):
            release = "defer; collect more evidence"
        elif grade.startswith("D"):
            release = "refuse; not identified"
        else:
            release = "not available"
        L.append(f"- **Decision reliability:** **{grade}** — **{release}**")
    assumption_label = {
        "action": "action-dependent (declared)",
        "outcome": "outcome-dependent (declared)",
        "unknown": "not declared",
    }[result.identification.observation_assumption]
    L.append(f"- **Observation assumption:** {assumption_label}")
    L.append("")
    L.append("## 2. Estimate")
    L.append("")
    if not result.identification.passed:
        L.append(
            "**Not identified.** The log does not support a point estimate for "
            "the `P0` population."
        )
        L.append("")
        for reason in result.identification.reasons:
            L.append(f"- {reason}")
        if result.identification.warnings:
            L.append("")
            L.append("**Warnings:**")
            for warning in result.identification.warnings:
                L.append(f"- {warning}")
        L.append("")
        L.append(
            "Point estimates are withheld from this memo. The JSON retains the "
            "diagnostic estimates, but they are not a policy value."
        )
    else:
        L.append(
            "| Estimator | Target | Value | SE | 95% CI | n used | ESS | Max weight |"
        )
        L.append("|---|---|---:|---:|---|---:|---:|---:|")
        for name, est in result.estimates.items():
            value = est["value"]
            se = est["se"]
            if (
                isinstance(value, float)
                and np.isfinite(value)
                and isinstance(se, float)
                and np.isfinite(se)
            ):
                ci = f"[{value - 1.96 * se:.6f}, {value + 1.96 * se:.6f}]"
            else:
                ci = "n/a"
            L.append(
                f"| `{name}` | {est['target']} | {_fmt(value)} | {_fmt(se)} | {ci} | "
                f"{est['n_used']:,} | {_fmt(est['ess'], 0)} | {_fmt(est['max_weight'], 2)} |"
            )
        L.append("")
        L.append(
            "**Target note:** `P0` is the logging non-rejected population; `approved` "
            "is the **logging-approved** population (the audit sample), not the "
            "candidate's approved population; `full` is the reject-margin bounds "
            "target."
        )
        if "audit_only" in result.estimates:
            method = result.diagnostics.get("audit_only_method", "complete_case")
            if method == "post_stratified_by_followup":
                L.append(
                    "- **Audit-only method:** post-stratified by follow-up time "
                    "(5 bins), weighted by 1/P(observed) within each bin. It "
                    "assumes labels are missing at random within a bin. The pilot "
                    "uses the true per-row resolution probability, so the two are "
                    "close but not identical."
                )
            else:
                L.append(
                    "- **Audit-only caveat:** this report's audit-only estimate is "
                    "a complete-case mean over observed audit labels. Under delayed "
                    "labels it is biased toward early-resolving rows. The pilot's "
                    "audit-only estimator is resolution-weighted; they are not the "
                    "same estimator."
                )
        if result.identification.warnings:
            L.append("")
            L.append("**Warnings:**")
            for warning in result.identification.warnings:
                L.append(f"- {warning}")
    L.append("")
    L.append("### 2.1 Candidate vs incumbent (`P0`)")
    L.append("")
    comp = result.comparison
    if result.identification.passed and np.isfinite(comp["difference"]):
        L.append("| Quantity | Value |")
        L.append("|---|---:|")
        L.append(f"| Candidate `P0` value | {_fmt(comp['candidate_value'])} |")
        L.append(f"| Incumbent `P0` value | {_fmt(comp['incumbent_value'])} |")
        L.append(f"| Difference (candidate − incumbent) | {_fmt(comp['difference'])} |")
        L.append(
            f"| 95% interval | [{_fmt(comp['difference_ci_low'])}, "
            f"{_fmt(comp['difference_ci_high'])}] |"
        )
        L.append(f"| P(candidate cheaper) | {_fmt(comp['p_candidate_better'])} |")
        L.append(f"| Expected regret if candidate | {_fmt(comp['regret_candidate'])} |")
        L.append(f"| Expected regret if incumbent | {_fmt(comp['regret_incumbent'])} |")
        L.append(f"| **`P0`-conditional recommendation** | **{comp['decision']}** |")
        full = comp.get("full_policy", {})
        if full:
            L.append(
                f"| **Full-policy decision (including rejects)** | **{full['decision']}** |"
            )
        rel = result.diagnostics.get("reliability", {})
        profile = rel.get("profile", {})
        if profile:
            L.append(f"| **Decision reliability grade** | **{profile['grade']}** |")
        L.append("")
        if full:
            full_decision = str(full.get("decision", "not identified"))
            if comp["decision"] == "keep incumbent" and full_decision.startswith(
                "candidate cheaper"
            ):
                L.append(
                    "> **Warning:** the `P0`-conditional recommendation is to keep "
                    "the incumbent, but the full-policy bound favors the candidate. "
                    "The reject margin dominates; do not act on the `P0` "
                    "recommendation alone."
                )
                L.append("")
            elif comp["decision"] == "prefer candidate" and full_decision.startswith(
                "incumbent cheaper"
            ):
                L.append(
                    "> **Warning:** the `P0`-conditional recommendation favors the "
                    "candidate, but the full-policy bound favors the incumbent. "
                    "The reject margin dominates; do not act on the `P0` "
                    "recommendation alone."
                )
                L.append("")
            elif comp["decision"] in {"prefer candidate", "keep incumbent"} and (
                full_decision == "depends on the reject margin"
            ):
                L.append(
                    "> **Warning:** the `P0` recommendation is directional, but the "
                    "full-policy direction is not identified. Do not present it as "
                    "a full-policy decision."
                )
                L.append("")
        L.append(
            "Negative difference favors the candidate. The comparison is "
            "`P0`-conditional, uses the same observation model, and ignores "
            "nuisance-estimation uncertainty; it is not a production decision on "
            "its own. §4.1 reports whether the direction survives the unobserved "
            "reject margin."
        )
        power = comp.get("power", {})
        if power:
            L.append("")
            L.append("**Labels needed (approximate, 80% power):**")
            for key, target in power.items():
                L.append(
                    f"- `{key}`: **{target['labels_needed']:,}** labels "
                    f"({target['additional_labels']:,} additional) to detect a "
                    f"{target['delta']:.4f} difference."
                )
    else:
        L.append(
            "Not reported: `P0` is not identified, so a candidate-vs-incumbent "
            "comparison would be spurious."
        )
    L.append("")
    L.append("## 3. Diagnostics")
    L.append("")
    d = result.diagnostics
    L.append(
        f"- **Propensity source:** `{d['propensity_source']}`; "
        f"`e_review={d['e_review']:.3f}`, `e_approve={d['e_approve']:.3f}`, "
        f"audit rate among approved `{d['audit_rate_among_approved']:.3%}`."
    )
    cal = d.get("calibration_ratio")
    if cal is not None and isinstance(cal, float) and np.isfinite(cal):
        L.append(
            f"- **Propensity calibration:** observed/expected = **{cal:.3f}** "
            f"({d['actual_observed']:.0f} observed vs {d['expected_observed']:.0f} "
            "expected under the stated `e`). A value below 0.5 means the provided "
            "`e` may be too high or the labels heavily censored; a value above 1 "
            "is impossible under the stated `e`."
        )
    else:
        if d.get("propensity_source") != "provided":
            L.append(
                "- **Propensity calibration:** not computable from an estimated "
                "propensity; provide `e` or an audit-labeled sample."
            )
        else:
            L.append(
                "- **Propensity calibration:** not computable (the provided `e` does "
                "not cover every `P0` row)."
            )
    if d.get("propensity_model") == "covariate":
        L.append(
            f"- **Propensity model:** per-action logistic P(observed | action, X); "
            f"features: {', '.join(d.get('propensity_features', [])) or 'n/a'}."
        )
        L.append(
            "- **Propensity-model caveat:** the covariate model is only as good as "
            "the features and the overlap. Check the weight range and ESS; a "
            "heavy-tailed weight distribution undercovers the interval even when "
            "the point estimate is close."
        )
    if d["propensity_source"] == "provided":
        L.append(
            "- **Positivity:** "
            f"{'OK on observed P0 rows' if d['positivity_ok'] else 'FAILED - no point estimate'}; "
            "a structural zero on an unobserved row cannot be detected from a "
            "provided column."
        )
    else:
        L.append(
            f"- **Positivity:** {'OK on P0 rows' if d['positivity_ok'] else 'FAILED - no point estimate'}."
        )
    L.append(
        f"- **Observed propensity range:** [{_fmt(d['e_min_observed'])}, {_fmt(d['e_max_observed'])}]; "
        f"fraction with `e < 0.01`: {_fmt(d['frac_observed_e_lt_001'])}."
    )
    L.append(
        f"- **IPW effective sample size:** {_fmt(d['ess_ipw'], 0)}; "
        f"max weight {_fmt(d['max_weight_ipw'], 2)}."
    )
    if "weight_p99" in d:
        L.append(
            f"- **Weight distribution (observed rows):** median "
            f"{_fmt(d['weight_p50'], 1)}, p99 {_fmt(d['weight_p99'], 1)}, "
            f"max {_fmt(d['weight_max'], 1)}. Heavy tails mean the interval can "
            "undercover even when the point estimate is close."
        )
    L.append(
        f"- **Candidate review outside `P0`:** {d['candidate_review_outside_p0']:,}; "
        f"candidate approve outside `P0`: {d['candidate_approve_outside_p0']:,}. "
        "These rows are outside the primary estimand and enter only the bounds."
    )
    if "label_source_counts" in d:
        L.append(f"- **Label-source mix:** {d['label_source_counts']}.")
    for action in ("approve", "review"):
        key = f"{action}_observed_rate_by_amount_quintile"
        if key in d:
            rates = ", ".join(f"{v:.3f}" for v in d[key])
            L.append(
                f"- **{action.capitalize()} observation rate by amount quintile:** "
                f"[{rates}]. A strong gradient means action-level `e` is "
                "misspecified; use `--propensity-model covariate`."
            )
    if "label_delay_days" in d:
        L.append(
            f"- **Label delay (observed):** median {d['label_delay_days']['median']:.1f} days, "
            f"p90 {d['label_delay_days']['p90']:.1f} days."
        )
    if "segment_diagnostics" in d:
        L.append("")
        L.append("### 3.1 Segment diagnostic (observational)")
        L.append("")
        L.append(
            "| Segment | n | Incumbent A/R/J | Candidate reject | Candidate change | Observed fraud | Candidate false-reject (observed legit) |"
        )
        L.append("|---|---:|---|---:|---:|---:|---:|")
        for name, seg in d["segment_diagnostics"].items():
            if seg.get("suppressed"):
                L.append(
                    f"| `{name}` | {seg['n']:,} | suppressed | suppressed | "
                    "suppressed | suppressed | suppressed |"
                )
                continue
            fraud = seg.get("observed_fraud_rate")
            false_rej = seg.get("candidate_false_reject_share")
            prefix = (
                f"| `{name}` | {seg['n']:,} | "
                f"{seg['incumbent_approve']:,}/{seg['incumbent_review']:,}/"
                f"{seg['incumbent_reject']:,} | "
                f"{seg['candidate_reject_share']:.1%} | "
                f"{seg['candidate_change_share']:.1%} | "
            )
            if fraud is None or false_rej is None:
                L.append(prefix + "n/a | n/a |")
            else:
                L.append(prefix + f"{fraud:.1%} | {false_rej:.1%} |")
        L.append("")
        L.append(
            "Small segments (<50 rows) are suppressed. The rates are "
            "**descriptive**, not a fairness certification: logging-rejected "
            "applicants have no outcome, and the observed false-reject share is "
            "conditioned on the rows that were observed. Use this to decide "
            "whether a full segment audit is needed, not to clear the policy."
        )
    L.append("")
    L.append("## 4. Reject-margin bounds")
    L.append("")
    b = result.bounds
    L.append(f"- **Lower:** {_fmt(b['lower'])}")
    L.append(f"- **Upper:** {_fmt(b['upper'])}")
    L.append(f"- **Width:** {_fmt(b['width'])}")
    L.append(f"- **Logging-rejected rows:** {b['n_rejected']:,}")
    L.append("")
    if not result.identification.passed:
        L.append(
            "**Because `P0` is not identified, these bounds are diagnostic only.**"
        )
        L.append("")
    L.append(
        "These are **partial-identification intervals conditional on the `P0` "
        "estimate**, not confidence intervals. Do not interpret them as 95% "
        "coverage. If the reject margin is material and unobserved, report the "
        "bounds, not a point estimate."
    )
    L.append("")
    full = result.comparison.get("full_policy", {})
    if full and not result.identification.passed:
        L.append("### 4.1 Full-policy decision (candidate vs incumbent)")
        L.append("")
        L.append(
            "**Not identified.** The `P0` identification gate failed; the "
            "full-policy bound is diagnostic only and is not used for a decision."
        )
        full = {}
    if full:
        L.append("### 4.1 Full-policy decision (candidate vs incumbent)")
        L.append("")
        n_rej = int(full.get("n_rejected", 0))
        if n_rej == 0:
            L.append(
                "There are no logging-rejected rows in this log; the full-policy "
                "decision is the `P0` decision."
            )
        elif not np.isfinite(full.get("full_difference_lower", float("nan"))):
            L.append(
                "The full-policy difference is not identified because the `P0` "
                "difference is not identified."
            )
        else:
            lower = full["full_difference_lower"]
            upper = full["full_difference_upper"]
            L.append(
                f"- **Logging-rejected rows:** {n_rej:,} "
                f"({full['reject_share']:.1%} of the log)."
            )
            L.append(
                f"- **Full-policy difference (candidate − incumbent):** "
                f"[{_fmt(lower)}, {_fmt(upper)}] per application."
            )
            decision = str(full.get("decision", "not identified"))
            if decision.startswith("candidate cheaper for any"):
                reading = (
                    "The candidate is cheaper even if every rejected outcome is "
                    "adversarial. The `P0` recommendation is robust to the reject "
                    "margin."
                )
            elif decision.startswith("incumbent cheaper for any"):
                reading = (
                    "The incumbent is cheaper even under the most favorable "
                    "rejected outcomes. The `P0` recommendation does **not** "
                    "survive the reject margin."
                )
            elif decision == "P0 inconclusive":
                reading = (
                    "The full-policy interval includes zero because the `P0` "
                    "estimate is uncertain; the reject margin does not flip the "
                    "sign at the `P0` point estimate. Collect more `P0` labels "
                    "or report an inconclusive decision."
                )
            else:
                reading = (
                    "The direction depends on the unobserved reject margin. The "
                    "`P0` recommendation alone is not a full-policy decision."
                )
            L.append(f"- **Interpretation:** {reading}")
            p_star = full.get("breakeven_reject_fraud_rate", float("nan"))
            if np.isfinite(p_star):
                slope = (
                    full["reject_difference_if_fraud"]
                    - full["reject_difference_if_legit"]
                )
                if 0.0 < p_star < 1.0:
                    side = "below" if slope > 0 else "above"
                    L.append(
                        f"- **Break-even:** under a common fraud rate `p` among "
                        f"logging-rejected rows, the candidate is cheaper when "
                        f"`p` is **{side} {p_star:.1%}**. This is a sensitivity "
                        "threshold, not an estimate."
                    )
                    lo = full.get("breakeven_low", float("nan"))
                    hi = full.get("breakeven_high", float("nan"))
                    if np.isfinite(lo) and np.isfinite(hi):
                        L.append(
                            f"- **Break-even interval from the `P0` 95% "
                            f"interval:** [{lo:.1%}, {hi:.1%}]."
                        )
                else:
                    L.append(
                        "- **Break-even:** the homogeneous-p threshold lies "
                        "outside `[0, 1]`; the reject margin still leaves the "
                        "direction unidentified."
                    )
            ref_review = d.get("review_fraud_rate_observed", float("nan"))
            ref_approved = d.get("approved_fraud_rate_observed", float("nan"))
            if np.isfinite(ref_review) and np.isfinite(ref_approved):
                suffix = (
                    "the break-even is a threshold for the risk team to judge, "
                    "not a prior."
                    if np.isfinite(p_star) and 0.0 < p_star < 1.0
                    else "they are not a prior for the rejected population."
                )
                L.append(
                    f"- **Reference rates:** observed fraud is {ref_review:.2%} "
                    f"among reviewed applications and {ref_approved:.2%} among "
                    "observed approved applications. Rejected applicants are not "
                    f"a random sample of either; {suffix}"
                )
            L.append(
                "- **Method:** per-row worst/best case over the two possible "
                "outcomes of each rejected application. The sharp bound needs no "
                "assumption about the rejected fraud rate; the break-even adds a "
                "common-rate assumption for interpretation."
            )
    rel = result.diagnostics.get("reliability", {})
    profile = rel.get("profile", {})
    if profile:
        L.append("")
        L.append("### 4.2 Decision reliability profile")
        L.append("")
        L.append(
            "The point estimate is not the product. This profile separates the "
            "dimensions that determine whether the decision is reliable."
        )
        L.append("")
        L.append("| Dimension | Status | Evidence |")
        L.append("|---|---|---|")
        labels = {
            "identification": "Identification",
            "statistical_stability": "Statistical stability",
            "structural_reject_margin": "Full-policy / reject margin",
            "model_calibration": "Model calibration",
            "cost_stress": "Cost stress",
            "operational_readiness": "Operational readiness",
        }
        for key, label in labels.items():
            dim = profile.get("dimensions", {}).get(key)
            if not dim:
                continue
            L.append(f"| {label} | **{dim['status']}** | {dim['evidence']} |")
        L.append("")
        L.append(f"**Overall grade:** **{profile['grade']}**")
        L.append("")
        grade = str(profile.get("grade", ""))
        if grade.startswith("A"):
            reading = (
                "The P0 decision is stable across the measured dimensions. The "
                "observation model, cost matrix, and audit design remain "
                "assumptions."
            )
        elif grade.startswith("B"):
            reading = (
                "The P0 decision is credible but has at least one caveat. Read "
                "the dimensions before acting; the full-policy reject margin is "
                "usually the binding caveat."
            )
        elif grade.startswith("C"):
            reading = (
                "Do not treat this as a decision-grade P0 recommendation. "
                "Collect more evidence: labels, an audit, a cost agreement, or a "
                "tighter observation model."
            )
        else:
            reading = "The log does not support a decision-grade estimate."
        L.append(reading)
        if profile.get("reasons"):
            L.append("")
            L.append("**Why this grade:**")
            for reason in profile["reasons"]:
                L.append(f"- {reason}")
        L.append("")
        L.append(
            "_This profile is a decision aid, not a certification. It measures "
            "stability under the stated assumptions; it does not prove them._"
        )
    L.append("")
    L.append("## 5. Audit recommendation")
    L.append("")
    a = result.audit
    L.append(f"- **Design:** {a['design']}.")
    L.append(
        f"- **Current audit:** {a['current_audit_count']:,} labels "
        f"({a['current_audit_share_of_approved']:.2%} of approved)."
    )
    L.append(
        f"- **Observed approved fraud rate:** {_fmt(a['approved_fraud_rate_observed'])}."
    )
    if "fraud_rate_targets" in a:
        for key, t in a["fraud_rate_targets"].items():
            L.append(
                f"- **{key}:** {t['labels_needed']:,} labels needed; "
                f"{t['additional_labels']:,} additional; "
                f"additional review cost {t['additional_review_cost']:.2f} cost units."
            )
    if "policy_value_target_5pct" in a and result.identification.passed:
        t = a["policy_value_target_5pct"]
        L.append(
            f"- **Policy value, 5% relative SE:** {t['labels_needed']:,} labels; "
            f"{t['additional_labels']:,} additional; "
            f"additional review cost {t['additional_review_cost']:.2f} cost units."
        )
    elif not result.identification.passed:
        L.append(
            "- **Policy-value precision:** not reported because `P0` is not identified."
        )
    L.append("")
    L.append("## 6. Claim ledger")
    L.append("")
    L.append("| Claim | Status | Evidence |")
    L.append("|---|---|---|")
    if result.identification.passed:
        calibration_flagged = bool(
            result.identification.metrics.get("calibration_flagged", 0.0)
        )
        if calibration_flagged:
            status = "Measured (propensity calibration flagged)"
        elif result.identification.observation_assumption == "action":
            status = "Measured"
        else:
            status = "Measured (observation assumption unverified)"
        L.append(
            f"| `P0`-conditional policy value is estimated | {status} | `{result.report_path}` |"
        )
    else:
        L.append(
            "| `P0`-conditional policy value | **Not identified** | see §2 reasons |"
        )
    L.append(
        "| Full-policy value including logging-rejected rows | **Not identified** | bounds only; see §4 |"
    )
    if full:
        full_decision = str(full.get("decision", "not identified"))
        if full_decision.endswith("for any reject outcome"):
            full_status = "Derived (direction robust to the reject margin)"
        elif full_decision == "depends on the reject margin":
            full_status = "Derived (depends on the reject margin)"
        elif full_decision == "P0 inconclusive":
            full_status = "Derived (P0 inconclusive)"
        elif full_decision in {"candidate cheaper", "incumbent cheaper"}:
            full_status = f"Derived ({full_decision})"
        elif full_decision == "inconclusive":
            full_status = "Derived (inconclusive)"
        else:
            full_status = "Derived (not identified)"
        L.append(
            f"| Full-policy difference (candidate − incumbent) | {full_status} | §4.1 |"
        )
    L.append(
        f"| Propensities are `{d['propensity_source']}` | Assumed | log's audit/observation design |"
    )
    L.append("| Reject margin is point-identified | **Not claimed** | bounds only |")
    if "segment_diagnostics" in d:
        L.append(
            "| Segment diagnostic is a fairness certification | **Not claimed** | "
            "descriptive only; see §3.1 |"
        )
    if profile:
        L.append(
            "| Decision reliability profile is a certification | **Not claimed** | "
            "decision aid; see §4.2 |"
        )
    L.append(
        "| The candidate is better in production | **Not claimed** | no head-to-head experiment; this is a value estimate |"
    )
    L.append("")
    L.append("## 7. What would change the estimate")
    L.append("")
    L.append(
        "- **Overlap:** if the candidate explores regions the logging policy never labeled, the estimate is driven by the audit/outcome model, not the log."
    )
    L.append(
        "- **Label maturity/delay:** unresolved labels are not negatives; a later cutoff can change the estimate."
    )
    L.append(
        "- **Unmeasured confounding:** if reviewers use unlogged information, the observation model is incomplete."
    )
    L.append(
        "- **Cost assumptions:** the cost matrix is a configurable assumption; a different false-reject or review cost can change the ranking."
    )
    L.append(
        "- **Inclusion:** the false-rejection rate and the affected segments should be reviewed separately."
    )
    L.append("")
    L.append("## 8. Limitations")
    L.append("")
    L.append(
        "- This memo uses the log's observed labels and the configured propensity source; it does not prove the observation model is correct."
    )
    L.append("- The reject margin is bounded, not point-identified.")
    L.append("- The audit design is a recommendation and requires legal/risk review.")
    L.append("- This is not a production approval or a causal deployment claim.")
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


def run_report(
    log_path: Path | str,
    candidate_path: Path | str,
    config_path: Path | str,
    out_dir: Path | str,
    *,
    capacity: float = 0.02,
    feature_cols: list[str] | tuple[str, ...] | None = None,
    propensity_col: str = "propensity",
    audit_col: str = "audit_flag",
    propensity_model: str = "action",
    propensity_features: list[str] | tuple[str, ...] | None = None,
    observation_assumption: str = "unknown",
    seed: int | None = None,
    reliability_n_boot: int = 500,
) -> ReportResult:
    log_path = Path(log_path)
    candidate_path = Path(candidate_path)
    config = load_config(config_path)
    out_dir = Path(out_dir)
    if not 0.0 < capacity <= 1.0:
        raise ValueError("capacity must be in (0, 1]")
    if propensity_model not in {"action", "covariate"}:
        raise ValueError("propensity_model must be 'action' or 'covariate'")
    if observation_assumption not in {"action", "outcome", "unknown"}:
        raise ValueError(
            "observation_assumption must be 'action', 'outcome', or 'unknown'"
        )

    df = _read(log_path)
    report = validate_log(df)
    if not report.ok:
        raise ValueError("invalid log:\n" + "\n".join(report.errors))
    candidate = _read(candidate_path)

    features = (
        list(feature_cols)
        if feature_cols is not None
        else list(config.outcome_features)
    )
    propensity = estimate_propensities(
        df,
        propensity_col=propensity_col,
        audit_col=audit_col,
        propensity_model=propensity_model,
        feature_cols=(
            list(propensity_features) if propensity_features is not None else features
        ),
        amount_col="amount",
        seed=seed,
    )
    candidate_actions = _candidate_actions(df, candidate, config.costs, capacity)
    estimates, diagnostics, bounds, audit, comparison, identification = evaluate_report(
        df,
        candidate_actions,
        propensity,
        config,
        feature_cols=features,
        seed=seed,
        observation_assumption=observation_assumption,
        reliability_n_boot=reliability_n_boot,
        readiness=report.reliability_readiness,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    result = ReportResult(
        n=len(df),
        p0_n=diagnostics["p0_n"],
        rejected_n=diagnostics["rejected_n"],
        observed_n=diagnostics["observed_n"],
        action_counts=diagnostics["action_counts"],
        candidate_action_counts=diagnostics["candidate_action_counts"],
        propensity=propensity,
        identification=identification,
        estimates=estimates,
        diagnostics=diagnostics,
        bounds=bounds,
        audit=audit,
        comparison=comparison,
        memo_path=str(out_dir / "report.md"),
        report_path=str(out_dir / "report.json"),
    )
    payload = {
        "result": {
            "n": result.n,
            "p0_n": result.p0_n,
            "rejected_n": result.rejected_n,
            "observed_n": result.observed_n,
            "action_counts": result.action_counts,
            "candidate_action_counts": result.candidate_action_counts,
            "identification": result.identification.to_dict(),
            "estimates": estimates,
            "diagnostics": diagnostics,
            "bounds": bounds,
            "audit": audit,
            "comparison": comparison,
        },
        "inputs": {
            "log": str(log_path),
            "candidate": str(candidate_path),
            "config": str(config_path),
            "capacity": capacity,
            "observation_assumption": observation_assumption,
            "features": features,
        },
    }
    (out_dir / "report.json").write_text(
        json.dumps(_clean(payload), indent=2), encoding="utf-8"
    )
    write_memo(
        result,
        out_dir / "report.md",
        log_path=str(log_path),
        candidate_path=str(candidate_path),
    )
    return result
