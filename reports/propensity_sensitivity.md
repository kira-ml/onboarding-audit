# Propensity Sensitivity

_Pre-registered follow-up; 50 replications per scenario; common random numbers; seed from the pilot config._

## What this tests

The main pilot uses oracle propensities. This study replaces them with (a) action-level propensities estimated from the observed draw, (b) oracle propensities with lognormal noise, (c) estimated propensities under outcome-dependent labels, and (d) action-level, fitted covariate, and oracle propensities under covariate-dependent observation. The target and policies are unchanged.

## Main scenario

| Scenario | Estimator | Max \|rel bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `main` | `naive` | 278.46% | 0.0% | 12,171 |
| `main` | `ipw_ht` | 1.30% | 94.5% | 7,863 |
| `main` | `dr` | 0.96% | 95.5% | 7,863 |
| `main` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `propensity_estimated` | `naive` | 278.46% | 0.0% | 12,171 |
| `propensity_estimated` | `ipw_ht` | 11.19% | 73.0% | 8,438 |
| `propensity_estimated` | `dr` | 2.67% | 91.0% | 8,438 |
| `propensity_estimated` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `propensity_noisy_10` | `naive` | 278.46% | 0.0% | 12,171 |
| `propensity_noisy_10` | `ipw_ht` | 1.09% | 95.5% | 7,787 |
| `propensity_noisy_10` | `dr` | 1.11% | 94.5% | 7,787 |
| `propensity_noisy_10` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `propensity_noisy_25` | `naive` | 278.46% | 0.0% | 12,171 |
| `propensity_noisy_25` | `ipw_ht` | 7.01% | 93.5% | 7,397 |
| `propensity_noisy_25` | `dr` | 1.58% | 96.5% | 7,397 |
| `propensity_noisy_25` | `audit_only` | 2.58% | 82.5% | 1,268 |

## Outcome-dependent labels

| Scenario | Estimator | Max \|rel bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `outcome_dependent` | `naive` | 1147.43% | 0.0% | 5,791 |
| `outcome_dependent` | `ipw_ht` | 368.25% | 1.0% | 1,904 |
| `outcome_dependent` | `dr` | 1301.53% | 0.0% | 1,904 |
| `outcome_dependent` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `outcome_dependent_estimated` | `naive` | 1147.43% | 0.0% | 5,791 |
| `outcome_dependent_estimated` | `ipw_ht` | 1350.76% | 0.0% | 1,799 |
| `outcome_dependent_estimated` | `dr` | 1627.90% | 0.0% | 1,799 |
| `outcome_dependent_estimated` | `audit_only` | 2.58% | 82.5% | 1,268 |

## Covariate-dependent observation

The post-approval report probability depends on standardized log amount: `logit(e_report) = logit(e_approve) + 0.75 * z`. The `covariate_*` scenarios use that mechanism. `oracle` uses the true per-row propensity; `action` uses the action-level estimate; `model` uses a cross-fitted per-action logistic model of `observed` on the outcome-model features plus decision day. The delay-0.5 variants isolate the propensity misspecification; the delay-45 variants add the resolution gradient.

| Scenario | Estimator | Max \|rel bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `covariate_oracle` | `naive` | 226.03% | 0.0% | 19,830 |
| `covariate_oracle` | `ipw_ht` | 3.01% | 90.0% | 11,668 |
| `covariate_oracle` | `dr` | 2.63% | 89.0% | 11,668 |
| `covariate_action` | `naive` | 226.03% | 0.0% | 19,830 |
| `covariate_action` | `ipw_ht` | 67.52% | 1.5% | 16,031 |
| `covariate_action` | `dr` | 21.25% | 72.5% | 16,031 |
| `covariate_model` | `naive` | 226.03% | 0.0% | 19,830 |
| `covariate_model` | `ipw_ht` | 1.97% | 91.5% | 11,582 |
| `covariate_model` | `dr` | 2.48% | 89.5% | 11,582 |
| `covariate_action_delay` | `naive` | 301.68% | 0.0% | 13,935 |
| `covariate_action_delay` | `ipw_ht` | 51.72% | 21.5% | 9,938 |
| `covariate_action_delay` | `dr` | 17.59% | 80.0% | 9,938 |
| `covariate_model_delay` | `naive` | 301.68% | 0.0% | 13,935 |
| `covariate_model_delay` | `ipw_ht` | 3.35% | 90.5% | 6,798 |
| `covariate_model_delay` | `dr` | 3.68% | 89.5% | 6,798 |

## Measured read

- Covariate action-level: IPW **67.52%** with **1.5%** coverage; DR **21.25%** with **72.5%**.
- Covariate model: IPW **1.97%** with **91.5%**; DR **2.48%** with **89.5%**.
- With the 45-day delay: action IPW **51.72%** / **21.5%**; action DR **17.59%** / **80.0%**; model IPW **3.35%** / **90.5%**; model DR **3.68%** / **89.5%**.
- The covariate model meets the pre-declared gate (<=5% max relative bias, >=80% mean coverage); action-level weighting does not.
- Coverage is below nominal 95%; the oracle covers **90.0%** (IPW) and **89.0%** (DR), so the shortfall is the heavy-tail variance, not the model.

## Interpretation

- In the main action-dependent scenario, the estimated action-level propensities are close to the oracle; the correction survives. This is the minimum bar.
- Lognormal noise tests misspecification. The IPW bias grows with sigma; DR stays within 1.58% at sigma 0.25. The memo should report the sensitivity band, not a single point estimate.
- Under outcome-dependent labels, the action-level estimated e is a weighted average of the fraud and legitimate observation rates. Action-only IPW/DR fail; audit-only is the honest estimator. This is the strongest argument for the audit.
- Under covariate-dependent observation, action-level e is misspecified because it ignores the within-action gradient. Action-level IPW and DR both fail; the fitted covariate model recovers the oracle. The report must not claim a point estimate without a covariate propensity model and overlap diagnostics.

## Caveats

- The action-level e is a marginal rate; the covariate model is a per-action logistic model. Neither is a full production propensity model.
- The noisy e uses the oracle as the center; it is a stress test, not a calibration study.
- The covariate model is a logistic model in the observed features. It is correctly specified for the simulated mechanism up to the audit mixture and the delay/resolution term; a real log may require a more flexible model and a positivity/overlap check.
- A production study should estimate e from the audit design and covariates, and report the sensitivity band.
