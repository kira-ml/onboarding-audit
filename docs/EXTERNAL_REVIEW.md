# External Review Log

**Status:** Open. No external reviewer is recorded as of 2026-11-26.
**Purpose:** Record the two external readers required by the V1 definition of
done, their objections, and the changes those objections force. This is the
binding-constraint artifact: the project does not need another estimator before
this log has entries.

---

## 1. Reviewer packet

The ready-to-send cover note, shortlist template, 30-minute agenda, and outreach
tracker are in [`REVIEWER_PACKET.md`](REVIEWER_PACKET.md). Send a short cover note
and these links, not the whole repository:

| Item | Why |
|---|---|
| [`../README.md`](../README.md) | The public claim, scope, and limitations |
| [`ONE_PAGER.md`](ONE_PAGER.md) | The 1-page brief |
| [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) | What was run, what passed, what did not |
| [`MODEL_CARD.md`](MODEL_CARD.md) | Intended use, assumptions, limits |
| [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md) | What a real-log pilot would require |
| [`REPORT_USAGE.md`](REPORT_USAGE.md) | How to read the memo, including §4.1 |
| [`CLAIMS.md`](CLAIMS.md) | Every public claim and its evidence tier |
| [`THREATS.md`](THREATS.md) | The strongest counter-case |
| [`CASE_STUDY.md`](CASE_STUDY.md) | The decision the tool changes |

**The ask:** 30 minutes to challenge the assumptions and tell us where you would
reject the package. Offer to run the demo or a read-only review on a synthetic
log; do not ask for PII or proprietary data before a DPA and sandbox exist.

## 2. The ten questions

Ask these in order. The reviewer's answers are the data.

1. What decision does this change in your workflow, if any?
2. Is the `P0` estimand the right one for that decision, or does the reject
   margin dominate?
3. Does the full-policy difference bound and break-even (§4.1 of the memo) change
   how you would read the recommendation?
4. Is the observation mechanism plausible for your log? Which part is wrong?
5. Is the cost matrix in the units your risk committee uses? What is missing?
6. Is the post-hoc verification audit legal and operationally feasible?
7. What would you need to run this on a historical log? Which fields are missing?
8. What would make you reject the package outright?
9. Would the memo survive a risk-committee or internal-audit review? What would
   you change?
10. What is the smallest pilot you would approve, and what would make you stop it?

## 3. Log

Add one row per reviewer. Do not paraphrase an objection into something weaker.

| Date | Reviewer | Role | Format | Objection | Severity | Response | Claim changed? |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Severity:** critical (blocks the release), high (changes a headline or a
recommendation), medium (changes a document or a workflow), low (editorial).

## 4. Gate

The public-release gate is met when:

- [ ] A fraud/KYC practitioner has reviewed the problem, schema, and audit design.
- [ ] A researcher or model-risk reviewer has reviewed the methods and claims.
- [ ] At least one reviewer has run the demo or the report command.
- [ ] Every critical and high objection is fixed, narrowed, or explicitly
  recorded as a residual risk in [`CLAIMS.md`](CLAIMS.md) and
  [`THREATS.md`](THREATS.md).
- [ ] The reviewer's objections and the author's responses are in this log.

If no reviewer can be reached, the fallback is a documented peer review plus the
red-team record in [`AUDIT_REPORT.md`](AUDIT_REPORT.md). The fallback is weaker
and must be labeled as such; it does not turn the tag into a public release.

## 5. What not to do

- Do not send PII, proprietary logs, or customer records.
- Do not ask a reviewer to sign off on a claim the repository does not support.
- Do not treat a proofread as an external validation.
- Do not change a headline number without updating [`CLAIMS.md`](CLAIMS.md) and
  the validation report first.
