# Glossary

| Term | Meaning in this project |
|---|---|
| **Account opening** | The decision to approve, review, or reject a new bank/e-wallet account application. The unit is the application, not a transaction. |
| **Action** | `approve`, `review`, or `reject`. A review is a manual KYC/document/identity check. |
| **BAF** | Bank Account Fraud dataset (Jesus et al., NeurIPS 2022): 1M synthetic, privacy-preserving online account-opening applications. |
| **Censoring** | A label that has not arrived by the evaluation cutoff. It is unresolved, not negative. |
| **DR** | Doubly robust estimator: an outcome model plus an IPW residual correction. |
| **eKYC** | Electronic know-your-customer; digital identity proofing under BSP Circular 1170. |
| **ESS** | Effective sample size, `(sum w)^2 / sum w^2`; a measure of how much the weights concentrate. |
| **FMS** | Fraud Management System under BSP Circular 1213. |
| **IPW** | Inverse probability weighting: reweight observed labels by `1 / P(observed | action, x)`. |
| **Label source** | The door that produced a label: review, post-approval report, chargeback, mule investigation, or audit. |
| **Naive** | The mean cost on the labeled subset. It ignores selection and delay. |
| **`P0`** | The logging non-rejected population (applications the incumbent policy approved or reviewed). The primary estimand is defined on `P0`. |
| **Positivity** | Every row in `P0` must have a positive probability of being observed. The audit/review channels provide it. |
| **Propensity** | The probability that a row's label is observed, given its action and features. |
| **Reject margin** | The value contributed by applications the policy rejects. It is not point-identified from logs because rejected applicants have no outcome. |
| **Shadow scoring** | Computing a challenger score without changing the decision, for overlap/coverage diagnostics. |
| **Post-hoc verification** | A random audit of approved applications after approval; it labels a sample without changing the decision. |
| **Selective labels** | The observed labels are a non-random sample chosen by the current policy. |
| **Target policy** | The candidate onboarding policy being evaluated. |
| **Uplift / L2D** | Learning to defer: combining algorithmic and human review under capacity. FiFAR is the public benchmark. |
