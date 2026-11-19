"""Command-line interface for onboarding-audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from .config import load_config
from .pilot import run_pilot
from .schema import validate_log


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

    p_val = sub.add_parser("validate", help="Validate a decision log schema.")
    p_val.add_argument("--log", required=True, type=Path)
    p_val.add_argument("--json", action="store_true")
    p_val.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
