# Data Dictionary — `data/scored_test.parquet`

**Status:** Canonical column reference for v1.0.0 (2026-11-22).
**Purpose:** Describe every column in the processed BAF test frame, its role, and
its limitations. The file is local and gitignored; this document is the
committed description.

---

## 1. File identity

| Item | Value |
|---|---|
| Path | `data/scored_test.parquet` |
| Rows | 227,491 |
| Columns | 39 |
| Months | 5 and 6 |
| Fraud rate | 1.2576% (`fraud_bool=1`) |
| SHA-256 | `f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593` |
| Source | BAF (Jesus et al., NeurIPS 2022), processed by the archived V2 pipeline |
| License | BAF CC BY 4.0; see the BAF repository |

The file is a **scored evaluation frame**, not a raw BAF download. It contains
the V2 model scores and the `amount_proxy` used by the pilot.

## 2. Roles

| Role | Meaning |
|---|---|
| `target` | The fraud label. Never a feature. |
| `id` | Row identifier. Not a feature. |
| `time` | Temporal split or decision timing. |
| `feature` | Pre-decision application/eKYC feature. |
| `score` | Pre-decision model score. |
| `exposure` | Amount/credit-line proxy used by the cost model. |
| `aux` | Diagnostic or archived column; not used by the main pilot. |

## 3. Columns

### 3.1 Target and identifiers

| Column | Type | Role | Notes |
|---|---|---|---|
| `fraud_bool` | int64 | target | 0/1 account-opening fraud label |
| `transaction_id` | int64 | id | Row key from the origin pipeline; despite the name, the unit is an application |
| `month` | int64 | time | 5 or 6; the test window |
| `label_month` | int64 | aux | V2 label month (6 or 7); ignored by the pilot |
| `observed` | bool | aux | V2 observed flag; constant `True`; ignored by the pilot |

### 3.2 Exposure and cost

| Column | Type | Role | Notes |
|---|---|---|---|
| `amount_proxy` | float64 | exposure | `proposed_credit_limit`; 12 discrete values (190–2,100) |
| `proposed_credit_limit` | float64 | exposure | Raw credit-limit field; source of `amount_proxy` |

`amount_proxy` is a **credit-line exposure proxy**, not the realized loss. The
cost model multiplies it by `fraud_loss_rate` (0.0019187869) in the normalized
configuration.

### 3.3 Application and eKYC features

| Column | Type | Role | Notes |
|---|---|---|---|
| `income` | float64 | feature | BAF income bucket |
| `name_email_similarity` | float64 | feature | Name/email similarity |
| `prev_address_months_count` | int64 | feature | Previous address tenure |
| `current_address_months_count` | int64 | feature | Current address tenure |
| `customer_age` | int64 | feature | Age in years (bucketed) |
| `days_since_request` | float64 | feature | Days since the application request |
| `intended_balcon_amount` | float64 | feature | Intended balance/amount |
| `payment_type` | object | feature | Categorical: `AA`–`AE` |
| `zip_count_4w` | int64 | feature | Address/zip velocity |
| `velocity_6h` | float64 | feature | Application velocity, 6 hours |
| `velocity_24h` | float64 | feature | Application velocity, 24 hours |
| `velocity_4w` | float64 | feature | Application velocity, 4 weeks |
| `bank_branch_count_8w` | int64 | feature | Branch count, 8 weeks |
| `date_of_birth_distinct_emails_4w` | int64 | feature | Distinct emails linked to DOB |
| `employment_status` | object | feature | Categorical: `CA`–`CG` |
| `credit_risk_score` | int64 | feature | Credit risk score |
| `email_is_free` | int64 | feature | Free-email flag |
| `housing_status` | object | feature | Categorical: `BA`–`BG` |
| `phone_home_valid` | int64 | feature | Home-phone validity |
| `phone_mobile_valid` | int64 | feature | Mobile-phone validity |
| `bank_months_count` | int64 | feature | Bank relationship tenure |
| `has_other_cards` | int64 | feature | Other-card flag |
| `foreign_request` | int64 | feature | Foreign-request flag |
| `source` | object | feature | `INTERNET` or `TELEAPP` |
| `session_length_in_minutes` | float64 | feature | Session length |
| `device_os` | object | feature | `windows`, `linux`, `other`, `macintosh`, `x11` |
| `keep_alive_session` | int64 | feature | Keep-alive flag |
| `device_distinct_emails_8w` | int64 | feature | Distinct emails per device |
| `device_fraud_count` | int64 | aux | Constant 0 in this window; not used |

### 3.4 Scores

| Column | Type | Role | Notes |
|---|---|---|---|
| `p_fraud` | float64 | score | V2 logistic-regression score; incumbent policy |
| `p_fraud_lgbm` | float64 | score | V2 LightGBM score; candidate policy |
| `p_fraud_rf` | float64 | aux | V2 random-forest score; diagnostic, not used in the main pilot |

All three scores are pre-decision. They were trained on months 0–2 and validated
on months 3–4 but are not used for hyperparameter selection in the reproduction
script; the evaluation window is months 5–6. The nuisance outcome model is
cross-fitted on the evaluation window's observed labels; the candidate policy's
labels are not used to fit the policy scores. No evaluation labels were
used to fit them.

## 4. Feature set used by the outcome model

`configs/pilot.yaml` selects:

```
p_fraud
p_fraud_lgbm
customer_age
credit_risk_score
velocity_6h
velocity_24h
velocity_4w
bank_months_count
zip_count_4w
session_length_in_minutes
```

`data.load_eval_data` adds:

```
log1p(amount_proxy)
month
```

The matrix is standardized on the evaluation window with `StandardScaler`. The
scaler uses features only, not labels.

Categorical columns (`payment_type`, `employment_status`, `housing_status`,
`source`, `device_os`) are **not** in the default outcome-model feature set. A
real log should one-hot encode them before passing them to the report's
`--features`.

## 5. Data quality checks

| Check | Result |
|---|---|
| Missing values | 0 in all 39 columns |
| `fraud_bool` values | `{0, 1}` |
| `month` values | `{5, 6}` |
| `amount_proxy` | finite, non-negative, 12 discrete values |
| `observed` | constant `True` (V2 artifact; ignored) |
| `device_fraud_count` | constant `0` (not used) |
| Score ranges | `[0, 1]` for `p_fraud`, `p_fraud_lgbm`, `p_fraud_rf` |
| Duplicate `transaction_id` | none (227,491 unique) |

## 6. What the pilot ignores

- `observed` and `label_month`: V2 artifacts. The pilot simulates its own
  observation mechanism; using the V2 observed flag would import a different
  selection process.
- `p_fraud_rf`: diagnostic only.
- `device_fraud_count`: constant, no signal.
- `proposed_credit_limit`: used only through `amount_proxy`.

## 7. What the pilot does not have

- Native approve/review/reject actions.
- Native review capacity.
- Native propensities.
- Native label timestamps or delay.
- A realized loss given fraud.

These are simulated or assumed; see [`DATA.md`](DATA.md) and
[`METHODS.md`](METHODS.md).

## 8. Related documents

- Data card: [`DATA.md`](DATA.md)
- Methods: [`METHODS.md`](METHODS.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Schema for a real log: [`SCHEMA.md`](SCHEMA.md)
