# Reviewer Packet

**Status:** Ready to send. The shortlist and contact details are user-owned; no
names are invented here.
**Purpose:** Get two external readers — one fraud/KYC practitioner and one
researcher or model-risk reviewer — to challenge the V1 package before a public
release.

---

## 1. Who to ask

The strongest reviewers are not the people most likely to praise the work. They
are the people who can say “I would reject this because …”.

| # | Profile | Why this person | Where to look |
|---|---|---|---|
| 1 | Head of Model Risk / Model Validation, universal bank | Owns independent validation and the risk-committee memo | LinkedIn, BSP supervised institutions, FRM/PRM networks |
| 2 | Model validation lead, digital bank or e-wallet | Deals with challenger models and historical logs | Fintech LinkedIn, local risk meetups |
| 3 | Fraud / KYC analytics lead, e-wallet | Knows the review-capacity and label-delay reality | Fintech fraud communities, AFASA working groups |
| 4 | Internal audit / data science, bank | Tests whether the memo is audit-ready | IIA Philippines, internal audit networks |
| 5 | Former BSP or AMLC official (informal) | Tests the regulatory mapping without a formal opinion | Professional network; clearly label as informal |
| 6 | Academic in selective labels / off-policy evaluation | Tests the identification and novelty claims | ICAIF, NeurIPS, KDD authors; Google Scholar |
| 7 | ICAIF 2026 author on selective/delayed labels | Closest related work; can compare contributions | ICAIF proceedings, arXiv |
| 8 | Credit-scoring / reject-inference researcher | The closest methodological literature | EJOR, JBF, credit scoring conferences |
| 9 | Fintech risk consultant | Tests the business case and adoption path | Consulting networks, fintech associations |
| 10 | Privacy / DPO reviewer | Tests the data-handling and audit design | NPC-registered DPOs, privacy practitioners |

Do not send to all ten at once. Send in two waves of five, personalize the first
line, and stop after two substantive calls.

## 2. Cover note (copy, then personalize)

> Subject: 30-minute critique of an audit-ready onboarding-policy evaluation?
>
> Hi [Name],
>
> I built an open-source measurement layer for account-opening fraud policy
> evaluation. It estimates what a challenger policy would have cost on the
> population the incumbent did not reject, bounds the reject margin, and writes a
> memo that separates measured, assumed, and unverifiable claims.
>
> I am looking for a **critique**, not a endorsement. The project's own review
> found that the naive ranking is cost-dependent, that the audit only targets the
> logging-approved population, and that the release gate is still open. I would
> value 30 minutes on where you would reject the package.
>
> Packet: [link to README] · [one-pager] · [validation report] · [memo example]
>
> No PII or proprietary data is involved. If it is useful, I can run the demo on
> a synthetic log during the call.
>
> Would any of [two slots] work?
>
> Thanks,
> Ken Ira Lacson Talingting

## 3. 30-minute agenda

| Minutes | Item | Output |
|---:|---|---|
| 0–5 | The decision and the `P0`/reject-margin split | Shared context |
| 5–15 | Walk through the memo: gate, estimate, full-policy check, §4.1 break-even | Where the reader stops |
| 15–25 | The ten questions (below) | Objections, ranked |
| 25–30 | What would make you run it / reject it | Next step or stop |

## 4. The ten questions

1. What decision does this change in your workflow, if any?
2. Is the `P0` estimand the right one for that decision, or does the reject
   margin dominate?
3. Does the full-policy difference bound and break-even change how you read the
   recommendation?
4. Is the observation mechanism plausible for your log? Which part is wrong?
5. Is the cost matrix in the units your risk committee uses? What is missing?
6. Is the post-hoc verification audit legal and operationally feasible?
7. What would you need to run this on a historical log? Which fields are missing?
8. What would make you reject the package outright?
9. Would the memo survive a risk-committee or internal-audit review? What would
   you change?
10. What is the smallest pilot you would approve, and what would make you stop it?

## 5. What to send

Do not send the whole repository. Send:

- [`../README.md`](../README.md) — the public claim and scope.
- [`ONE_PAGER.md`](ONE_PAGER.md) — the one-page brief.
- [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) — what was run and what failed.
- [`MODEL_CARD.md`](MODEL_CARD.md) — intended use and limits.
- [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md) — what a real-log pilot requires.
- [`REPORT_USAGE.md`](REPORT_USAGE.md) — how to read the memo, including §3.1 and
  §4.1.
- [`CLAIMS.md`](CLAIMS.md) — the claim ledger.
- [`THREATS.md`](THREATS.md) — the strongest counter-case.

## 6. Outreach tracker

| # | Name | Role / institution | Wave | Sent | Reply | Call | Objection (one line) | Severity | Logged in |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | | | 1 | | | | | | |
| 2 | | | 1 | | | | | | |
| 3 | | | 1 | | | | | | |
| 4 | | | 1 | | | | | | |
| 5 | | | 1 | | | | | | |
| 6 | | | 2 | | | | | | |
| 7 | | | 2 | | | | | | |
| 8 | | | 2 | | | | | | |
| 9 | | | 2 | | | | | | |
| 10 | | | 2 | | | | | | |

Record every substantive objection in [`EXTERNAL_REVIEW.md`](EXTERNAL_REVIEW.md),
not here. This table is only the outreach state.

## 7. Stop rules

- Two substantive calls: stop outreach, synthesize objections, fix or disclose.
- No reply after two follow-ups: move to the next name; do not spam.
- A reviewer asks for PII or proprietary data: decline until a DPA and sandbox
  exist.
- A reviewer finds a critical claim error: stop the release, fix the claim
  ledger first, then resume.
- A reviewer asks for a paid engagement: keep the research call separate from any
  commercial discussion.

## 8. Related documents

- External review log: [`EXTERNAL_REVIEW.md`](EXTERNAL_REVIEW.md)
- Release status: [`RELEASE_STATUS.md`](RELEASE_STATUS.md)
- Strategic review: [`STRATEGIC_REVIEW_v1.md`](STRATEGIC_REVIEW_v1.md)
