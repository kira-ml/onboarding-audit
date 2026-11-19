# Using the Arbitrary-Log Report

**Status:** Canonical report guide for v0.2.1 (2026-11-20).

**Command:** `onboarding-audit report`
**Purpose:** Evaluate a candidate onboarding policy from a decision log and a
candidate score file, and produce an audit-ready memo.

This is the v0.2 product surface. It does not simulate anything: propensities
come from the log (provided or estimated), labels are the observed labels, and
the reject margin is bounded.

---

## 1. Minimum log

The log is one row per application. Required columns:

| Column | Meaning |
|---|---|
| `application_id` | Stable, non-PII key |
| `action` | Logging action: `approve`, `review`, or `reject` |
| `score` | Logging-policy score |
| `amount` | Exposure / credit-line proxy |
| `label` | Observed fraud label (0/1) or null |
| `label_time` | Label timestamp (required when `label` is present) |

Strongly recommended:

| Column | Why |
|---|---|
| `reviewed` | Separates the review channel from the approve channel |
| `audit_flag` | Identifies the random post-hoc verification sample |
| `propensity` | Uses the known observation probability instead of estimating it |
| `label_source` | Diagnostics: review / audit / post-approval report / chargeback / mule investigation |
| `decision_time` | Label-maturity and delay diagnostics |
| `customer_age`, `credit_risk_score`, ... | Outcome-model features for DR |

The full schema, including the BSP 1213 / 1170 fields, is in
[`SCHEMA.md`](SCHEMA.md). Validate the log first:

```bash
onboarding-audit validate --log data/decisions.parquet
```

## 2. Candidate score file

One row per application in the log:

| Column | Meaning |
|---|---|
| `application_id` | Must match the log |
| `score` | Candidate-policy score in [0, 1] |
| `action` | Optional; if present and complete, used instead of deriving from the score |

If `action` is absent, the tool derives the candidate actions with the configured
cost matrix and the `--capacity` review cap.

## 3. Command

```bash
onboarding-audit report \
  --log data/decisions.parquet \
  --candidate data/candidate_scores.parquet \
  --config configs/pilot.yaml \
  --capacity 0.02 \
  --out reports/my_policy
```

Optional: `--features customer_age,credit_risk_score,...` if the log's feature
names differ from the config. Feature columns must be **numeric**; one-hot
encode categoricals before the report. If no usable features are present, the
DR estimate is reported as `n/a`; IPW and audit-only still run.

For covariate-dependent observation, add:

```bash
onboarding-audit report \
  --log data/decisions.parquet \
  --candidate data/candidate_scores.parquet \
  --config configs/pilot.yaml \
  --capacity 0.02 \
  --propensity-model covariate \
  --propensity-features customer_age,credit_risk_score,velocity_6h \
  --out reports/my_policy
```

`--propensity-model covariate` fits a cross-fitted per-action logistic model
`P(observed | action, X)` instead of the action-level rate. It is the right
choice when the log shows different observation rates across application
segments (for example, larger credit lines generating more post-approval
reports). The memo reports the feature list and a weight/ESS caveat. A provided
`propensity` column still takes precedence.

Outputs:

- `reports/my_policy/report.md` — the audit-ready memo.
- `reports/my_policy/report.json` — the machine-readable result.

## 4. How to read the memo

### Target population

The primary estimand is the **logging non-rejected population (`P0`)** — the
applications the incumbent policy approved or reviewed. Logging-rejected
applications have no outcome and are outside the primary estimate. They enter
only the full-population bounds.

### Propensity source

- `provided`: the log has a `propensity` column for the observed rows. Use it
  if it is the true observation probability.
- `estimated`: the tool estimated action-level rates from the log:
  - `e_review = observed / reviewed`;
  - `e_approve = audit_rate + (1 - audit_rate) * observed / (approved, not audited)`.
- `estimated_covariate`: the tool fit a cross-fitted per-action logistic model
  `P(observed | action, X)` on the numeric features. Use it when observation
  depends on application characteristics, not only on the action.

The estimated versions are diagnostics, not a substitute for a designed audit.
If the audit flag is absent, the tool cannot separate the audit from the base
approve-label rate. Covariate-dependent observation also produces heavy-tailed
weights: check the ESS, max weight, and the reported propensity range before
trusting the interval.

### Estimates

| Estimator | Target | How to read it |
|---|---|---|
| `naive` | `P0` | Mean cost on the labeled subset. It is the number a naive backtest would report; it is biased by selection. |
| `ipw_ht` | `P0` | Inverse-probability weighted; can be unstable with high weights. |
| `ipw_hajek` | `P0` | Self-normalized; usually more stable. |
| `dr` | `P0` | Doubly robust; the preferred point estimate when the outcome model is reasonable. |
| `audit_only` | `approved` | Mean cost on the random audit sample; unbiased for the approved population, high variance. |
| `bounds` | `full` | Partial-identification interval for the full population, including logging-rejected rows. |

### Positivity and overlap

- If `positivity_ok` is false, the tool should not report a point estimate.
  Add audit labels, or report bounds/diagnostics.
- Check the ESS and max weight. A high max weight or low ESS means the estimate
  is driven by a few rows.
- Check the candidate review/approve-outside-`P0` counts. If the candidate
  explores regions the logging policy never labeled, the log cannot identify
  that region without an audit or a model assumption.

### Choosing the propensity model

- The memo reports the observation rate by amount quintile. If the rate varies
  strongly across quintiles within an action, action-level `e` is misspecified;
  rerun with `--propensity-model covariate`.
- Measured on the pilot's covariate mechanism: action-level IPW was **67.52%**
  biased; the covariate model was **1.97%**. Action-level DR was **21.25%**; the
  covariate DR was **2.48%**. The covariate model is the correction, not DR
  alone.
- The covariate model is a logistic approximation. Check the weight tail and
  ESS; coverage was **89–91.5%**, below nominal 95%, because the weights are
  heavy-tailed.

### Bounds

The bounds are **partial-identification intervals conditional on the `P0`
estimate**, not confidence intervals. Do not report 95% coverage. If the reject
margin is material, the bounds are the honest output.

### Audit recommendation

The memo reports the current audit share and the labels needed for a target
relative standard error. The audit is a **random post-hoc verification of
approved applications**; shadow scoring is the no-customer-impact alternative.
Do not randomize approvals or rejections:
- random approval deliberately onboards fraud/mule accounts;
- random rejection deliberately excludes legitimate customers.

## 5. Common errors

| Error | Meaning | Fix |
|---|---|---|
| `missing required columns` | The log lacks a required field | Add the field or fix the export |
| `reviewed=1 requires action='review'` | The flags are inconsistent | Fix the log; do not silently coerce |
| `audit_flag=1 requires action='approve'` | The audit is a post-approval verification | Fix the log |
| `candidate score missing for N applications` | The candidate file does not cover the log | Export scores for every application |
| `positivity failure` | An action has zero observed probability | Add audit labels or report bounds |
| `DR` is `n/a` | No usable outcome-model features | Pass `--features` or use IPW/audit-only |
| `covariate propensity model requires at least one numeric feature` | The log has no numeric features for the model | Pass `--propensity-features`, or use the action-level model |
| `positivity failure` under the covariate model | A fitted `e` is numerically zero for an observed row | Check the feature/overlap; add audit labels or report bounds |

## 6. Privacy

- Use a hashed/pseudonymized evaluation extract.
- Do not log raw documents, names, account numbers, or unhashed contact data.
- Follow the Data Privacy Act, NPC Advisory 2024-04, and BSP Circular 1170.
- The open-source examples use synthetic data only.

## 7. Example

```bash
onboarding-audit validate --log examples/sample_log.csv
onboarding-audit report \
  --log examples/sample_log.csv \
  --candidate examples/sample_candidate.csv \
  --config configs/pilot.yaml \
  --capacity 0.10 \
  --out reports/sample_report
```

The sample log is a 20-row schema/CLI smoke example, not a research result.
