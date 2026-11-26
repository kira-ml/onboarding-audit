# Decision Memo — What To Do With `onboarding-audit` Now

**Decision owner:** Ken Ira Lacson Talingting.
**Date:** 2026-11-27.
**Horizon:** 2026-11-27 to 2027-02-15 (12 weeks), with Summer 2027 internship
applications in the same window.
**Status:** **Proposed; owner decision.** This memo recommends; it does not
assume acceptance.

**Models used:** Inversion & Falsification (pre-mortem, kill criteria), Fat
Tails / Ruin / Non-Ergodicity (absorbing barriers, path survival, convexity),
with Constraints / Opportunity Cost as the framing check.

---

## 1. The real decision

Not “what feature next.” The real decision is:

> **How much of my scarce time and reputational capital should go to this
> project now — finish it as a research artifact, probe for external validation,
> push a commercial pilot, submit the paper, freeze it, or pivot?**

The project has just survived a credibility audit that found a false
research-gap claim and missing closest-work citations. Those are fixed in
`v1.0.2`, but the episode changes the risk calculus: **the project has already
had one public near-miss, and a second overclaim would be a repeated-game
drawdown, not a fresh start.**

### Binding constraint

**Access to external evidence and a risk-team reviewer — not code.** The
project has enough methods, tests, docs, and simulation. It does not have a real
log, two external readers, a model ablation, or a legal/ops review. Adding more
features does not relax that constraint.

### Smallest acceptable outcome

A **narrow, honest research/portfolio artifact** that:
- states the `P0`-conditional claim and the full-policy limitation;
- has the 2026 citations and no false research-gap claim;
- is internally consistent and reproducible;
- has a concrete path to one external reader or one real-log conversation.

A completed pilot is upside, not the minimum.

---

## 2. Options (including doing nothing)

| Option | What it means | Time | Reversible? |
|---|---|---|---|
| **A. Finish as research artifact** | Fix open audit items, trim paper, run holdout/ablation, no commercial push | 40–60 h | Yes |
| **B. A + small outreach probe (barbell)** | A plus 2–5 practitioner asks, 2 reader calls, one real-log conversation | 50–70 h | Yes |
| **C. Commercial/model-risk pilot push** | Find a bank partner, DPA/sandbox, pilot, service packaging | 120–200 h | Hard to reverse; legal/reputational tail |
| **D. Submit paper now** | Send the 7-page draft to a venue before external feedback | 10–20 h | Recoverable but reputational drawdown |
| **E. Freeze/stop** | Use the current artifact in applications; no new project work | 5 h | Yes |
| **F. Pivot to a new project** | Start a transaction-fraud or other project | 60–100 h | Yes, but abandons compounding |

Doing nothing is a real option. The current artifact is already stronger than
most student projects. The question is whether the marginal 50–70 hours buys
enough information and optionality to justify the opportunity cost.

---

## 3. States and subjective probabilities

The states describe **external engagement** over the next 12 weeks. They are
subjective, based on cold outreach, not measured frequencies. If you have a warm
partner, shift mass to S3 and re-run.

| State | Meaning | Base probability |
|---|---|---:|
| **S1. Cold** | No reader or partner engages | 0.45 |
| **S2. Reader / real-log lead** | 1–2 readers engage, or a scoped real-log conversation | 0.35 |
| **S3. Pilot / partner** | A bank partner with a log and a DPA path | 0.20 |

The probabilities are deliberately conservative. The audit found no warm
partner and no external reader; cold outreach to busy practitioners is low-yield.

---

## 4. Payoff matrix (subjective strategic value, 0–100)

The scores are **subjective composites** of credibility, external evidence,
internship story, learning, and optionality. They are not expected returns. The
decision does not depend on the precision of these numbers; it depends on the
shape of the payoff and the absorbing barriers.

| Option | S1 Cold | S2 Reader | S3 Pilot |
|---|---:|---:|---:|
| A. Research artifact | 72 | 78 | 82 |
| **B. A + outreach probe** | **74** | **85** | **90** |
| C. Commercial pilot push | 45 | 60 | 92 |
| D. Submit paper now | 52 | 62 | 68 |
| E. Freeze/stop | 58 | 58 | 58 |
| F. Pivot | 48 | 52 | 55 |

### Subjective expected values

Using the base probabilities:

| Option | EV | Time | Reading |
|---|---:|---:|---|
| A | 76.4 | 50 h | Safe, but leaves the binding constraint unaddressed |
| **B** | **81.6** | **60 h** | Highest expected value with bounded downside |
| C | 59.7 | 160 h | A concentrated bet on a low-probability partner |
| D | 59.5 | 15 h | Cheap, but high rejection and reputational drawdown |
| E | 58.0 | 5 h | Rational fallback if constraints bind |
| F | 51.1 | 80 h | Abandons compounding; not justified |

**B dominates on expected value.** But expected value is not the decision; the
tail and path matter more.

---

## 5. Inversion pre-mortem — how each option fails

Assume it is May 2027 and the choice failed. What happened?

### A fails
- No external reader; the artifact stays at Level 2.
- The paper is still 7 pages/applied/incremental; no venue.
- The portfolio story is “a student project with good docs,” not “validated by a
  risk team.”
- **Cost:** 50 hours; no absorbing barrier.

### B fails
- The 5 asks produce no calls; the real-log conversation stalls at “we do not
  log that.”
- The project remains a strong research artifact; the downside is the 10–15
  extra hours of outreach.
- **Cost:** bounded; no absorbing barrier.

### C fails
- No partner; 4–6 months lost; the package goes stale; applications/GPA slip.
- A partner asks for PII/proprietary data; a DPA/sandbox is not ready; the
  project is exposed to a legal/privacy tail.
- The project is still simulation-bound; the “commercial” claim is not
  validated.
- **Cost:** high time, reputational and legal tail; **absorbing** in the worst
  case.

### D fails
- Desk reject or harsh review: “7 pages, applied, no real data, closest work
  now cited but the contribution is incremental.”
- A public rejection is a reputational drawdown; it is recoverable, but it
  compounds with the earlier false-claim near-miss.
- **Cost:** 15 hours + reputational drawdown.

### E fails
- The project stagnates; the internship story is static; no new information.
- **Cost:** low; no absorbing barrier, but opportunity cost/regret.

### F fails
- The new project resets the compounding; the old artifact is abandoned; the
  application story is “started over.”
- **Cost:** 80 hours; no absorbing barrier, but high opportunity cost.

---

## 6. Fat tails, ruin, and non-ergodicity

### Absorbing barriers

| Barrier | Why it is absorbing | Which options risk it |
|---|---|---|
| **Health / burnout** | Cannot recover the semester or internship window | C (high hours), D (deadline stress), B if uncapped |
| **GPA / academic failure** | Closes the internship path | C, D, B if uncapped |
| **Legal / privacy breach** | Reputational and legal damage; cannot be undone | C (partner data/DPA), any PII use |
| **Public overclaim** | Recoverable, but a repeated drawdown; the v1.0.1 false claim was a near-miss | C, D; A/B if claims narrow |
| **Losing the application window** | Time-bound | C, D, F |

### Ruin test

Can you survive the worst case?

- **A/B:** Yes. Bounded time, no PII, no production claim, reusable artifacts.
- **C:** Not clearly. The worst case includes a legal/privacy incident, a
  six-month distraction, or a public overclaim. The expected gain does not
  justify an absorbing barrier.
- **D:** Yes financially, but the reputational drawdown is real and repeated.
- **E/F:** Yes, with opportunity cost/regret.

### Non-ergodicity

The ensemble average across hypothetical projects is not the path you will
actually live. A single burnout, GPA slip, or privacy breach zeros the path’s
future value. **Optimize for the survival and growth of the path, not the
average across parallel worlds.**

The project’s upside is an **option** on a real-log pilot, a reader, or a paper.
A cheap probe (B) buys that option without risking the path. A full commercial
push (C) is a concentrated bet on a low-probability partner; it has higher
variance and an absorbing tail.

### Fat tails of opportunity

The distribution of external outcomes is fat-tailed: one reader or one partner
can change the trajectory far more than ten more simulations. The project’s
simulation results are thin-tailed relative to the career outcome; the real tail
is **access and validation**. B is the cheapest way to buy a claim on that tail.

### Kelly-style sizing

If this were a bet, the conservative size is small: **10–12 hours/week, 50–70
hours total, with a hard stop**. Do not lever up to a full commercial push on a
0.20 partner probability and an unvalidated audit design. The project is a
portfolio option, not a concentrated venture bet.

---

## 7. Falsification tests — what would change the decision

| Claim | Test | If false |
|---|---|---|
| A real log is accessible | Ask 2–5 practitioners; one scoped conversation | C is not viable; stay at A/B |
| The paper is competitive | One researcher reads the 7-page draft | D is not viable; trim/reposition or don't submit |
| The vendor gap is real | Ask 2 practitioners what they use | C's value drops; narrow to model-risk validation |
| The audit design is legal/ops feasible | One risk/legal reviewer | C is not viable; keep the audit as a recommendation |
| The action-weighted result survives a holdout baseline | Run a holdout baseline | If it collapses, narrow the headline and don't submit |
| The marginal project hour beats applications/GPA | Weekly time review | If not, choose E or reduce to A |

The cheapest tests are the outreach asks and the holdout baseline. Run them
before committing to C or D.

---

## 8. Decision

**Choose B: finish-first research artifact plus a small outreach probe.**

### Why B is the most defensible

- **Bounded downside:** 50–70 hours, no PII, no production claim, reusable
  artifacts.
- **Open upside:** a reader, a real-log lead, or a paper review can change the
  trajectory; B buys that option cheaply.
- **Protects the path:** it does not risk the absorbing barriers (health, GPA,
  legal/privacy, application window).
- **Addresses the binding constraint:** the extra 10–15 hours are the only part
  of the plan that buys external information.
- **Preserves credibility:** narrow claims, no commercial overclaim, no
  premature submission.

### What B is not

- It is **not** a commercial pilot push. C is only justified if a warm partner
  with a log and a DPA path appears.
- It is **not** a paper submission. D is only justified after a reader says the
  paper is competitive and it is trimmed to the venue limit.
- It is **not** more features. The method set is frozen; no new estimators or
  scenarios.

### Allocation (12 weeks, 10–12 h/week)

| Block | Hours | Output |
|---|---:|---|
| Finish the paper reposition/trim (7 → 6 pages if needed) | 15–20 | Venue-ready draft or technical report |
| Run holdout baseline + model ablation | 10–15 | Falsification result; claim update |
| Close open audit items (metadata, intervals, vendor matrix or downgrade) | 8–12 | Updated `RED_FLAG_AUDIT.md` |
| Reviewer packet + 5 asks + 2 calls | 10–15 | `EXTERNAL_REVIEW.md` entries |
| One real-log conversation (no PII/DPA) | 5–8 | Go/no-go on a pilot |
| Buffer / applications / rest | 10–15 | Protect GPA/health |

### Stop rules

- **No reader/real-log lead by 2027-01-15:** stop outreach; freeze as a
  portfolio artifact. Do not chase.
- **Paper not trimmed/repositioned by 2026-12-31:** do not submit.
- **Health/GPA/applications slip:** stop; the project can wait.
- **A partner asks for PII/proprietary data without a DPA/sandbox:** decline.
- **A reviewer finds a critical claim error:** stop, fix the claim ledger first.
- **The holdout baseline collapses the effect:** narrow the claim; do not submit
  the current headline.

### Conditions for upgrading to C (commercial pilot)

Only if **all** hold:
1. a warm partner with a named sponsor;
2. a historical log with the required fields (or a funded reconstruction);
3. a DPA/sandbox and legal/ops review path;
4. a cost matrix agreed before the run;
5. the audit design is feasible;
6. the project’s time cap is respected.

Without all six, C is a high-variance distraction.

### Conditions for upgrading to D (paper submission)

Only if:
1. the paper is trimmed to the venue limit;
2. one researcher says the contribution is competitive;
3. the 2026 citations/positioning are in the draft;
4. the holdout/ablation result does not contradict the headline.

Otherwise, a technical report or workshop paper is the better target.

---

## 9. Tail-risk register

| Risk | Probability | Cost | Mitigation |
|---|---:|---|---|
| No reader/partner responds | High (0.45) | 50–70 h; artifact remains | B, not C; keep the package |
| Partner delays DPA | Medium | Pilot slips | Do not block the package; no PII |
| Risk team rejects the assumptions | Medium | Claim narrows | Use the review to narrow; no overclaim |
| Burnout | Medium if >15 h/week | High | 10–12 h/week cap; weekly review |
| PII/proprietary data request | Low | Catastrophic | Decline without DPA/sandbox |
| Hostile public review | Low–medium | Reputational, recoverable | Claim ledger; no production claim; v1.0.2 corrections |
| Paper rejection | High if submitted now | Reputational drawdown | Don't submit until reader/trim |
| Holdout baseline collapses effect | Unknown | Headline narrows | Run it before submission |

---

## 10. Review dates and kill criteria

- **2026-12-15:** paper trim/reposition status; reviewer packet sent; holdout
  baseline started.
- **2027-01-15:** at least one reader/real-log lead? If no, freeze outreach.
- **2027-02-15:** end-of-period. Decide whether to continue to a 2027 pilot or
  freeze at Level 2.

**Kill criteria:** no reader/lead by 2027-01-15; paper not trimmed by 2026-12-31;
health/GPA/applications slip; PII request without DPA; critical claim error;
holdout baseline collapses the effect.

---

## 11. Reasoning check

**Claim and tier.** The recommendation — “B is the most defensible” — is a
**proposed decision**, not a measured result. The state probabilities and
payoffs are subjective estimates; the expected values are a heuristic, not a
forecast. The external-evidence facts are **verified** in the audit; the
commercial judgment is **inferred**.

**Strongest counter-case.** The strongest argument against B is that the project
may have **diminishing marginal value**: the artifact is already strong, the
paper is applied/incremental, the vendor gap is unproven, and the marginal 50–70
hours may be better spent on applications, GPA, or a new project. If the job
market is the binding constraint, **E (freeze)** or a reduced A is more rational
than B. The response is that B’s incremental 10–15 outreach hours are the
cheapest test of whether the project has any external value; if the answer is no,
B stops cheaply. B is not a commitment to the project; it is an option.

**Not verified.** No reader/partner has been asked; no real log exists; the
holdout baseline and model ablation are not run; the audit/legal feasibility is
not reviewed; the vendor gap is search-based; the paper is not peer-reviewed.
Any of these could change the ranking. A real log showing action-dependent
observation and a feasible audit would strengthen B/C; a log showing
outcome-dependent observation would weaken the point-estimate claim and make
audit-only the fallback.

**Next action.** Freeze the method set. Run the holdout baseline and model
ablation. Send the reviewer packet to five targeted people. Book two calls. Have
one real-log conversation without PII. Review on 2026-12-15; stop outreach on
2027-01-15 if no lead. Do not submit the paper or chase a commercial pilot until
the tests say yes.
