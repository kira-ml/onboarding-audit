import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "double_robustness", ROOT / "scripts" / "double_robustness.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dr_beats_ipw_when_propensity_is_wrong():
    module = _load()
    module.TRUE_VALUE = module._true_value(np.random.default_rng(1), 100_000)
    arm = module._run_arm(
        np.random.default_rng(2),
        reps=3,
        n=10_000,
        wrong_outcome=False,
        wrong_propensity=True,
    )
    assert abs(arm["dr"]["rel_bias"]) < abs(arm["ipw"]["rel_bias"])


def test_dr_beats_plugin_when_outcome_model_is_wrong():
    module = _load()
    module.TRUE_VALUE = module._true_value(np.random.default_rng(1), 100_000)
    arm = module._run_arm(
        np.random.default_rng(3),
        reps=3,
        n=10_000,
        wrong_outcome=True,
        wrong_propensity=False,
    )
    assert abs(arm["dr"]["rel_bias"]) < abs(arm["plug_in"]["rel_bias"])
