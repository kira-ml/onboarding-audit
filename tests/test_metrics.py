import numpy as np
import pandas as pd

from onboarding_audit.metrics import bounds_summary, pairwise_inversions


def test_pairwise_inversions_known_example():
    est = np.array([1.0, 2.0, 3.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 0
    est = np.array([3.0, 2.0, 1.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 3
    est = np.array([1.0, 3.0, 2.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 1


def test_pairwise_inversions_ties_are_not_inversions():
    est = np.array([1.0, 1.0, 2.0])
    true = np.array([1.0, 2.0, 3.0])
    assert pairwise_inversions(est, true) == 0


def test_bounds_summary_records_f5_and_unconditional_coverage():
    rows = pd.DataFrame(
        [
            {
                "scenario": "main",
                "policy": "incumbent",
                "estimator": "bounds",
                "true_full": 0.10,
                "lower": 0.00,
                "upper": 0.20,
                "lower_unconditional": -0.01,
                "upper_unconditional": 0.21,
                "n_rejected": 10,
            },
            {
                "scenario": "main",
                "policy": "incumbent",
                "estimator": "bounds",
                "true_full": 0.30,
                "lower": 0.00,
                "upper": 0.20,
                "lower_unconditional": -0.01,
                "upper_unconditional": 0.21,
                "n_rejected": 10,
            },
        ]
    )
    out = bounds_summary(rows)
    assert out.iloc[0]["coverage_full"] == 0.5
    assert not bool(out.iloc[0]["f5_pass"])
    assert out.iloc[0]["unconditional_coverage"] == 0.5

    inside = rows.copy()
    inside["true_full"] = 0.10
    out_inside = bounds_summary(inside)
    assert bool(out_inside.iloc[0]["f5_pass"])
    assert out_inside.iloc[0]["unconditional_coverage"] == 1.0
