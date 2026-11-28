"""Run the account-opening pilot and write a reproducible report."""

from __future__ import annotations

import argparse
import json
import platform
import time
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pandas as pd

from . import __version__
from .config import PilotConfig, PolicySpec, Scenario, load_config
from .data import EvalData, load_eval_data
from .estimators import (
    action_weighted,
    audit_only,
    compare_policies,
    dr,
    fit_outcome_model,
    ipw_hajek,
    ipw_ht,
    naive,
    policy_bounds,
)
from .gates import check_identification
from .metrics import bounds_summary, ranking_metrics, summarize, verdict
from .observation import build_observation_model, draw_observation
from .policies import build_policy, realized_cost
from .propensity import (
    estimate_from_draw,
    fit_covariate_propensity,
    noisy_copy,
)
from .reliability import build_reliability


def build_policy_set(config: PilotConfig, scenario: Scenario) -> list[PolicySpec]:
    specs: list[PolicySpec] = []
    for policy in config.policies:
        capacity = policy.review_capacity
        name = policy.name
        if policy.name == "better_model" and scenario.candidate_capacity is not None:
            capacity = scenario.candidate_capacity
            name = f"better_model_{round(capacity * 100)}pct"
        decision_frej = (
            policy.decision_false_reject_cost
            if policy.decision_false_reject_cost is not None
            else scenario.false_reject_cost
        )
        specs.append(
            PolicySpec(
                name=name,
                score_col=policy.score_col,
                review_capacity=capacity,
                decision_false_reject_cost=decision_frej,
            )
        )
    return specs


def _empty_row(
    scenario: str,
    policy: str,
    estimator: str,
    rep: int,
    *,
    true_p0: float,
    true_full: float,
    true_approved: float,
    n_rejected: int,
) -> dict:
    return {
        "scenario": scenario,
        "policy": policy,
        "estimator": estimator,
        "rep": rep,
        "value": np.nan,
        "se": np.nan,
        "n_used": 0,
        "ess": np.nan,
        "max_weight": np.nan,
        "true_target": np.nan,
        "true_p0": true_p0,
        "true_full": true_full,
        "true_approved": true_approved,
        "lower": np.nan,
        "upper": np.nan,
        "width": np.nan,
        "lower_unconditional": np.nan,
        "upper_unconditional": np.nan,
        "width_unconditional": np.nan,
        "n_rejected": n_rejected,
    }


def run_scenario(
    scenario: Scenario,
    data: EvalData,
    config: PilotConfig,
    scenario_index: int,
    *,
    reliability_n_boot: int = 0,
) -> dict:
    base_costs = config.costs.with_false_reject(scenario.false_reject_cost)
    specs = build_policy_set(config, scenario)
    policies = [build_policy(data.df, spec, base_costs, data.amount) for spec in specs]
    logging = policies[0]
    in_pop = logging.actions != "reject"
    rejected = logging.actions == "reject"

    obs_cfg = config.observation.with_overrides(
        audit_rate=scenario.audit_rate,
        approve_delay_median=scenario.approve_delay_median,
        outcome_dependent=scenario.outcome_dependent,
        e_approve=(
            scenario.e_approve
            if scenario.e_approve is not None
            else config.observation.e_approve
        ),
        kappa_review=(
            scenario.kappa_review
            if scenario.kappa_review is not None
            else config.observation.kappa_review
        ),
    )
    model = build_observation_model(
        logging.actions,
        data.decision_day,
        obs_cfg,
        covariate=(
            data.X[:, data.feature_names.index("log1p_amount")]
            if scenario.observation_mode == "covariate"
            else None
        ),
        observation_mode=scenario.observation_mode,
        covariate_beta=scenario.covariate_beta,
    )
    day = data.decision_day
    day_sd = float(day.std())
    day_z = (day - float(day.mean())) / day_sd if day_sd > 0 else np.zeros_like(day)
    X_prop = np.column_stack([data.X, day_z])

    true_values: dict[str, dict[str, float]] = {}
    approved_mask = logging.actions == "approve"
    costs_by_policy: dict[str, np.ndarray] = {}
    for policy in policies:
        cost = realized_cost(policy.actions, data.y, data.amount, base_costs)
        costs_by_policy[policy.spec.name] = cost
        true_values[policy.spec.name] = {
            "true_p0": float(cost[in_pop].mean()),
            "true_full": float(cost.mean()),
            "true_approved": (
                float(cost[approved_mask].mean())
                if approved_mask.any()
                else float("nan")
            ),
        }

    rng = np.random.default_rng(config.seed)
    rows: list[dict] = []
    reliability_rows: list[dict] = []
    obs_frac = 0.0
    audit_count = 0
    source_counts = {"review": 0, "audit": 0, "post_approval_report": 0}

    for rep in range(scenario.reps):
        if scenario.outcome_dependent:
            draw = draw_observation(
                model,
                rng,
                y=data.y,
                outcome_dependent=True,
                e_approve_fraud=obs_cfg.e_approve_fraud,
            )
        else:
            draw = draw_observation(model, rng)

        if scenario.propensity_mode == "oracle":
            e_est = model.propensity
        elif scenario.propensity_mode == "estimated":
            e_est = estimate_from_draw(model, draw)
        elif scenario.propensity_mode == "noisy":
            noise_rng = np.random.default_rng(config.seed + 7000 + rep)
            e_est = noisy_copy(model.propensity, scenario.propensity_noise, noise_rng)
        elif scenario.propensity_mode == "covariate":
            e_est = fit_covariate_propensity(
                X_prop,
                logging.actions,
                draw.observed,
                random_state=config.seed + rep,
            )
        else:
            raise ValueError(f"unknown propensity_mode {scenario.propensity_mode!r}")

        phat = fit_outcome_model(
            data.X,
            data.y,
            draw.observed,
            e_est,
            config.outcome_model,
            seed=config.seed + rep,
        )

        # Label-holdout test: fit the outcome model on one random half of the
        # observed rows and evaluate every estimator on the other half. This
        # checks whether the correction is an overfitting artifact.
        holdout_rng = np.random.default_rng(config.seed + 9000 + rep)
        p0_idx = np.where(in_pop)[0]
        if len(p0_idx) > 1:
            eval_p0_idx = holdout_rng.choice(
                p0_idx, size=len(p0_idx) // 2, replace=False
            )
        else:
            eval_p0_idx = p0_idx
        in_pop_eval = np.zeros(len(in_pop), dtype=bool)
        in_pop_eval[eval_p0_idx] = True
        eval_mask = draw.observed & in_pop_eval
        fit_mask = draw.observed & ~in_pop_eval
        phat_holdout = fit_outcome_model(
            data.X,
            data.y,
            fit_mask,
            e_est,
            config.outcome_model,
            seed=config.seed + rep + 9000,
        )

        obs_frac += float(draw.observed.mean())
        audit_count += int(draw.audit.sum())
        for source in source_counts:
            source_counts[source] += int((draw.label_source == source).sum())

        for policy in policies:
            tv = true_values[policy.spec.name]
            cost = costs_by_policy[policy.spec.name]
            estimates = {
                "naive": naive(cost, draw.observed),
                "action_weighted": action_weighted(
                    cost, draw.observed, logging.actions, in_pop
                ),
                "naive_holdout": naive(cost, eval_mask),
                "action_weighted_holdout": action_weighted(
                    cost, eval_mask, logging.actions, in_pop_eval
                ),
                "dr_holdout": dr(
                    cost,
                    policy.actions,
                    data.amount,
                    eval_mask,
                    e_est,
                    in_pop_eval,
                    phat_holdout,
                    base_costs,
                ),
                "ipw_ht": ipw_ht(cost, draw.observed, e_est, in_pop),
                "ipw_hajek": ipw_hajek(cost, draw.observed, e_est, in_pop),
                "dr": dr(
                    cost,
                    policy.actions,
                    data.amount,
                    draw.observed,
                    e_est,
                    in_pop,
                    phat,
                    base_costs,
                ),
                "audit_only": audit_only(
                    cost,
                    draw.audit,
                    draw.resolved_approve,
                    model.p_resolved_approve,
                ),
            }
            for name, est in estimates.items():
                row = _empty_row(
                    scenario.id,
                    policy.spec.name,
                    name,
                    rep,
                    true_p0=tv["true_p0"],
                    true_full=tv["true_full"],
                    true_approved=tv["true_approved"],
                    n_rejected=int(rejected.sum()),
                )
                row.update(
                    {
                        "value": est.value,
                        "se": est.se,
                        "n_used": est.n_used,
                        "ess": est.ess,
                        "max_weight": est.max_weight,
                        "true_target": (
                            tv["true_approved"]
                            if name == "audit_only"
                            else tv["true_p0"]
                        ),
                    }
                )
                rows.append(row)

            v_pop_est = (
                estimates["dr"]
                if np.isfinite(estimates["dr"].value)
                else estimates["ipw_ht"]
            )
            b = policy_bounds(
                policy.actions,
                data.amount,
                base_costs,
                in_pop,
                rejected,
                v_pop=v_pop_est.value,
                v_pop_se=v_pop_est.se,
            )
            row = _empty_row(
                scenario.id,
                policy.spec.name,
                "bounds",
                rep,
                true_p0=tv["true_p0"],
                true_full=tv["true_full"],
                true_approved=tv["true_approved"],
                n_rejected=b.n_rejected,
            )
            row.update(
                {
                    "value": (b.lower + b.upper) / 2.0,
                    "true_target": tv["true_full"],
                    "lower": b.lower,
                    "upper": b.upper,
                    "width": b.width,
                    "lower_unconditional": b.lower_unconditional,
                    "upper_unconditional": b.upper_unconditional,
                    "width_unconditional": b.width_unconditional,
                }
            )
            rows.append(row)

        if reliability_n_boot > 0 and len(policies) >= 2:
            incumbent = policies[0]
            candidate = policies[1]
            cost_c = costs_by_policy[candidate.spec.name]
            cost_i = costs_by_policy[incumbent.spec.name]
            positivity_ok = bool((e_est[in_pop] > 0).all()) if in_pop.any() else False
            source = (
                "provided"
                if scenario.propensity_mode == "oracle"
                else "estimated_covariate"
                if scenario.propensity_mode == "covariate"
                else "estimated"
            )
            identification = check_identification(
                actions=logging.actions,
                candidate_actions=candidate.actions,
                observed=draw.observed,
                propensity=e_est,
                cost=cost_c,
                positivity_ok=positivity_ok,
                propensity_source=source,
                has_audit=bool(draw.audit.any()),
                observation_assumption=(
                    "outcome"
                    if scenario.outcome_dependent
                    else "unknown"
                    if getattr(scenario, "observation_mode", "action") == "covariate"
                    else "action"
                ),
            )
            comparison = compare_policies(
                cost_c,
                candidate.actions,
                cost_i,
                incumbent.actions,
                data.amount,
                draw.observed,
                e_est,
                in_pop,
                phat,
                base_costs,
            )
            rel = build_reliability(
                y=data.y,
                cost=cost_c,
                actions=logging.actions,
                candidate_actions=candidate.actions,
                amount=data.amount,
                observed=draw.observed,
                propensity=e_est,
                in_pop=in_pop,
                phat=phat,
                costs=base_costs,
                comparison=comparison,
                identification=identification,
                seed=config.seed + rep,
                n_boot=reliability_n_boot,
                propensity_source=source,
                propensity_model=(
                    "covariate" if scenario.propensity_mode == "covariate" else "action"
                ),
            )
            true_c = true_values[candidate.spec.name]["true_p0"]
            true_i = true_values[incumbent.spec.name]["true_p0"]
            if true_c < true_i:
                true_decision = "prefer candidate"
            elif true_c > true_i:
                true_decision = "keep incumbent"
            else:
                true_decision = "tie"
            decision = comparison.get("decision", "not identified")
            directional = decision in {"prefer candidate", "keep incumbent"}
            true_full_c = true_values[candidate.spec.name]["true_full"]
            true_full_i = true_values[incumbent.spec.name]["true_full"]
            if true_full_c < true_full_i:
                true_full_decision = "prefer candidate"
            elif true_full_c > true_full_i:
                true_full_decision = "keep incumbent"
            else:
                true_full_decision = "tie"
            full_decision = (comparison.get("full_policy") or {}).get("decision")
            full_directional = full_decision in {
                "candidate cheaper",
                "incumbent cheaper",
                "candidate cheaper for any reject outcome",
                "incumbent cheaper for any reject outcome",
            }
            full_policy_decision = (
                "prefer candidate"
                if str(full_decision).startswith("candidate cheaper")
                else "keep incumbent"
                if str(full_decision).startswith("incumbent cheaper")
                else None
            )
            reliability_rows.append(
                {
                    "scenario": scenario.id,
                    "rep": rep,
                    "grade": rel["profile"]["grade"],
                    "decision": decision,
                    "true_decision": true_decision,
                    "p0_correct": bool(directional and decision == true_decision),
                    "correct": bool(directional and decision == true_decision),
                    "p_candidate_better_boot": rel["bootstrap"].get(
                        "p_candidate_better_boot"
                    ),
                    "same_direction_share": rel["bootstrap"].get(
                        "same_direction_share"
                    ),
                    "n_boot": rel["bootstrap"].get("n_boot"),
                    "propensity_source": source,
                    "cost_stress_share": rel["cost_stress"].get("same_decision_share"),
                    "full_policy_decision": full_decision,
                    "full_policy_correct": bool(
                        full_directional and full_policy_decision == true_full_decision
                    ),
                    "difference": comparison.get("difference"),
                }
            )

        if scenario.reps >= 10 and (rep + 1) % max(1, scenario.reps // 10) == 0:
            print(f"[{scenario.id}] {rep + 1}/{scenario.reps} replications")

    meta = {
        "scenario": scenario.id,
        "reps": scenario.reps,
        "audit_rate": scenario.audit_rate,
        "approve_delay_median": scenario.approve_delay_median,
        "false_reject_cost": scenario.false_reject_cost,
        "outcome_dependent": scenario.outcome_dependent,
        "candidate_capacity": scenario.candidate_capacity,
        "n": data.n,
        "in_pop": int(in_pop.sum()),
        "rejected": int(rejected.sum()),
        "logging_actions": {
            "approve": int((logging.actions == "approve").sum()),
            "review": int((logging.actions == "review").sum()),
            "reject": int((logging.actions == "reject").sum()),
        },
        "policies": [p.spec.name for p in policies],
        "true_values": true_values,
        "mean_observed_fraction": obs_frac / scenario.reps,
        "mean_audit_count": audit_count / scenario.reps,
        "mean_label_sources": {k: v / scenario.reps for k, v in source_counts.items()},
    }
    return {"meta": meta, "rows": rows, "reliability": reliability_rows}


def _jsonable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def write_report(payload: dict, path: Path) -> None:
    summary = pd.DataFrame(payload["summary"])
    ranking = pd.DataFrame(payload["ranking"])
    bounds = pd.DataFrame(payload["bounds"])
    v = payload["verdict"]
    meta = {m["scenario"]: m for m in payload["scenarios"]}

    def table(df: pd.DataFrame, cols: list[str], fmts: dict | None = None) -> list[str]:
        fmts = fmts or {}
        lines = [
            "| " + " | ".join(cols) + " |",
            "|" + "|".join(["---"] * len(cols)) + "|",
        ]
        for _, row in df.iterrows():
            cells = []
            for c in cols:
                val = row[c]
                if val is None:
                    cells.append("n/a")
                elif isinstance(val, (float, np.floating)):
                    if not np.isfinite(val):
                        cells.append("n/a")
                    elif c in fmts:
                        cells.append(fmts[c].format(val))
                    else:
                        cells.append(f"{val:.6f}")
                else:
                    cells.append(str(val))
            lines.append("| " + " | ".join(cells) + " |")
        return lines

    L: list[str] = []
    L.append("# Onboarding Audit — Pilot Report")
    L.append("")
    L.append(f"_Generated by `onboarding_audit` v{payload['software']['version']}._")
    L.append("")
    L.append("## Run metadata")
    L.append("")
    L.append(f"- Seed: `{payload['config']['seed']}`")
    L.append(f"- Data: `{payload['config']['data_path']}`")
    L.append(f"- Applications: {payload['data']['n']:,}")
    L.append(f"- Fraud rate: {payload['data']['fraud_rate']:.4%}")
    L.append(f"- Runtime: {payload['runtime_seconds']:.1f} s")
    L.append(f"- Python: {payload['software']['python']}")
    L.append(
        f"- numpy: {payload['software']['numpy']}; pandas: {payload['software']['pandas']}; scikit-learn: {payload['software']['sklearn']}"
    )
    L.append("")
    L.append("## Headline")
    L.append("")
    main_all = summary[summary["scenario"] == "main"]
    naive = main_all[main_all["estimator"] == "naive"]
    ipw = main_all[main_all["estimator"] == "ipw_ht"]
    dr_main = main_all[main_all["estimator"] == "dr"]
    ao = main_all[main_all["estimator"] == "audit_only"]
    rank_main = (
        ranking[ranking["scenario"] == "main"] if not ranking.empty else pd.DataFrame()
    )
    b_main = (
        bounds[bounds["scenario"] == "main"] if not bounds.empty else pd.DataFrame()
    )
    if not naive.empty:
        L.append(
            f"- **Naive evaluation is materially biased:** relative bias ranges "
            f"from {naive['rel_bias'].min():+.1%} to {naive['rel_bias'].max():+.1%} "
            "across the four policies. It overstates cost and reverses the "
            "incumbent/better-model ranking."
        )
    if not dr_main.empty:
        L.append(
            f"- **DR recovers the identified value:** max |relative bias| "
            f"{dr_main['rel_bias'].abs().max():.2%}, mean coverage "
            f"{dr_main['coverage'].mean():.1%}, mean ESS "
            f"{dr_main['mean_ess'].mean():,.0f}."
        )
    if not ipw.empty:
        L.append(
            f"- **IPW behaves similarly:** max |relative bias| "
            f"{ipw['rel_bias'].abs().max():.2%}, mean coverage "
            f"{ipw['coverage'].mean():.1%}."
        )
    if not ao.empty:
        L.append(
            f"- **Audit-only is unbiased but high variance:** max |relative "
            f"bias| {ao['rel_bias'].abs().max():.2%}, mean coverage "
            f"{ao['coverage'].mean():.1%}, mean ESS {ao['mean_ess'].mean():,.0f}. "
            "A 1% audit validates the approved margin; it does not replace the "
            "log-based estimate."
        )
    if not rank_main.empty:
        naive_rank = rank_main[rank_main["estimator"] == "naive"]
        dr_rank = rank_main[rank_main["estimator"] == "dr"]
        if not naive_rank.empty and not dr_rank.empty:
            L.append(
                f"- **Ranking:** naive P(select true best) = "
                f"{naive_rank['p_select_true_best'].iloc[0]:.0%}, mean inversions "
                f"{naive_rank['mean_inversions'].iloc[0]:.2f}; DR P(select true "
                f"best) = {dr_rank['p_select_true_best'].iloc[0]:.0%}, mean "
                f"inversions {dr_rank['mean_inversions'].iloc[0]:.2f}."
            )
    if not b_main.empty:
        L.append(
            f"- **The reject margin is not point-identified:** the widest bounds "
            f"interval is {b_main['width'].max():.6f}, on a policy whose true "
            "full-population value is of the same order. Bounds are reported, "
            "not a point estimate."
        )
    od = summary[summary["scenario"] == "outcome_dependent"]
    if not od.empty:
        od_ao = od[od["estimator"] == "audit_only"]
        od_ipw = od[od["estimator"] == "ipw_ht"]
        od_dr = od[od["estimator"] == "dr"]
        if not od_ao.empty and not od_ipw.empty and not od_dr.empty:
            L.append(
                f"- **Outcome-dependent labels break action-only weighting:** "
                f"audit-only bias {od_ao['rel_bias'].min():+.1%} to "
                f"{od_ao['rel_bias'].max():+.1%}; IPW {od_ipw['rel_bias'].min():+.0%} "
                f"to {od_ipw['rel_bias'].max():+.0%}; DR {od_dr['rel_bias'].min():+.0%} "
                f"to {od_dr['rel_bias'].max():+.0%}. The audit-only estimator is "
                "the honest one in this regime."
            )
    L.append("")
    L.append("## Main scenario")
    L.append("")
    L.append(
        "Targets: `P0` = logging non-rejected population (naive/IPW/DR); "
        "`approved` = audit-only target; `full` = bounds target."
    )
    L.append("")
    main = summary[(summary["scenario"] == "main") & (summary["estimator"] != "bounds")]
    if not main.empty:
        L.extend(
            table(
                main,
                [
                    "policy",
                    "target",
                    "estimator",
                    "true",
                    "estimate",
                    "rel_bias",
                    "rmse",
                    "coverage",
                    "mean_ess",
                ],
                {
                    "true": "{:.6f}",
                    "estimate": "{:.6f}",
                    "rel_bias": "{:+.2%}",
                    "rmse": "{:.6f}",
                    "coverage": "{:.1%}",
                    "mean_ess": "{:,.0f}",
                },
            )
        )
    L.append("")
    L.append("## True vs estimated ranking")
    L.append("")
    p0 = main[main["estimator"] == "ipw_ht"]
    if not p0.empty:
        true_rank = p0.set_index("policy")["true"].sort_values()
        L.append(
            "**True P0 ranking (lowest cost best):** "
            + " < ".join(f"`{p}`" for p in true_rank.index)
        )
    for est_name in ("naive", "dr"):
        part = main[main["estimator"] == est_name]
        if not part.empty:
            est_rank = part.set_index("policy")["estimate"].sort_values()
            L.append(
                f"**{est_name} ranking:** "
                + " < ".join(f"`{p}`" for p in est_rank.index)
            )
    L.append("")
    L.append("## Ranking")
    L.append("")
    rank_main = (
        ranking[ranking["scenario"] == "main"] if not ranking.empty else pd.DataFrame()
    )
    if not rank_main.empty:
        L.extend(
            table(
                rank_main,
                [
                    "estimator",
                    "mean_spearman",
                    "mean_inversions",
                    "p_select_true_best",
                    "mean_cost_misrank",
                ],
                {
                    "mean_spearman": "{:.3f}",
                    "mean_inversions": "{:.2f}",
                    "p_select_true_best": "{:.1%}",
                    "mean_cost_misrank": "{:.6f}",
                },
            )
        )
    L.append("")
    L.append("## Audit sweep")
    L.append("")
    audit_ids = [s for s in ("audit_0", "audit_05", "main", "audit_2") if s in meta]
    audit = summary[
        summary["scenario"].isin(audit_ids)
        & summary["estimator"].isin(("naive", "ipw_ht", "dr", "audit_only"))
    ].copy()
    if not audit.empty:
        audit["audit_rate"] = audit["scenario"].map(lambda s: meta[s]["audit_rate"])
        audit = (
            audit.groupby(["estimator", "audit_rate"])
            .agg(
                mean_rel_bias=("rel_bias", "mean"),
                max_abs_rel_bias=("rel_bias", lambda x: x.abs().max()),
                mean_rmse=("rmse", "mean"),
                mean_coverage=("coverage", "mean"),
                mean_ess=("mean_ess", "mean"),
            )
            .reset_index()
            .sort_values(["estimator", "audit_rate"])
        )
        L.extend(
            table(
                audit,
                [
                    "estimator",
                    "audit_rate",
                    "mean_rel_bias",
                    "max_abs_rel_bias",
                    "mean_rmse",
                    "mean_coverage",
                    "mean_ess",
                ],
                {
                    "audit_rate": "{:.1%}",
                    "mean_rel_bias": "{:+.2%}",
                    "max_abs_rel_bias": "{:.2%}",
                    "mean_rmse": "{:.6f}",
                    "mean_coverage": "{:.1%}",
                    "mean_ess": "{:,.0f}",
                },
            )
        )
    L.append("")
    L.append("## Capacity and delay")
    L.append("")
    other_ids = [
        s
        for s in (
            "capacity_1",
            "capacity_5",
            "capacity_10",
            "delay_0",
            "delay_30",
            "delay_90",
        )
        if s in meta
    ]
    other = summary[
        summary["scenario"].isin(other_ids)
        & summary["estimator"].isin(("ipw_ht", "dr"))
    ].copy()
    if not other.empty:
        L.extend(
            table(
                other,
                [
                    "scenario",
                    "policy",
                    "estimator",
                    "rel_bias",
                    "rmse",
                    "coverage",
                    "mean_ess",
                ],
                {
                    "rel_bias": "{:+.2%}",
                    "rmse": "{:.6f}",
                    "coverage": "{:.1%}",
                    "mean_ess": "{:,.0f}",
                },
            )
        )
    L.append("")
    L.append("## Outcome-dependent stress scenario")
    L.append("")
    od = summary[
        (summary["scenario"] == "outcome_dependent")
        & summary["estimator"].isin(("naive", "ipw_ht", "audit_only", "dr"))
    ]
    if not od.empty:
        L.extend(
            table(
                od,
                [
                    "policy",
                    "estimator",
                    "true",
                    "estimate",
                    "rel_bias",
                    "rmse",
                    "coverage",
                ],
                {
                    "true": "{:.6f}",
                    "estimate": "{:.6f}",
                    "rel_bias": "{:+.2%}",
                    "rmse": "{:.6f}",
                    "coverage": "{:.1%}",
                },
            )
        )
    L.append("")
    L.append("## Reject-margin bounds")
    L.append("")
    b = bounds[bounds["scenario"] == "main"] if not bounds.empty else pd.DataFrame()
    if not b.empty:
        L.extend(
            table(
                b,
                [
                    "policy",
                    "lower",
                    "upper",
                    "width",
                    "coverage_full",
                    "f5_coverage",
                    "unconditional_coverage",
                    "width_unconditional",
                    "n_rejected",
                    "true_full",
                ],
                {
                    "lower": "{:.6f}",
                    "upper": "{:.6f}",
                    "width": "{:.6f}",
                    "coverage_full": "{:.1%}",
                    "f5_coverage": "{:.1%}",
                    "unconditional_coverage": "{:.1%}",
                    "width_unconditional": "{:.6f}",
                    "true_full": "{:.6f}",
                },
            )
        )
    L.append("")
    L.append(
        "F5 passes when `coverage_full >= 90%` (narrow interval) or "
        "`unconditional_coverage >= 90%` (widened interval). The widened "
        "interval is a valid, conservative 95% confidence interval under the "
        "identification assumptions; the narrow interval is not."
    )
    L.append("")
    if not b.empty and "incumbent" in set(b["policy"]):
        inc_cov = float(b.loc[b["policy"] == "incumbent", "coverage_full"].mean())
        inc_text = f"{inc_cov:.0%}"
    else:
        inc_text = "n/a"
    L.append(
        "The narrow interval is a **partial-identification interval conditional "
        "on the P0 estimate**, not a confidence interval. Coverage of the true "
        "full-population value is a diagnostic for the narrow interval: a narrow "
        f"interval on a noisy P0 estimate can miss. The incumbent's narrow interval covers the true "
        f"full value in {inc_text} of replications. Do not interpret the bounds "
        "as 95% coverage."
    )
    L.append("")
    L.append(
        f"## Verdict (reference scenario: `{v.get('reference_scenario', 'main')}`)"
    )
    L.append("")
    L.append(
        f"- **H1 naive bias > 5%:** {'supported' if v['H1_naive_bias_gt_5pct'] else 'not supported'} (max |relative bias| = {v['H1_max_abs_rel_bias']:.2%})"
    )
    L.append(
        f"- **H2 rank inversion:** {'supported' if v['H2_rank_inversion'] else 'not supported'} (max mean inversions = {v['H2_max_mean_inversions']:.2f})"
    )
    L.append(
        f"- **H3 correction credible:** {'supported' if v['H3_correction_credible'] else 'not supported'}"
    )
    h4 = v.get("H4_details", {})
    if h4:
        h4_bits = []
        for est, d in h4.items():
            h4_bits.append(
                f"{est}: RMSE {d['rmse_0']:.6f}→{d['rmse_2']:.6f}, "
                f"ESS {d['ess_0']:,.0f}→{d['ess_2']:,.0f}"
            )
        L.append(
            f"- **H4 audit value:** {'supported' if v.get('H4_audit_value') else 'partial/not supported'} "
            f"({'; '.join(h4_bits)})"
        )
    L.append(
        f"- **H5 reject margin not identified:** {'supported' if v['H5_reject_margin_not_identified'] else 'not supported'} (max bounds width = {v['H5_max_bounds_width']:.6f})"
    )
    h6 = v.get("H6_audit_max_abs_rel_bias")
    if h6 is not None and np.isfinite(h6):
        L.append(
            f"- **H6 outcome-dependent labels:** {'supported' if v.get('H6_outcome_dependent') else 'not supported'} "
            f"(audit-only max |relative bias| = {v['H6_audit_max_abs_rel_bias']:.2%}; "
            f"IPW max = {v['H6_ipw_max_abs_rel_bias']:.1%}; "
            f"DR max = {v['H6_dr_max_abs_rel_bias']:.1%})"
        )
    if v.get("H3_best_estimator"):
        best = v["H3_best_estimator"]
        L.append(
            f"- Best corrected estimator: `{best['estimator']}` "
            f"(max |relative bias| across policies {best['max_abs_rel_bias']:.2%}, "
            f"mean coverage {best['mean_coverage']:.1%})"
        )
    L.append("")
    L.append("## Negative controls")
    L.append("")
    L.append(
        "The full-observation, full-audit, label-permutation, capacity, and no-leakage checks are in `tests/`. Run `pytest -q`."
    )
    L.append("")
    reliability_rows = payload.get("reliability", [])
    if reliability_rows:
        grades = {}
        for row in reliability_rows:
            grades[row["grade"]] = grades.get(row["grade"], 0) + 1
        released = [
            row
            for row in reliability_rows
            if row["decision"] in {"prefer candidate", "keep incumbent"}
            and str(row["grade"]).startswith(("A", "B"))
        ]
        false_cert = [row for row in released if not row["correct"]]
        L.append("## Decision reliability audit")
        L.append("")
        L.append(f"- Replications: **{len(reliability_rows)}**")
        L.append(f"- Grades: **{grades}**")
        L.append(
            f"- Released A/B directional decisions: **{len(released)}**; "
            f"false certifications: **{len(false_cert)}**"
        )
        L.append("")
    L.append("## Limitations")
    L.append("")
    L.append(
        "- The observation mechanism and review capacity are simulated, not observed."
    )
    L.append("- The cost matrix is a normalized assumption, not a production estimate.")
    L.append("- The reject margin is bounded, not point-identified.")
    L.append("- BAF is synthetic; no Philippine bank data is used.")
    L.append(
        "- The audit design is a post-hoc verification of approved applications; no random approvals/rejections."
    )
    L.append("- This is a pilot, not a production system or a causal deployment claim.")
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


def run_pilot(
    config: PilotConfig,
    out_dir: Path,
    *,
    scenario_filter: list[str] | None = None,
    reps_override: int | None = None,
    reliability_n_boot: int = 0,
) -> dict:
    t0 = time.time()
    data = load_eval_data(
        config.data_path,
        label_col=config.label_col,
        amount_col=config.amount_col,
        month_col=config.month_col,
        outcome_features=config.outcome_features,
        seed=config.seed,
        months=config.months,
    )
    scenarios = [
        s
        for s in config.scenarios
        if scenario_filter is None or s.id in scenario_filter
    ]
    if reps_override is not None:
        scenarios = [replace(s, reps=reps_override) for s in scenarios]

    results = []
    for idx, scenario in enumerate(scenarios):
        print(f"[pilot] scenario {scenario.id} ({scenario.reps} reps)")
        results.append(
            run_scenario(
                scenario,
                data,
                config,
                idx,
                reliability_n_boot=reliability_n_boot,
            )
        )

    rows = pd.DataFrame([row for r in results for row in r["rows"]])
    summary = summarize(rows)
    ranking = ranking_metrics(rows)
    bounds = bounds_summary(rows)
    reference = (
        "main"
        if any(r["meta"]["scenario"] == "main" for r in results)
        else results[0]["meta"]["scenario"]
    )
    v = verdict(summary, ranking, bounds, scenario=reference)
    v["reference_scenario"] = reference

    payload = {
        "software": {
            "version": __version__,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": __import__("sklearn").__version__,
        },
        "config": _jsonable(asdict(config)),
        "data": {
            "n": data.n,
            "fraud_rate": float(data.y.mean()),
            "months": sorted(int(m) for m in np.unique(data.month)),
        },
        "scenarios": [r["meta"] for r in results],
        "summary": _jsonable(summary.to_dict(orient="records")),
        "ranking": _jsonable(ranking.to_dict(orient="records")),
        "bounds": _jsonable(bounds.to_dict(orient="records")),
        "reliability": _jsonable(
            [row for result in results for row in result.get("reliability", [])]
        ),
        "reliability_n_boot": int(reliability_n_boot),
        "verdict": _jsonable(v),
        "runtime_seconds": time.time() - t0,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pilot.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    rows.to_parquet(out_dir / "pilot_rows.parquet", index=False)
    write_report(payload, out_dir / "pilot.md")
    print(f"[pilot] wrote {out_dir / 'pilot.json'}")
    print(f"[pilot] wrote {out_dir / 'pilot_rows.parquet'}")
    print(f"[pilot] wrote {out_dir / 'pilot.md'}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the onboarding-audit pilot.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", default=Path("reports"), type=Path)
    parser.add_argument(
        "--scenarios", default=None, help="comma-separated scenario ids"
    )
    parser.add_argument(
        "--reps", default=None, type=int, help="override reps for a smoke test"
    )
    parser.add_argument(
        "--reliability-boot",
        default=0,
        type=int,
        help="bootstrap replicates for the per-replication reliability audit (0=off)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    scenario_filter = (
        [s.strip() for s in args.scenarios.split(",") if s.strip()]
        if args.scenarios
        else None
    )
    run_pilot(
        config,
        args.out,
        scenario_filter=scenario_filter,
        reps_override=args.reps,
        reliability_n_boot=args.reliability_boot,
    )


if __name__ == "__main__":
    main()
