# One-Pager — For a Fintech Research Reviewer

**Project:** Onboarding Audit — audit-ready evaluation of account-opening fraud
policies under selective and delayed labels.
**Author:** Ken Ira Lacson Talingting.
**Status:** v0.1 pilot; results below are generated from the pre-registered run.

---

## The problem

A bank or e-wallet decides whether to approve, review, or reject a new account.
The current onboarding policy determines which applications are reviewed and
therefore which fraud outcomes are ever observed. Approved accounts are labeled
late, if at all; rejected applicants have no outcome. The "expected impact" of a
new policy is estimated on the subset the incumbent policy produced.

## The question

> When the onboarding policy chooses its own labels, how biased is the naive
> policy-value estimate — and which estimator, bound, or audit design makes the
> estimate defensible?

## The approach

- **Primary estimand:** policy value on the logging non-rejected population
  (`P0`), the part logs can identify.
- **Reject margin:** full-population bounds, not a point estimate.
- **Estimators:** naive, IPW, doubly robust, audit-only, bounds.
- **Benchmark:** BAF account-opening applications with known ground truth.
- **Stress tests:** review capacity, label delay, audit size, outcome-dependent
  labels, false-reject cost.
- **Negative controls:** full observation, full audit, permutation, capacity,
  no leakage.

## The pilot result

- **Naive relative bias: +111.6% to +278.5%** across the four policies. It
  overstates cost and reverses the better-model/incumbent ranking: the naive
  estimate puts the incumbent ahead of the better model, while the true ranking
  reverses it.
- **Rank inversion:** mean **1.00** pairwise inversion for the naive estimate;
  P(select true best) **0%**.
- **Best corrected estimator: DR**, max |relative bias| **0.94%**, mean 95% CI
  coverage **96.0%**; IPW max **1.18%**, coverage **95.0%**.
- **Audit-only:** unbiased but high variance at 1% — max |relative bias|
  **2.98%**, coverage **84.5%**, mean ESS **1,271**. A 2% audit improves to
  **1.82% / 86.5% / 2,546**.
- **Audit value:** modest in the main scenario (DR RMSE **0.001159 → 0.001068**
  from 0% to 2%; ESS **6,610 → 9,126**), but **decisive when approved labels are
  outcome-dependent**: audit-only bias **-2.37% to -1.98%**, while action-only
  IPW is **+43.9% to +368.3%** and DR **+596.4% to +1301.5%**.
- **Reject-margin bounds:** widest interval **0.009942**; the incumbent's narrow
  interval covers the true full value in only **35%** of replications. The
  bounds are partial-identification intervals, not confidence intervals.

**What this means:** the naive evaluation is not a small approximation; it would
reject the better policy. Doubly robust estimation recovers the identified value
and the true ranking, but the reject margin still requires bounds or a
controlled approval design. The audit is a validation and outcome-dependent-label
tool, not a universal bias fix.

## What a team gets

- A **decision-log schema** that extends BSP 1213's 11 fields with the missing
  decision/observation/label fields.
- A **schema validator** that says which estimators the log can support.
- An **audit design**: random post-hoc verification of approved applications and
  shadow scoring; no random approvals/rejections.
- An **audit-ready memo** separating measured, assumed, and unverifiable claims.
- A **public benchmark** and reproducible pilot.

## Why it matters

BSP Circular 1213 requires continuous calibration, stress testing, and
independent review/audit of fraud systems — but its mandated log schema contains
no decision, score, or outcome. AFASA s.6 ties inadequate controls to
restitution. BSP Project Sapiens names sampling bias and labelling bias. The
project supplies the missing measurement layer.

## What it is not

- Not a fraud detector or a new classifier.
- Not a production system or a claim about a specific bank.
- Not a causal deployment effect.
- Not a point estimate for the unobserved reject margin.

## Limits

- The observation mechanism and review capacity are simulated.
- BAF is synthetic; no Philippine bank data.
- The cost matrix is a normalized assumption.
- The pilot uses oracle propensities; estimated propensities are the next study.
- The audit design requires legal/risk review.

## Reproduce

```bash
pip install -e ".[dev]"
pytest -q
onboarding-audit pilot --config configs/pilot.yaml --out reports
```
