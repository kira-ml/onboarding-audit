"""Generate the deterministic synthetic demo log and candidate scores.

The demo is a usability fixture, not a research result. It has no `propensity`
column, so the report must estimate action-level propensities and exercise the
identification gate. The true P0 value is written to `demo_truth.json` for tests.

Usage:
    python scripts/make_demo_log.py
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


def main() -> None:
    rng = np.random.default_rng(7)
    n = 2500
    score = rng.beta(2, 8, n)
    y = rng.binomial(1, np.clip(0.005 + 0.45 * score, 0, 1))
    amount = rng.uniform(200, 1000, n)
    action = np.where(
        score > 0.70, "reject", np.where(score > 0.45, "review", "approve")
    )
    reviewed = action == "review"
    approve = action == "approve"
    audit = approve & (rng.random(n) < 0.02)
    review_obs = reviewed & (rng.random(n) < 0.90)
    base_obs = approve & (rng.random(n) < 0.05)
    observed = review_obs | audit | base_obs

    label = np.where(observed, y, np.nan)
    decision_time = pd.Timestamp("2026-06-01") + pd.to_timedelta(
        rng.integers(0, 60, n), unit="D"
    )
    application_time = decision_time - pd.to_timedelta(2, unit="s")
    label_time = pd.Series(decision_time) + pd.to_timedelta(30, unit="D")
    label_time = label_time.where(observed)

    label_source = np.full(n, "none", dtype=object)
    label_source[review_obs] = "review"
    label_source[audit] = "audit"
    label_source[base_obs & ~audit] = "post_approval_report"

    df = pd.DataFrame(
        {
            "application_id": [f"demo_{i:05d}" for i in range(n)],
            "application_time": application_time,
            "decision_time": decision_time,
            "action": action,
            "score": score,
            "amount": amount,
            "reviewed": reviewed.astype(int),
            "audit_flag": audit.astype(int),
            "label": label,
            "label_time": label_time,
            "label_source": label_source,
            "customer_age": rng.integers(18, 70, n),
            "credit_risk_score": rng.normal(100, 20, n),
        }
    )
    candidate = pd.DataFrame(
        {
            "application_id": df["application_id"],
            "score": np.clip(score + rng.normal(0, 0.05, n), 0, 1),
        }
    )

    config = load_config(ROOT / "configs" / "pilot.yaml")
    _, (c_app, c_rev, c_rej) = choose_actions(
        candidate["score"].to_numpy(float), config.costs, amount
    )
    capacity = 0.10
    k = int(np.ceil(capacity * n))
    candidate_actions = apply_capacity(c_app, c_rev, c_rej, k)
    cost = realized_cost(candidate_actions, y, amount, config.costs)
    in_pop = action != "reject"
    truth = {
        "n": n,
        "p0_n": int(in_pop.sum()),
        "candidate_capacity": capacity,
        "true_p0": float(cost[in_pop].mean()),
        "true_full": float(cost.mean()),
        "true_approved": float(cost[action == "approve"].mean()),
        "note": "Synthetic demo fixture; not a research result.",
    }

    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "demo_log.csv", index=False)
    candidate.to_csv(OUT / "demo_candidate.csv", index=False)
    (OUT / "demo_truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
    print(f"wrote {OUT / 'demo_log.csv'}")
    print(f"wrote {OUT / 'demo_candidate.csv'}")
    print(f"wrote {OUT / 'demo_truth.json'}")
    print(
        f"n={n}, P0={truth['p0_n']}, true_p0={truth['true_p0']:.6f}, "
        f"observed={int(observed.sum())}"
    )


if __name__ == "__main__":
    main()
