from pathlib import Path

from onboarding_audit.sensitivity import write_markdown


def _row(scenario, estimator, bias, coverage, ess=1000):
    return {
        "scenario": scenario,
        "estimator": estimator,
        "max_abs_rel_bias": bias,
        "mean_coverage": coverage,
        "mean_ess": ess,
        "reps": 2,
    }


def test_write_markdown_from_payload(tmp_path):
    payload = {
        "reps": 2,
        "scenarios": ["covariate_action", "covariate_model"],
        "summary": [],
        "aggregate": [
            _row("covariate_oracle", "ipw_ht", 0.03, 0.90),
            _row("covariate_oracle", "dr", 0.02, 0.89),
            _row("covariate_action", "ipw_ht", 0.67, 0.02),
            _row("covariate_action", "dr", 0.21, 0.72),
            _row("covariate_model", "ipw_ht", 0.02, 0.91),
            _row("covariate_model", "dr", 0.03, 0.89),
            _row("covariate_action_delay", "ipw_ht", 0.52, 0.22),
            _row("covariate_action_delay", "dr", 0.18, 0.80),
            _row("covariate_model_delay", "ipw_ht", 0.03, 0.90),
            _row("covariate_model_delay", "dr", 0.04, 0.89),
        ],
    }
    path = write_markdown(payload, tmp_path)
    assert isinstance(path, Path)
    text = path.read_text(encoding="utf-8")
    assert "Measured read" in text
    assert "67.00%" in text
    assert "1.97%" not in text  # no invented number
    assert "Covariate model: IPW **2.00%**" in text
