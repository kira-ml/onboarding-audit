# Propensity Sensitivity

_Pre-registered follow-up; 50 replications per scenario; common random numbers; seed from the pilot config._

## What this tests

The main pilot uses oracle propensities. This study replaces them with (a) action-level propensities estimated from the observed draw, (b) oracle propensities with lognormal noise, and (c) estimated propensities under outcome-dependent labels. The target and policies are unchanged.

## Main scenario

| Scenario | Estimator | Max \|rel bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `main` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `main` | `dr` | 0.96% | 95.5% | 7,863 |
| `main` | `ipw_ht` | 1.30% | 94.5% | 7,863 |
| `propensity_estimated` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `propensity_estimated` | `dr` | 2.67% | 91.0% | 8,438 |
| `propensity_estimated` | `ipw_ht` | 11.19% | 73.0% | 8,438 |
| `propensity_noisy_10` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `propensity_noisy_10` | `dr` | 1.11% | 94.5% | 7,787 |
| `propensity_noisy_10` | `ipw_ht` | 1.09% | 95.5% | 7,787 |
| `propensity_noisy_25` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `propensity_noisy_25` | `dr` | 1.58% | 96.5% | 7,397 |
| `propensity_noisy_25` | `ipw_ht` | 7.01% | 93.5% | 7,397 |

## Outcome-dependent labels

| Scenario | Estimator | Max \|rel bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `outcome_dependent` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `outcome_dependent` | `dr` | 1301.53% | 0.0% | 1,904 |
| `outcome_dependent` | `ipw_ht` | 368.25% | 1.0% | 1,904 |
| `outcome_dependent_estimated` | `audit_only` | 2.58% | 82.5% | 1,268 |
| `outcome_dependent_estimated` | `dr` | 1627.90% | 0.0% | 1,799 |
| `outcome_dependent_estimated` | `ipw_ht` | 1350.76% | 0.0% | 1,799 |

## Interpretation

- In the main action-dependent scenario, the estimated action-level propensities should be close to the oracle; the correction should survive. This is the minimum bar.
- Lognormal noise tests misspecification. If the bias grows quickly with sigma, the memo must report a propensity-sensitivity band, not a single point estimate.
- Under outcome-dependent labels, the action-level estimated e is a weighted average of the fraud and legitimate observation rates. Action-only IPW/DR are expected to fail; audit-only is the honest estimator. This is the strongest argument for the audit.

## Caveats

- The estimated e is action-level and estimated from the same draw; it is not a full propensity model with covariates.
- The noisy e uses the oracle as the center; it is a stress test, not a calibration study.
- A production study should estimate e from the audit design and covariates, and report the sensitivity band.

## Recommendation

- Use **DR**, not IPW, when `e` is estimated: DR max **2.67%** with **91.0%** coverage; IPW **11.19%** with **73.0%**.
- Under outcome-dependent labels with estimated `e`, only audit-only is honest: **2.58% / 82.5%**; IPW and DR fail.
- Report the propensity source and a sensitivity band; do not treat the oracle result as a production estimate.
