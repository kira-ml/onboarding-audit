"""Check the headline claims against the committed artifacts.

Every public number must trace to a committed JSON. This script recomputes the
headline values and compares them to the constants used in the README, the claim
ledger, and the one-pager. It runs in a second and needs no data.

Usage:
    python scripts/check_claims.py

Exits non-zero on a mismatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOL = 5e-4


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(payload: dict, scenario: str, estimator: str):
    return [
        r
        for r in payload["summary"]
        if r["scenario"] == scenario and r["estimator"] == estimator
    ]


def _max_abs(rows) -> float:
    return max(abs(r["rel_bias"]) for r in rows)


def _mean(values) -> float:
    return sum(values) / len(values)


def main() -> int:
    pilot = _load(ROOT / "reports" / "pilot.json")
    sweep = _load(ROOT / "reports" / "obs_sweep" / "pilot.json")
    sens = _load(ROOT / "reports" / "propensity_sensitivity.json")
    agg = sens["aggregate"]

    def sens_rows(scenario: str, estimator: str):
        return [
            r for r in agg if r["scenario"] == scenario and r["estimator"] == estimator
        ]

    checks: list[tuple[str, float, float]] = []

    # Main pilot.
    checks.append(
        ("main naive max |bias|", _max_abs(_rows(pilot, "main", "naive")), 2.7849)
    )
    dr_main = _rows(pilot, "main", "dr")
    checks.append(("main DR max |bias|", _max_abs(dr_main), 0.0094))
    checks.append(
        ("main DR mean coverage", _mean([r["coverage"] for r in dr_main]), 0.96)
    )
    ipw_main = _rows(pilot, "main", "ipw_ht")
    checks.append(("main IPW max |bias|", _max_abs(ipw_main), 0.0118))
    checks.append(
        ("main IPW mean coverage", _mean([r["coverage"] for r in ipw_main]), 0.945)
    )
    audit_main = _rows(pilot, "main", "audit_only")
    checks.append(("main audit max |bias|", _max_abs(audit_main), 0.0298))
    checks.append(
        ("main audit mean coverage", _mean([r["coverage"] for r in audit_main]), 0.845)
    )

    # Sweep: maximum across policies per cell.
    cells = sorted({r["scenario"] for r in sweep["summary"]})
    naive_cell_max = []
    incumbent_above = 0
    for cell in cells:
        rows = [
            r
            for r in sweep["summary"]
            if r["scenario"] == cell and r["estimator"] == "naive"
        ]
        naive_cell_max.append(max(abs(r["rel_bias"]) for r in rows))
        inc = [r for r in rows if r["policy"] == "incumbent"]
        if inc and abs(inc[0]["rel_bias"]) > 0.05:
            incumbent_above += 1
    checks.append(("sweep naive min cell max", min(naive_cell_max), 0.0776))
    checks.append(("sweep naive max cell max", max(naive_cell_max), 5.3846))
    checks.append(
        (
            "sweep cells with max naive >5%",
            float(sum(1 for v in naive_cell_max if v > 0.05)),
            12.0,
        )
    )
    checks.append(("sweep incumbent cells >5%", float(incumbent_above), 11.0))

    dr_cell_max = []
    for cell in cells:
        rows = [
            r
            for r in sweep["summary"]
            if r["scenario"] == cell and r["estimator"] == "dr"
        ]
        dr_cell_max.append(max(abs(r["rel_bias"]) for r in rows))
    checks.append(("sweep DR max mean bias", max(dr_cell_max), 0.0189))

    def mc_upper(cell: str) -> float:
        rows = [
            r
            for r in sweep["summary"]
            if r["scenario"] == cell and r["estimator"] == "dr"
        ]
        return max((abs(r["bias"]) + 1.96 * r["mc_se"]) / r["true"] for r in rows)

    checks.append(("sweep DR MC upper e020", mc_upper("e020_k090"), 0.0427))
    checks.append(("sweep DR MC upper e001", mc_upper("e001_k090"), 0.0963))

    # Bounds.
    main_bounds = [r for r in pilot["bounds"] if r["scenario"] == "main"]
    checks.append(
        ("main max bounds width", max(r["width"] for r in main_bounds), 0.009942)
    )
    frej = [
        r
        for r in pilot["bounds"]
        if r["scenario"] == "frej_002" and r["policy"] == "lenient_cost"
    ]
    checks.append(("frej_002 lenient width", frej[0]["width"], 0.203154))
    checks.append(
        (
            "F5 narrow passes",
            float(sum(1 for r in pilot["bounds"] if r["f5_pass"])),
            15.0,
        )
    )
    checks.append(
        (
            "F5 widened passes",
            float(sum(1 for r in pilot["bounds"] if r["f5_pass_unconditional"])),
            77.0,
        )
    )

    # Sensitivity.
    checks.append(
        (
            "estimated DR max |bias|",
            max(r["max_abs_rel_bias"] for r in sens_rows("propensity_estimated", "dr")),
            0.0143,
        )
    )
    checks.append(
        (
            "estimated IPW max |bias|",
            max(
                r["max_abs_rel_bias"]
                for r in sens_rows("propensity_estimated", "ipw_ht")
            ),
            0.0292,
        )
    )
    checks.append(
        (
            "outcome-dependent DR max |bias|",
            max(r["max_abs_rel_bias"] for r in sens_rows("outcome_dependent", "dr")),
            13.0153,
        )
    )
    checks.append(
        (
            "outcome-dependent estimated DR max |bias|",
            max(
                r["max_abs_rel_bias"]
                for r in sens_rows("outcome_dependent_estimated", "dr")
            ),
            17.3702,
        )
    )
    checks.append(
        (
            "outcome-dependent estimated IPW max |bias|",
            max(
                r["max_abs_rel_bias"]
                for r in sens_rows("outcome_dependent_estimated", "ipw_ht")
            ),
            20.6490,
        )
    )
    checks.append(
        (
            "covariate action IPW max |bias|",
            max(r["max_abs_rel_bias"] for r in sens_rows("covariate_action", "ipw_ht")),
            0.6752,
        )
    )
    checks.append(
        (
            "covariate action DR max |bias|",
            max(r["max_abs_rel_bias"] for r in sens_rows("covariate_action", "dr")),
            0.2125,
        )
    )
    checks.append(
        (
            "covariate model IPW max |bias|",
            max(r["max_abs_rel_bias"] for r in sens_rows("covariate_model", "ipw_ht")),
            0.0197,
        )
    )
    checks.append(
        (
            "covariate model DR max |bias|",
            max(r["max_abs_rel_bias"] for r in sens_rows("covariate_model", "dr")),
            0.0248,
        )
    )

    # Double robustness.
    dr_test = _load(ROOT / "reports" / "double_robustness.json")
    arms = dr_test["arms"]
    checks.append(
        (
            "DR correct e / wrong outcome",
            arms["correct_e_wrong_outcome"]["dr"]["rel_bias"],
            0.0014,
        )
    )
    checks.append(
        (
            "plug-in correct e / wrong outcome",
            arms["correct_e_wrong_outcome"]["plug_in"]["rel_bias"],
            0.0509,
        )
    )
    checks.append(
        (
            "DR wrong e / correct outcome",
            arms["wrong_e_correct_outcome"]["dr"]["rel_bias"],
            0.0036,
        )
    )
    checks.append(
        (
            "IPW wrong e / correct outcome",
            arms["wrong_e_correct_outcome"]["ipw"]["rel_bias"],
            -0.3672,
        )
    )
    checks.append(
        (
            "DR both wrong",
            arms["wrong_e_wrong_outcome"]["dr"]["rel_bias"],
            0.0209,
        )
    )

    # Temporal stability.
    temporal = _load(ROOT / "reports" / "temporal_stability.json")["results"]
    for month in ("month_5", "month_6"):
        r = temporal[month]
        checks.append(
            (
                f"{month} naive bias > 200%",
                r["naive_max_abs_rel_bias"],
                2.3037 if month == "month_5" else 2.5499,
            )
        )
        checks.append(
            (
                f"{month} DR bias < 1%",
                r["dr_max_abs_rel_bias"],
                0.0089 if month == "month_5" else 0.0043,
            )
        )
        checks.append((f"{month} naive P(best)", float(r["naive_p_best"]), 0.0))
        checks.append(
            (
                f"{month} DR P(best) > 60%",
                float(r["dr_p_best"]),
                0.65 if month == "month_5" else 0.63,
            )
        )

    # Reliability audit.
    audit = _load(ROOT / "reports" / "reliability_audit" / "summary.json")["overall"]
    checks.append(("audit replications", float(audit["n"]), 60.0))
    checks.append(("audit grade A", float(audit["grade_letters"].get("A", 0)), 1.0))
    checks.append(("audit grade B", float(audit["grade_letters"].get("B", 0)), 1.0))
    checks.append(("audit grade C", float(audit["grade_letters"].get("C", 0)), 38.0))
    checks.append(("audit grade D", float(audit["grade_letters"].get("D", 0)), 20.0))
    checks.append(("audit released", float(audit["released_n"]), 2.0))
    checks.append(
        ("audit false certifications", float(audit["false_certification_n"]), 0.0)
    )
    checks.append(("audit directional", float(audit["directional_n"]), 11.0))
    checks.append(
        ("audit directional withheld", float(audit["directional_withheld_n"]), 9.0)
    )
    checks.append(
        (
            "audit identified directional accuracy",
            float(audit["identified_directional_accuracy"]),
            4.0 / 7.0,
        )
    )
    checks.append(
        (
            "audit all directional accuracy",
            float(audit["directional_accuracy_all"]),
            5.0 / 11.0,
        )
    )
    checks.append(
        ("audit no-A/B release", float(audit["abstention_rate"]), 58.0 / 60.0)
    )
    audit_pilot = _load(ROOT / "reports" / "reliability_audit" / "pilot.json")
    checks.append(
        ("audit bootstrap replicates", float(audit_pilot["reliability_n_boot"]), 100.0)
    )
    restricted = _load(
        ROOT / "reports" / "reliability_audit_restricted" / "summary.json"
    )["overall"]
    checks.append(
        (
            "restricted audit grade A",
            float(restricted["grade_letters"].get("A", 0)),
            5.0,
        )
    )
    checks.append(
        (
            "restricted audit grade C",
            float(restricted["grade_letters"].get("C", 0)),
            35.0,
        )
    )
    checks.append(
        (
            "restricted audit grade D",
            float(restricted["grade_letters"].get("D", 0)),
            20.0,
        )
    )
    checks.append(("restricted audit releases", float(restricted["released_n"]), 5.0))
    checks.append(
        (
            "restricted audit false certifications",
            float(restricted["false_certification_n"]),
            5.0,
        )
    )
    restricted_main = _load(ROOT / "reports" / "restricted_main100" / "pilot.json")
    restricted_dr = [
        r
        for r in restricted_main["summary"]
        if r["scenario"] == "main" and r["estimator"] == "dr"
    ]
    checks.append(("restricted DR max |bias|", _max_abs(restricted_dr), 0.0133))
    restricted_rank = [
        r
        for r in restricted_main["ranking"]
        if r["scenario"] == "main" and r["estimator"] == "dr"
    ]
    checks.append(
        ("restricted DR P(best)", float(restricted_rank[0]["p_select_true_best"]), 0.60)
    )
    case_report = _load(ROOT / "reports" / "case_reliability" / "report.json")["result"]
    case_rel = case_report["diagnostics"]["reliability"]
    demo_report = _load(ROOT / "reports" / "demo_reliability" / "report.json")["result"]
    demo_rel = demo_report["diagnostics"]["reliability"]
    checks.append(
        (
            "case grade A",
            1.0 if str(case_rel["profile"]["grade"]).startswith("A") else 0.0,
            1.0,
        )
    )
    checks.append(
        (
            "case bootstrap P(better)",
            float(case_rel["bootstrap"]["p_candidate_better_boot"]),
            0.998,
        )
    )
    checks.append(
        (
            "case cost-stress cells same",
            float(case_rel["cost_stress"]["same_decision_share"]),
            1.0,
        )
    )
    checks.append(
        (
            "demo grade C",
            1.0 if str(demo_rel["profile"]["grade"]).startswith("C") else 0.0,
            1.0,
        )
    )
    checks.append(
        (
            "demo bootstrap P(better)",
            float(demo_rel["bootstrap"]["p_candidate_better_boot"]),
            0.934,
        )
    )
    checks.append(
        (
            "demo cost-stress share",
            float(demo_rel["cost_stress"]["same_decision_share"]),
            6.0 / 9.0,
        )
    )

    # Case study.
    case = _load(ROOT / "examples" / "case_truth.json")
    checks.append(
        (
            "case naive ranking flips (candidate worse)",
            1.0 if case["naive_candidate"] > case["naive_incumbent"] else 0.0,
            1.0,
        )
    )
    checks.append(
        (
            "case true ranking favors candidate",
            1.0 if case["true_candidate"] < case["true_incumbent"] else 0.0,
            1.0,
        )
    )
    checks.append(
        (
            "case true candidate cost",
            case["true_candidate"],
            0.601556,
        )
    )

    failures = 0
    for name, computed, expected in checks:
        ok = abs(computed - expected) <= TOL
        failures += 0 if ok else 1
        status = "PASS" if ok else "FAIL"
        print(f"{status}  {name:<42} computed={computed:.6f} expected={expected:.6f}")
    print(f"\n{len(checks) - failures}/{len(checks)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
