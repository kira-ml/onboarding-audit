# Data Card — BAF Account-Opening Test Window

**Status:** Canonical data card for v1.0.0 (2026-11-22).

## 1. Dataset

| Item | Value |
|---|---|
| Name | Bank Account Fraud (BAF) `Base.csv` |
| Source | Jesus et al., NeurIPS 2022, arXiv:2211.13358; Feedzai BAF repository |
| License | **CC BY-NC-SA 4.0** (dataset; non-commercial). See [`DATA_SOURCES.md`](DATA_SOURCES.md) |
| Unit | Online bank account application |
| Raw rows | 1,000,000 |
| Raw features | 32 |
| Time | 8 monthly buckets (`month` 0–7) |
| Target | `fraud_bool` (account-opening fraud) |
| Base rate | ~1.1% raw; 1.2576% in the test window |
| Nature | Synthetic, privacy-preserving, generated from a real anonymized account-opening fraud dataset |

## 2. Processed pilot file

`data/scored_test.parquet` — 227,491 rows, months 5–6.

SHA-256:
`f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593`.

Every column, its role, and its limitations are in
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

| Column | Meaning |
|---|---|
| `fraud_bool` | True account-opening fraud label |
| `month` | 5 or 6 |
| `transaction_id` | Row identifier from the origin pipeline (despite the name, the row is an application) |
| `amount_proxy` | `proposed_credit_limit`; credit-line exposure proxy |
| `p_fraud` | V2 logistic-regression score (incumbent) |
| `p_fraud_lgbm` | V2 LightGBM score (candidate) |
| `p_fraud_rf` | V2 random-forest score (diagnostic) |
| Other columns | BAF application features |
| Protected attributes | `customer_age`, `employment_status`, `income`; all three are currently used in the feature set. This is a research-only conflict under review; see [`DATA_USE_PLAN.md`](DATA_USE_PLAN.md) §6. |

The file is derived from the archived V2 pipeline. The scores were trained on
months 0–2 with fixed hyperparameters; months 3–4 are held out but are not used
for hyperparameter selection in the reproduction script. The nuisance outcome
model is cross-fitted on the evaluation window's observed labels; the candidate
policy's labels are not used to fit the policy scores. The V2
`observed` and `label_month` columns are ignored; this pilot simulates its own
observation mechanism.

## 3. How to rebuild

The processed file is rebuilt by `scripts/prepare_baf.py` from the public raw
file:

```bash
pip install -e ".[baf]"
python scripts/prepare_baf.py --raw /path/to/Base.csv --verify
```

The script:

1. Downloads nothing; it takes `Base.csv` from the BAF repository/Kaggle.
2. Adds `transaction_id` and `amount_proxy`, sorts by `month`, and simulates the
   one-month label delay.
3. Splits months 0–2 (train), 3–4 (validation), 5–6 (test).
4. Fits the incumbent logistic regression (`C=10`) and the candidate LightGBM
   (300 trees, learning rate 0.05) on the training window; refits the random
   forest as a diagnostic.
5. Writes the 39-column test frame and a provenance sidecar with the input hash,
   the output hash, the model parameters, the library versions, and per-score
   column hashes.
6. Verifies the SHA-256 hash above; `--verify` exits non-zero on a mismatch.

Do not fabricate the processed file from a different split. The scores and the
test window are part of the benchmark; a different split changes the result.

The processed file is not committed to the public repo (see `.gitignore`). The
pilot and the report are reproducible from the committed code and the public raw
data; exact bit-for-bit agreement across a library upgrade is not guaranteed, and
the provenance sidecar records the versions so a mismatch is visible. The
verified rebuild record is in
[`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md).

## 4. Known limitations

- **Synthetic.** BAF is synthetic, generated from a real anonymized dataset. It
  is realistic but not a production sample.
- **One dataset.** No Philippine account-opening data is public. The pilot is a
  simulation benchmark, not an empirical estimate for a specific bank.
- **No native action log.** BAF has no approve/review/reject actions,
  propensities, or label timestamps. The pilot simulates them.
- **No native review capacity.** The review capacity is a parameter, calibrated
  to a plausible range (1–10%) and sensitivity-tested.
- **No native cost matrix.** The cost matrix is a normalized assumption, not a
  production estimate.
- **Credit-line proxy.** `proposed_credit_limit` is used as an exposure proxy;
  the actual loss given fraud is not observed.
- **Temporal split.** The test window is months 5–6; results may differ in
  other periods.

## 5. Ethical and legal notes

- The data is public and synthetic; no PII is included.
- The examples use synthetic or public data only; BAF is not redistributed.
- A production deployment must comply with the Data Privacy Act (RA 10173), NPC
  Advisory 2024-04, BSP Circular 1170 (eKYC), and BSP Circular 1213 (logging and
  audit).
- Do not attempt to re-identify individuals or reconstruct the source data.
