import numpy as np
import pandas as pd

from onboarding_audit.config import Costs, OutcomeModel, PolicySpec
from onboarding_audit.estimators import fit_outcome_model
from onboarding_audit.policies import build_policy


def test_policy_actions_do_not_depend_on_labels():
    """Permuting labels must not change the policy actions (no leakage)."""
    rng = np.random.default_rng(0)
    n = 500
    df = pd.DataFrame(
        {
            "p_fraud": rng.uniform(0, 1, n),
            "p_fraud_lgbm": rng.uniform(0, 1, n),
            "amount": rng.uniform(100, 1000, n),
        }
    )
    amount = df["amount"].to_numpy()
    costs = Costs(
        fraud_loss_rate=0.01,
        review_cost=0.02,
        false_reject_cost=0.10,
        residual_fraud_loss=0.30,
    )
    spec = PolicySpec("incumbent", "p_fraud", 0.05)
    a1 = build_policy(df, spec, costs, amount).actions
    # Permute a label column; the policy does not read it.
    df2 = df.copy()
    df2["fraud_bool"] = rng.permutation(n) % 2
    a2 = build_policy(df2, spec, costs, amount).actions
    assert np.array_equal(a1, a2)


def test_outcome_model_does_not_predict_permuted_labels():
    """A real leak would survive target shuffling; this test must collapse to chance."""
    from sklearn.metrics import roc_auc_score

    rng = np.random.default_rng(0)
    n = 4_000
    X = rng.normal(size=(n, 5))
    y = rng.integers(0, 2, n)
    observed = np.ones(n, dtype=bool)
    prop = np.full(n, 0.5)
    cfg = OutcomeModel(C=0.5, n_splits=3)
    aucs = []
    for seed in range(5):
        shuffled = rng.permutation(y)
        phat = fit_outcome_model(X, shuffled, observed, prop, cfg, seed)
        aucs.append(roc_auc_score(shuffled, phat))
    mean_auc = float(np.mean(aucs))
    assert 0.45 <= mean_auc <= 0.55, (
        f"permuted-label AUC {mean_auc:.3f} suggests leakage"
    )
