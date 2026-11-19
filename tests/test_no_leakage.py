import numpy as np
import pandas as pd

from onboarding_audit.config import Costs, PolicySpec
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
