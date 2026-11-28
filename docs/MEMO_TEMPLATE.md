# Onboarding Policy Change Memo — Template

**Status:** Current-tree document (2026-11-28; v1.1.0 tag plus post-release negative result).

**Policy:** `[name / model version / threshold version]`
**Prepared by:** `[decision strategy / analytics / model risk]`
**Date:** `[YYYY-MM-DD]`
**Status:** `[draft / reviewed / approved / rejected]`

---

## 1. Decision

- **Policy under evaluation:** `[approve / review / reject rule, score, threshold, review capacity]`
- **Comparison:** `[incumbent policy]`
- **Decision requested:** `[approve the change / run an audit / reject the change]`
- **Decision owner:** `[name / committee]`

## 2. Estimate

- **Estimand:** policy value on the logging non-rejected population (`P0`).
- **Estimate or bounds:** `[value]`
- **Uncertainty:** `[95% CI or bounds interval]`
- **Estimator:** `[naive / IPW / DR / audit-only / bounds]`
- **Why this estimator:** `[assumptions / diagnostics]`
- **Reject margin:** `[bounds width / not identified / excluded]`

## 3. Diagnostics

| Diagnostic | Value | Interpretation |
|---|---:|---|
| Propensity source | `[provided / estimated / estimated_covariate]` | `[known / action-level / covariate]` |
| Propensity range | `[min, max]` | `[overlap OK / weak]` |
| Effective sample size | `[ESS]` | `[precision]` |
| Max weight / p99 weight | `[max / p99]` | `[heavy-tail risk]` |
| Share with propensity < 0.01 | `[%]` | `[positivity risk]` |
| Label maturity | `[% resolved]` | `[censoring risk]` |
| Label-source mix | `[review / report / audit / ...]` | `[selection risk]` |
| Observation rate by amount quintile | `[approve / review]` | `[within-action gradient]` |
| Audit share | `[%]` | `[validation strength]` |

If the observation rate varies strongly across amount quintiles within an
action, action-level `e` is misspecified. Rerun with
`--propensity-model covariate` and report the feature list. Heavy weights
(max or p99 far above the median) mean the interval can undercover even when the
point estimate is close.

## 4. What would change the estimate

- **Overlap:** `[what happens if the candidate policy explores unseen regions]`
- **Delay/censoring:** `[what happens if the cutoff moves]`
- **Unmeasured confounding:** `[what the reviewers may use that is not logged]`
- **Cost assumptions:** `[which cost parameter drives the result]`
- **Inclusion:** `[false-reject rate / segments affected]`
- **Data quality:** `[missing fields / label noise]`

## 5. Audit recommendation

- **Design:** random post-hoc verification of approved applications; shadow
  scoring; **not** random approvals/rejections.
- **Sample size:** `[n]` for `[target precision/power]`.
- **Cost:** `[review cost]`.
- **What it buys:** `[bias/variance reduction / validation]`.
- **What it does not buy:** the reject margin; small fraud-rate differences.

## 6. Bounds and uncertainty language

- The reject-margin interval is a **partial-identification interval conditional
  on the `P0` estimate**, not a confidence interval.
- Do not write "95% confident" about the bounds.
- Report the width and the share of rejected applications.
- If the reject margin is material, do not report a full-population point
  estimate.

## 7. Claim ledger

| Claim | Status | Evidence |
|---|---|---|
| `[estimate]` | Measured / Pre-registered / Post-hoc / Non-finding | `[artifact]` |
| `[assumption]` | Assumed | `[source]` |
| `[unverifiable]` | Unverifiable | `[why]` |

## 8. Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Decision strategy | | | |
| Model risk / validation | | | |
| Compliance / legal | | | |
| Internal audit | | | |
