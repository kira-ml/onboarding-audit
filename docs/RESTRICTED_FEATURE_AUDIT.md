# Restricted-Feature Audit — Negative Result

**Status:** Post-hoc ablation, 2026-11-28. **Not a headline result.**
**Purpose:** test whether removing BAF protected attributes preserves the
reliability conclusions.
**Result:** the point-estimate conclusions survive; **the A/B release rule does
not**. This is a failure of the profile, not a success story.

---

## 1. What was changed

BAF names **age, employment status, and income** as protected attributes. The
original scores used all three because `scripts/prepare_baf.py` did not exclude
them.

The restricted run:

- rebuilds the BAF Base frame from the public OpenML copy of the same rows;
- removes `customer_age`, `employment_status`, and `income` from the score
  features;
- uses a restricted outcome-model feature set without `customer_age`;
- keeps the same split, costs, observation simulation, and policies.

The processed frame matches the original on all 227,491 rows for label, amount,
month, age, employment status, and income. The raw-file hash differs because the
source file is a different public copy; the exact Kaggle version remains unpinned.

Artifacts:

- `reports/restricted_main100/` — 100-replication main scenario
- `reports/reliability_audit_restricted/` — 60-replication reliability audit
- `configs/pilot_restricted.yaml`
- `configs/reliability_audit_restricted.yaml`

## 2. Main scenario, 100 replications

| Metric | Original scores | Restricted scores |
|---|---|---|
| DR max absolute relative bias | 0.94% | **1.33%** |
| DR mean coverage | 96.0% | **92–95%** |
| DR P(select true best) | 72% | **60%** |
| DR mean inversions | 0.29 | **0.41** |
| Naive max absolute relative bias | 278% | **291%** |
| Naive P(select true best) | 0% | **0%** |

**Read:** the large naive-bias contrast survives; the DR ranking is weaker but
still far better than naive. Removing protected attributes does not destroy the
point-estimate result in the main scenario.

## 3. Reliability audit, 60 replications

| Metric | Result |
|---|---|
| Grades | **5 A, 35 C, 20 D** |
| A/B releases | **5 of 60** |
| Correct A/B releases | **0 of 5** |
| False certifications | **5 of 5** (95% upper bound 45%) |
| Directional decisions withheld | 6 of 11 |
| Identified directional accuracy | **1 of 8 (12%)** |
| All directional accuracy | **1 of 11 (9%)** |

All five false certifications are in the high-false-reject-cost scenario
(`frej_050`). The true candidate advantage there is about **0.53% of cost**.
The estimate put the candidate about **7% worse**; the bootstrap agreed with the
wrong sign (`P(candidate better)` 0.00–0.04), the 3×3 cost grid was 9/9 stable,
and the full-policy bound also said the incumbent was cheaper.

**Read:** every measured reliability dimension agreed with a biased estimate.
The profile had no diagnostic that could see the bias. A near-tie plus a small
outcome-model bias was enough to produce a confident wrong release.

## 4. Interpretation

This is not evidence that the code has a bug. It is evidence that the **grade is
not a certification** and that the current A/B rule is unsafe for small effects.

The failure mode is:

1. true effect is small relative to cost;
2. the outcome model is slightly biased;
3. the bootstrap, cost stress, and full-policy check all inherit that bias;
4. calibration does not detect it;
5. the profile releases a confident wrong decision.

This is exactly the distinction the project is about: **point accuracy is not
decision reliability**, and the profile can be confidently wrong.

## 5. Consequence

- **Do not run the BAF-suite audit** as a success test.
- **Do not claim** that the profile made zero false certifications in general.
  The original audit's zero is feature-set-specific and not replicated.
- **Do not add a post-hoc threshold** just to make the five failures disappear.
  A materiality or bias guard must be designed and pre-registered, then tested on
  a fresh audit.
- The current paper's reliability claim is under revision. The restricted result
  belongs in the limitations or a negative-results section.

## 6. Next design question

What guard would have blocked these five releases **before** seeing the result?

Candidates:

- a minimum relative effect size, fixed in advance;
- an independent audit-sample check on the candidate's review set;
- a bias bound from the held-out or temporal stability study;
- an outcome-model sensitivity analysis that includes the observed bias range;
- a requirement that the audit-only estimate agree with the DR estimate.

The next run must pre-register the guard and evaluate it on the same restricted
feature set, with the five failures included. Tuning until the audit shows zero
is not evidence.
