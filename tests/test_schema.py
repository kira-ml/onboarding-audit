import pandas as pd

from onboarding_audit.schema import validate_log


def _valid_frame(n=10):
    return pd.DataFrame(
        {
            "application_id": [f"app_{i}" for i in range(n)],
            "application_time": pd.date_range("2026-06-01", periods=n, freq="h"),
            "decision_time": pd.date_range("2026-06-01 00:01", periods=n, freq="h"),
            "action": ["approve"] * n,
            "score": [0.01] * n,
            "amount": [200.0] * n,
            "reviewed": [0] * n,
            "audit_flag": [0] * n,
            "label": [0] * n,
            "label_time": pd.date_range("2026-07-01", periods=n, freq="h"),
            "label_source": ["audit"] * n,
            "propensity": [0.05] * n,
            "customer_age": [30] * n,
        }
    )


def test_valid_log_passes():
    report = validate_log(_valid_frame())
    assert report.ok
    assert report.estimator_readiness["naive"]
    assert report.estimator_readiness["ipw"]
    assert report.estimator_readiness["audit_only"]


def test_missing_required_column_fails():
    df = _valid_frame().drop(columns=["score"])
    report = validate_log(df)
    assert not report.ok
    assert any("missing required columns" in e for e in report.errors)


def test_invalid_action_fails():
    df = _valid_frame()
    df.loc[0, "action"] = "block"
    report = validate_log(df)
    assert not report.ok


def test_reviewed_requires_review_action():
    df = _valid_frame()
    df.loc[0, "reviewed"] = 1
    report = validate_log(df)
    assert not report.ok
    assert any("reviewed=1" in e for e in report.errors)


def test_audit_requires_approve_action():
    df = _valid_frame()
    df.loc[0, "action"] = "review"
    df.loc[0, "reviewed"] = 1
    df.loc[0, "audit_flag"] = 1
    report = validate_log(df)
    assert not report.ok
    assert any("audit_flag=1" in e for e in report.errors)


def test_missing_label_breaks_naive():
    df = _valid_frame().drop(columns=["label", "label_time"])
    report = validate_log(df)
    assert report.ok  # the schema can still be valid for other estimators
    assert not report.estimator_readiness["naive"]
