# Pilot Specification — Pre-Registered

**Status:** Frozen before the first account-opening pilot run.
**Date:** 2026-11-19.
**Owner:** Ken Ira Lacson Talingting.
**Purpose:** Test whether naive onboarding-policy evaluation is materially
biased, and whether a corrected estimator, bound, or audit design makes the
estimate defensible. This is the cheapest decisive test before building the
full tool.

---

## 1. Decision this pilot informs

**Go/no-go:** Does the account-opening measurement problem have a real premise,
and can a defensible estimate be produced from logs?

| Outcome | Verdict |
|---|---|
| Naive relative bias > 5% in the main scenario **or** at least one pairwise policy-rank inversion vs the true ranking | Premise is real |
| Premise real **and** at least one of IPW, DR, or audit-only has relative bias <= 5% and 95% CI coverage >= 80% on the identified population | Correction is credible |
| Premise real but no estimator meets the bar | Narrow to a bounds/diagnostic protocol |
| Naive bias <= 5% and no rank inversion | Premise weak; pivot to the FiFAR capacity study or a descriptive decision-value benchmark |

The pilot also tests whether the **reject margin** is point-identified. It is
not expected to be. The result will be reported as bounds, not a point estimate.

---

## 2. Estimand

### 2.1 Primary estimand: identified population

Let `P0` be the set of applications the **logging (incumbent) policy did not
reject** — i.e., its action was `approve` or `review`. The primary target is:

```
V_P0(pi) = E[ C(pi(X), Y) | X in P0 ]
```

where `pi` is a candidate onboarding policy, `Y` is account-opening fraud, and
`C(a, Y)` is the realized cost of action `a` under the evaluation cost matrix.

**Why this population:** rejected applications have no observed outcome. A
point estimate of a policy's value on the full population, including the
logging-rejected applicants, is not identified from logs alone. Restricting the
primary estimand to `P0` keeps the claim honest and answers the decision: *for
the applications the institution would still consider, is the new policy
better?*

### 2.2 Secondary estimand: full-population bounds

For the full population (including logging-rejected applications), report an
interval `[L, U]` obtained by bounding the unobserved cost of the rejected
applications. This is a partial-identification result, not a point estimate.
The bounds are reported separately and never used to claim a precise policy
value.

### 2.3 What is not claimed

- No point-identified full-population value.
- No causal deployment effect.
- No claim about a real bank's production system.
- No claim that a random approval/rejection experiment is acceptable.

---

## 3. Data

| Item | Choice |
|---|---|
| Dataset | BAF `Base.csv` test window, processed as `data/scored_test.parquet` |
| Unit | Online bank account application |
| Rows | 227,491 (months 5–6) |
| Label | `fraud_bool`; base rate 1.2576% |
| Exposure | `amount_proxy = proposed_credit_limit` (credit-line exposure proxy) |
| Scores | `p_fraud` (logistic regression, V2 incumbent) and `p_fraud_lgbm` (LightGBM) |
| Score provenance | Trained on months 0–2, validated on 3–4; no evaluation labels used |
| Features for the outcome model | scores + pre-decision numeric features + `log1p(amount)` + month |
| Replication | FiFAR capacity layer in a follow-on; not in this pilot |

The V2 `observed` and `label_month` columns are ignored; this pilot simulates
its own observation mechanism. The true `fraud_bool` is used only for ground
truth and for the estimators' labeled rows.

**Domain note:** BAF is account-opening data, not transaction authorization
data. The action is approve/review/reject an application, not approve/review/
block a transaction.

---

## 4. Policies and cost model

### 4.1 Actions

`a in {approve, review, reject}`. The policy chooses the action with the lowest
expected cost:

```
c_approve = p * fraud_loss
c_review  = review_cost + p * residual_fraud_loss
c_reject  = (1 - p) * false_reject_cost
```

A review capacity cap `K` keeps the top-`K` review-band applications by savings
and reroutes the overflow by the approve-vs-reject argmin.

### 4.2 Cost matrix (normalized, assumed)

| Parameter | Base value | Meaning |
|---|---:|---|
| `fraud_loss_rate` | 0.0019187869 | `fraud_loss = amount * rate`; normalized cost unit, not pesos |
| `review_cost` | 0.02 | Manual KYC review |
| `false_reject_cost` | 0.10 | Lost legitimate applicant (inclusion harm) |
| `residual_fraud_loss` | 0.30 | Fraud that survives a review |
| `amount_scaled` | true | Credit-line exposure proxy |

These are the V2 normalized values, reused for comparability. They are **not**
production estimates. The false-reject cost is the key inclusion parameter and
is swept (0.02, 0.10, 0.50).

### 4.3 Policies

| Policy | Score | Review capacity | Decision cost matrix | Role |
|---|---|---:|---|---|
| `incumbent` | `p_fraud` (LR) | 2% | base | Logging policy and self-evaluation case |
| `better_model` | `p_fraud_lgbm` | 2% | base | Stronger score, same capacity |
| `strict_cost` | `p_fraud_lgbm` | 2% | `false_reject_cost=0.02` | Rejects more; tests the reject margin |
| `lenient_cost` | `p_fraud_lgbm` | 2% | `false_reject_cost=0.50` | Rejects less; tests inclusion |

The **true value** of every policy is computed with the **base** cost matrix.
A policy may use a different cost matrix to make decisions; that is a policy
assumption, not the evaluation target.

### 4.4 Capacity scenarios

The logging policy stays at 2% in every scenario. The capacity sweep replaces
`better_model` with capacities 1%, 5%, and 10%, keeping `incumbent` as the
reference.

---

## 5. Observation model

### 5.1 Decision time and cutoff

- Decision day `T`: uniform within month 5 (`[0,30)`) or month 6 (`[30,60)`).
- Evaluation cutoff: day 90 (end of month 7).
- A label resolves if `T + delay <= 90`; otherwise it is censored.

### 5.2 Label channels

| Logging action | Channel | Probability | Delay (median, sigma) |
|---|---|---:|---|
| `review` | KYC/review disposition | 0.90 | 3 days, 0.5 |
| `approve` | Post-approval detection / report | 0.05 | 45 days, 0.8 |
| `approve` | Random post-hoc verification audit | `rho_audit` | 45 days, 0.8 |
| `reject` | None | 0 | — |

The audit is a **random post-hoc verification of approved applications**, not a
random approval or rejection. It labels a random sample of approved
applications without changing the decision.

### 5.3 Propensities

```
e_review  = p_resolved_review(T)  * kappa_review
e_approve = p_resolved_approve(T) * (1 - (1 - e_approve)(1 - rho_audit))
e_reject  = 0
```

`P0` is the logging approve/review population, so positivity holds for every
row in `P0` (`e_review > 0`, `e_approve > 0`). The logging-rejected population
is outside the primary estimand and is handled by bounds.

### 5.4 Outcome-dependent stress scenario

In the `outcome_dependent` scenario, approved **fraud** is labeled with
probability 0.30, while approved **legitimate** applications are labeled only
by the audit (`rho_audit`). This violates the action-only observation
assumption. The pilot reports:

- action-only IPW, which is biased;
- audit-only, which is unbiased for the approved population;
- the label-source mix, which is the diagnostic a team could inspect.

The oracle propensity conditional on `Y` is a diagnostic, not an estimator.

---

## 6. Estimators

All estimators target `V_P0(pi)` unless stated.

| Estimator | Definition |
|---|---|
| **Naive** | Mean realized cost on observed/labeled `P0` rows |
| **IPW-HT** | `(1/n_P0) * sum_i (M_i/e_i) * C_i(pi)` over `P0` |
| **IPW-Hajek** | `sum_i w_i C_i / sum_i w_i` over `P0` |
| **DR** | `(1/n_P0) sum_i mu_hat(X_i, pi) + (1/n_P0) sum_i (M_i/e_i)[C_i(pi) - mu_hat(X_i, pi)]` |
| **Audit-only** | Weighted mean cost on approved + audit + resolved rows, weight `1/p_resolved`; target the approved population |
| **Bounds** | Primary `P0` estimate plus the min/max cost of the logging-rejected rows; target the full population |
| **Oracle** | Mean realized cost with true labels; reference only |

### 6.1 DR outcome model

`mu_hat(X, a)` is the expected cost of action `a` given features, computed from
an estimated fraud probability `p_hat(X)`:

```
mu_hat(approve) = p_hat * amount * fraud_loss_rate
mu_hat(review)  = review_cost + p_hat * residual_fraud_loss
mu_hat(reject)  = (1 - p_hat) * false_reject_cost
```

`p_hat` is a logistic regression (L2 `C=0.5`, `max_iter=300`) fit on observed
`P0` rows with sample weights `1/e_i`, 5-fold cross-fitted. Features: the two
scores, `customer_age`, `credit_risk_score`, `velocity_6h`, `velocity_24h`,
`velocity_4w`, `bank_months_count`, `zip_count_4w`,
`session_length_in_minutes`, `log1p(amount)`, `month`. All are pre-decision.
No label, observation flag, or post-decision field.

The DR residual uses `C_i(pi)` for every observed row, not only rows where the
logging action equals the candidate action. The label identifies the
counterfactual cost for any action.

### 6.2 Standard errors and coverage

- Naive: `sd(C_obs)/sqrt(n_obs)`.
- IPW-HT: influence values `psi_i = (M_i/e_i) C_i - V`; `SE = sd(psi)/sqrt(n_P0)`.
- IPW-Hajek: delta-method influence values.
- Audit-only: ratio influence values with weights `1/p_resolved`.
- DR: `psi_i = mu_hat_i + (M_i/e_i)(C_i - mu_hat_i) - V`; `SE = sd(psi)/sqrt(n_P0)`.
- Coverage: 95% CI `V_hat +/- 1.96 SE` contains `V_P0`.
- The SEs treat the outcome model as fixed; model-selection uncertainty is a
  stated limitation.

### 6.3 Bounds

For each logging-rejected application and candidate action `a1`:

| Candidate action | Min cost | Max cost |
|---|---:|---:|
| approve | 0 | `fraud_loss` |
| review | `review_cost` | `review_cost + residual_fraud_loss` |
| reject | 0 | `false_reject_cost` |

Then:

```
V_full in (n_P0/n) * V_P0_hat + (n_rej/n) * [mean(min_rej), mean(max_rej)]
```

The interval is reported with its width. It is a valid partial-identification
interval under the stated cost model; it is not a confidence interval.

---

## 7. Metrics

For each scenario, policy, and estimator, over `R` replications:

| Metric | Definition |
|---|---|
| Bias | `mean(V_hat) - V_P0` |
| Relative bias | `bias / V_P0` |
| RMSE | `sqrt(mean((V_hat - V_P0)^2))` |
| 95% CI coverage | fraction of replications whose CI contains `V_P0` |
| Mean SE | mean estimated standard error |
| ESS | `(sum w)^2 / sum w^2` |
| Max weight | `max(1/e)` among observed rows |
| Overlap | fraction of `P0` rows with `e < 0.01` |

Ranking metrics across the four policies, per replication:

| Metric | Definition |
|---|---|
| Spearman rho | rank correlation between estimated and true `V_P0` |
| Pairwise inversions | number of policy pairs ordered differently from the truth |
| P(select true best) | fraction of replications where the lowest estimate is the true best policy |
| Cost of misranking | `V_P0(estimated best) - V_P0(true best)` |

Bounds metrics:

- interval width;
- coverage of `V_full` (the true full-population value).

Audit-only metrics:

- bias and coverage against the true approved-population value.

Monte Carlo precision: report the MC standard error of the mean estimate.

---

## 8. Scenarios

All scenarios use the main observation model unless the column changes it.
Common random numbers are used within a scenario.

| ID | Audit | Candidate capacity | Approve delay | Approve labels | Base false-reject cost | Reps | Purpose |
|---|---:|---:|---:|---|---:|---:|---|
| `main` | 1% | 2% | 45 d | action-only | 0.10 | 100 | Headline |
| `audit_0` | 0% | 2% | 45 d | action-only | 0.10 | 50 | Audit value |
| `audit_05` | 0.5% | 2% | 45 d | action-only | 0.10 | 50 | Audit sweep |
| `audit_2` | 2% | 2% | 45 d | action-only | 0.10 | 50 | Audit sweep |
| `capacity_1` | 1% | 1% | 45 d | action-only | 0.10 | 50 | Candidate capacity |
| `capacity_5` | 1% | 5% | 45 d | action-only | 0.10 | 50 | Candidate capacity |
| `capacity_10` | 1% | 10% | 45 d | action-only | 0.10 | 50 | Candidate capacity |
| `delay_0` | 1% | 2% | 0.5 d | action-only | 0.10 | 50 | No delay |
| `delay_30` | 1% | 2% | 30 d | action-only | 0.10 | 50 | Moderate delay |
| `delay_90` | 1% | 2% | 90 d | action-only | 0.10 | 50 | Severe censoring |
| `outcome_dependent` | 1% | 2% | 45 d | fraud 30%, legit audit-only | 0.10 | 50 | Violation stress test |
| `frej_002` | 1% | 2% | 45 d | action-only | 0.02 | 50 | Inclusion trade-off |
| `frej_050` | 1% | 2% | 45 d | action-only | 0.50 | 50 | Inclusion trade-off |

The `frej_*` scenarios rebuild all policies with the scenario's false-reject
cost; the true value uses the same cost matrix. The `outcome_dependent` scenario
keeps the base cost matrix and changes only the approved-label mechanism.

---

## 9. Negative controls and falsification

| ID | Test | Pass criterion |
|---|---|---|
| F1 | Full observation: `kappa=1`, `e_approve=1`, `rho_audit=1`, delay 0 | Naive = IPW = DR = oracle on `P0` |
| F2 | Full audit, no delay: `rho_audit=1`, `kappa=1`, delay 0 | Corrected estimators equal the oracle |
| F3 | Known-propensity recovery | Mean IPW across reps within 2 MC SE of `V_P0` |
| F4 | Label permutation | Permuting `Y` leaves policy actions unchanged; estimates track the permuted truth; no leakage |
| F5 | Bounds validity | The full-population interval contains `V_full` in >= 90% of reps |
| F6 | Capacity | Review count <= `ceil(capacity * n)` in every scenario |
| F7 | Monte Carlo convergence | MC SE of the main-scenario bias < 1% of `V_P0` |
| F8 | No label leakage | Policy actions are a deterministic function of scores and amounts only |

F1/F2/F4/F6/F8 are unit-test level. F3/F5/F7 are reported in the pilot output.

---

## 10. Decision rule and kill criteria

**Premise supported:** `main` naive |relative bias| > 5% **or** at least one
pairwise rank inversion vs the true `V_P0` ranking.

**Correction supported:** at least one of IPW or DR has a
**maximum absolute relative bias across the four policies <= 5%** and
**mean 95% CI coverage >= 80%** in `main`. Audit-only is a separate
approved-population diagnostic.

**Audit value supported:** at least one corrected estimator's RMSE is lower at
2% audit than at 0% audit, with a larger ESS.

**Reject margin not identified (expected):** the full-population bounds width
exceeds 5% of `V_full` for `strict_cost` or `lenient_cost`, and the interval
does not collapse without an assumption or controlled approval design.

| Trigger | Action |
|---|---|
| Day 14: account-opening reframing cannot be defended | Pivot to the FiFAR capacity study |
| Day 30: H1 and H2 both fail | Pivot to a descriptive decision-value benchmark |
| Day 45: H3 fails even with a 2% audit | Narrow to a bounds/diagnostic protocol |
| Day 60: two external readers cannot use the CLI/report | Drop the tool; keep the paper and protocol |
| Day 75: replication is not feasible | State it as a limitation |
| Any time: asked to claim PH production data, GCash data, or a causal deployment effect | Stop; rewrite the claim |
| Any time: the only way to get data is to scrape or use PII | Stop; public-data only |

---

## 11. Reproducibility

- Master seed: `20261120`.
- **Common random numbers:** the master seed is used for every scenario; the
  scenario index is metadata only. This isolates the effect of the audit rate,
  capacity, and delay across scenarios.
- Per-replication outcome-model fold seed: `master_seed + rep`.
- Package versions and the config hash are written to the JSON output.
- `python -m onboarding_audit.pilot --config configs/pilot.yaml --out reports`
- The JSON is the source of truth; the Markdown report is generated from it.

---

## 12. Calibration disclosure

This is the first account-opening pilot. The earlier transaction-framed
exploratory run in the archived repository is **not** used as evidence and is
not comparable: it evaluated a different decision unit on the same dataset.
The main scenario is pre-registered before the first run.

---

## 13. Non-goals

- No FiFAR analyst layer in v0.1 (planned follow-on).
- No IEEE-CIS/PaySim transaction extension.
- No propensity estimation; propensities are oracle-known to isolate estimator
  behavior. A follow-on will estimate them and test sensitivity.
- No new estimator theory; the contribution is the account-opening application,
  the audit design, the capacity layer, and the usable memo.
- No production integration or vendor replacement.
- No random approval/rejection experiment.

---

## 14. Post-run addendum (2026-11-19)

The pilot ran as pre-registered: 13 scenarios, 700 replications, seed
`20261120`, 1,114 s. The full claim ledger is in `docs/CLAIMS.md`. Summary:

| Hypothesis | Verdict | Key number |
|---|---|---|
| H1 naive bias > 5% | **Supported** | Relative bias **+111.55% to +278.49%** |
| H2 naive rank inversion | **Supported** | Mean **1.00** inversion; P(select true best) **0%** |
| H3 correction <= 5% / coverage >= 80% | **Supported** | DR max **0.94%**, mean coverage **96.0%**; IPW **1.18% / 95.0%** |
| H4 audit value | **Supported (modest effect)** | DR RMSE **0.001159 → 0.001068** (0% → 2%); ESS **6,610 → 9,126**; decisive under outcome-dependent labels |
| H5 reject margin not point-identified | **Supported** | Widest bounds **0.009942**; incumbent coverage **35%** (not a CI) |
| H6 outcome-dependent labels break action-only IPW | **Supported** | Audit-only **-2.37% to -1.98%**; IPW **+43.9% to +368.3%**; DR **+596.4% to +1301.5%** |

**Post-run methodological note:** H2 is evaluated on the naive estimator only;
H3 is evaluated on the `P0` estimators (IPW/DR). Audit-only targets the approved
population and is reported separately. The bounds are partial-identification
intervals conditional on the `P0` estimate, not confidence intervals. See
`docs/DECISIONS.md` D7 and D8.

### 15. Propensity sensitivity addendum (2026-11-20)

The oracle-propensity pilot was followed by a 50-replication sensitivity with
estimated and noisy propensities:

- Estimated action-level `e`: DR max **2.67%**, coverage **91.0%**; IPW max
  **11.19%**, coverage **73.0%**.
- Lognormal noise sigma 0.25: DR **1.58% / 96.5%**; IPW **7.01% / 93.5%**.
- Outcome-dependent labels with estimated `e`: audit-only **2.58% / 82.5%**;
  IPW **1350.8%**; DR **1627.9%**.

The claim gate is met for **DR**, not for IPW. The paper should claim DR
robustness, not IPW robustness. See `reports/propensity_sensitivity.md` and
`docs/DECISIONS.md` D10.

### 16. Covariate-dependent observation addendum (2026-11-20)

**Motivation.** The action-level sensitivity treats observation as a function of
the logging action only. A real log may have `P(observed | action, X)` depending
on the application. If so, action-level `e` is misspecified even when it is
estimated without noise.

**Mechanism.** The post-approval report probability is
`logit(e_report) = logit(e_approve) + beta * z`, where `z` is standardized
`log1p(amount)` and `beta = 0.75`. The review channel uses the same gradient on
`kappa_review`. The audit remains random. `z` is pre-decision, so the mechanism
is a legitimate observation design, not label leakage. The outcome model already
includes `log1p(amount)`, so DR has a second chance to adjust; IPW does not.

**Scenarios.** Five 50-replication scenarios:

| Scenario | Delay | Propensity | Purpose |
|---|---:|---|---|
| `covariate_oracle` | 0.5 | true per-row `e` | ceiling |
| `covariate_action` | 0.5 | action-level estimated `e` | misspecified comparator |
| `covariate_model` | 0.5 | cross-fitted per-action logistic `P(observed | action, X)` | fitted correction |
| `covariate_action_delay` | 45 | action-level estimated `e` | delay + misspecification |
| `covariate_model_delay` | 45 | cross-fitted covariate model | delay robustness |

The covariate model uses the outcome-model features plus standardized decision
day, fit with 3-fold cross-fitting within each action. The action-level estimate
is the audit-aware marginal rate.

**Pre-declared read.** The correction is adequate if the covariate model's DR/IPW
max relative bias is within 5% and mean coverage is at least 80%. The
action-level comparator is expected to fail IPW; DR may be partially robust
because the outcome model includes the observation covariate. If the covariate
model does not recover the oracle, the paper reports the propensity-sensitivity
band and does not claim a point estimate under covariate-dependent observation.

**Variance caveat.** Covariate-dependent observation creates heavy-tailed
weights. The HT variance estimator can undercover even with oracle propensities;
the report must show ESS, max weight, and the weight range. A point estimate
within 5% is not evidence that the interval is calibrated.

**Status.** The 50-replication run is in progress; results will be appended to
this section and to `reports/propensity_sensitivity.md`.
