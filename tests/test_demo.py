import json
from pathlib import Path

from onboarding_audit.report import run_report

ROOT = Path(__file__).resolve().parents[1]


def test_demo_report_passes_gate_and_dr_beats_naive(tmp_path):
    truth = json.loads(
        (ROOT / "examples" / "demo_truth.json").read_text(encoding="utf-8")
    )
    result = run_report(
        ROOT / "examples" / "demo_log.csv",
        ROOT / "examples" / "demo_candidate.csv",
        ROOT / "configs" / "pilot.yaml",
        tmp_path / "demo",
        capacity=0.10,
        observation_assumption="action",
    )
    assert result.identification.passed
    assert result.propensity.source == "estimated"
    memo = Path(result.memo_path).read_text(encoding="utf-8")
    assert "`P0`-conditional policy value is estimated | Measured |" in memo
    assert "action-dependent (declared)" in memo
    assert "Candidate vs incumbent" in memo
    assert "P(candidate cheaper)" in memo
    assert result.comparison["decision"] in {
        "prefer candidate",
        "keep incumbent",
        "inconclusive",
    }
    assert result.comparison["difference"] < 0
    naive_err = abs(result.estimates["naive"]["value"] - truth["true_p0"])
    dr_err = abs(result.estimates["dr"]["value"] - truth["true_p0"])
    assert dr_err < naive_err
