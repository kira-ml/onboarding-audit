# Data Card — BAF Account-Opening Test Window

## 1. Dataset

| Item | Value |
|---|---|
| Name | Bank Account Fraud (BAF) `Base.csv` |
| Source | Jesus et al., NeurIPS 2022, arXiv:2211.13358; Feedzai BAF repository |
| License | CC BY 4.0 (see the BAF repository for the current terms) |
| Unit | Online bank account application |
| Raw rows | 1,000,000 |
| Raw features | 32 |
| Time | 8 monthly buckets (`month` 0–7) |
| Target | `fraud_bool` (account-opening fraud) |
| Base rate | ~1.1% raw; 1.2576% in the test window |
| Nature | Synthetic, privacy-preserving, generated from a real anonymized account-opening fraud dataset |

## 2. Processed pilot file

`data/scored_test.parquet` — 227,491 rows, months 5–6.

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

The file is derived from the archived V2 pipeline. The scores were trained on
months 0–2 and validated on 3–4; no evaluation labels were used. The V2
`observed` and `label_month` columns are ignored; this pilot simulates its own
observation mechanism.

## 3. How to rebuild

1. Download `Base.csv` from the BAF repository/Kaggle.
2. Place it at `data/Base.csv`.
3. Run the preparation script (to be added in v0.1.1):

```bash
python scripts/prepare_baf.py --raw data/Base.csv --out data/scored_test.parquet
```

The script will:
- sort by month;
- split months 0–2 (train), 3–4 (validation), 5–6 (test);
- fit the incumbent logistic regression and the candidate LightGBM;
- score the test window;
- write the processed file.

Until then, the local pilot uses the archived processed file, which is not
committed to the public repo (see `.gitignore`).

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
- The open-source examples use synthetic or public data only.
- A production deployment must comply with the Data Privacy Act (RA 10173), NPC
  Advisory 2024-04, BSP Circular 1170 (eKYC), and BSP Circular 1213 (logging and
  audit).
- Do not attempt to re-identify individuals or reconstruct the source data.
