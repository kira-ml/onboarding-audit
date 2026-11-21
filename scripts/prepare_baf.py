"""Rebuild the BAF scored test window from the public raw file.

This reproduces the archived V2 recipe that produced
`data/scored_test.parquet`:

1. Load `Base.csv`, add `transaction_id` and `amount_proxy`, sort by `month`.
2. Simulate the 1-month label delay (`label_month`, `observed`).
3. Split the observed rows chronologically: train months 0-2, validation
   months 3-4, test months 5-6.
4. Fit the incumbent logistic regression (C=10) and the candidate LightGBM
   (300 trees, learning rate 0.05) on the training window; refit the random
   forest (400 trees) as a diagnostic.
5. Score the test window and write the 39-column frame.

The script records an input hash, an output hash, the model parameters, the
library versions, and per-score column hashes in a provenance sidecar. It does
**not** silently accept a different result: `--verify` compares the output to
the recorded SHA-256 and exits non-zero on a mismatch, so a library upgrade
that changes the scores is visible rather than hidden.

Usage:
    python scripts/prepare_baf.py --raw /path/to/Base.csv
    python scripts/prepare_baf.py --raw Base.csv --verify

Requires `scikit-learn` and `lightgbm` (the `baf` extra).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EXPECTED_SHA256 = "f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593"
EXPECTED_ROWS = 227_491

TRAIN_MONTHS = [0, 1, 2]
VAL_MONTHS = [3, 4]
TEST_MONTHS = [5, 6]
DELAY_MONTHS = 1
LAST_MONTH = 7

CATEGORICAL_COLS = [
    "payment_type",
    "employment_status",
    "housing_status",
    "source",
    "device_os",
]

FEATURE_EXCLUDE = [
    "transaction_id",
    "fraud_bool",
    "month",
    "label_month",
    "observed",
    "amount_proxy",
    "proposed_credit_limit",
    "device_fraud_count",
]

SCORE_COLUMNS = {
    "logistic_regression": "p_fraud",
    "random_forest": "p_fraud_rf",
    "lightgbm": "p_fraud_lgbm",
}

PARAMS = {
    "logistic_regression": {"C": 10.0, "max_iter": 1000},
    "random_forest": {"n_estimators": 400, "n_jobs": -1, "random_state": 42},
    "lightgbm": {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "verbose": -1,
        "random_state": 42,
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_frame(df: pd.DataFrame) -> str:
    """Hash a frame deterministically (column names, dtypes, values)."""
    h = hashlib.sha256()
    h.update("\x1f".join(map(str, df.columns)).encode("utf-8"))
    h.update(str(list(df.dtypes.astype(str))).encode("utf-8"))
    h.update(np.ascontiguousarray(df.to_numpy()).tobytes())
    return h.hexdigest()


def sha256_column(series: pd.Series) -> str:
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(series.to_numpy()).tobytes())
    return h.hexdigest()


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index(drop=True)
    df["transaction_id"] = df.index.astype("int64")
    if "proposed_credit_limit" not in df.columns:
        raise ValueError("Base.csv is missing proposed_credit_limit")
    df["amount_proxy"] = df["proposed_credit_limit"].astype("float64")
    return df.sort_values("month").reset_index(drop=True)


def simulate_delay(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["label_month"] = df["month"] + DELAY_MONTHS
    df["observed"] = df["label_month"] <= LAST_MONTH
    return df


def feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in FEATURE_EXCLUDE]


def build_preprocessor(algorithm: str, numeric: list[str], categorical: list[str]):
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

    if algorithm == "logistic_regression":
        return ColumnTransformer(
            [
                ("num", StandardScaler(), numeric),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    categorical,
                ),
            ]
        )
    if algorithm == "random_forest":
        return ColumnTransformer(
            [
                ("num", "passthrough", numeric),
                (
                    "cat",
                    OrdinalEncoder(
                        handle_unknown="use_encoded_value", unknown_value=-1
                    ),
                    categorical,
                ),
            ]
        )
    if algorithm == "lightgbm":
        return _LGBMPreprocessor(categorical)
    raise ValueError(algorithm)


class _LGBMPreprocessor:
    """Convert categorical columns to the training categories."""

    def __init__(self, categorical_cols: list[str]):
        self.categorical_cols = categorical_cols
        self.categories_: dict[str, pd.Index] = {}

    def fit(self, X: pd.DataFrame, y=None):
        for c in self.categorical_cols:
            if c in X.columns:
                self.categories_[c] = X[c].astype("category").cat.categories
        return self

    def fit_transform(self, X: pd.DataFrame, y=None):
        return self.fit(X, y).transform(X)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        for c in self.categorical_cols:
            if c in X.columns and c in self.categories_:
                X[c] = pd.Categorical(X[c], categories=self.categories_[c])
        return X


def make_model(algorithm: str):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression

    if algorithm == "logistic_regression":
        return LogisticRegression(**PARAMS[algorithm])
    if algorithm == "random_forest":
        return RandomForestClassifier(**PARAMS[algorithm])
    if algorithm == "lightgbm":
        import lightgbm as lgb

        return lgb.LGBMClassifier(**PARAMS[algorithm])
    raise ValueError(algorithm)


def _to_array(x):
    return x.toarray() if hasattr(x, "toarray") else x


def score_test(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    features = feature_columns(train)
    categorical = [c for c in CATEGORICAL_COLS if c in features]
    numeric = [c for c in features if c not in categorical]
    out = test.copy()
    for algorithm, column in SCORE_COLUMNS.items():
        pre = build_preprocessor(algorithm, numeric, categorical)
        x_train = _to_array(pre.fit_transform(train[features]))
        model = make_model(algorithm)
        model.fit(x_train, train["fraud_bool"])
        x_test = _to_array(pre.transform(test[features]))
        p = model.predict_proba(x_test)[:, 1]
        if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
            raise ValueError(f"{column} outside [0, 1]")
        out[column] = p
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, type=Path, help="Path to Base.csv")
    parser.add_argument(
        "--out",
        default=Path("data/scored_test.parquet"),
        type=Path,
        help="Output parquet path",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Fail if the output SHA-256 differs from the recorded value",
    )
    args = parser.parse_args()

    if not args.raw.exists():
        print(f"raw file not found: {args.raw}", file=sys.stderr)
        return 2

    input_hash = sha256_file(args.raw)
    df = normalize(pd.read_csv(args.raw))
    df = simulate_delay(df)
    observed = df[df["observed"]]
    train = observed[observed["month"].isin(TRAIN_MONTHS)]
    val = observed[observed["month"].isin(VAL_MONTHS)]
    test = observed[observed["month"].isin(TEST_MONTHS)]
    if train.empty or test.empty:
        print("empty split; check the month column", file=sys.stderr)
        return 2

    scored = score_test(train, test)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    scored.to_parquet(args.out, index=False)
    output_hash = sha256_file(args.out)

    import lightgbm
    import sklearn

    provenance = {
        "raw_path": str(args.raw),
        "raw_sha256": input_hash,
        "output_path": str(args.out),
        "output_sha256": output_hash,
        "expected_sha256": EXPECTED_SHA256,
        "sha_match": output_hash == EXPECTED_SHA256,
        "rows": int(len(scored)),
        "expected_rows": EXPECTED_ROWS,
        "months": sorted(int(m) for m in scored["month"].unique()),
        "train_rows": int(len(train)),
        "val_rows": int(len(val)),
        "test_rows": int(len(test)),
        "fraud_rate_test": float(scored["fraud_bool"].mean()),
        "params": PARAMS,
        "sklearn_version": sklearn.__version__,
        "lightgbm_version": lightgbm.__version__,
        "score_columns": {
            column: {
                "sha256": sha256_column(scored[column]),
                "mean": float(scored[column].mean()),
            }
            for column in SCORE_COLUMNS.values()
        },
        "split": {
            "train_months": TRAIN_MONTHS,
            "val_months": VAL_MONTHS,
            "test_months": TEST_MONTHS,
            "label_delay_months": DELAY_MONTHS,
        },
    }
    sidecar = args.out.with_suffix(".provenance.json")
    sidecar.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    print(f"wrote {args.out} ({len(scored):,} rows)")
    print(f"wrote {sidecar}")
    print(f"output sha256: {output_hash}")
    print(f"sha match: {provenance['sha_match']}")
    if args.verify and not provenance["sha_match"]:
        print(
            "MISMATCH: the output does not reproduce the recorded hash. "
            "A different library version or a changed split produces different "
            "scores; do not present the pilot as reproducing until this is "
            "resolved.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
