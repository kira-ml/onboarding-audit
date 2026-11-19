# Methods

**Status:** Canonical methods reference for v0.2.1 (2026-11-20).
**Purpose:** State the estimand, identification assumptions, estimators,
simulation design, and metrics in one place. The pre-registered protocol is
[`PILOT_SPEC.md`](PILOT_SPEC.md); the measured findings are in
[`RESULTS.md`](RESULTS.md) and [`CLAIMS.md`](CLAIMS.md).

This document describes what the code does, not what the results are.

---

## 1. Decision and notation

For application `i`:

- `X_i`: pre-decision features (application, eKYC, device, velocity, scores).
- `Y_i in {0,1}`: account-opening fraud outcome.
- `a_i in {approve, review, reject}`: the action.
- `A` (or `pi`) is a policy mapping `X` to an action.
- `C(a, Y, amount)` is the realized cost.

The institution chooses a policy to minimize expected cost subject to a review
capacity `K`. The evaluation question is the value of a candidate policy `pi`
relative to the incumbent, not the accuracy of a classifier.

## 2. Estimands

### 2.1 Primary: `P0`

```
V_P0(pi) = E[ C(pi(X), Y) | i in P0 ]
P0 = { i : a_incumbent(i) != reject }
```

`P0` is the logging non-rejected population: the applications the incumbent
approved or reviewed. It is the part of the population for which the log can
identify an outcome, under the assumptions in §3.

### 2.2 Secondary: approved population

```
V_approved(pi) = E[ C(pi(X), Y) | a_incumbent(i) = approve ]
```

This is the target of the audit-only estimator. It is not the primary estimand
because it excludes the review band.

### 2.3 Secondary: full population bounds

```
V_full(pi) = E[ C(pi(X), Y) ]
```

The logging-rejected rows have no outcome. `V_full` is reported as a
partial-identification interval conditional on the `P0` estimate, not a point
estimate and not a confidence interval.

## 3. Identification assumptions

The `P0` estimand is identified under:

1. **Consistency:** the observed label is the outcome that would occur under the
   logging action.
2. **Positivity:** every row in `P0` has a positive probability of being
   observed, `e_i = P(observed_i = 1 | action_i, X_i) > 0`.
3. **No unmeasured confounding of observation:** conditional on the logging
   action and the observed features, observation is independent of the outcome.
   This fails if reviewers use unlogged information or if fraud is more likely
   to be reported than legitimate behavior.
4. **Correct observation model:** `e_i` is known or estimated consistently.
5. **Stable cost model:** the configured cost matrix represents the
   institution's decision costs.
6. **No interference / no anticipation:** one application's label does not
   depend on another application's action.

The reject margin is **not** identified from logs alone: rejected applicants
never become customers, so `Y` is structurally missing. Bounds require the cost
model and an assumption about the unobserved cost range.

## 4. Policy construction

For a score `p_i = P(fraud | X_i)`, the expected cost of each action is:

```
c_approve = p_i * fraud_loss(amount_i)
c_review  = review_cost + p_i * residual_fraud_loss
c_reject  = (1 - p_i) * false_reject_cost
```

with

```
fraud_loss(amount) = amount * fraud_loss_rate    (amount-scaled)
```

The unconstrained action is the argmin. The review capacity `K = ceil(capacity *
n)` is enforced by ranking the review candidates by the savings from reviewing
them relative to the better of approve/reject:

```
savings_i = min(c_approve_i, c_reject_i) - c_review_i
```

The top `K` candidates are reviewed; the overflow is routed to approve or reject
by the lower of `c_approve` and `c_reject`. This keeps the policy
capacity-constrained without assuming unlimited analysts.

The logging policy is the incumbent. Candidate policies may use a different
score and a different decision false-reject cost; the evaluation cost matrix is
the same for all policies, so the comparison is on a common cost scale.

## 5. Observation model

### 5.1 Action-dependent (main pilot)

Each application has a decision day `d_i` and a label delay. The probability that
a label has resolved by the cutoff is:

```
p_resolved(d; median, sigma, cutoff) =
    Phi( (log(cutoff - d) - log(median)) / sigma )
```

For review rows:

```
e_review_i = p_resolved_review_i * kappa_review
```

For approved rows, a post-approval report channel and a random audit are
independent:

```
e_approve_i = p_resolved_approve_i *
              (1 - (1 - e_report_i) * (1 - audit_rate))
```

where `e_report_i` is the post-approval report probability (the config field is
named `e_approve` for historical reasons).

Rejected rows have `e_i = 0` and are outside `P0`. Positivity requires
`e_i > 0` for every row in `P0`; the model raises if it fails.

### 5.2 Outcome-dependent (stress test)

When approved fraud is more likely to be labeled than approved legitimate
accounts:

```
P(approve report | fraud) = e_approve_fraud
P(approve report | legit) = 0
audit ~ Bernoulli(audit_rate) for all approved rows
```

The action-level propensity is then a weighted average of the fraud and
legitimate observation rates. It cannot separate the two without an
audit-labeled approved sample. This is the mechanism that breaks action-only
IPW/DR and motivates audit-only.

### 5.3 Covariate-dependent (stress test)

The report and review channel probabilities depend on standardized
`log1p(amount)`:

```
logit(e_report_i) = logit(e_approve) + beta * z_i
logit(kappa_review_i) = logit(kappa_review) + beta * z_i
z_i = standardized log1p(amount_i)
```

The audit remains random. The outcome model already includes `log1p(amount)`, so
DR has a second chance to adjust; IPW does not. This is the mechanism used to
test whether a covariate propensity model is needed.

### 5.4 Delay and censoring

Resolution is a lognormal delay draw. A label that has not arrived by the cutoff
is unresolved, not negative. The observation model uses the resolution
probability; the audit-only estimator uses the inverse resolution probability for
the audit sample.

## 6. Estimators

Let `O_i = 1` if the label is observed, `n_P0 = sum(P0)`, and
`w_i = O_i / e_i`.

### 6.1 Naive

```
V_naive = sum_i O_i C_i / sum_i O_i
```

The mean cost on the labeled subset. It is the number a naive backtest reports.
It is biased when observation depends on the action or the outcome.

### 6.2 IPW, Horvitz-Thompson

```
V_HT = (1 / n_P0) * sum_i w_i C_i
```

Unbiased for `V_P0` when `e_i` is the true observation probability and positivity
holds. High variance when weights are heavy.

### 6.3 IPW, Hájek

```
V_Hajek = sum_i w_i C_i / sum_i w_i
```

Self-normalized; usually more stable, at the cost of a small ratio bias.

### 6.4 Doubly robust

Fit an outcome model `mu_i = E[C(pi(X_i), Y_i) | X_i]` on the observed rows, then:

```
V_DR = (1 / n_P0) * sum_{i in P0} [ mu_i + w_i (C_i - mu_i) ]
```

Consistent if either the outcome model or the propensity model is correct. The
pilot uses a cross-fitted logistic outcome model:

- 5-fold cross-fitting on the observed rows;
- sample weights `1 / e_i` on the training fold;
- predict on the held-out fold;
- for rows outside the observed set, average the fold predictions.

### 6.5 Audit-only

```
V_audit = sum_{i in audit & resolved_approve} C_i / p_resolved_approve_i
          / sum_{i in audit & resolved_approve} 1 / p_resolved_approve_i
```

Unbiased for the approved population under random audit and correct resolution.
It does not target `P0` and is reported separately.

### 6.6 Reject-margin bounds

```
L = (n_P0 / n) * V_P0 + (n_rej / n) * mean_{rejected}(min cost of pi)
U = (n_P0 / n) * V_P0 + (n_rej / n) * mean_{rejected}(max cost of pi)
```

with the min/max taken over the candidate action's cost range:

| Action | Min | Max |
|---|---:|---:|
| approve | 0 | `fraud_loss(amount)` |
| review | `review_cost` | `review_cost + residual_fraud_loss` |
| reject | 0 | `false_reject_cost` |

These are **partial-identification intervals conditional on the `P0` estimate**.
They are not confidence intervals. The incumbent's narrow interval can miss the
true full value because the `P0` estimate itself is noisy and because the
unobserved cost can fall outside the assumed range.

### 6.7 Standard errors and coverage

The estimators use influence-function standard errors:

```
se = std(psi_i) / sqrt(n)
```

where `psi_i` is the per-row influence term and `n` is `n_P0` for the `P0`
estimators or the audit sample size for audit-only. Coverage is the share of
replications whose 95% interval `value +/- 1.96 se` contains the true target.
Coverage is a diagnostic, not a guarantee: heavy-tailed weights can undercover
even when the point estimate is close.

### 6.8 Propensity estimation

The pilot compares four modes:

| Mode | Definition | Purpose |
|---|---|---|
| `oracle` | true per-row `e` | isolates estimator behavior |
| `estimated` | action-level marginal rate from the draw | realistic minimum |
| `noisy` | oracle `e` times mean-one lognormal noise | misspecification stress |
| `covariate` | cross-fitted per-action logistic `P(O | action, X)` | covariate-dependent observation |

The covariate model is fit separately for review and approve rows with 3-fold
cross-fitting. Reject rows have `e = 0`. If an action has too few rows or one
class, the action mean is used. The model is a diagnostic correction, not a
claim that the observation mechanism is logistic.

## 7. Metrics

| Metric | Definition | What it answers |
|---|---|---|
| Relative bias | `(mean estimate - true) / true` | Is the estimator centered? |
| RMSE | `sqrt(mean((estimate - true)^2))` | Accuracy including variance |
| Coverage | share of 95% intervals containing the truth | Is uncertainty calibrated? |
| ESS | `(sum w)^2 / sum w^2` | How concentrated are the weights? |
| Max weight | `max w_i` | Is one row driving the estimate? |
| Rank inversions | pairwise disagreements with the true policy ranking | Would the estimate choose the wrong policy? |
| P(select true best) | share of replications selecting the true lowest-cost policy | Decision quality |
| Cost of misranking | true cost of the selected policy minus true best | Economic size of the error |
| Bounds width | `U - L` | How much the reject margin costs in precision |
| Bounds coverage | share of intervals containing `V_full` | Diagnostic, not a CI guarantee |

The pilot uses common random numbers across scenarios where possible: the same
seed and the same evaluation frame, so differences are attributable to the
scenario, not to a different draw.

## 8. Simulation design

### 8.1 Data

The evaluation frame is the BAF account-opening test window (months 5–6,
227,491 applications, 1.2576% fraud). The incumbent and candidate scores are
pre-trained V2 models; no evaluation labels are used to fit them. See
[`DATA.md`](DATA.md).

### 8.2 Policies

Four policies share the evaluation cost matrix:

| Policy | Score | Review capacity | Decision false-reject cost |
|---|---|---:|---:|
| `incumbent` | `p_fraud` (logistic) | 2% | config default |
| `better_model` | `p_fraud_lgbm` (LightGBM) | 2% | config default |
| `strict_cost` | `p_fraud_lgbm` | 2% | 0.02 |
| `lenient_cost` | `p_fraud_lgbm` | 2% | 0.50 |

The true `P0` ranking is computed from the realized costs, not from the scores.

### 8.3 Scenarios

The main scenario is 1% audit, 45-day median approve-label delay, and the default
false-reject cost. The sweeps vary audit size (0–2%), review capacity (1–10%),
approve-label delay (0.5–90 days), false-reject cost (0.02–0.50), and the
observation mechanism (outcome-dependent, covariate-dependent). See
[`PILOT_SPEC.md`](PILOT_SPEC.md) §8 for the pre-registered list and
[`../configs/pilot.yaml`](../configs/pilot.yaml) for the exact configuration.

### 8.4 Replications

The main pilot uses 100 replications; sweeps use 50; the sensitivity studies use
50. The replications are independent draws of the observation mechanism on the
same evaluation frame. The report includes Monte Carlo standard errors where
available.

## 9. What the method does not do

- It does not estimate a causal deployment effect. It estimates policy value
  under a stated observation model.
- It does not identify the full-population value when the reject margin is
  material.
- It does not replace a model-risk validator, legal review, or a bank's own
  cost accounting.
- It does not prove the observation model is correct. It reports what happens
  under alternative mechanisms.
- It does not optimize the fraud classifier. The policy layer is the object of
  study.

## 10. Related documents

- Pre-registration: [`PILOT_SPEC.md`](PILOT_SPEC.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Decisions: [`DECISIONS.md`](DECISIONS.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Code map: [`ARCHITECTURE.md`](ARCHITECTURE.md)
