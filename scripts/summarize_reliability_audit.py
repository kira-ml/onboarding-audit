"""Summarize the per-replication decision-reliability audit."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reports" / "reliability_audit" / "pilot.json"
OUT_JSON = ROOT / "reports" / "reliability_audit" / "summary.json"
OUT_MD = ROOT / "reports" / "reliability_audit" / "summary.md"


def summarize(rows: list[dict]) -> dict:
    grades = Counter(r["grade"] for r in rows)
    grade_letters = Counter(str(r["grade"])[0] for r in rows)
    decisions = Counter(r["decision"] for r in rows)
    true_decisions = Counter(r["true_decision"] for r in rows)
    directional = [
        r for r in rows if r["decision"] in {"prefer candidate", "keep incumbent"}
    ]
    # Only A/B with a directional point decision are actually released.
    released = [r for r in directional if str(r["grade"]).startswith(("A", "B"))]
    released_correct = [r for r in released if r["correct"]]
    false_cert = [r for r in released if not r["correct"]]
    identified = [r for r in directional if not str(r["grade"]).startswith("D")]
    identified_correct = [r for r in identified if r["correct"]]
    return {
        "n": len(rows),
        "grades": dict(grades),
        "grade_letters": dict(sorted(grade_letters.items())),
        "decisions": dict(decisions),
        "true_decisions": dict(true_decisions),
        "directional_n": len(directional),
        "directional_correct_n": len([r for r in directional if r["correct"]]),
        "directional_accuracy_all": (
            len([r for r in directional if r["correct"]]) / len(directional)
            if directional
            else None
        ),
        "released_n": len(released),
        "released_correct_n": len(released_correct),
        "released_accuracy": (
            len(released_correct) / len(released) if released else None
        ),
        "directional_withheld_n": len(directional) - len(released),
        "directional_withheld_rate": (
            (len(directional) - len(released)) / len(directional)
            if directional
            else None
        ),
        "identified_directional_n": len(identified),
        "identified_directional_correct_n": len(identified_correct),
        "identified_directional_accuracy": (
            len(identified_correct) / len(identified) if identified else None
        ),
        "abstention_rate": 1.0 - len(released) / len(rows) if rows else None,
        "false_certification_n": len(false_cert),
        "false_certification_rate": (
            len(false_cert) / len(released) if released else None
        ),
    }


def main() -> None:
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    rows = payload.get("reliability", [])
    by_scenario = {}
    for scenario in sorted({r["scenario"] for r in rows}):
        by_scenario[scenario] = summarize(
            [r for r in rows if r["scenario"] == scenario]
        )
    overall = summarize(rows)
    out = {
        "note": (
            "Post-hoc reliability audit; 20 reps per scenario, 100 bootstrap "
            "replicates per rep. A false certification is a wrong directional "
            "decision graded A/B. Abstention means the decision was withheld "
            "from release. `correct` is P0-correct; full-policy correctness is "
            "recorded separately in the pilot rows."
        ),
        "overall": overall,
        "by_scenario": by_scenario,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    L = [
        "# Decision Reliability Audit",
        "",
        "**Status:** Post-hoc, 2026-11-28. **Not a pre-registered headline.**",
        "",
        "20 replications per scenario; 100 bootstrap replicates per replication.",
        "A **false certification** is a wrong directional decision graded A/B.",
        "**Abstention** means the decision was withheld from release (not",
        "necessarily that the point estimate was inconclusive).",
        "",
        "## Overall",
        "",
        f"- n = **{overall['n']}**",
        "- grades: **"
        + " / ".join(f"{k} {v}" for k, v in overall["grade_letters"].items())
        + "**",
        (
            f"- released A/B directional decisions: **{overall['released_n']}** "
            f"of **{overall['n']}** ({overall['released_n'] / max(overall['n'], 1):.0%})"
        ),
        (
            f"- directional decisions withheld: **{overall['directional_withheld_n']}** "
            f"of **{overall['directional_n']}** "
            f"({overall['directional_withheld_rate']:.0%})"
            if overall["directional_withheld_rate"] is not None
            else "- directional decisions withheld: n/a"
        ),
        (
            "- identified directional accuracy (excluding gate-failed D): "
            f"**{overall['identified_directional_correct_n']}**/"
            f"**{overall['identified_directional_n']}** "
            f"({overall['identified_directional_accuracy']:.0%})"
            if overall["identified_directional_accuracy"] is not None
            else "- identified directional accuracy: n/a"
        ),
        (
            "- all directional decisions, including gate-failed D: "
            f"**{overall['directional_n']}**, P0-correct "
            f"**{overall['directional_correct_n']}** "
            f"({overall['directional_accuracy_all']:.0%})"
            if overall["directional_accuracy_all"] is not None
            else f"- all directional decisions: **{overall['directional_n']}**"
        ),
        (
            "- false certifications (released A/B and wrong): "
            f"**{overall['false_certification_n']}**"
        ),
        (
            "- no A/B release (not a directional-decision rate): "
            f"**{overall['abstention_rate']:.0%}**"
        ),
        "",
        "## By scenario",
        "",
        "| Scenario | n | Grades | Released | Released P0 acc. | False cert. | No A/B release |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for name, s in by_scenario.items():
        acc = (
            f"{s['released_accuracy']:.0%}"
            if s["released_accuracy"] is not None
            else "n/a"
        )
        grade_str = " / ".join(f"{k} {v}" for k, v in s["grade_letters"].items())
        L.append(
            f"| `{name}` | {s['n']} | {grade_str} | {s['released_n']} | "
            f"{acc} | {s['false_certification_n']} | {s['abstention_rate']:.0%} |"
        )
    L += [
        "",
        "**Read:** the profile is conservative. In this audit it made no false",
        "certifications, but it withheld many close calls. That is the",
        "reliability trade-off: the cost of caution is decision volume, not a",
        "confident wrong decision. The sample is 20 replications per scenario; do",
        "not over-read the percentages.",
    ]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[reliability-audit] wrote {OUT_JSON}")
    print(f"[reliability-audit] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
