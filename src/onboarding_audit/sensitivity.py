"""Propensity-estimation and misspecification sensitivity.

The main pilot uses oracle propensities. This script re-runs the headline
scenarios with:

- action-level propensities estimated from the observed draw;
- oracle propensities perturbed by lognormal noise (sigma 0.10, 0.25);
- the outcome-dependent label mechanism, with estimated e.

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
)
ESTIMATORS = ("ipw_ht", "dr", "audit_only")


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
        "(b) oracle propensities with lognormal noise, and (c) estimated "
        "propensities under outcome-dependent labels. The target and policies "
        "are unchanged."
    )
    L.append("")
    L.append("## Main scenario")
    L.append("")
    main_ids = (
        "main",
        "propensity_estimated",
        "propensity_noisy_10",
        "propensity_noisy_25",
    )
    main = agg[agg["scenario"].isin(main_ids)]
    L.append("| Scenario | Estimator | Max \\|rel bias\\| | Mean coverage | Mean ESS |")
    L.append("|---|---|---:|---:|---:|")
    for _, row in main.iterrows():
        L.append(
            f"| `{row['scenario']}` | `{row['estimator']}` | "
            f"{row['max_abs_rel_bias']:.2%} | {row['mean_coverage']:.1%} | "
            f"{row['mean_ess']:,.0f} |"
        )
    L.append("")
    L.append("## Outcome-dependent labels")
    L.append("")
    od_ids = ("outcome_dependent", "outcome_dependent_estimated")
    od = agg[agg["scenario"].isin(od_ids)]
    L.append("| Scenario | Estimator | Max \\|rel bias\\| | Mean coverage | Mean ESS |")
    L.append("|---|---|---:|---:|---:|")
    for _, row in od.iterrows():
        L.append(
            f"| `{row['scenario']}` | `{row['estimator']}` | "
            f"{row['max_abs_rel_bias']:.2%} | {row['mean_coverage']:.1%} | "
            f"{row['mean_ess']:,.0f} |"
        )
    L.append("")
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
