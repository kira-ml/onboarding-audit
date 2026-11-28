# Using the Arbitrary-Log Report

**Status:** Canonical report guide for v1.0.0 (2026-11-22).

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

The validator reports both estimator readiness and **reliability readiness**:
identification, statistical stability, calibration, structural reject margin,
operational readiness, and the segment diagnostic. A `no` means the log cannot
support that dimension; the report will mark it unavailable or grade down.

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

### Quick demo

```bash
onboarding-audit demo --out reports/demo
```

The demo uses a 2,500-row synthetic log with **no propensity column**, so it
exercises the estimated-propensity path and the identification gate. The known
true `P0` is in `examples/demo_truth.json`. The 20-row `sample_log.csv` is a
schema smoke example; at that size the gate reports “Not identified” and
withholds the point estimates.

## 4. How to read the memo

### Target population

The primary estimand is the **logging non-rejected population (`P0`)** — the
applications the incumbent policy approved or reviewed. Logging-rejected
applications have no outcome and are outside the primary estimate. They enter
only the full-population bounds.

### Candidate vs incumbent

The memo reports a paired comparison on `P0`:

- the candidate's `P0` value and the incumbent's logged-policy `P0` value;
- the difference (negative favors the candidate), with a 95% interval;
- **P(candidate cheaper)**;
- the **expected regret** of each choice, in cost units per application;
- a recommendation: **prefer candidate** (P ≥ 0.95), **keep incumbent** (P ≤ 0.05),
  or **inconclusive**.

The comparison uses the same outcome model and propensities for both policies and
the paired influence terms for the interval. It is a first-order approximation:
it ignores nuisance-estimation uncertainty. It is `P0`-conditional; a candidate
that changes logging-rejected rows is not fully evaluated by that comparison.

### Full-policy check

The memo adds a **full-policy check** that includes the logging-rejected rows:

- the full-policy difference (candidate − incumbent) over **all possible**
  outcomes for the rejected rows, not a point estimate;
- whether the direction survives any reject outcome, or depends on the unobserved
  reject margin;
- a **break-even** rejected-fraud rate under a common-rate assumption;
- reference fraud rates among reviewed and observed approved applications, as
  anchors — not as a prior for the rejected population.

Read the `P0` recommendation as conditional. If the full-policy check says
**depends on the reject margin**, the `P0` recommendation is not a full-policy
decision. The memo prints a warning when a directional `P0` recommendation does
not survive the reject margin.

A break-even near **0%** or **100%** means the decision is practically robust
even though it is not identified: the reject margin would have to be almost
entirely legitimate or almost entirely fraud to change the sign. A mid-range
break-even means the reject margin can change the decision, and the risk team
must judge which side is plausible. Do not quote the break-even as an estimate
of the rejected fraud rate. With this cost model, the candidate is cheaper
**below** `p*`; the "above" direction is not reachable under non-negative costs.

The decision labels are **candidate cheaper for any reject outcome**,
**incumbent cheaper for any reject outcome**, **depends on the reject margin**,
**P0 inconclusive**, and **not identified**. `P0 inconclusive` means the `P0`
interval includes zero and the reject margin does not flip the sign at the `P0`
point estimate; collecting more `P0` labels is the fix, not more reject labels.
If the identification gate fails, §4.1 is **diagnostic only** and does not print
a decision. If there are no logging-rejected rows, the full population equals
`P0` and the section says so.

### Decision reliability profile

The memo’s §4.2 grades the decision across six dimensions: identification,
bootstrap stability, full-policy/reject margin, model calibration, cost stress,
and operational readiness. The grade is **A–D**:

- **A:** all measured dimensions strong and a directional point decision;
  assumptions still apply.
- **B:** credible with one moderate dimension or a full-policy caveat.
- **C:** any weak or unavailable dimension, or an inconclusive point decision;
  collect more evidence (labels, audit, cost agreement) and do not act on the
  `P0` recommendation alone.
- **D:** the gate failed; no point estimate.

The profile is a decision aid, not a certification. It does not replace the
observation-model review, the cost matrix, or the audit design.

### Identification gate

The gate is a **readiness screen**, not a proof of identification. It catches
logs that are obviously unidentifiable; passing it does not prove the
observation model is correct or that unmeasured confounding is absent.

Before printing a point estimate, the report checks:

- positivity on `P0`;
- at least 100 observed labels and at least 30 per non-rejected action;
- ESS at least 100 and max weight at most 100;
- non-negative candidate costs;
- the declared observation mechanism.

If a check fails, the memo says **"Not identified"**, withholds the point
estimates, and lists the reasons. The JSON keeps the diagnostic estimates, but
they are not a policy value. The CLI also prints the gate status and withholds
the estimates.

### Declare the observation mechanism

The gate cannot test the observation mechanism, which is the assumption that
matters most. Declare it:

```bash
onboarding-audit report ... --observation-assumption action
```

| Value | Behavior |
|---|---|
| `action` | Labels are assumed ignorable given the logged action and covariates. The memo says **Measured**. |
| `outcome` | The analyst declares that approved labels depend on the outcome. The report **refuses**: action-only estimators are known to fail there (up to 1,737.0% bias in the pilot). Use an audit-labeled sample. |
| `unknown` (default) | The memo says **Measured (observation assumption unverified)** and adds a warning. |

The default is deliberately not `action`: a memo should not claim an assumption
the analyst never declared.

Warnings (not refusals) cover candidate actions outside `P0`, ESS below 500,
max weight above 50, action-level propensities estimated without an audit, and an
undeclared observation mechanism.

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
| `audit_only` | `approved` | Mean cost on the random audit sample; unbiased for the **logging-approved** population, high variance. |
| `bounds` | `full` | Partial-identification interval for the full population, including logging-rejected rows. |

`audit_only` targets the **logging-approved** population: the rows the incumbent
approved and the audit sampled. A candidate that expands or shrinks the approved
set is outside that target; the candidate's approved-population value is not
identified without a candidate-specific audit.

### Positivity and overlap

- If `positivity_ok` is false, the tool should not report a point estimate.
  Add audit labels, or report bounds/diagnostics.
- Check the ESS and max weight. A high max weight or low ESS means the estimate
  is driven by a few rows.
- Check the candidate review/approve-outside-`P0` counts. If the candidate
  explores regions the logging policy never labeled, the log cannot identify
  that region without an audit or a model assumption.

### Segment diagnostic

If the log has a `segment` column, the memo adds an **observational** segment
table: incumbent approve/review/reject counts, candidate reject share, candidate
change share, observed fraud rate, and the candidate false-reject share among
observed legitimate rows. Segments with fewer than 50 rows are suppressed.

This is **not** a fairness certification. Logging-rejected applicants have no
outcome, and the observed false-reject share is conditioned on the rows that were
observed. Use it to decide whether a full segment audit is needed, not to clear
the policy. A full fairness audit needs outcomes for the rejected margin, which
the log does not have.

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

The full-policy **difference** bounds are separate and usually sharper than
differencing two policy bounds, because the same rejected application's outcome
is shared by both policies. The break-even is a sensitivity threshold, not an
estimate; it assumes a common fraud rate among rejected rows.

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
