# V1 Vision — A Credibility-First Fintech Measurement Layer

**Status:** Planning, 2026-11-21.
**Owner:** Ken Ira Lacson Talingting.
**Horizon:** v1.0.0 by 2026-12-31.

---

## 1. The decision this project supports

A bank or e-wallet must decide whether to **approve, review, or reject** each new
account application. The current onboarding policy determines which applications
are reviewed and therefore which fraud outcomes are ever observed. Approved
accounts are labeled late, if at all; rejected applicants have no outcome.

The practical question is:

> If we change the onboarding policy, will it catch more fraud without rejecting
> more good customers — and can we defend the expected-impact number to a risk
> committee, an internal auditor, and the regulator?

A normal backtest on the labeled data answers a different question. It measures
the population the old policy chose, not the value of the new policy.

## 2. The audience

| Audience | What they need |
|---|---|
| **Fintech fraud/KYC analytics** | A defensible way to compare a challenger policy on a historical log |
| **Model risk / validation** | A model card, validation report, evidence tiers, and explicit limits |
| **Risk committee / internal audit** | A memo that separates measured, assumed, and unverifiable claims |
| **Regulatory/compliance** | A logging schema and audit design mapped to BSP 1170/1213, AFASA, and NPC |
| **Research reviewer** | A pre-registered, falsifiable, reproducible study with negative results |

## 3. The problem, from first principles

1. A decision is a choice among actions with costs.
2. A rejected applicant never becomes a customer, so the outcome is structurally
   missing.
3. A label is a measurement chosen by the current policy, so the labeled sample
   is selected.
4. A policy comparison is a counterfactual; you cannot observe both actions for
   the same applicant.
5. Identification requires positivity and a credible observation model.
6. The cost matrix is a value judgment, not a fact in the data.
7. The full-population value is not point-identified from logs alone; the honest
   output is a bound.
8. An audit can create random labels for the approved margin, not the reject
   margin.

This is the spine of the project. V1 must make every claim trace back to one of
these facts.

## 4. Where the project is now

The current v0.2.1 is a strong **Level 1 reproducible research artifact**:

- 47 tests, a schema, an audit design, a report/memo, 22 configured scenarios,
  and 11 sensitivity scenarios.
- A public repository at `https://github.com/kira-ml/onboarding-audit`.
- A documentation set covering methods, results, claims, threats, decisions,
  reproducibility, architecture, testing, and communication.

But the red-team review found six credibility gaps:

1. The headline bias may be driven by the fixed `0.90`/`0.05` observation-rate
   gap and the 2% review band, never swept.
2. The pre-registered F5 bounds control reportedly failed and was reinterpreted.
3. The report path defaults to action-level propensities and can print
   "Measured" on an unidentified estimate.
4. The score-generation pipeline is not in the repository.
5. The Level 3 pilot is infeasible without a partner.
6. The business case has no bank costs or volume.

These are not feature gaps. They are **credibility gaps**. V1 exists to close
them.

## 5. The V1 thesis

> **Credibility compounds faster than features.**

A risk team will not adopt another estimator. It will adopt a measurement layer
it can audit. A hostile reviewer will not dismiss a release that records its own
failed controls, states the conditions under which its claim holds, and refuses
to overclaim.

V1 is therefore a **credibility-first release**:

- The claim becomes conditional on a sweep of plausible observation rates.
- The bounds become a recorded partial-identification result, not a confidence
  interval.
- The report gets an identification gate: no "Measured" when the estimate is
  unidentified.
- The benchmark gets a reproducible pipeline and score provenance.
- The package gets a model card, validation report, pilot protocol, and
  business-case template.
- The external pilot is deferred to V1.1/V2.

## 6. The V1 claim

> On the BAF account-opening benchmark, the naive policy-value estimate is
> biased in **12/12** plausible observation-rate cells, ranging from **7.8% to
> 538.5%**, and can reverse the policy ranking. DR with known propensities stays
> within **1.89%** (coverage **84.5–96.0%**); at low approve-label rates its
> P(select true best) is **64%**, so the correction is accurate but the ranking
> is not guaranteed. Audit-only recovers the approved population under
> outcome-dependent labels. The reject margin is a partial-identification
> interval, not a point estimate or confidence interval. The tool refuses to
> report a point estimate when identification fails.

The claim is **conditional and evidence-tiered**. V1 does not claim a universal
bias magnitude, a production estimate, a causal deployment effect, or a
pilot-proven risk-team adoption.

## 7. The three value pillars

### 7.1 Scientific credibility

- A pre-registered observation-rate sweep, not a single hand-set scenario.
- A recorded F5 pass/fail, not a reinterpreted failure.
- A report gate that refuses to overclaim.
- A claim ledger that maps every public number to an artifact.

### 7.2 Practical usability

- `validate` and `report` on a real log.
- A memo a risk committee can read.
- A real-log adapter and one-command demo.
- A model card, validation report, pilot protocol, and business-case template.

### 7.3 Portfolio signal

- Research discipline: falsification, negative results, evidence tiers.
- Engineering discipline: tests, CI, reproducibility, packaging.
- Communication discipline: claim ledger, model card, reviewer guide, limits.
- A defensible interview story: "I found the headline was conditional, and I
  rebuilt the release around that finding."

## 8. Positioning

**Category:** research-grade measurement layer for account-opening fraud policy
evaluation.

**Not:** a fraud detector, a classifier, a vendor replacement, a production
system, or a causal deployment study.

**Closest work:** selective labels, reject inference, PU learning, delayed
feedback, off-policy evaluation, and the 2026 finance work on selective/delayed
labels. The contribution is the applied measurement layer and the identification
discipline, not a new estimator.

**Why a fintech team should care:** the tool answers a question they already
have — "is the challenger policy actually better?" — and it answers it with an
audit trail, a schema, and a memo they can defend.

## 9. The strategic bet and its payoff

| Bet | Downside | Upside |
|---|---|---|
| Build the credibility package before a pilot | Six weeks of work; no new features | A review-ready release, two external readers, a defensible story |
| Make the claim conditional | A smaller headline | A claim that survives a hostile reviewer |
| Record the F5 failure | A visible negative result | Credibility; no false confidence in the bounds |
| Add the report gate | Some users see "cannot estimate" | No "confident-looking memo that is not identified" |
| Defer the pilot | No Level 3 claim in 2026 | A clean V1.1/V2 path with a real partner |

The payoff shape is convex: bounded downside (the package is reusable), open
upside (reviewers, pilot, paper, adoption).

## 10. What V1 is not

- Not a new fraud detector or classifier.
- Not a production system or a vendor replacement.
- Not a causal deployment claim.
- Not a point estimate for the reject margin.
- Not a universal "112–278% bias" claim.
- Not a Level 3 pilot-proven tool.

## 11. Success narrative

At the end of V1, the one-paragraph story is:

> "I built a measurement layer for account-opening fraud policy evaluation. The
> first version had a strong simulation result, but a red-team review showed the
> headline was conditional on the observation model, the bounds control failed,
> and the report could overclaim. I rebuilt the release around those findings: a
> pre-registered observation-rate sweep, a recorded bounds failure, an
> identification gate, a reproducible benchmark pipeline, and a model card. The
> result is a tool that says what it can and cannot identify — and a claim that
> survives review."

## 12. Risks to the thesis

| Risk | Mitigation |
|---|---|
| The sweep shows the bias collapses at plausible observation rates | Report the conditional claim; narrow the headline; keep the tool's value in the correction and the gate |
| F5 cannot be fixed cheaply | Record the failure; drop the coverage claim; report bounds as partial identification |
| The report gate is too strict for small logs | Make it a warning with a clear "not identified" label, not a silent pass |
| The benchmark pipeline cannot reproduce the scores | Narrow the Level 1 claim; publish the data hash and the exact gap |
| No external reader by Dec 15 | Use the red-team + one strong peer; plan the external review for January |
| The six weeks are too short | Cut scope to the validation report, model card, pilot protocol, and report gate; defer CI/adapter |

## 13. Review dates

- **2026-12-05:** V1 package freeze.
- **2026-12-15:** reviewer status and V1 claim freeze.
- **2026-12-31:** v1.0.0 release.

## 14. Related documents

- V1 index: [`README.md`](README.md)
- Requirements: [`REQUIREMENTS.md`](REQUIREMENTS.md)
- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Decisions: [`DECISIONS.md`](DECISIONS.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Experiments: [`EXPERIMENTS.md`](EXPERIMENTS.md)
- Evaluation: [`EVALUATION.md`](EVALUATION.md)
- Progress: [`PROGRESS.md`](PROGRESS.md)
