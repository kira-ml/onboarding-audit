"""Double-robustness stress test with a known nonlinear outcome.

The pilot uses BAF's real labels, so the outcome model's misspecification is
unknown. This experiment makes it known: the outcome is generated from a
logistic model with an interaction, and the analyst fits either a main-effects
model (misspecified) or the interaction model (correct). The propensity is
either the true one or a biased copy.

The prediction of double robustness:

- correct propensity, wrong outcome model: IPW and DR unbiased, plug-in biased;
- wrong propensity, correct outcome model: plug-in and DR unbiased, IPW biased;
- both wrong: all biased.

Usage:
    python scripts/double_robustness.py --reps 200 --out reports/double_robustness.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

from onboarding_audit.config import Costs
from onboarding_audit.estimators import effective_sample_size
from onboarding_audit.policies import realized_cost

COSTS = Costs(
    fraud_loss_rate=0.01,
    review_cost=0.02,
    false_reject_cost=0.10,
    residual_fraud_loss=0.30,
)
AMOUNT = 1000.0
THRESHOLDS = (0.60, 0.80)


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def _generate(rng: np.random.Generator, n: int):
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    x3 = rng.binomial(1, 0.5, n).astype(float)
    # True outcome: nonlinear, with an interaction the main-effects model misses.
    p = _sigmoid(1.5 * x1 - 1.0 * x2 + 1.5 * x1 * x2 + 0.8 * x3)
    y = rng.binomial(1, p)
    score = _sigmoid(0.8 * x1 + 0.5 * x2)
    actions = np.where(
        score > THRESHOLDS[1],
        "reject",
        np.where(score > THRESHOLDS[0], "review", "approve"),
    )
    e = np.zeros(n)
    e[actions == "approve"] = 0.05
    e[actions == "review"] = 0.90
    observed = rng.random(n) < e
    return x1, x2, x3, p, y, actions, e, observed


def _fit_phat(
    X: np.ndarray, y: np.ndarray, observed: np.ndarray, e: np.ndarray, seed: int
):
    """Cross-fitted logistic P(Y=1|X), weighted by 1/e."""
    n = len(y)
    idx = np.where(observed & (e > 0))[0]
    phat = np.full(n, np.nan)
    if len(idx) < 20 or len(np.unique(y[idx])) < 2:
        return phat
    folds = np.array_split(np.random.default_rng(seed).permutation(idx), 5)
    preds = np.zeros((5, n))
    for k in range(5):
        test = folds[k]
        train = np.concatenate([folds[j] for j in range(5) if j != k])
        model = LogisticRegression(C=0.5, max_iter=500)
        model.fit(X[train], y[train], sample_weight=1.0 / e[train])
        preds[k] = model.predict_proba(X)[:, 1]
        phat[test] = preds[k, test]
    unobserved = np.setdiff1d(np.arange(n), idx)
    if len(unobserved):
        phat[unobserved] = preds[:, unobserved].mean(axis=0)
    return phat


def _estimates(phat, actions, y, observed, e, in_pop):
    fl = AMOUNT * COSTS.fraud_loss_rate
    cost = np.where(
        actions == "approve",
        y * fl,
        np.where(
            actions == "review",
            COSTS.review_cost + y * COSTS.residual_fraud_loss,
            (1 - y) * COSTS.false_reject_cost,
        ),
    )
    mu = np.where(
        actions == "approve",
        phat * fl,
        np.where(
            actions == "review",
            COSTS.review_cost + phat * COSTS.residual_fraud_loss,
            (1 - phat) * COSTS.false_reject_cost,
        ),
    )
    n_pop = int(in_pop.sum())
    plug_in = float(mu[in_pop].mean())
    w = np.zeros(len(e))
    w[observed & (e > 0)] = 1.0 / e[observed & (e > 0)]
    ipw = float((w * cost).sum() / n_pop)
    dr = float(mu[in_pop].mean() + (w * (cost - mu))[in_pop].mean())
    return plug_in, ipw, dr, float(effective_sample_size(w))


def _run_arm(rng, reps, n, wrong_outcome: bool, wrong_propensity: bool):
    plug, ipw, dr = [], [], []
    for rep in range(reps):
        x1, x2, x3, p, y, actions, e, observed = _generate(rng, n)
        in_pop = actions != "reject"
        design = [x1, x2, x3] if wrong_outcome else [x1, x2, x3, x1 * x2]
        X = np.column_stack(design)
        e_fit = np.clip(e * 1.6, 0, 1) if wrong_propensity else e
        phat = _fit_phat(X, y, observed, e_fit, seed=rep)
        if not np.isfinite(phat).all():
            continue
        a, b, c, _ = _estimates(phat, actions, y, observed, e_fit, in_pop)
        plug.append(a)
        ipw.append(b)
        dr.append(c)
    return {
        "plug_in": _summary(plug),
        "ipw": _summary(ipw),
        "dr": _summary(dr),
        "reps": len(plug),
    }


def _summary(values):
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(arr.mean()),
        "bias": float(arr.mean() - TRUE_VALUE),
        "rel_bias": float((arr.mean() - TRUE_VALUE) / TRUE_VALUE),
        "mc_se": float(arr.std(ddof=1) / np.sqrt(len(arr))),
    }


def _true_value(rng, n):
    x1, x2, x3, p, y, actions, e, observed = _generate(rng, n)
    in_pop = actions != "reject"
    fl = AMOUNT * COSTS.fraud_loss_rate
    cost = np.where(
        actions == "approve",
        y * fl,
        np.where(
            actions == "review",
            COSTS.review_cost + y * COSTS.residual_fraud_loss,
            (1 - y) * COSTS.false_reject_cost,
        ),
    )
    return float(cost[in_pop].mean())


TRUE_VALUE = 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reps", default=200, type=int)
    parser.add_argument("--n", default=20_000, type=int)
    parser.add_argument("--seed", default=20261121, type=int)
    parser.add_argument(
        "--out", default=Path("reports/double_robustness.json"), type=Path
    )
    args = parser.parse_args()

    global TRUE_VALUE
    TRUE_VALUE = _true_value(np.random.default_rng(args.seed + 1), 200_000)

    rng = np.random.default_rng(args.seed)
    arms = {
        "correct_e_wrong_outcome": _run_arm(
            rng, args.reps, args.n, wrong_outcome=True, wrong_propensity=False
        ),
        "wrong_e_correct_outcome": _run_arm(
            rng, args.reps, args.n, wrong_outcome=False, wrong_propensity=True
        ),
        "wrong_e_wrong_outcome": _run_arm(
            rng, args.reps, args.n, wrong_outcome=True, wrong_propensity=True
        ),
    }
    payload = {
        "true_value": TRUE_VALUE,
        "n": args.n,
        "reps": args.reps,
        "seed": args.seed,
        "costs": {
            "fraud_loss_rate": COSTS.fraud_loss_rate,
            "review_cost": COSTS.review_cost,
            "false_reject_cost": COSTS.false_reject_cost,
            "residual_fraud_loss": COSTS.residual_fraud_loss,
            "amount": AMOUNT,
        },
        "arms": arms,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"true value: {TRUE_VALUE:.6f}")
    for arm, result in arms.items():
        print(f"\n{arm} ({result['reps']} reps)")
        for estimator in ("plug_in", "ipw", "dr"):
            r = result[estimator]
            print(
                f"  {estimator:<8} rel bias {r['rel_bias']:+.2%}  "
                f"mc_se {r['mc_se'] / TRUE_VALUE:.2%}"
            )
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
