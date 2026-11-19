"""Arbitrary-log report: evaluate a candidate onboarding policy from a log.

This is the v0.2 product surface. It reuses the pilot estimators but takes a
team's own decision log and a candidate score file. It does not simulate
anything: propensities come from the log (provided or estimated), labels are the
observed labels, and the reject margin is bounded.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .config import Costs, OutcomeModel, PilotConfig, load_config
from .estimators import (
    Estimate,
    dr,
    fit_outcome_model,
    ipw_hajek,
    ipw_ht,
    naive,
    policy_bounds,
)
from .policies import apply_capacity, choose_actions, realized_cost
from .schema import validate_log

TARGET_P0 = "P0"
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
    estimates: dict
    diagnostics: dict
    bounds: dict
    audit: dict
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
) -> PropensityEstimate:
    """Use a provided propensity when complete for observed rows; else estimate.

    The estimate is action-level:
      e_review  = observed / reviewed
      e_approve = audit_rate + (1 - audit_rate) * observed / (approved, not audited)

    The audit-aware form separates the random audit from the base approve-label
    rate. If no audit flag is present, e_approve is the observed approve rate.
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

    provided = (
        propensity_col in df.columns
        and observed.any()
        and df.loc[observed, propensity_col].notna().all()
    )
    if provided:
        e = np.zeros(len(df), dtype=float)
        e[observed] = df.loc[observed, propensity_col].astype(float).to_numpy()
        e_review = float(e[review].mean()) if review.any() else 0.0
        e_approve = float(e[approve].mean()) if approve.any() else 0.0
        source = "provided"
    else:
        e_review = float(observed[review].mean()) if review.any() else 0.0
        if approve.any():
            non_audit = approve & ~audit
            base = float(observed[non_audit].mean()) if non_audit.any() else 0.0
            e_approve = audit_rate + (1.0 - audit_rate) * base
        else:
            e_approve = 0.0
        e = np.zeros(len(df), dtype=float)
        e[review] = e_review
        e[approve] = e_approve
        source = "estimated"

    if provided:
        positivity_ok = bool(observed.any() and (e[observed] > 0).all())
    else:
        in_pop = ~reject
        positivity_ok = bool(in_pop.any() and (e[in_pop] > 0).all())
    details = {
        "n_review": int(review.sum()),
        "n_approve": int(approve.sum()),
        "n_reject": int(reject.sum()),
        "n_observed_review": int((review & observed).sum()),
        "n_observed_approve": int((approve & observed).sum()),
        "n_audit": int(audit.sum()),
        "audit_rate_among_approved": audit_rate,
        "provided_propensity": provided,
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
) -> Estimate:
    mask = audit & observed
    n = int(mask.sum())
    if n == 0:
        return Estimate(float("nan"), float("nan"), 0, 0.0, float("nan"))
    c = cost[mask]
    se = float(c.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return Estimate(float(c.mean()), se, n, float(n), 1.0)


def evaluate_report(
    df: pd.DataFrame,
    candidate_actions: np.ndarray,
    propensity: PropensityEstimate,
    config: PilotConfig,
    *,
    feature_cols: list[str] | tuple[str, ...],
    seed: int | None = None,
) -> tuple[dict, dict, dict, dict]:
    """Return estimates, diagnostics, bounds, audit recommendation."""
    y = df["label"].fillna(0).astype(int).to_numpy()
    observed = df["label"].notna().to_numpy()
    amount = df["amount"].to_numpy(dtype=float)
    actions = df["action"].astype(str).to_numpy()
    in_pop = actions != "reject"
    rejected = ~in_pop
    e = propensity.e

    cost = realized_cost(candidate_actions, y, amount, config.costs)
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
    add("audit_only", _audit_estimate(cost, audit, observed), TARGET_APPROVED)

    v_pop = estimates["dr"]["value"]
    if not np.isfinite(v_pop):
        v_pop = estimates["ipw_ht"]["value"]
    b = policy_bounds(candidate_actions, amount, config.costs, in_pop, rejected, v_pop)
    bounds = {
        "lower": b.lower,
        "upper": b.upper,
        "width": b.width,
        "n_rejected": b.n_rejected,
        "v_pop": v_pop,
    }

    diagnostics = {
        "n": int(len(df)),
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
        "propensity_source": propensity.source,
        "positivity_ok": propensity.positivity_ok,
        "e_review": propensity.e_review,
        "e_approve": propensity.e_approve,
        "audit_rate_among_approved": propensity.audit_rate,
        "e_min_observed": float(e[observed].min()) if observed.any() else float("nan"),
        "e_max_observed": float(e[observed].max()) if observed.any() else float("nan"),
        "frac_observed_e_lt_001": float((e[observed] < 0.01).mean())
        if observed.any()
        else float("nan"),
        "ess_ipw": estimates["ipw_ht"]["ess"],
        "max_weight_ipw": estimates["ipw_ht"]["max_weight"],
        "feature_names": names,
    }
    if "label_source" in df.columns:
        diagnostics["label_source_counts"] = {
            str(k): int(v) for k, v in df["label_source"].value_counts().items()
        }
    if "decision_time" in df.columns and "label_time" in df.columns:
        dec = pd.to_datetime(df["decision_time"], errors="coerce")
        lab = pd.to_datetime(df["label_time"], errors="coerce")
        delay = (lab - dec).dt.total_seconds() / 86400.0
        delay = delay[np.isfinite(delay)]
        if len(delay):
            diagnostics["label_delay_days"] = {
                "median": float(delay.median()),
                "p90": float(delay.quantile(0.9)),
                "n": int(len(delay)),
            }

    audit_rec = _audit_recommendation(
        df, cost, observed, audit, config.costs, estimates
    )
    return estimates, diagnostics, bounds, audit_rec


def _audit_recommendation(
    df: pd.DataFrame,
    cost: np.ndarray,
    observed: np.ndarray,
    audit: np.ndarray,
    costs: Costs,
    estimates: dict,
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
    if np.isfinite(point) and observed.any():
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
    L.append("")
    L.append("## 2. Estimate")
    L.append("")
    L.append("| Estimator | Target | Value | SE | 95% CI | n used | ESS | Max weight |")
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
        "**Target note:** `P0` is the logging non-rejected population; `approved` is "
        "the audit-only target; `full` is the reject-margin bounds target."
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
    L.append(
        f"- **Positivity:** {'OK' if d['positivity_ok'] else 'FAILED — no point estimate'}."
    )
    L.append(
        f"- **Observed propensity range:** [{_fmt(d['e_min_observed'])}, {_fmt(d['e_max_observed'])}]; "
        f"fraction with `e < 0.01`: {_fmt(d['frac_observed_e_lt_001'])}."
    )
    L.append(
        f"- **IPW effective sample size:** {_fmt(d['ess_ipw'], 0)}; "
        f"max weight {_fmt(d['max_weight_ipw'], 2)}."
    )
    L.append(
        f"- **Candidate review outside `P0`:** {d['candidate_review_outside_p0']:,}; "
        f"candidate approve outside `P0`: {d['candidate_approve_outside_p0']:,}. "
        "These rows are outside the primary estimand and enter only the bounds."
    )
    if "label_source_counts" in d:
        L.append(f"- **Label-source mix:** {d['label_source_counts']}.")
    if "label_delay_days" in d:
        L.append(
            f"- **Label delay (observed):** median {d['label_delay_days']['median']:.1f} days, "
            f"p90 {d['label_delay_days']['p90']:.1f} days."
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
    L.append(
        "These are **partial-identification intervals conditional on the `P0` "
        "estimate**, not confidence intervals. Do not interpret them as 95% "
        "coverage. If the reject margin is material and unobserved, report the "
        "bounds, not a point estimate."
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
    if "policy_value_target_5pct" in a:
        t = a["policy_value_target_5pct"]
        L.append(
            f"- **Policy value, 5% relative SE:** {t['labels_needed']:,} labels; "
            f"{t['additional_labels']:,} additional; "
            f"additional review cost {t['additional_review_cost']:.2f} cost units."
        )
    L.append("")
    L.append("## 6. Claim ledger")
    L.append("")
    L.append("| Claim | Status | Evidence |")
    L.append("|---|---|---|")
    L.append(f"| `P0` policy value is estimated | Measured | `{result.report_path}` |")
    L.append(
        f"| Propensities are `{d['propensity_source']}` | Assumed | log's audit/observation design |"
    )
    L.append("| Reject margin is point-identified | **Not claimed** | bounds only |")
    L.append(
        "| The candidate is better than the incumbent | **Not claimed** | no head-to-head experiment; this is a value estimate |"
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
    seed: int | None = None,
) -> ReportResult:
    log_path = Path(log_path)
    candidate_path = Path(candidate_path)
    config = load_config(config_path)
    out_dir = Path(out_dir)
    if not 0.0 < capacity <= 1.0:
        raise ValueError("capacity must be in (0, 1]")

    df = _read(log_path)
    report = validate_log(df)
    if not report.ok:
        raise ValueError("invalid log:\n" + "\n".join(report.errors))
    candidate = _read(candidate_path)

    propensity = estimate_propensities(
        df, propensity_col=propensity_col, audit_col=audit_col
    )
    candidate_actions = _candidate_actions(df, candidate, config.costs, capacity)
    features = (
        list(feature_cols)
        if feature_cols is not None
        else list(config.outcome_features)
    )
    estimates, diagnostics, bounds, audit = evaluate_report(
        df,
        candidate_actions,
        propensity,
        config,
        feature_cols=features,
        seed=seed,
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
        estimates=estimates,
        diagnostics=diagnostics,
        bounds=bounds,
        audit=audit,
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
            "estimates": estimates,
            "diagnostics": diagnostics,
            "bounds": bounds,
            "audit": audit,
        },
        "inputs": {
            "log": str(log_path),
            "candidate": str(candidate_path),
            "config": str(config_path),
            "capacity": capacity,
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
