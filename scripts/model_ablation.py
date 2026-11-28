"""Post-hoc model/score ablation on the BAF test window.

Not a replacement for the benchmark scores. It checks whether the LightGBM
candidate is a genuinely better ranker than the logistic incumbent, and whether
a same-feature logistic vs gradient-boosting ablation reproduces the direction.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "scored_test.parquet"
OUT_JSON = ROOT / "reports" / "model_ablation.json"
OUT_MD = ROOT / "reports" / "model_ablation.md"

DROP = {
    "fraud_bool",
    "month",
    "transaction_id",
    "label_month",
    "observed",
    "p_fraud",
    "p_fraud_rf",
    "p_fraud_lgbm",
}
VELOCITY = {
    "velocity_6h",
    "velocity_24h",
    "velocity_4w",
    "zip_count_4w",
    "device_distinct_emails_8w",
}


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    fpr, tpr, _ = roc_curve(y, p)
    return {
        "auc": float(roc_auc_score(y, p)),
        "average_precision": float(average_precision_score(y, p)),
        "ks": float(np.max(tpr - fpr)),
        "n": len(y),
        "fraud_rate": float(np.mean(y)),
    }


def preprocessor(features: list[str], frame: pd.DataFrame) -> ColumnTransformer:
    categorical = [c for c in features if frame[c].dtype == object]
    numeric = [c for c in features if c not in categorical]
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                categorical,
            ),
        ]
    )


def fit_score(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    model,
) -> np.ndarray:
    pipe = Pipeline(
        [
            ("pre", preprocessor(features, train)),
            ("clf", model),
        ]
    )
    pipe.fit(train[features], train["fraud_bool"].to_numpy(int))
    return pipe.predict_proba(test[features])[:, 1]


def main() -> None:
    df = pd.read_parquet(DATA)
    train = df[df["month"] == 5].copy()
    test = df[df["month"] == 6].copy()
    y_test = test["fraud_bool"].to_numpy(int)

    features = [c for c in df.columns if c not in DROP]
    reduced = [c for c in features if c not in VELOCITY]

    out: dict = {
        "note": (
            "Post-hoc ablation on the BAF test window. The policy scores are not "
            "retrained; the logistic/HistGB models are trained on month 5 and "
            "tested on month 6. Not a production estimate."
        ),
        "n_train_month5": len(train),
        "n_test_month6": len(test),
        "score_metrics_month6": {
            "incumbent_p_fraud": metrics(y_test, test["p_fraud"].to_numpy()),
            "candidate_p_fraud_lgbm": metrics(y_test, test["p_fraud_lgbm"].to_numpy()),
            "random_forest_diagnostic": metrics(y_test, test["p_fraud_rf"].to_numpy()),
        },
        "retrained_ablation_month6": {},
    }

    models = {
        "logistic_all_features": (
            features,
            LogisticRegression(max_iter=1000, n_jobs=-1),
        ),
        "hist_gradient_boosting_all_features": (
            features,
            HistGradientBoostingClassifier(
                max_iter=200,
                learning_rate=0.05,
                max_leaf_nodes=31,
                random_state=20261121,
            ),
        ),
        "logistic_reduced_no_velocity": (
            reduced,
            LogisticRegression(max_iter=1000, n_jobs=-1),
        ),
    }
    for name, (cols, model) in models.items():
        p = fit_score(train, test, cols, model)
        out["retrained_ablation_month6"][name] = {
            "n_features": len(cols),
            "metrics": metrics(y_test, p),
        }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    L = [
        "# Model / Score Ablation",
        "",
        "**Status:** Post-hoc, 2026-11-27. Not a production estimate.",
        "",
        "## Existing scores (month 6)",
        "",
        "| Score | AUC | Average precision | KS | Fraud rate | n |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, m in out["score_metrics_month6"].items():
        L.append(
            f"| `{name}` | {m['auc']:.4f} | {m['average_precision']:.4f} | "
            f"{m['ks']:.4f} | {m['fraud_rate']:.4%} | {m['n']:,} |"
        )
    L += [
        "",
        "## Retrained ablation (train month 5, test month 6)",
        "",
        "| Model | Features | AUC | Average precision | KS |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, rec in out["retrained_ablation_month6"].items():
        m = rec["metrics"]
        L.append(
            f"| `{name}` | {rec['n_features']} | {m['auc']:.4f} | "
            f"{m['average_precision']:.4f} | {m['ks']:.4f} |"
        )
    L += [
        "",
        "**Read:** if the LightGBM candidate has a higher AUC/AP than the logistic",
        "incumbent on the same test window, the “better model” premise is",
        "supported as a ranking claim. The retrained ablation is a same-window",
        "temporal check, not the original benchmark score; a same-feature",
        "gradient-boosting model should beat logistic if model class is the",
        "driver. This does not isolate observation selection from model capacity.",
    ]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[ablation] wrote {OUT_JSON}")
    print(f"[ablation] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
