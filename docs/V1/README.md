# V1 — Credibility-First Release

**Status:** Planning, 2026-11-21.
**Target:** v1.0.0, 2026-12-31.
**Purpose:** Define the first release of `onboarding-audit` that a fintech risk
team can review without the author in the room, and that a hostile reviewer
cannot dismiss with an undocumented overclaim.

---

## 1. The V1 thesis

The current project is a strong research artifact, but the red-team review found
six issues that block a credible V1:

1. The headline bias may be driven by the fixed `0.90`/`0.05` observation-rate
   gap and the 2% review band, never swept.
2. The pre-registered F5 bounds control reportedly failed, and the failure was
   reinterpreted rather than recorded.
3. The `report` path defaults to action-level propensities and can print
   "Measured" on an unidentified estimate.
4. The score-generation pipeline is not in the repository, so the "better model"
   premise is not reproducible.
5. The Level 3 pilot is infeasible without a partner; the plan has no path to
   one.
6. The business case is a template with no bank costs or volume.

**V1 is the credibility reset.** It does not add estimators or scenarios. It
makes the claim conditional, the bounds honest, the report safe, the benchmark
reproducible, and the package review-ready.

**V1 claim:**

> On the BAF account-opening benchmark, the naive policy-value estimate is
> biased in **12/12** plausible observation-rate cells, ranging from **7.8% to
> 538.5%**, and can reverse the policy ranking. DR with known propensities stays
> within **1.89%** (coverage **84.5–96.0%**); at low approve-label rates its
> P(select true best) is **64%**, so the correction is accurate but the ranking
> is not guaranteed. Audit-only recovers the approved population under
> outcome-dependent labels. The reject margin is a partial-identification
> interval, not a point estimate or confidence interval. The tool refuses to
> report a point estimate when identification fails.

**V1 does not claim:** a universal bias magnitude, a production estimate, a
causal deployment effect, a point-identified full-population value, or a
pilot-proven risk-team adoption.

---

## 2. What V1 is

| Dimension | V1 target |
|---|---|
| **Release type** | Credibility-first research tool, not a feature release |
| **Maturity** | Level 2 review-ready: a risk team can review it without the author |
| **Primary experiment** | Observation-rate robustness sweep |
| **Primary product feature** | Identification gate: no "Measured" when the estimate is unidentified |
| **Primary engineering fix** | Reproducible benchmark pipeline and score provenance |
| **Primary evidence** | Sweep + bounds F5 record + report-gate tests + reproducibility |
| **Primary non-goal** | A real bank pilot or production integration |
| **Review** | Two external readers; red-team findings triaged and documented |

## 3. What V1 is not

- Not a new fraud detector or classifier.
- Not a production system or a vendor replacement.
- Not a causal deployment claim.
- Not a point estimate for the reject margin.
- Not a universal claim that "naive evaluation is always 112–278% biased."
- Not a Level 3 pilot-proven tool; that is V1.1/V2.

## 4. The V1 value proposition

### 4.1 Technical value

- A conditional, parameter-robust claim instead of a single-scenario headline.
- A report that refuses to overclaim when positivity, overlap, ESS, or sample
  size fail.
- A reproducible benchmark pipeline with score provenance and hashes.
- A bounds treatment that records F5 pass/fail and does not sell a partial
  identification interval as a confidence interval.

### 4.2 Practical value

- A risk team can run `validate` and `report` on a historical log and get a memo
  that says what is measured, assumed, and unverifiable.
- A real-log adapter and a one-command demo reduce the integration cost.
- A model card, validation report, pilot protocol, and business-case template
  give the risk team the artifacts it expects.

### 4.3 Portfolio value

- Demonstrates research discipline: pre-registration, falsification, negative
  results, evidence tiers.
- Demonstrates engineering discipline: tests, CI, reproducibility, packaging.
- Demonstrates communication discipline: claim ledger, model card, reviewer
  guide, limitations.
- Produces a defensible interview story: "I found the headline was conditional,
  and I rebuilt the release around that finding."

## 5. The V1 strategic bet

The bet is that **credibility compounds faster than features**. A risk team will
not adopt another estimator; it will adopt a measurement layer it can audit.
A hostile reviewer will not dismiss a release that records its own failed
controls and refuses to overclaim.

The V1 release is therefore deliberately smaller than the current feature set:
no new methods, no dashboard, no pilot. The scope is the evidence, the gates, and
the package.

## 6. Reading order

1. [`VISION.md`](VISION.md) — strategy, positioning, and the V1 claim.
2. [`REQUIREMENTS.md`](REQUIREMENTS.md) — functional and non-functional
   requirements, acceptance criteria, risks.
3. [`ARCHITECTURE.md`](ARCHITECTURE.md) — target architecture, interfaces,
   invariants, trade-offs.
4. [`DECISIONS.md`](DECISIONS.md) — the six V1 technical decisions.
5. [`ROADMAP.md`](ROADMAP.md) — phases, dates, deliverables, kill criteria.
6. [`EXPERIMENTS.md`](EXPERIMENTS.md) — the observation sweep, bounds F5, report
   gates, reproducibility.
7. [`EVALUATION.md`](EVALUATION.md) — evidence tiers, claim matrix, release
   gates.
8. [`PROGRESS.md`](PROGRESS.md) — live status and next actions.

## 7. Definition of done

V1 is done when:

- [x] The observation-rate sweep is run and the claim is updated to its measured
      conditions.
- [x] F5 is recorded as pass/fail; the narrow interval has no coverage claim.
- [x] The report gate refuses or flags every adversarial unidentified log.
- [x] The benchmark pipeline reproduces the scores byte-for-byte (SHA-256 match).
- [x] `pytest` passes with 92 tests.
- [x] CI is green on GitHub (run 44918141562).
- [x] The model card, validation report, pilot protocol, and business case are
      complete.
- [ ] Two external readers have reviewed the package (user-owned).
- [ ] v1.0.0 is tagged and the README/claim ledger are consistent.
- [x] No unresolved critical red-team finding (the independent findings are
      fixed or disclosed in `../AUDIT_REPORT.md`).

## 8. Canonical links

- Current methods: [`../METHODS.md`](../METHODS.md)
- Current results: [`../RESULTS.md`](../RESULTS.md)
- Current claims: [`../CLAIMS.md`](../CLAIMS.md)
- Current threats: [`../THREATS.md`](../THREATS.md)
- Red-team review: [`../RED_TEAM_CREDIBILITY_PLAN.md`](../RED_TEAM_CREDIBILITY_PLAN.md)
- Decision memo: [`../DECISION_MEMO_2026-11.md`](../DECISION_MEMO_2026-11.md)
- Documentation index: [`../README.md`](../README.md)
