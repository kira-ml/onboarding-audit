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
    )
    assert result.identification.passed
    assert result.propensity.source == "estimated"
    memo = Path(result.memo_path).read_text(encoding="utf-8")
    assert "Measured" in memo
    naive_err = abs(result.estimates["naive"]["value"] - truth["true_p0"])
    dr_err = abs(result.estimates["dr"]["value"] - truth["true_p0"])
    assert dr_err < naive_err
