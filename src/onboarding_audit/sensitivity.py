"""Propensity-estimation and misspecification sensitivity.

The main pilot uses oracle propensities. This script re-runs the headline
scenarios with:

- action-level propensities estimated from the observed draw;
- oracle propensities perturbed by lognormal noise (sigma 0.10, 0.25);
- the outcome-dependent label mechanism, with estimated e;
- covariate-dependent observation, comparing action-level, fitted covariate,
  and oracle propensities.

The question: does the correction survive the loss of the oracle?
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PilotConfig, load_config
from .data import load_eval_data
from .metrics import summarize
from .pilot import run_scenario

SCENARIOS = (
    "main",
    "propensity_estimated",
    "propensity_noisy_10",
    "propensity_noisy_25",
    "outcome_dependent",
    "outcome_dependent_estimated",
    "covariate_oracle",
    "covariate_action",
    "covariate_model",
    "covariate_action_delay",
    "covariate_model_delay",
)
ESTIMATORS = ("naive", "ipw_ht", "dr", "audit_only")


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


def run_sensitivity(
    config: PilotConfig,
    out_dir: Path | str,
    *,
    reps: int = 50,
) -> dict:
    data = load_eval_data(
        config.data_path,
        label_col=config.label_col,
        amount_col=config.amount_col,
        month_col=config.month_col,
        outcome_features=config.outcome_features,
        seed=config.seed,
    )
    scenarios = [s for s in config.scenarios if s.id in SCENARIOS]
    scenarios = [replace(s, reps=reps) for s in scenarios]
    results = []
    for i, scenario in enumerate(scenarios):
        print(f"[sensitivity] scenario {scenario.id} ({scenario.reps} reps)")
        results.append(run_scenario(scenario, data, config, i))

    rows = pd.DataFrame([row for r in results for row in r["rows"]])
    summary = summarize(rows)
    sl = summary[summary["estimator"].isin(ESTIMATORS)].copy()
    agg = (
        sl.groupby(["scenario", "estimator"])
        .agg(
            max_abs_rel_bias=("rel_bias", lambda x: float(np.abs(x).max())),
            mean_rel_bias=("rel_bias", "mean"),
            mean_coverage=("coverage", "mean"),
            mean_ess=("mean_ess", "mean"),
            reps=("reps", "first"),
        )
        .reset_index()
    )

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "reps": reps,
        "scenarios": [s.id for s in scenarios],
        "summary": _clean(summary.to_dict(orient="records")),
        "aggregate": _clean(agg.to_dict(orient="records")),
    }
    (out_dir / "propensity_sensitivity.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    L: list[str] = []
    L.append("# Propensity Sensitivity")
    L.append("")
    L.append(
        f"_Pre-registered follow-up; {reps} replications per scenario; common "
        "random numbers; seed from the pilot config._"
    )
    L.append("")
    L.append("## What this tests")
    L.append("")
    L.append(
        "The main pilot uses oracle propensities. This study replaces them with "
        "(a) action-level propensities estimated from the observed draw, "
        "(b) oracle propensities with lognormal noise, (c) estimated "
        "propensities under outcome-dependent labels, and (d) action-level, "
        "fitted covariate, and oracle propensities under covariate-dependent "
        "observation. The target and policies are unchanged."
    )
    L.append("")
    L.append("## Main scenario")
    L.append("")

    def add_table(ids, estimators) -> None:
        L.append(
            "| Scenario | Estimator | Max \\|rel bias\\| | Mean coverage | Mean ESS |"
        )
        L.append("|---|---|---:|---:|---:|")
        for sid in ids:
            for est in estimators:
                match = agg[(agg["scenario"] == sid) & (agg["estimator"] == est)]
                if match.empty:
                    continue
                row = match.iloc[0]
                L.append(
                    f"| `{sid}` | `{est}` | "
                    f"{row['max_abs_rel_bias']:.2%} | {row['mean_coverage']:.1%} | "
                    f"{row['mean_ess']:,.0f} |"
                )
        L.append("")

    main_ids = (
        "main",
        "propensity_estimated",
        "propensity_noisy_10",
        "propensity_noisy_25",
    )
    add_table(main_ids, ("naive", "ipw_ht", "dr", "audit_only"))
    L.append("## Outcome-dependent labels")
    L.append("")
    od_ids = ("outcome_dependent", "outcome_dependent_estimated")
    add_table(od_ids, ("naive", "ipw_ht", "dr", "audit_only"))
    L.append("## Covariate-dependent observation")
    L.append("")
    L.append(
        "The post-approval report probability depends on standardized log "
        "amount: `logit(e_report) = logit(e_approve) + 0.75 * z`. The "
        "`covariate_*` scenarios use that mechanism. `oracle` uses the true "
        "per-row propensity; `action` uses the action-level estimate; `model` "
        "uses a cross-fitted per-action logistic model of `observed` on the "
        "outcome-model features plus decision day. The delay-0.5 variants "
        "isolate the propensity misspecification; the delay-45 variants add the "
        "resolution gradient."
    )
    L.append("")
    cov_ids = (
        "covariate_oracle",
        "covariate_action",
        "covariate_model",
        "covariate_action_delay",
        "covariate_model_delay",
    )
    add_table(cov_ids, ("naive", "ipw_ht", "dr"))
    L.append("## Interpretation")
    L.append("")
    L.append(
        "- In the main action-dependent scenario, the estimated action-level "
        "propensities should be close to the oracle; the correction should "
        "survive. This is the minimum bar."
    )
    L.append(
        "- Lognormal noise tests misspecification. If the bias grows quickly "
        "with sigma, the memo must report a propensity-sensitivity band, not a "
        "single point estimate."
    )
    L.append(
        "- Under outcome-dependent labels, the action-level estimated e is a "
        "weighted average of the fraud and legitimate observation rates. "
        "Action-only IPW/DR are expected to fail; audit-only is the honest "
        "estimator. This is the strongest argument for the audit."
    )
    L.append(
        "- Under covariate-dependent observation, action-level e is misspecified "
        "because it ignores the within-action gradient. The fitted covariate "
        "model should recover most of the correction; if it does not, the "
        "report must not claim a point estimate without a covariate propensity "
        "model and overlap diagnostics."
    )
    L.append("")
    L.append("## Caveats")
    L.append("")
    L.append(
        "- The estimated e is action-level and estimated from the same draw; it "
        "is not a full propensity model with covariates."
    )
    L.append(
        "- The noisy e uses the oracle as the center; it is a stress test, not a "
        "calibration study."
    )
    L.append(
        "- The covariate model is a logistic model in the observed features. It "
        "is correctly specified for the simulated mechanism up to the audit "
        "mixture and the delay/resolution term; a real log may require a more "
        "flexible model and a positivity/overlap check."
    )
    L.append(
        "- A production study should estimate e from the audit design and "
        "covariates, and report the sensitivity band."
    )
    L.append("")
    (out_dir / "propensity_sensitivity.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[sensitivity] wrote {out_dir / 'propensity_sensitivity.json'}")
    print(f"[sensitivity] wrote {out_dir / 'propensity_sensitivity.md'}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Propensity sensitivity study.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", default=Path("reports"), type=Path)
    parser.add_argument("--reps", default=50, type=int)
    args = parser.parse_args()
    config = load_config(args.config)
    run_sensitivity(config, args.out, reps=args.reps)


if __name__ == "__main__":
    main()
