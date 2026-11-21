import json
from pathlib import Path

from onboarding_audit.report import run_report

ROOT = Path(__file__).resolve().parents[1]


def test_case_study_flips_the_naive_ranking(tmp_path):
    truth = json.loads(
        (ROOT / "examples" / "case_truth.json").read_text(encoding="utf-8")
    )
    # The naive ranking is wrong; the true ranking favors the candidate.
    assert truth["naive_candidate"] > truth["naive_incumbent"]
    assert truth["true_candidate"] < truth["true_incumbent"]

    result = run_report(
        ROOT / "examples" / "case_log.csv",
        ROOT / "examples" / "case_candidate.csv",
        ROOT / "configs" / "case_study.yaml",
        tmp_path / "case",
        capacity=0.05,
        observation_assumption="action",
    )
    assert result.identification.passed
    comp = result.comparison
    assert comp["difference"] < 0
    assert comp["difference_ci_high"] < 0
    assert comp["p_candidate_better"] >= 0.95
    assert comp["decision"] == "prefer candidate"
    assert comp["regret_candidate"] < comp["regret_incumbent"]
