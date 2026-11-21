"""Command-line interface for onboarding-audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from .config import load_config
from .pilot import run_pilot
from .report import run_report
from .schema import validate_log
from .sensitivity import run_sensitivity


def _read_log(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_parquet(path)


def cmd_validate(args: argparse.Namespace) -> int:
    df = _read_log(args.log)
    report = validate_log(df)
    print(f"Schema valid: {report.n_rows:,} rows")
    if report.errors:
        print("\nErrors:")
        for e in report.errors:
            print(f"  - {e}")
    if report.warnings:
        print("\nWarnings:")
        for w in report.warnings:
            print(f"  - {w}")
    print("\nEstimator readiness:")
    for name, ok in report.estimator_readiness.items():
        missing = report.missing_by_estimator.get(name, [])
        status = "yes" if ok else f"no (missing: {missing})"
        print(f"  {name:<12} {status}")
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.ok else 1


def cmd_pilot(args: argparse.Namespace) -> int:
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
    )
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    feature_cols = (
        [f.strip() for f in args.features.split(",") if f.strip()]
        if args.features
        else None
    )
    propensity_features = (
        [f.strip() for f in args.propensity_features.split(",") if f.strip()]
        if args.propensity_features
        else None
    )
    result = run_report(
        args.log,
        args.candidate,
        args.config,
        args.out,
        capacity=args.capacity,
        feature_cols=feature_cols,
        propensity_col=args.propensity_col,
        audit_col=args.audit_col,
        propensity_model=args.propensity_model,
        propensity_features=propensity_features,
    )
    print(
        f"Applications: {result.n:,}; P0: {result.p0_n:,}; observed: {result.observed_n:,}"
    )
    print(
        f"Propensity source: {result.propensity.source}; positivity: {result.propensity.positivity_ok}"
    )
    print(f"Identification: {'passed' if result.identification.passed else 'FAILED'}")
    if not result.identification.passed:
        for reason in result.identification.reasons:
            print(f"  - {reason}")
        print("Point estimates withheld; see the memo for diagnostics.")
    else:
        print("\nEstimates:")
        for name, est in result.estimates.items():
            print(
                f"  {name:<12} {est['value']:.6f}  target={est['target']}  ESS={est['ess']:.0f}"
            )
        print(
            f"\nBounds: [{result.bounds['lower']:.6f}, {result.bounds['upper']:.6f}] width={result.bounds['width']:.6f}"
        )
    print(f"Memo: {result.memo_path}")
    print(f"JSON: {result.report_path}")
    return 0


def cmd_sensitivity(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    run_sensitivity(config, args.out, reps=args.reps)
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    result = run_report(
        Path("examples/demo_log.csv"),
        Path("examples/demo_candidate.csv"),
        args.config,
        args.out,
        capacity=0.10,
    )
    print(
        f"Applications: {result.n:,}; P0: {result.p0_n:,}; "
        f"observed: {result.observed_n:,}"
    )
    print(f"Identification: {'passed' if result.identification.passed else 'FAILED'}")
    if result.identification.passed:
        print(
            f"DR: {result.estimates['dr']['value']:.6f}; "
            f"naive: {result.estimates['naive']['value']:.6f}"
        )
    else:
        for reason in result.identification.reasons:
            print(f"  - {reason}")
    print(f"Memo: {result.memo_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="onboarding-audit",
        description="Audit-ready evaluation of account-opening fraud policies.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pilot = sub.add_parser("pilot", help="Run the pre-registered pilot.")
    p_pilot.add_argument("--config", required=True, type=Path)
    p_pilot.add_argument("--out", default=Path("reports"), type=Path)
    p_pilot.add_argument(
        "--scenarios", default=None, help="comma-separated scenario ids"
    )
    p_pilot.add_argument(
        "--reps", default=None, type=int, help="override reps for a smoke test"
    )
    p_pilot.set_defaults(func=cmd_pilot)

    p_report = sub.add_parser(
        "report", help="Evaluate a candidate policy from a decision log."
    )
    p_report.add_argument("--log", required=True, type=Path)
    p_report.add_argument("--candidate", required=True, type=Path)
    p_report.add_argument("--config", required=True, type=Path)
    p_report.add_argument("--out", default=Path("reports/report"), type=Path)
    p_report.add_argument(
        "--capacity",
        default=0.02,
        type=float,
        help="candidate review capacity (fraction)",
    )
    p_report.add_argument(
        "--features", default=None, help="comma-separated outcome-model features"
    )
    p_report.add_argument("--propensity-col", default="propensity")
    p_report.add_argument("--audit-col", default="audit_flag")
    p_report.add_argument(
        "--propensity-model",
        choices=["action", "covariate"],
        default="action",
        help="estimate action-level e or a per-action covariate model",
    )
    p_report.add_argument(
        "--propensity-features",
        default=None,
        help="comma-separated numeric features for the covariate propensity model",
    )
    p_report.set_defaults(func=cmd_report)

    p_sens = sub.add_parser(
        "sensitivity", help="Run the propensity-estimation sensitivity."
    )
    p_sens.add_argument("--config", required=True, type=Path)
    p_sens.add_argument("--out", default=Path("reports"), type=Path)
    p_sens.add_argument("--reps", default=50, type=int)
    p_sens.set_defaults(func=cmd_sensitivity)

    p_demo = sub.add_parser(
        "demo", help="Run the end-to-end demo on the synthetic log."
    )
    p_demo.add_argument("--config", default=Path("configs/pilot.yaml"), type=Path)
    p_demo.add_argument("--out", default=Path("reports/demo"), type=Path)
    p_demo.set_defaults(func=cmd_demo)

    p_val = sub.add_parser("validate", help="Validate a decision log schema.")
    p_val.add_argument("--log", required=True, type=Path)
    p_val.add_argument("--json", action="store_true")
    p_val.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
