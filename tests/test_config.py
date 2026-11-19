from pathlib import Path

from onboarding_audit.config import load_config


def test_pilot_config_parses_covariate_scenarios():
    config = load_config(Path(__file__).parents[1] / "configs" / "pilot.yaml")
    scenarios = {s.id: s for s in config.scenarios}
    assert scenarios["covariate_model"].propensity_mode == "covariate"
    assert scenarios["covariate_model"].observation_mode == "covariate"
    assert scenarios["covariate_model"].covariate_beta == 0.75
    assert scenarios["covariate_action"].propensity_mode == "estimated"
    assert scenarios["covariate_oracle"].propensity_mode == "oracle"
