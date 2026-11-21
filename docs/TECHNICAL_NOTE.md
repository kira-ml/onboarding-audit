# Technical Note — Identification, Estimators, and Bounds

**Status:** V1 methods note, 2026-11-21.
**Audience:** a model-risk validator or research reviewer who wants the argument,
not the narrative.
**Companion:** [`METHODS.md`](METHODS.md) (reference), [`RESULTS.md`](RESULTS.md)
(evidence), [`AUDIT_REPORT.md`](AUDIT_REPORT.md) (adversarial review).

---

## 1. Estimand

Let `A ∈ {approve, review, reject}` be the logging action, `X` pre-decision
covariates, `Y ∈ {0,1}` fraud, and `C(a, Y, amount)` the cost of action `a`.

The primary estimand is

```
V_P0(π) = E[ C(π(X), Y) | A != reject ]
```

the mean cost of policy `π` on the population the incumbent did not reject
(`P0`). The candidate policy is evaluated on the same rows; its actions may
differ from the logged actions, but `Y` is a property of the application, not of
the action.

The reject margin is **not** identified: for `A = reject`, `Y` is never observed.
The full-population value is bounded, not estimated.

## 2. Identification

`V_P0` is identified under:

1. **Consistency:** the observed label is the application's fraud status.
2. **Positivity:** `e_i = P(R_i = 1 | A_i, X_i) > 0` on `P0`.
3. **No unmeasured confounding of observation:** `R ⊥ Y | A, X`.
4. **Correct observation model:** `e` is known or consistently estimated.
5. **Stable cost model.**
6. **No interference.**
7. **Action-invariant outcome:** the action does not change `Y`.

Assumption 3 is the one that fails in practice when approved fraud is more
likely to be reported than approved legitimate behavior. The report cannot test
it; it requires a declaration and, ideally, an audit.

## 3. Estimators

With `R_i` the observation indicator and `w_i = R_i / e_i`:

```
naive   = mean(C_i | R_i = 1)
IPW-HT  = (1/n_P0) sum_i w_i C_i
IPW-Hajek = sum_i w_i C_i / sum_i w_i
DR      = (1/n_P0) sum_i [ m(X_i, π) + w_i (C_i - m(X_i, π)) ]
```

where `m(X, π) = E[C(π(X), Y) | X]` is estimated by a cross-fitted outcome model.
`C_i` is the cost under the candidate action, computed from the observed `Y`; this
is a counterfactual cost, not the logged cost.

The influence term for DR is

```
psi_i = m_i + w_i (C_i - m_i) - V_hat
```

and `se = sd(psi_i) / sqrt(n_P0)`. The report uses the same form for the paired
candidate-vs-incumbent difference, `psi_i(candidate) - psi_i(incumbent)`.

### 3.1 Why DR is doubly robust

Write `m*` for the true outcome mean and `e*` for the true propensity. Then

```
E[DR] = E[m] + E[(e*/e)(m* - m)]
```

If `m = m*`, the second term is zero for any `e > 0`. If `e = e*`, the second
term is `E[m* - m]`, which cancels the first term. Hence `E[DR] = V` if either
model is correct. The known-truth test in `RESULTS.md` §10 confirms this:
**+0.14%** with a wrong outcome model, **+0.36%** with a wrong propensity.

The property is a safety net, not a guarantee: when both models are wrong, DR is
biased (**+2.09%** in the test).

## 4. Bounds

For a logging-rejected row, the candidate action's cost is bounded by the cost
model's min/max for that action:

| Candidate action | min | max |
|---|---:|---:|
| approve | 0 | `fraud_loss(amount)` |
| review | `review_cost` | `review_cost + residual_fraud_loss` |
| reject | 0 | `false_reject_cost` |

The conditional interval is

```
L(v) = (n_P0/n) v + (n_rej/n) mean(min_cost)
U(v) = (n_P0/n) v + (n_rej/n) mean(max_cost)
```

where `v` is the `P0` estimate. It is **not** a confidence interval: it ignores
the sampling error in `v`.

Because `L` and `U` are monotone increasing in `v` (the coefficient `n_P0/n` is
positive), a 95% interval for `v` maps to a 95% interval for the identified set:

```
[L(v_hat) - 1.96 (n_P0/n) se_v,  U(v_hat) + 1.96 (n_P0/n) se_v]
```

This widened interval covers the true full-population value with at least 95%
probability under the bounds assumptions. It is conservative because it ignores
the correlation between the `P0` estimate and the rejected-row cost. The pilot
confirms **99–100%** coverage in the main scenario, at ~4× the narrow width.

The 11 widened-interval failures are exactly the cells where `v` itself is
biased (outcome-dependent labels, action-level covariate misspecification,
`delay_90`). Widening cannot repair a biased center.

## 5. The identification gate

| Check | Threshold | Rationale |
|---|---|---|
| Positivity | `e > 0` on `P0` (observed rows for a provided column) | A zero-propensity row cannot be reweighted |
| Observed labels | ≥ 100 | Below this, the normal approximation and the ESS are not meaningful |
| Labels per non-rejected action | ≥ 30 | Prevents one action from dominating the weights |
| ESS | ≥ 100 | Guards against a few rows driving the estimate |
| Max weight | ≤ 100 | A single row should not carry the estimate |
| Cost support | finite, non-negative | A negative cost is not a decision input |
| Observation mechanism | declared; `outcome` refuses | The gate cannot test the assumption that matters most |
| Propensity calibration | observed/expected > 1.5 refuses; < 0.5 flags | A provided `e` can be wrong even when it is positive |

The thresholds are conventions, not derivations. They are deliberately
conservative: a false "not identified" is cheaper than a confident memo on an
unidentified quantity.

## 6. Monte Carlo design

- 100 replications for the main scenario, 50 for each sweep/sensitivity cell.
- Common random numbers: the same evaluation frame and seed across scenarios, so
  differences are attributable to the scenario.
- Bias is a mean over replications; its Monte Carlo standard error is
  `sd(estimate)/sqrt(reps)`. The 95% MC bound on `|bias|` is
  `|mean bias| + 1.96 mc_se`.
- Coverage proportions use Wilson intervals. The coverage interval treats
  policy–replications as independent; they are not, so it is an optimistic lower
  bound on the uncertainty.
- A 50-replication cell cannot distinguish 84.5% from 85.0% coverage. The claims
  that survive are the large contrasts, not the decimals.

## 7. What the evidence supports

| Claim | Evidence tier | Basis |
|---|---|---|
| The naive labeled mean is biased under selective observation | E2 (known-truth simulation, pre-registered sweep) | 12/12 cells, 7.8–538.5% |
| DR recovers the `P0` value with known propensities | E2 | mean bias ≤1.89%, MC upper 4.3–9.6% |
| DR is doubly robust | E2 (known-truth test) | +0.14% / +0.36% |
| The ranking can flip | E2 | naive P(best) 0%, DR 64–100% |
| The result holds across both test months | E2 (split-sample) | naive 230–255%, DR 0.43–0.89%, naive P(best) 0% in both |
| The reject margin is not point-identified | E2 (bounds + F5) | narrow 15/88, widened 77/88 |
| The method works on a bank's log | **not established** | no partner log, no independent validator |
| The reject margin can be estimated from logs alone | **false** | F5 narrow failure |

## 8. Open problems

1. **Resolution-weighted audit-only in the report.** The report now
   post-stratifies audit labels by follow-up time and weights by
   `1/P(observed)` within each stratum. The remaining assumption is missing at
   random *within* a stratum; a per-row Kaplan-Meier correction is the next step.
2. **Nuisance-estimation uncertainty in the comparison.** The paired influence
   interval treats the outcome model and propensity as fixed. A bootstrap that
   refits both would be more honest, at a large computational cost.
3. **Outcome-dependent labels.** No action-only estimator survives; the audit is
   the only fallback. A design that combines a small audit with a covariate
   propensity model is untested.
4. **External validity.** BAF is one public synthetic dataset. A second benchmark
   or a partner log is the only way to test generalization.
5. **Cost-model validation.** The normalized matrix is an assumption. A bank's
   cost curve is the input the method cannot supply.

## 9. Related documents

- Methods reference: [`METHODS.md`](METHODS.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Audit report: [`AUDIT_REPORT.md`](AUDIT_REPORT.md)
- Model card: [`MODEL_CARD.md`](MODEL_CARD.md)
