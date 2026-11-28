"""Generate the reproducible case study: a better candidate that looks worse.

The log is synthetic and small enough to commit. The incumbent reviews the top
5% of its score; the candidate reviews the top 5% of a less noisy score. Approved
applications are labeled at 8%, reviewed applications at 90%, so the naive
labeled mean is dominated by review rows. The candidate's review set is enriched
in fraud, so its naive mean is *higher* even though its true cost is lower.

The case config sets a high false-reject cost, so the policy is approve-vs-review
and the case isolates selective labels rather than the reject margin.

Usage:
    python scripts/make_case_study.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from onboarding_audit.config import load_config
from onboarding_audit.policies import apply_capacity, choose_actions, realized_cost

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples"
N = 20_000
CAPACITY = 0.05


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def main() -> None:
    rng = np.random.default_rng(20261121)
    z = rng.normal(size=N)
    p_true = _sigmoid(-4.2 + 1.8 * z)
    y = rng.binomial(1, p_true)
    amount = rng.uniform(200, 2000, N)
    # Both scores are calibrated around the true probability; the candidate is
    # less noisy, so it ranks better without a calibration advantage.
    incumbent = np.clip(p_true + rng.normal(0, 0.080, N), 1e-4, 1 - 1e-4)
    candidate = np.clip(p_true + rng.normal(0, 0.003, N), 1e-4, 1 - 1e-4)

    config = load_config(ROOT / "configs" / "case_study.yaml")
    k = int(np.ceil(CAPACITY * N))

    _, (i_app, i_rev, i_rej) = choose_actions(incumbent, config.costs, amount)
    incumbent_actions = apply_capacity(i_app, i_rev, i_rej, k)
    _, (c_app, c_rev, c_rej) = choose_actions(candidate, config.costs, amount)
    candidate_actions = apply_capacity(c_app, c_rev, c_rej, k)

    review = incumbent_actions == "review"
    in_pop = incumbent_actions != "reject"

    audit = (~review) & (rng.random(N) < 0.01)
    approve_obs = (~review) & (~audit) & (rng.random(N) < 0.08)
    review_obs = review & (rng.random(N) < 0.90)
    observed = review_obs | audit | approve_obs

    decision_time = pd.Timestamp("2026-06-01") + pd.to_timedelta(
        rng.integers(0, 60, N), unit="D"
    )
    application_time = decision_time - pd.to_timedelta(2, unit="s")
    label_time = pd.Series(decision_time) + pd.to_timedelta(
        rng.integers(30, 61, N), unit="D"
    )
    label_time = label_time.where(observed)
    label_source = np.full(N, "none", dtype=object)
    label_source[review_obs] = "review"
    label_source[audit] = "audit"
    label_source[approve_obs & ~audit] = "post_approval_report"

    df = pd.DataFrame(
        {
            "application_id": [f"case_{i:05d}" for i in range(N)],
            "application_time": application_time,
            "decision_time": decision_time,
            "action": incumbent_actions,
            "score": incumbent,
            "amount": amount,
            "reviewed": review.astype(int),
            "audit_flag": audit.astype(int),
            "label": np.where(observed, y, np.nan),
            "label_time": label_time,
            "label_source": label_source,
            "propensity": np.where(review, 0.90, 1.0 - (1.0 - 0.01) * (1.0 - 0.08)),
            "customer_age": rng.integers(18, 70, N),
            "credit_risk_score": rng.normal(100, 20, N),
        }
    )
    cand = pd.DataFrame({"application_id": df["application_id"], "score": candidate})

    cost_incumbent = realized_cost(incumbent_actions, y, amount, config.costs)
    cost_candidate = realized_cost(candidate_actions, y, amount, config.costs)
    truth = {
        "n": N,
        "capacity": CAPACITY,
        "fraud_rate": float(y.mean()),
        "true_incumbent": float(cost_incumbent[in_pop].mean()),
        "true_candidate": float(cost_candidate[in_pop].mean()),
        "naive_incumbent": float(cost_incumbent[observed].mean()),
        "naive_candidate": float(cost_candidate[observed].mean()),
        "incumbent_review_fraud_rate": float(y[review].mean()),
        "candidate_review_fraud_rate": float(y[candidate_actions == "review"].mean()),
        "note": "Synthetic case study; not a bank result.",
    }

    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "case_log.csv", index=False)
    cand.to_csv(OUT / "case_candidate.csv", index=False)
    (OUT / "case_truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
    print(json.dumps(truth, indent=2))


if __name__ == "__main__":
    main()
