"""Pilot metrics: bias, RMSE, coverage, ranking, bounds."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

RANKED_ESTIMATORS = ("naive", "ipw_ht", "ipw_hajek", "dr")


def pairwise_inversions(est: np.ndarray, true: np.ndarray) -> int:
    count = 0
    for i in range(len(est)):
        for j in range(i + 1, len(est)):
            if (est[i] - est[j]) * (true[i] - true[j]) < 0:
                count += 1
    return count


def summarize(rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    for keys, part in rows.groupby(["scenario", "policy", "estimator"]):
        scenario, policy, estimator = keys
        true = float(part["true_target"].mean())
        values = part["value"].to_numpy(dtype=float)
        se = part["se"].to_numpy(dtype=float)
        bias = float(values.mean() - true)
        rel = bias / true if abs(true) > 1e-12 else float("nan")
        rmse = float(np.sqrt(np.mean((values - part["true_target"].to_numpy()) ** 2)))
        target = (
            "approved"
            if estimator == "audit_only"
            else "full"
            if estimator == "bounds"
            else "P0"
        )
        if estimator == "bounds":
            cov = float("nan")
        else:
            cov = float(
                np.mean(np.abs(values - part["true_target"].to_numpy()) <= 1.96 * se)
            )
        se_valid = se[np.isfinite(se)]
        mw = part["max_weight"].to_numpy(dtype=float)
        mw = mw[np.isfinite(mw)]
        out.append(
            {
                "scenario": scenario,
                "policy": policy,
                "estimator": estimator,
                "target": target,
                "reps": len(part),
                "true": true,
                "estimate": float(values.mean()),
                "bias": bias,
                "rel_bias": rel,
                "rmse": rmse,
                "coverage": cov,
                "mean_se": float(se_valid.mean()) if len(se_valid) else float("nan"),
                "mc_se": float(values.std(ddof=1) / np.sqrt(len(part)))
                if len(part) > 1
                else float("nan"),
                "mean_ess": float(part["ess"].mean()),
                "mean_max_weight": float(mw.mean()) if len(mw) else float("nan"),
            }
        )
    return pd.DataFrame(out)


def ranking_metrics(rows: pd.DataFrame) -> pd.DataFrame:
    df = rows[rows["estimator"].isin(RANKED_ESTIMATORS)].copy()
    out = []
    for keys, part in df.groupby(["scenario", "estimator", "rep"]):
        scenario, estimator, rep = keys
        part = part.sort_values("policy")
        est = part["value"].to_numpy(dtype=float)
        true = part["true_p0"].to_numpy(dtype=float)
        if len(part) < 2 or not np.isfinite(est).all():
            continue
        rho = spearmanr(est, true).statistic
        if not np.isfinite(rho):
            rho = 0.0
        inv = pairwise_inversions(est, true)
        est_best = int(np.argmin(est))
        true_best = int(np.argmin(true))
        out.append(
            {
                "scenario": scenario,
                "estimator": estimator,
                "rep": rep,
                "spearman": float(rho),
                "inversions": inv,
                "p_best": float(est_best == true_best),
                "cost_misrank": float(true[est_best] - true[true_best]),
            }
        )
    if not out:
        return pd.DataFrame()
    raw = pd.DataFrame(out)
    agg = (
        raw.groupby(["scenario", "estimator"])
        .agg(
            reps=("rep", "count"),
            mean_spearman=("spearman", "mean"),
            mean_inversions=("inversions", "mean"),
            p_select_true_best=("p_best", "mean"),
            mean_cost_misrank=("cost_misrank", "mean"),
            max_cost_misrank=("cost_misrank", "max"),
        )
        .reset_index()
    )
    return agg


def bounds_summary(rows: pd.DataFrame) -> pd.DataFrame:
    df = rows[rows["estimator"] == "bounds"].copy()
    if df.empty:
        return pd.DataFrame()
    out = []
    for keys, part in df.groupby(["scenario", "policy"]):
        scenario, policy = keys
        true_full = part["true_full"].to_numpy(dtype=float)
        lower = part["lower"].to_numpy(dtype=float)
        upper = part["upper"].to_numpy(dtype=float)
        out.append(
            {
                "scenario": scenario,
                "policy": policy,
                "reps": len(part),
                "lower": float(np.nanmean(lower)),
                "upper": float(np.nanmean(upper)),
                "width": float(np.nanmean(upper - lower)),
                "coverage_full": float(
                    np.nanmean((lower <= true_full) & (true_full <= upper))
                ),
                "true_full": float(np.nanmean(true_full)),
                "n_rejected": int(part["n_rejected"].mean()),
            }
        )
    return pd.DataFrame(out)


def verdict(
    summary: pd.DataFrame,
    ranking: pd.DataFrame,
    bounds: pd.DataFrame,
    *,
    scenario: str = "main",
) -> dict:
    """Compute the pre-registered H1-H6 checks from the pilot output."""
    main = summary[summary["scenario"] == scenario]
    naive = main[main["estimator"] == "naive"]
    max_naive_rel = (
        float(naive["rel_bias"].abs().max()) if not naive.empty else float("nan")
    )
    rank = ranking[
        (ranking["scenario"] == scenario) & (ranking["estimator"] == "naive")
    ]
    inversions = (
        float(rank["mean_inversions"].max()) if not rank.empty else float("nan")
    )

    h1 = bool(np.isfinite(max_naive_rel) and max_naive_rel > 0.05)
    h2 = bool(np.isfinite(inversions) and inversions > 0)

    # H3 is a P0 claim: IPW/DR only. Audit-only targets the approved population
    # and is reported separately.
    corrected = main[main["estimator"].isin(("ipw_ht", "ipw_hajek", "dr"))]
    stats = []
    for estimator, part in corrected.groupby("estimator"):
        finite = part[np.isfinite(part["rel_bias"]) & np.isfinite(part["coverage"])]
        if finite.empty:
            continue
        stats.append(
            {
                "estimator": estimator,
                "max_abs_rel_bias": float(finite["rel_bias"].abs().max()),
                "mean_coverage": float(finite["coverage"].mean()),
                "n_policies": int(len(finite)),
            }
        )
    credible = [
        s for s in stats if s["max_abs_rel_bias"] <= 0.05 and s["mean_coverage"] >= 0.80
    ]
    h3 = bool(credible)
    best = min(stats, key=lambda s: s["max_abs_rel_bias"]) if stats else None

    b = bounds[bounds["scenario"] == scenario] if not bounds.empty else pd.DataFrame()
    h5 = bool((not b.empty) and (b["width"] > 0.05 * b["true_full"].abs()).any())

    audit = summary[
        summary["scenario"].isin(("audit_0", "audit_2"))
        & summary["estimator"].isin(("ipw_ht", "dr"))
    ]
    h4_details = {}
    h4 = False
    for estimator, part in audit.groupby("estimator"):
        a0 = part[part["scenario"] == "audit_0"]
        a2 = part[part["scenario"] == "audit_2"]
        if not a0.empty and not a2.empty:
            rmse_0 = float(a0["rmse"].mean())
            rmse_2 = float(a2["rmse"].mean())
            ess_0 = float(a0["mean_ess"].mean())
            ess_2 = float(a2["mean_ess"].mean())
            improved = bool(rmse_2 < rmse_0 and ess_2 > ess_0)
            h4_details[estimator] = {
                "rmse_0": rmse_0,
                "rmse_2": rmse_2,
                "ess_0": ess_0,
                "ess_2": ess_2,
                "improved": improved,
            }
            h4 = h4 or improved

    od = summary[summary["scenario"] == "outcome_dependent"]
    od_ao = od[od["estimator"] == "audit_only"]
    od_ipw = od[od["estimator"] == "ipw_ht"]
    od_dr = od[od["estimator"] == "dr"]
    ao_max = float(od_ao["rel_bias"].abs().max()) if not od_ao.empty else float("nan")
    ipw_max = (
        float(od_ipw["rel_bias"].abs().max()) if not od_ipw.empty else float("nan")
    )
    dr_max = float(od_dr["rel_bias"].abs().max()) if not od_dr.empty else float("nan")
    h6 = bool(
        np.isfinite(ao_max)
        and np.isfinite(ipw_max)
        and ao_max <= 0.05
        and ipw_max > 0.05
    )

    return {
        "H1_naive_bias_gt_5pct": h1,
        "H1_max_abs_rel_bias": max_naive_rel,
        "H2_rank_inversion": h2,
        "H2_max_mean_inversions": inversions,
        "H3_correction_credible": h3,
        "H3_estimator_stats": stats,
        "H3_best_estimator": best,
        "H4_audit_value": h4,
        "H4_details": h4_details,
        "H5_reject_margin_not_identified": h5,
        "H5_max_bounds_width": float(b["width"].max()) if not b.empty else float("nan"),
        "H6_outcome_dependent": h6,
        "H6_audit_max_abs_rel_bias": ao_max,
        "H6_ipw_max_abs_rel_bias": ipw_max,
        "H6_dr_max_abs_rel_bias": dr_max,
    }
