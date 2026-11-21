import numpy as np
import pandas as pd
import pytest

from onboarding_audit.data import _decision_day, load_eval_data


def _frame():
    return pd.DataFrame(
        {
            "fraud_bool": [0, 1, 0, 1],
            "amount_proxy": [100.0, 200.0, 300.0, 400.0],
            "month": [5, 5, 6, 6],
            "score": [0.1, 0.4, 0.6, 0.9],
        }
    )


def test_single_month_maps_to_the_first_window():
    month = np.array([5, 5, 5])
    day = _decision_day(month, np.random.default_rng(0), months=(5,))
    assert ((day >= 0) & (day < 30)).all()


def test_two_months_map_to_consecutive_windows():
    month = np.array([5, 6])
    day = _decision_day(month, np.random.default_rng(0), months=(5, 6))
    assert 0 <= day[0] < 30
    assert 30 <= day[1] < 60


def test_invalid_month_raises():
    with pytest.raises(ValueError):
        _decision_day(np.array([7]), np.random.default_rng(0), months=(5, 6))


def test_load_eval_data_filters_months(tmp_path):
    path = tmp_path / "frame.parquet"
    _frame().to_parquet(path, index=False)
    one = load_eval_data(
        path,
        label_col="fraud_bool",
        amount_col="amount_proxy",
        month_col="month",
        outcome_features=["score"],
        seed=0,
        months=(5,),
    )
    assert one.n == 2
    assert set(one.month.tolist()) == {5}
    assert ((one.decision_day >= 0) & (one.decision_day < 30)).all()

    both = load_eval_data(
        path,
        label_col="fraud_bool",
        amount_col="amount_proxy",
        month_col="month",
        outcome_features=["score"],
        seed=0,
        months=(5, 6),
    )
    assert both.n == 4
