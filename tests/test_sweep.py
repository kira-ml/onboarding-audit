from pathlib import Path

from onboarding_audit.config import Observation, load_config

ROOT = Path(__file__).resolve().parents[1]


def test_obs_sweep_config_has_twelve_cells():
    config = load_config(ROOT / "configs" / "obs_sweep.yaml")
    assert len(config.scenarios) == 12
    assert {s.e_approve for s in config.scenarios} == {0.01, 0.05, 0.20, 0.50}
    assert {s.kappa_review for s in config.scenarios} == {0.50, 0.90, 1.00}
    assert all(s.reps == 50 for s in config.scenarios)


def test_observation_override_accepts_e_and_kappa():
    observation = Observation(e_approve=0.05, kappa_review=0.90)
    overridden = observation.with_overrides(e_approve=0.20, kappa_review=0.50)
    assert overridden.e_approve == 0.20
    assert overridden.kappa_review == 0.50
