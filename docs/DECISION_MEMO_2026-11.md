# Decision Memo — November–December 2026 Strategic Move

**Decision:** How should I spend the remaining six weeks of 2026 on the
`onboarding-audit` flagship, given the goal of a strong Summer 2027 fintech
internship and a durable research project?

**Decision owner:** Ken Ira Lacson Talingting.
**Date:** 2026-11-20.
**Horizon:** 2026-11-20 to 2026-12-31 (6 weeks).
**Status:** Revised 2026-11-20 — finish-first sequence: package freeze by
2026-12-05; external reviewer search 2026-12-08 to 2026-12-23.

**Models used:** 2 (constraints and opportunity cost), 9 (expected value and
value of information), 10 (fat tails, ruin, margin of safety), 11 (convexity and
optionality).

---

## 1. Framing

### 1.1 The real decision

Not "what feature should I build?" The real decision is:

> **How much of my scarce pre-holiday time should go to the flagship, and to
> which part, versus applications, interview prep, GPA, and rest?**

The project is already a strong reproducible research artifact. The next
bottleneck is not code. It is **external evidence and adoption packaging**.

### 1.2 The binding constraint (Model 2)

**Access to a real decision log and a risk-team reviewer.**

The project has enough methods, tests, scenarios, and documentation for a
pilot: 47 tests, 22 configured scenarios, 1,150 pilot replications, 11
sensitivity scenarios, a schema, an audit design, and a report/memo. What it
lacks is:

- a real historical log with the required fields;
- a risk-team reviewer who will challenge the assumptions;
- a pilot protocol, model card, validation report, and business case;
- two external readers and an independent replication.

Adding another estimator or simulation scenario does not relax this
constraint. Building the review package and asking real practitioners does.

### 1.3 Opportunity cost

Every hour on the flagship is an hour not spent on:

- internship applications and interview practice;
- GPA and coursework;
- rest and health;
- other portfolio projects.

The project work is only worth it if it **doubles as application material** and
**buys information** about whether a risk team would engage. The recommended
option is designed to do both.

### 1.4 Smallest acceptable outcome

A **Level 2 review-ready package by 2026-12-05**: validation report, model card,
pilot protocol, business case, real-log adapter, one-command demo, CI, and the
reviewer packet. The external reviewer search happens in December. A completed
pilot is upside, not the minimum.

---

## 2. Options, including doing nothing

| Option | What it means | Time |
|---|---|---:|
| **A. Do nothing / maintain** | Freeze the repo; use the current artifact in applications; no new work | 5 h |
| **B. Research polish** | More docs, paper draft, more scenarios, README polish; no external evidence | 50 h |
| **C. Level 2 package + outreach** | Validation report, model card, pilot protocol, business case, real-log adapter, demo, CI, security/privacy/maintainers; 10 practitioner asks; 2 readers | 65 h |
| **C-seq. Finish-first** | Package by Dec 5; reviewer shortlist prepared in late November; reviewer search Dec 8–23; no parallel outreach | 65 h |
| **C+. Convex barbell** | C plus a public real-action fallback and 20% pilot scouting; preserve the option to convert to D | 75 h |
| **D. Full pilot push** | Spend the six weeks chasing a partner and a data-sharing agreement; build only what the partner needs | 65 h |
| **E. Pivot** | Start a new project or a transaction-fraud extension | 65 h |
| **F. Application package only** | One-pager, 10-minute walkthrough, mock interviews, applications; no new project evidence | 30 h |

**Doing nothing is a real option.** The current artifact is already stronger than
most student projects. The question is whether the marginal six weeks buy enough
to justify the opportunity cost.

---

## 3. States, probabilities, costs, and payoffs

### 3.1 States

The states describe the **outreach outcome** over the six weeks. They are
subjective estimates, not measured frequencies.

| State | Meaning | Base probability |
|---|---|---:|
| **S1. Cold** | No practitioner or reader engages | 0.35 |
| **S2. Readers** | 1–2 readers engage; no pilot | 0.45 |
| **S3. Pilot lead** | A practitioner agrees to a scoped pilot or a real-log review | 0.20 |

The probabilities are based on cold outreach to busy practitioners, not a warm
network. If you have a warm intro, shift probability mass to S3 and re-run the
memo.

### 3.2 Payoff scale

A 0–100 **strategic value** score for the flagship plus internship readiness:

| Score | Meaning |
|---:|---|
| 50 | Current Level 1: strong reproducible artifact, no external validation |
| 60 | Polished artifact, still no external validation |
| 70 | Level 2 package: validation report, model card, pilot protocol, business case, demo, CI |
| 80 | Level 2 plus two external readers |
| 90 | Level 3: pilot lead or real-log case study |
| 95 | Pilot completed plus publication/adoption |

The score is a weighted composite of evidence/credibility (40%), external
validation (30%), interview story (20%), and optionality (10%). The weights are
subjective; the sensitivity analysis tests the ranking.

### 3.3 State-contingent values

| Option | S1 Cold | S2 Readers | S3 Pilot lead |
|---|---:|---:|---:|
| A. Do nothing | 50 | 50 | 50 |
| B. Research polish | 58 | 62 | 60 |
| C. Level 2 package + outreach | 72 | 82 | 88 |
| C-seq. Finish-first | 72 | 80 | 86 |
| C+. Convex barbell | 72 | 82 | 88 |
| D. Full pilot push | 48 | 58 | 90 |
| E. Pivot | 45 | 50 | 55 |
| F. Application package only | 58 | 66 | 68 |

**Why C is high in every state:** the package is valuable even if no one
responds. It makes the project review-ready, gives you a concrete artifact to
send, and doubles as application material. **Why C-seq is slightly lower in
S2/S3:** the reviewer feedback arrives later, so less of it can be incorporated
by December 31. The package quality is higher because attention is not split.
**Why D is low in S1/S2:** if the partner does not engage, the six weeks produce
an incomplete package and no pilot. **Why D is high in S3:** a real pilot is the
strongest evidence.

### 3.4 Expected values

Using the base probabilities (S1 0.35, S2 0.45, S3 0.20):

| Option | Expected value | Time cost | Net (0.1 pt/hour) |
|---|---:|---:|---:|
| A. Do nothing | 50.0 | 5 | 49.5 |
| B. Research polish | 60.0 | 50 | 55.0 |
| **C. Level 2 package + outreach** | **79.7** | **65** | **73.2** |
| **C-seq. Finish-first** | **78.4** | **65** | **71.9** |
| C+. Convex barbell | 81.3 | 75 | 73.8 |
| D. Full pilot push | 60.4 | 65 | 53.9 |
| E. Pivot | 49.0 | 65 | 42.5 |
| F. Application package only | 63.2 | 30 | 60.2 |

**C, C-seq, and C+ dominate.** C+ is marginally higher in the model (net 73.8
vs 71.9), but it assumes parallel attention and a higher coordination cost. The
difference is within the noise of the subjective estimates. Given the explicit
focus constraint, **C-seq is the chosen implementation**: finish the package
first, then run the reviewer search in December.

---

## 4. Sensitivity analysis (Model 9)

### 4.1 Probability of a pilot lead

| P(S3) | C net | D net | Winner |
|---:|---:|---:|---|
| 0.05 | 71.1 | 48.4 | C |
| 0.10 | 71.8 | 50.4 | C |
| 0.20 | 73.2 | 53.9 | C |
| 0.30 | 74.3 | 58.0 | C |
| 0.40 | 75.0 | 61.3 | C |

C wins across the plausible range. D only catches up if P(S3) is very high
(>0.60) **and** the package has little standalone value. If you have a warm
partner in hand, shift 30–40% of time from C to D, but keep the package.

### 4.2 Time cost

If the time-cost penalty is 0.05–0.15 points per hour, C's net ranges from
76.5 to 69.5; D's net ranges from 57.2 to 50.7. C remains first. If your time is
much scarcer than 65 hours, choose F or a reduced C (package only, no
outreach).

### 4.3 Value of the package

If the package is worth only 60 in S1/S2 (not 72/82), C's net falls to ~63.6,
still above D's 53.9. The package would have to be nearly worthless for D to
win. That is not the case: the package is reusable for applications, future
pilots, and the paper.

### 4.4 What the sensitivity says

The ranking is **robust to reasonable changes**. The decision is not fragile to
the exact probabilities. The one condition that flips it is a **warm partner**:
if a practitioner is already willing to run a pilot, D becomes competitive, and
you should shift time toward the pilot while keeping the package. C-seq is
within about two points of C+ across the plausible range; the choice is about
focus and sequencing, not a meaningful expected-value difference.

---

## 5. Value of information

The biggest uncertainty is **whether a risk team will engage**. Buy that
information cheaply before committing the full six weeks.

| Information | Cost | What it changes | Value |
|---|---:|---|---|
| Prepare a 1-page pilot brief in late November; send it Dec 8–15 | 5–8 h | If 0 responses, P(S3) drops; pivot to the package + public fallback. If 2+ respond, invest in the pilot. | **High** |
| One 30-minute review with a practitioner using the memo template | 1–2 h | Reveals whether the reject margin, cost matrix, or audit design is a blocker | **High** |
| Check a public real-action dataset (credit approval/reject inference) | 5 h | Creates a credible fallback if no bank partner | **Medium-high** |
| Check paper venue/reviewer fit | 2 h | Changes the paper target, not the November decision | **Low** |
| Run more simulations or add an estimator | 20–40 h | Does not change the adoption probability | **Low** |

**Sequence (revised):** finish the package by **2026-12-05**. Prepare the
reviewer shortlist and one-pager in late November, but send the packet
**2026-12-08 to 2026-12-15**. The package is the information asset; the reviewer
calls are the December information purchase. Do not split attention in November.

---

## 6. Tail risk, absorbing barriers, and margin of safety (Model 10)

### 6.1 Absorbing barriers

| Barrier | Why it is absorbing | Mitigation |
|---|---|---|
| **Burnout / health** | Cannot recover the lost semester or internship window | Cap 10–12 h/week; weekly review; stop if sleep, mood, or GPA slips |
| **Academic failure** | Closes the internship path | Protect coursework first; the project is secondary |
| **Legal/privacy breach** | Reputational and legal damage; cannot be undone | No PII or proprietary data without a DPA; read-only sandbox; hashed identifiers |
| **Overclaiming** | Public correction is costly, though recoverable | Claim ledger; external review; no production/causal claims |
| **Losing the application window** | Time-bound | Reserve 30% of the period for applications and interviews |

### 6.2 Tail risks

| Risk | Probability | Cost | Mitigation |
|---|---|---|---|
| No partner responds | High (0.35–0.45) | Six weeks, but the package remains | Build C, not D; keep the public fallback |
| Partner delays the DPA | Medium | Pilot slips into 2027 | Start the conversation now; do not block the package |
| Risk team rejects the assumptions | Medium | The pilot claim narrows | Use the review to narrow to `P0` + bounds |
| Burnout | Medium if >15 h/week | High | Cap hours; weekly review |
| PII/proprietary data request | Low | Catastrophic | Decline without a DPA and sandbox |
| Hostile public review | Low–medium | Reputational, recoverable | Claim ledger; red team; no overclaiming |

### 6.3 Margin of safety

- **Time:** plan 65 hours, keep a 20–30% buffer; do not plan 75+ hours.
- **Scope:** freeze the method set; no new estimators or scenarios.
- **Data:** public/synthetic only until a DPA and a sandbox exist.
- **Claims:** every public number traces to an artifact; no production/causal
  claims.
- **Optionality:** keep the public real-action fallback; do not sign an
  exclusive partner agreement.
- **Recovery:** keep the repo clean and documented at all times; never leave it
  in a broken state before a holiday or a deadline.

### 6.4 Ruin test

Can you survive the worst case? **Yes**, if you avoid PII/proprietary data and
overclaiming. The downside is six weeks of work and a package that is still
useful. The absorbing risks are health, academic failure, and legal/privacy
breaches — none of which are necessary for this project.

---

## 7. Payoff shape and optionality (Model 11)

| Option | Shape | Why |
|---|---|---|
| A. Do nothing | Flat | No new evidence; current value only |
| B. Research polish | Linear, bounded | More polish, no external validation |
| **C. Level 2 package + outreach** | **Convex** | Bounded downside (reusable package), open upside (readers, pilot, publication) |
| C+. Convex barbell | **Most convex** | 80% safe package, 20% high-upside pilot scouting; preserves the option to convert to D |
| D. Full pilot push | High variance, less convex | A single low-probability bet; if it fails, the package may be incomplete |
| E. Pivot | Negative convexity | Abandons the compounding advantage; high downside, uncertain upside |
| F. Application package only | Linear, bounded | Improves interview readiness, not evidence |

**The key insight:** C is not a compromise between research and applications. It
is the **option-creating asset**. The package makes the project review-ready
even if no partner appears, and it makes the pilot ask credible if a partner
does appear. That is bounded downside with open upside.

---

## 8. Recommendation

**Choose C-seq: finish the Level 2 package by 2026-12-05, then run the external
review search in December.**

### 8.1 Allocation

- **Until Dec 5 — 100% Level 2 package:** validation report, model card, pilot
  protocol, business case, real-log adapter, one-command demo, CI,
  security/privacy/maintainers.
- **Late November — reviewer shortlist only:** names and a 1-page brief, no
  outreach yet. This preserves focus and makes December faster.
- **Dec 8–23 — reviewer search:** send the packet to 10 targeted practitioners,
  schedule 2 calls, record objections.
- **0% — New methods:** no new estimators, scenarios, or simulation depth.

### 8.2 Finish-first plan

| Dates | Focus | Deliverables |
|---|---|---|
| Nov 20–24 | Freeze scope; reviewer-critical docs | `docs/VALIDATION_REPORT.md`, `docs/MODEL_CARD.md` |
| Nov 25–30 | Pilot and business case | `docs/PILOT_PROTOCOL.md`, `docs/BUSINESS_CASE.md`; reviewer shortlist |
| Dec 1–5 | Make it runnable and reviewable | Real-log adapter, one-command demo, CI, `SECURITY.md`, `PRIVACY.md`, `MAINTAINERS.md`; **freeze v0.3** |
| Dec 6–7 | Buffer; apply red-team findings | Fix only critical issues; no new features |
| Dec 8–15 | Reviewer search | Reviewer packet, 10-person shortlist, 2 calls scheduled |
| Dec 16–23 | Review calls | `docs/EXTERNAL_REVIEW.md`; update claims/threats |
| Dec 24–31 | Freeze and plan January | Reviewer response, v0.3.1 if needed, January pilot plan |

### 8.3 Kill criteria

- **Dec 5:** if the package is not frozen, cut scope to the validation report,
  model card, and pilot protocol. Ship those; defer the rest.
- **Dec 15:** if no reviewer has agreed to a call, use the red-team review plus
  one strong peer reviewer, and plan the external review for January.
- **Any time:** if GPA, applications, sleep, or health slip, stop. The project
  can wait; the internship window cannot.
- **A partner asks for PII or proprietary data without a DPA/sandbox** →
  decline; keep the public/synthetic path.
- **The risk team finds the assumptions untenable** → narrow the claim to a
  methods paper; do not claim a pilot.

### 8.4 Review dates

- **2026-12-05:** package freeze. If not met, cut scope.
- **2026-12-15:** reviewer status. If no call, use the red-team + peer and plan
  January.
- **2026-12-31:** end-of-period. Decide whether to continue to a 2027 pilot or
  freeze at Level 2.

### 8.5 What would change the decision

- **A warm partner in hand:** contact them in late November and shift 30–40% of
  time to the pilot, but keep the package.
- **A usable public real-action dataset:** add a case study after the package
  freeze.
- **A health/GPA constraint:** drop to A or F; the project can wait.
- **A red-team finding that the package is the wrong shape:** revise the package,
  not the decision to build one.

---

## 9. Reasoning check

- **Claim and tier:** This is a **proposed decision**, not a measured result.
  The probabilities and payoffs are subjective estimates; the ranking is
  derived from them.
- **Strongest counter-case:** The six weeks could be better spent on
  applications and interview prep, and the project's marginal value may be
  lower than the package suggests. If the job market is the binding constraint,
  F (application package) or a reduced C is better.
- **Not verified:** No practitioner has been asked; no partner exists; no
  public real-action dataset has been checked. The red-team review found six
  issues that must be triaged before the package freeze.
- **Next action:** Freeze the package by Dec 5; send the reviewer packet Dec 8.
  If there is no call by Dec 15, use the red-team + peer and plan January.

## 10. Related documents

- Credibility and adoption plan: [`CREDIBILITY_PLAN.md`](CREDIBILITY_PLAN.md)
- Decision journal: [`DECISIONS.md`](DECISIONS.md) (D13, D14)
- Results: [`RESULTS.md`](RESULTS.md)
- Claims: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Worklog: [`WORKLOG.md`](WORKLOG.md)
