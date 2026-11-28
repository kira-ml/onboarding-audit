import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "prepare_baf", ROOT / "scripts" / "prepare_baf.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tiny_frame(n=40):
    return pd.DataFrame(
        {
            "fraud_bool": [0, 1] * (n // 2),
            "month": [0, 1, 2, 3, 4, 5, 6, 7] * (n // 8),
            "proposed_credit_limit": [100.0 + i for i in range(n)],
            "income": [0.5] * n,
            "payment_type": ["AA"] * n,
            "device_fraud_count": [0] * n,
        }
    )


def test_normalize_adds_id_and_amount_and_sorts_by_month():
    module = _load()
    df = module.normalize(_tiny_frame())
    assert sorted(df["transaction_id"]) == list(range(len(df)))
    assert df["month"].is_monotonic_increasing
    assert (df["amount_proxy"] == df["proposed_credit_limit"]).all()


def test_delay_marks_month_seven_censored():
    module = _load()
    df = module.simulate_delay(module.normalize(_tiny_frame()))
    assert (df.loc[df["month"] == 7, "label_month"] == 8).all()
    assert not df.loc[df["month"] == 7, "observed"].any()
    assert df.loc[df["month"] == 6, "observed"].all()


def test_features_exclude_target_id_time_and_exposure():
    module = _load()
    df = module.simulate_delay(module.normalize(_tiny_frame()))
    features = module.feature_columns(df)
    for forbidden in module.FEATURE_EXCLUDE:
        assert forbidden not in features
    for forbidden in module.PROTECTED_COLUMNS:
        assert forbidden not in features
    assert "fraud_bool" not in features
    assert "month" not in features
    assert "amount_proxy" not in features
    legacy = module.feature_columns(df, include_protected=True)
    assert "income" in legacy


def test_train_and_test_months_are_disjoint():
    module = _load()
    assert not set(module.TRAIN_MONTHS) & set(module.TEST_MONTHS)
    assert not set(module.TRAIN_MONTHS) & set(module.VAL_MONTHS)
    assert not set(module.VAL_MONTHS) & set(module.TEST_MONTHS)


def test_recorded_hash_and_row_count_are_pinned():
    module = _load()
    assert len(module.EXPECTED_SHA256) == 64
    assert module.EXPECTED_ROWS == 227_491


def test_provenance_doc_matches_script_constants():
    module = _load()
    text = (ROOT / "docs" / "BENCHMARK_PROVENANCE.md").read_text(encoding="utf-8")
    assert module.EXPECTED_SHA256 in text
    assert f"{module.EXPECTED_ROWS:,}" in text
    assert "7bf10a37ce07e72e14c1b09e5efee3d27261baff4facc7da767b0474dcf9b809" in text
