# Pilot Protocol — Shadow Evaluation with a Partner Institution

**Status:** V1 protocol template, 2026-11-21.
**Scope:** A retrospective, read-only shadow evaluation of one candidate
account-opening policy on one historical decision log.
**Not in scope:** production deployment, live traffic, randomized decisions, or
any change to the incumbent policy.

---

## 1. Purpose

Answer one question with evidence:

> On the institution's own historical decisions, what would the candidate policy
> have cost on the applications the incumbent did not reject, and is that
> estimate identified well enough to justify a controlled pilot?

The pilot does **not** test whether the candidate model is better in general. It
tests whether the audit can produce a defensible estimate on this log, and what
that estimate says.

## 2. Preconditions

All must hold before the first row is read:

| # | Precondition | Owner |
|---|---|---|
| 1 | A signed data-sharing agreement and, where required, a data processing agreement | Institution legal / DPO |
| 2 | A pseudonymized extract; no raw PII | Institution data owner |
| 3 | A named business sponsor and a named independent validator | Institution |
| 4 | A frozen cost matrix, agreed before the evaluation | Institution risk |
| 5 | A frozen candidate score file with a recorded hash | Candidate owner |
| 6 | A read-only sandbox with no production write access | Institution IT |

If any precondition is missing, stop. Do not start with a partial extract and
"fill in later."

## 3. Design

| Item | Choice |
|---|---|
| Design | Retrospective, observational, shadow scoring |
| Unit | One account application |
| Population | Applications in the extract with a logged action |
| Primary estimand | Mean realized cost per application on `P0` (approved or reviewed by the incumbent) |
| Secondary estimand | Full-population partial-identification bounds |
| Treatment | The candidate policy's action at the institution's review capacity |
| Randomization | None |
| Production effect | None |

No application is approved, rejected, or reviewed differently because of the
pilot. The candidate score is applied offline to historical rows.

## 4. Data requirements

Before assembling the extract, run the readiness check in
[`DATA_READINESS.md`](DATA_READINESS.md). It lists the minimum fields, the BSP
1213 gap, and the stop rules. A log that cannot supply the action, label, and
observation fields is a data-readiness failure, not a modeling result.

### 4.1 Required

| Field | Requirement |
|---|---|
| `application_id` | Stable, non-PII key |
| `application_time`, `decision_time` | Timestamps, for delay and censoring checks |
| `action` | `approve`, `review`, or `reject` |
| `amount` | Credit-line exposure proxy |
| `label` | 0/1, present only when observed |
| `label_time` | When the outcome became known |
| `label_source` | `review`, `audit`, `post_approval_report`, or similar |
| `reviewed`, `audit_flag` | Flags consistent with `action` and `label_source` |

### 4.2 Strongly recommended

| Field | Why |
|---|---|
| `propensity` | Avoids estimating the observation mechanism |
| Outcome covariates | Needed if observation depends on applicant characteristics |
| Policy version / cutoff | Reproduces the incumbent decision |
| Review outcome | Separates "reviewed and cleared" from "reviewed and confirmed fraud" |

### 4.3 Minimum size

The report's gate requires at least **100 observed labels** and at least **30 per
non-rejected action**, with an effective sample size of at least **100**. A
smaller extract is allowed, but the memo will say **“Not identified”** and
withhold the point estimate. Do not treat that as a failure of the pilot; treat
it as the gate doing its job.

## 5. Procedure

1. **Freeze the inputs.** Hash the log extract, the candidate score file, the
   config, and the cost matrix. Record the hashes in the pilot record.
2. **Validate the schema.** `onboarding-audit validate --log <extract>`.
3. **Run the identification gate.** `onboarding-audit report ...` on the full
   extract. Record pass/fail and every reason.
4. **Run the primary estimate.** DR is the primary estimator; IPW-HT, IPW-Hajek,
   naive, and audit-only are reported beside it.
5. **Run the cost sensitivity.** At least three cost matrices: the agreed base,
   a lenient, and a strict variant. Report the sign and size of the change.
6. **Run the observation sensitivity.** If propensities are estimated, compare
   action-level and covariate models. Report both.
7. **Write the memo.** Use [`MEMO_TEMPLATE.md`](MEMO_TEMPLATE.md). The memo
   states the gate result, the estimate or refusal, the assumptions, and the
   decision guidance.
8. **Independent review.** The validator re-runs the commands from the recorded
   hashes and signs the memo.

## 6. Pre-registered success criteria

Declared before the run; not adjusted after seeing the result.

| # | Criterion | Threshold |
|---|---|---|
| S1 | The identification gate passes on the full extract | pass |
| S2 | DR and IPW-HT agree on the sign of the candidate-vs-incumbent difference | same sign |
| S3 | DR effective sample size | ≥ 500 |
| S4 | Max IPW weight | ≤ 50 |
| S5 | The candidate-vs-incumbent conclusion is stable across the three cost matrices | same sign |
| S6 | The covariate and action-level propensity models agree on the sign | same sign |
| S7 | The full-population bounds contain the `P0`-scaled estimate | yes |

If S1 fails, the pilot reports a refusal, not an estimate. If S2, S5, or S6
fails, the memo reports an inconclusive result and does not recommend a pilot.

## 7. Falsification and stop conditions

Stop and report a negative result if any of the following occurs:

- the gate fails and cannot be fixed by a legitimate data fix (not by dropping
  rows until it passes);
- the corrected estimators disagree on the direction of the effect and no
  pre-specified reason explains it;
- the conclusion flips across the pre-specified cost matrices;
- the propensity model cannot include a known driver of observation;
- the extract cannot be pseudonymized to the agreed standard;
- the validator cannot reproduce the result from the recorded hashes.

A negative result is a valid pilot outcome. It is more credible than a
point estimate that the gate should have blocked.

## 8. Deliverables

| Deliverable | Owner |
|---|---|
| Pilot record with input hashes and commands | Analyst |
| `report.md` and `report.json` | Analyst |
| Cost and observation sensitivity tables | Analyst |
| Signed memo | Reviewer |
| Decision: proceed to a controlled pilot, refine, or stop | Sponsor |

## 9. Roles

| Role | Responsibility |
|---|---|
| Sponsor | Owns the decision and the cost matrix |
| Data owner | Provides the pseudonymized extract and confirms the field meanings |
| Analyst | Runs the audit and writes the memo |
| Validator | Independently reproduces the result and challenges the assumptions |
| DPO / legal | Confirms the data-sharing and privacy basis |

One person may not be both analyst and validator.

## 10. What the pilot does not prove

- It does not prove the candidate policy is better in production.
- It does not prove the incumbent's log is free of unmeasured confounding.
- It does not validate the institution's cost matrix.
- It does not authorize a live change.

A positive pilot justifies a **controlled** next step with a pre-agreed
monitoring plan, not a rollout.

## 11. Related documents

- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
- Audit design: [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md)
- Memo template: [`MEMO_TEMPLATE.md`](MEMO_TEMPLATE.md)
- Privacy: [`PRIVACY.md`](PRIVACY.md)
- Model card: [`MODEL_CARD.md`](MODEL_CARD.md)
- Threats: [`THREATS.md`](THREATS.md)
