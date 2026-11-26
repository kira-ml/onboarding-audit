# Glossary

**Status:** Canonical glossary for v1.0.0 (2026-11-22; updated 2026-11-26).

| Term | Meaning in this project |
|---|---|
| **Account opening** | The decision to approve, review, or reject a new bank/e-wallet account application. The unit is the application, not a transaction. |
| **Action** | `approve`, `review`, or `reject`. A review is a manual KYC/document/identity check. |
| **BAF** | Bank Account Fraud dataset (Jesus et al., NeurIPS 2022): 1M synthetic, privacy-preserving online account-opening applications. |
| **Censoring** | A label that has not arrived by the evaluation cutoff. It is unresolved, not negative. |
| **Action-dependent observation** | The probability that a label is observed depends on the logging action (`approve`, `review`, `reject`), not on the application's features. |
| **Audit-only** | The mean cost on the random post-hoc verification sample, reweighted by the resolution probability. Unbiased for the approved population; high variance. |
| **Bounds** | The partial-identification interval for the full-population value, conditional on the `P0` estimate. Not a confidence interval. |
| **Covariate-dependent observation** | The observation probability depends on pre-decision features (for example, amount), not only on the action. Action-level `e` is then misspecified. |
| **Covariate propensity model** | A per-action logistic model `P(observed \| action, X)`, cross-fitted, used when observation depends on application features. |
| **Coverage** | The share of replications whose 95% interval contains the true target. A diagnostic, not a guarantee. |
| **DR** | Doubly robust estimator: an outcome model plus an IPW residual correction. |
| **eKYC** | Electronic know-your-customer; digital identity proofing under BSP Circular 1170. |
| **ESS** | Effective sample size, `(sum w)^2 / sum w^2`; a measure of how much the weights concentrate. |
| **FMS** | Fraud Management System under BSP Circular 1213. |
| **Hájek** | Self-normalized IPW: `sum(w c) / sum(w)`. Usually more stable than HT. |
| **HT** | Horvitz–Thompson IPW: `sum(w c) / n`. Unbiased under correct propensities, high variance under heavy weights. |
| **IPW** | Inverse probability weighting: reweight observed labels by `1 / P(observed \| action, x)`. |
| **Label source** | The door that produced a label: review, post-approval report, chargeback, mule investigation, or audit. |
| **Monte Carlo SE** | The standard error of a simulation summary across replications; it says how precisely the simulation estimates the bias. |
| **Naive** | The mean cost on the labeled subset. It ignores selection and delay. |
| **`P0`** | The logging non-rejected population (applications the incumbent policy approved or reviewed). The primary estimand is defined on `P0`. |
| **Partial identification** | An interval for a parameter that is not point-identified from the data and assumptions. |
| **Positivity** | Every row in `P0` must have a positive probability of being observed. The audit/review channels provide it. |
| **Propensity** | The probability that a row's label is observed, given its action and features. |
| **Reject margin** | The value contributed by applications the policy rejects. It is not point-identified from logs because rejected applicants have no outcome. |
| **Shadow scoring** | Computing a challenger score without changing the decision, for overlap/coverage diagnostics. |
| **Post-hoc verification** | A random audit of approved applications after approval; it labels a sample without changing the decision. |
| **Selective labels** | The observed labels are a non-random sample chosen by the current policy. |
| **Target policy** | The candidate onboarding policy being evaluated. |
| **Uplift / L2D** | Learning to defer: combining algorithmic and human review under capacity. FiFAR is the public benchmark. |
| **Weight tail** | The upper quantiles of the IPW weights. A long tail means a few rows dominate the estimate and the interval may undercover. |
