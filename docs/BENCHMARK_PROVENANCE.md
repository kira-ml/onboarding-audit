# Benchmark Provenance — Reproduced

**Status:** Verified reproduction record, 2026-11-21.
**Purpose:** Record that `scripts/prepare_baf.py` rebuilds the BAF evaluation
frame byte-for-byte from the public raw file, and pin the hashes and versions.

---

## 1. Result

| Item | Value |
|---|---|
| Command | `python scripts/prepare_baf.py --raw Base.csv --verify` |
| Raw input | BAF `Base.csv` |
| Raw SHA-256 | `7bf10a37ce07e72e14c1b09e5efee3d27261baff4facc7da767b0474dcf9b809` |
| Output | `data/scored_test.parquet` |
| Output SHA-256 | `f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593` |
| Expected SHA-256 | `f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593` |
| Match | **yes** |
| Rows | 227,491 |
| Months | 5, 6 |
| Test fraud rate | 1.2576% |
| scikit-learn | 1.7.2 |
| lightgbm | 4.7.0 |

The rebuild matched the recorded hash on the first verified run. The hash covers
the full 39-column parquet, not only the score columns.

## 2. Split

| Window | Months | Rows |
|---|---|---|
| Train | 0, 1, 2 | 397,039 |
| Validation | 3, 4 | 278,627 |
| Test | 5, 6 | 227,491 |
| Label delay | 1 month | — |

The split is chronological. The test window is never used for fitting.

## 3. Model parameters

| Model | Column | Parameters |
|---|---|---|
| Logistic regression (incumbent) | `p_fraud` | `C=10.0`, `max_iter=1000` |
| Random forest (diagnostic) | `p_fraud_rf` | `n_estimators=400`, `random_state=42` |
| LightGBM (candidate) | `p_fraud_lgbm` | `n_estimators=300`, `learning_rate=0.05`, `random_state=42` |

The logistic regression is the V2 selected model; the LightGBM is the V2
candidate. The selection criterion in V2 was mean realized cost under the
policy, not classification accuracy.

## 4. Score-column hashes

| Column | SHA-256 | Mean |
|---|---|---|
| `p_fraud` | `8ee22212fb6a6a5c9b54bebc08fcf009e6508b26c4d1d09433c65cd0bfdf0996` | 0.010212 |
| `p_fraud_rf` | `6407a5c9b9328abee4fed6a24f72f86a5a44bea8657f5409e37a37455e0fa8e1` | 0.018620 |
| `p_fraud_lgbm` | `3023ad385d61e53ccb8513cbfda57829d89998465a77e717e0e7d3c87c77a035` | 0.011884 |

The per-column hashes let a reviewer check the scores even if a different
parquet writer changes the file-level hash.

## 5. Leakage controls

| Control | Implementation |
|---|---|
| Target excluded from features | `FEATURE_EXCLUDE` contains `fraud_bool` |
| Identifier excluded | `transaction_id` excluded |
| Time excluded | `month`, `label_month` excluded |
| Exposure excluded | `amount_proxy`, `proposed_credit_limit` excluded |
| Post-decision field excluded | `device_fraud_count` excluded |
| Split disjointness | train 0–2, validation 3–4, test 5–6; asserted in `tests/test_prepare_baf.py` |
| Test labels unused in fitting | the models fit on `train` only; the test frame is scored, not fitted |

The leakage controls are unit-tested in `tests/test_prepare_baf.py`.

## 6. What this does and does not prove

**Proves:** the benchmark frame is reproducible from the public raw file with the
recorded code and the recorded library versions; the split and the model
parameters are pinned; a library change that alters the scores is detectable.

**Does not prove:** that the V2 model selection was correct; that BAF resembles a
Philippine portfolio; that the scores are calibrated for a production cutoff.
Those remain limitations in [`DATA.md`](DATA.md) and [`THREATS.md`](THREATS.md).

## 7. Related documents

- Data card: [`DATA.md`](DATA.md)
- Data dictionary: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Validation report: [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md)
