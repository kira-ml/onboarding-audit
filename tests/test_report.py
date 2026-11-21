import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from onboarding_audit.config import load_config
from onboarding_audit.policies import apply_capacity, choose_actions, realized_cost
from onboarding_audit.report import estimate_propensities, run_report

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "pilot.yaml"


def _synthetic_log(n=2500, seed=7, with_propensity=True, audit=True):
    rng = np.random.default_rng(seed)
    score = rng.beta(2, 8, n)
    y = rng.binomial(1, np.clip(0.005 + 0.45 * score, 0, 1))
    amount = rng.uniform(200, 1000, n)
    action = np.where(
        score > 0.70, "reject", np.where(score > 0.45, "review", "approve")
    )
    reviewed = action == "review"
    approve = action == "approve"
    audit_flag = approve & (rng.random(n) < 0.02) if audit else np.zeros(n, bool)
    base = approve & (rng.random(n) < 0.05)
    review_obs = reviewed & (rng.random(n) < 0.90)
    observed = review_obs | audit_flag | base

    label = np.where(observed, y, np.nan)
    decision_time = pd.Timestamp("2026-06-01") + pd.to_timedelta(
        rng.integers(0, 60, n), unit="D"
    )
    label_time = pd.Series(decision_time) + pd.to_timedelta(30, unit="D")
    label_time = label_time.where(observed)

    label_source = np.full(n, "none", dtype=object)
    label_source[review_obs] = "review"
    label_source[audit_flag] = "audit"
    label_source[base & ~audit_flag] = "post_approval_report"

    propensity = np.full(n, np.nan)
    propensity[reviewed] = 0.90
    propensity[approve] = 0.02 + 0.98 * 0.05 if audit else 0.05
    propensity = np.where(observed, propensity, np.nan)

    df = pd.DataFrame(
        {
            "application_id": [f"app_{i:05d}" for i in range(n)],
            "application_time": decision_time,
            "decision_time": decision_time,
            "action": action,
            "score": score,
            "amount": amount,
            "reviewed": reviewed.astype(int),
            "audit_flag": audit_flag.astype(int),
            "label": label,
            "label_time": label_time,
            "label_source": label_source,
            "customer_age": rng.integers(18, 70, n),
            "credit_risk_score": rng.normal(100, 20, n),
            "p_fraud": score,
            "p_fraud_lgbm": np.clip(score + rng.normal(0, 0.05, n), 0, 1),
        }
    )
    if with_propensity:
        df["propensity"] = propensity
    candidate = pd.DataFrame(
        {
            "application_id": df["application_id"],
            "score": np.clip(score + rng.normal(0, 0.05, n), 0, 1),
        }
    )
    return df, candidate, y, amount, score


def _true_p0(df, candidate, y, amount, capacity=0.10):
    config = load_config(CONFIG)
    _, (ca, cr, cj) = choose_actions(
        candidate["score"].to_numpy(float), config.costs, amount
    )
    k = int(np.ceil(capacity * len(df)))
    actions = apply_capacity(ca, cr, cj, k)
    cost = realized_cost(actions, y, amount, config.costs)
    in_pop = df["action"].to_numpy() != "reject"
    return float(cost[in_pop].mean())


def test_report_runs_and_dr_beats_naive(tmp_path):
    df, candidate, y, amount, _ = _synthetic_log(with_propensity=True)
    log_path = tmp_path / "log.csv"
    cand_path = tmp_path / "candidate.csv"
    df.to_csv(log_path, index=False)
    candidate.to_csv(cand_path, index=False)

    result = run_report(
        log_path,
        cand_path,
        CONFIG,
        tmp_path / "out",
        capacity=0.10,
    )
    assert result.propensity.source == "provided"
    assert result.propensity.positivity_ok
    assert result.identification.passed
    assert Path(result.memo_path).exists()
    assert Path(result.report_path).exists()
    memo = Path(result.memo_path).read_text(encoding="utf-8")
    assert "Measured" in memo

    truth = _true_p0(df, candidate, y, amount, capacity=0.10)
    naive_err = abs(result.estimates["naive"]["value"] - truth)
    dr_err = abs(result.estimates["dr"]["value"] - truth)
    assert np.isfinite(dr_err)
    assert dr_err < naive_err


def test_report_estimates_propensity_when_missing(tmp_path):
    df, candidate, y, amount, _ = _synthetic_log(with_propensity=False)
    log_path = tmp_path / "log.csv"
    cand_path = tmp_path / "candidate.csv"
    df.to_csv(log_path, index=False)
    candidate.to_csv(cand_path, index=False)

    result = run_report(
        log_path,
        cand_path,
        CONFIG,
        tmp_path / "out",
        capacity=0.10,
    )
    assert result.propensity.source == "estimated"
    assert result.propensity.positivity_ok
    assert result.identification.passed
    assert 0 < result.propensity.e_review <= 1
    assert 0 < result.propensity.e_approve <= 1


def test_report_without_audit_has_no_audit_only_estimate(tmp_path):
    df, candidate, y, amount, _ = _synthetic_log(with_propensity=True, audit=False)
    log_path = tmp_path / "log.csv"
    cand_path = tmp_path / "candidate.csv"
    df.to_csv(log_path, index=False)
    candidate.to_csv(cand_path, index=False)

    result = run_report(
        log_path,
        cand_path,
        CONFIG,
        tmp_path / "out",
        capacity=0.10,
    )
    assert not np.isfinite(result.estimates["audit_only"]["value"])
    assert Path(result.memo_path).exists()


def test_report_rejects_missing_candidate_ids(tmp_path):
    df, candidate, _, _, _ = _synthetic_log(n=100)
    log_path = tmp_path / "log.csv"
    cand_path = tmp_path / "candidate.csv"
    df.to_csv(log_path, index=False)
    candidate.iloc[:-1].to_csv(cand_path, index=False)

    with pytest.raises(ValueError):
        run_report(log_path, cand_path, CONFIG, tmp_path / "out", capacity=0.10)


def test_report_rejects_invalid_log(tmp_path):
    df, candidate, _, _, _ = _synthetic_log(n=100)
    df = df.drop(columns=["score"])
    log_path = tmp_path / "log.csv"
    cand_path = tmp_path / "candidate.csv"
    df.to_csv(log_path, index=False)
    candidate.to_csv(cand_path, index=False)

    with pytest.raises(ValueError):
        run_report(log_path, cand_path, CONFIG, tmp_path / "out")


def test_report_withholds_point_estimate_on_small_log(tmp_path):
    df, candidate, _, _, _ = _synthetic_log(n=20)
    log_path = tmp_path / "log.csv"
    cand_path = tmp_path / "candidate.csv"
    df.to_csv(log_path, index=False)
    candidate.to_csv(cand_path, index=False)

    result = run_report(
        log_path,
        cand_path,
        CONFIG,
        tmp_path / "out",
        capacity=0.10,
    )
    assert not result.identification.passed
    memo = Path(result.memo_path).read_text(encoding="utf-8")
    assert "Not identified" in memo
    assert "Point estimates are withheld" in memo
    assert "| `P0` policy value is estimated | Measured |" not in memo
    report = json.loads(Path(result.report_path).read_text(encoding="utf-8"))
    assert "policy_value_target_5pct" not in report["result"]["audit"]


def test_covariate_propensity_model_varies_within_action():
    rng = np.random.default_rng(0)
    n = 6000
    amount = rng.uniform(100, 2000, n)
    log_amount = np.log1p(amount)
    z = (log_amount - log_amount.mean()) / log_amount.std()
    p = 1.0 / (1.0 + np.exp(-(-3.0 + 1.0 * z)))
    action = np.where(rng.random(n) < 0.7, "approve", "review")
    observed = np.zeros(n, dtype=bool)
    approve = action == "approve"
    review = action == "review"
    observed[approve] = rng.random(approve.sum()) < p[approve]
    observed[review] = rng.random(review.sum()) < 0.90
    df = pd.DataFrame(
        {
            "application_id": [f"a{i}" for i in range(n)],
            "action": action,
            "amount": amount,
            "label": np.where(observed, 0, np.nan),
            "audit_flag": 0,
            "customer_age": rng.integers(18, 70, n),
            "credit_risk_score": rng.normal(100, 20, n),
        }
    )
    propensity = estimate_propensities(
        df,
        propensity_model="covariate",
        feature_cols=["customer_age", "credit_risk_score"],
    )
    assert propensity.source == "estimated_covariate"
    assert propensity.positivity_ok
    assert propensity.e[approve].std() > 0.001
    assert np.corrcoef(propensity.e[approve], p[approve])[0, 1] > 0.5


def test_report_covariate_propensity_model_runs(tmp_path):
    df, candidate, _, _, _ = _synthetic_log(with_propensity=False)
    log_path = tmp_path / "log.csv"
    cand_path = tmp_path / "candidate.csv"
    df.to_csv(log_path, index=False)
    candidate.to_csv(cand_path, index=False)

    result = run_report(
        log_path,
        cand_path,
        CONFIG,
        tmp_path / "out",
        capacity=0.10,
        propensity_model="covariate",
        propensity_features=["customer_age", "credit_risk_score", "p_fraud"],
    )
    assert result.propensity.source == "estimated_covariate"
    assert result.propensity.positivity_ok
    assert result.identification.passed
    assert Path(result.memo_path).exists()
    memo = Path(result.memo_path).read_text(encoding="utf-8")
    assert "Propensity model" in memo
