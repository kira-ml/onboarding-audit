# Credibility and Adoption Plan

**Status:** Strategy document for v0.2.1 (2026-11-20).
**Purpose:** Define what it would take for a fintech risk team to actually run
this project, and for a hostile reviewer to engage with it rather than dismiss
it. This is a plan, not a claim that the project is already there.

**Current honest position:** the project is a strong **reproducible research
artifact**. It is not yet a **review-ready tool**, a **pilot-proven tool**, or a
**risk-team-adopted tool**. The gap is mostly evidence, access, and packaging —
not another estimator.

---

## 1. The two audiences

### 1.1 The risk team

A risk team does not adopt a model because it is clever. It adopts a tool
because it changes a decision they are accountable for, on their data, with a
defensible audit trail, a named owner, and a clear cost-benefit case.

They will ask:

1. What decision does this change?
2. What is the evidence on **our** log?
3. What are the assumptions, and what happens if they are wrong?
4. Is it safe, private, and legal?
5. Who owns it, and how is it maintained?
6. What does it cost, and what does it save?
7. What would make us stop using it?

### 1.2 The hostile reviewer

A hostile reviewer does not need to be unfair. They will attack the weakest
link in the identification, the data, the observation model, or the claim. They
will ask:

1. What is the estimand, and what is not identified?
2. What is the selection mechanism, and is the observation model realistic?
3. Is the data real, representative, and large enough?
4. Where are the baselines, negative controls, and sensitivity analyses?
5. Has anyone independent replicated it?
6. Does the claim exceed the evidence?
7. Is the paper/repository reproducible?

The goal is not to make dismissal impossible. The goal is to make dismissal
**unreasonable to a fair reader** because every attack has a documented response
and a residual-risk statement.

---

## 2. The credibility ladder

| Level | What it means | Minimum evidence | Current |
|---|---|---|---|
| **0. Demo** | A notebook or a plot | One result | — |
| **1. Reproducible research artifact** | Tests, docs, pre-registration, claim ledger, known-ground-truth benchmark | `pytest`, `reports/pilot.json`, `docs/CLAIMS.md`, `docs/THREATS.md`, `docs/REPRODUCIBILITY.md` | **Current — strong** |
| **2. Review-ready tool** | A risk team can review it without the author in the room | Model card, validation report, pilot protocol, real-log adapter, external readers, CI, demo | **Next target** |
| **3. Pilot-proven tool** | A real team has run it on a historical log and reviewed the memo | Partner log, case study, risk-team objections and responses, shadow-mode result | **2027 target** |
| **4. Risk-team-adopted tool** | It is part of a recurring workflow | Integration, ownership, monitoring, change control, legal/privacy sign-off | Requires a sponsor |
| **5. Industry/peer-reviewed standard** | Independent replication and publication | Replication, peer review, adoption | Long-term |

**The realistic goal for the Summer 2027 internship cycle is Level 3.** Level 4
requires a bank sponsor and a longer timeline; claiming it without one is the
fastest way to lose a hostile reviewer.

---

## 3. The binding constraint

**The binding constraint is access to a real decision log and a risk-team
sponsor — not more code.**

The project already has enough methods, scenarios, tests, and documentation for
a pilot. Adding another estimator or another simulation will not move a risk
team. A single historical log with a real policy change and a risk reviewer will.

The second constraint is **independent review**. A hostile reviewer will not
accept the author's own tests as external validation. Two external readers and
one independent replication are worth more than ten more scenarios.

---

## 4. What a risk team needs to say yes

- [ ] A named business owner and a specific policy decision.
- [ ] A historical decision log with the required fields (see `docs/SCHEMA.md`).
- [ ] A sandbox/read-only pilot with no production changes.
- [ ] A legal/privacy review (Data Privacy Act, NPC, BSP).
- [ ] A validation report and a model card.
- [ ] A cost-benefit case in the bank's units.
- [ ] A success metric and kill criteria.
- [ ] An audit/monitoring plan.
- [ ] A maintenance owner and a release cadence.
- [ ] A decision forum (risk committee / model risk) to review the memo.

If any of these is missing, the team may run a **desk review**, but not a
pilot.

---

## 5. What a hostile reviewer will attack

| Attack | What they will say | Current response | Gap | Fix |
|---|---|---|---|---|
| **Synthetic data** | "BAF is synthetic; this is not a bank." | Task-matched benchmark, known ground truth | No real log | Partner pilot; real-action public dataset; case study |
| **Oracle propensities** | "You know `e`; a bank does not." | Action-level, noisy, and covariate sensitivity | Real observation model unknown | Estimate `e` from a real audit/log; pre-register; report a sensitivity band |
| **Cost matrix** | "The costs are arbitrary." | False-reject sweep 0.02–0.50 | No bank cost accounting | Elicit costs; report a cost curve and break-even |
| **Reject margin** | "You cannot identify the full population." | Bounds, not confidence intervals | Bounds wide; 35% coverage | Report bounds; controlled design or explicit assumption |
| **Ranking instability** | "DR selects the best only 72%." | Inversions, P(best), cost of misranking | Close better-model/incumbent gap | More audit/features; decision threshold; report cost of misranking |
| **Audit feasibility** | "Ops/legal will not allow it." | Post-hoc verification + shadow scoring | No legal/ops review | Legal review; ops pilot; time-and-motion study |
| **No external validation** | "No one has reviewed it." | Docs and tests | No external readers | Two readers; red team; independent replication |
| **No peer review** | "Not published." | Technical report outline | No publication | arXiv/workshop; response to reviewers |
| **Integration** | "It is a CLI, not a workflow." | Python package + CLI | No real-log adapter/demo | CSV/parquet adapter; SQL export guide; one-command demo |
| **No business case** | "Where is the ROI?" | Memo template | No pesos/ROI | Cost-benefit model; pilot success metric |
| **Privacy/security** | "PII risk." | Hashed fields; no PII in examples | No DPIA/security review | DPIA; sandbox; read-only; hashing |
| **Model risk** | "No model card or validation report." | Methods, threats, tests | No MRM package | Model card; validation report; monitoring |
| **Overclaiming** | "You claim production/causal." | Claim ledger; threats register | Some derived docs may drift | Claim audit; red team; external review |
| **Maintenance** | "Who owns it?" | Docs | No maintainer/support file | `MAINTAINERS.md`; release cadence; support |
| **Reproducibility** | "I cannot reproduce it." | Repro guide; tests | Data not public | Public synthetic demo; data hash; container |

The pattern: **the project has an answer to most scientific attacks; it lacks
answers to the adoption attacks.** That is the next phase.

---

## 6. The minimum evidence package

1. **Real-log pilot:** one historical log, one policy change, one memo, one
   risk-team review.
2. **Validation report:** every claim, evidence, test, status, residual risk.
3. **Model card:** intended use, out-of-scope use, inputs, outputs, assumptions,
   performance, limitations, ethical/regulatory notes.
4. **Data adapter:** schema mapping, missingness, label maturity, data-quality
   report, "bring your own log" tutorial.
5. **Pilot protocol:** scope, data, analysis, success metrics, privacy/legal,
   rollback, timeline.
6. **Business case:** cost of the current evaluation, cost of a wrong policy,
   expected value, audit cost, pilot ROI.
7. **External review:** two readers, one red-team pass, one independent
   replication.
8. **Publication:** technical report/arXiv, workshop submission, blog post,
   DOI.
9. **Operational guide:** install, run, interpret, monitor, update.
10. **Ownership:** `MAINTAINERS.md`, `SUPPORT.md`, `SECURITY.md`, release
    cadence.

---

## 7. The 90-day plan

### Weeks 1–2 — Freeze and red-team

**Deliverables**
- `docs/VALIDATION_REPORT.md`: claim → evidence → test → status → residual risk.
- `docs/MODEL_CARD.md`: intended use, out-of-scope, inputs, outputs,
  assumptions, performance, limitations, regulatory notes.
- `docs/PILOT_PROTOCOL.md`: scope, data requirements, success metrics,
  privacy/legal, rollback, timeline.
- `docs/BUSINESS_CASE.md`: cost of the current evaluation, cost of a wrong
  policy, expected value, audit cost, pilot ROI.

**Acceptance:** a skeptical reader can answer "what is this, what does it claim,
what does it not claim, and how would I pilot it?" in 15 minutes.

### Weeks 3–4 — Pilot-ready tool

**Deliverables**
- Real-log adapter/validator: CSV/parquet, schema mapping, missingness, label
  maturity, data-quality report.
- One-command demo on a synthetic 2,500-row log.
- GitHub Actions CI: tests, lint, smoke test, link check.
- `SECURITY.md`, `PRIVACY.md`, `MAINTAINERS.md`, `SUPPORT.md`.
- A pinned environment or container for reproducibility.

**Acceptance:** a data scientist can run the demo in under 10 minutes and a
report in under 30 minutes, without the author.

### Weeks 5–8 — External evidence

**Deliverables**
- Send the one-pager and pilot protocol to 5 practitioners; get 2 readers.
- Run a historical-log pilot with a partner or a public real-action dataset.
- Write `docs/CASE_STUDY.md`.
- Record risk-team objections and responses in `docs/EXTERNAL_REVIEW.md`.
- Run a shadow-mode evaluation; compare with the team's current method.

**Acceptance:** a real log, a real reviewer, a real memo, and a documented
objection/response cycle.

### Weeks 9–12 — Publish and iterate

**Deliverables**
- Technical report/arXiv draft; workshop submission.
- v0.3 release with the pilot learnings.
- Blog post, 10-minute walkthrough, and reviewer's guide.
- README updated with the case study and external review.
- `docs/REVIEWER_GUIDE.md`: the 10 likely attacks and the responses.

**Acceptance:** a hostile reviewer has a concrete artifact to review — a real
pilot, a validation report, external readers, and a response to every attack.

---

## 8. The 6-month flagship plan

| Quarter | Focus | Evidence |
|---|---|---|
| **Q1 2027** | Pilot + case study | Real log, risk-team review, memo |
| **Q2 2027** | Publication + release + replication | arXiv/workshop, v0.3, independent replication |
| **Q3 2027** | Adoption + application package | Two readers, a pilot case study, talks, internship applications |

---

## 9. The pilot protocol

**Scope**
- One historical decision log (6–12 months).
- One candidate policy change.
- One business owner.
- One risk reviewer.
- One legal/privacy reviewer.
- A read-only sandbox.

**Data**
- `application_id`, `action`, `score`, `amount`, `label`, `label_time`,
  `reviewed`, `audit_flag`, `label_source`, pre-decision features.
- No PII; hashed identifiers; a data-sharing agreement.
- A data-quality report before the analysis.

**Analysis**
- Run `validate`, then `report`.
- Compare naive, IPW, DR, audit-only, and bounds.
- Check overlap, ESS, max weight, label maturity, label-source mix.
- Write the memo with measured/assumed/unverifiable claims.
- Have the risk team review the memo before the business owner decides.

**Success metrics**
1. The tool finds a material bias or a ranking flip the current evaluation
   misses.
2. The risk team agrees the corrected estimate is more credible.
3. The audit design is operationally feasible.
4. The memo passes internal review.
5. The pilot produces a decision recommendation.

**Kill criteria**
- The log lacks the required fields.
- The overlap is too poor for a point estimate.
- The audit is infeasible.
- The cost matrix cannot be elicited.
- The risk team finds the assumptions untenable.

---

## 10. The business case template

| Item | What to estimate |
|---|---|
| Current evaluation cost | Analyst hours × rate + tooling + audit |
| Cost of a wrong policy | Expected fraud loss + false-reject cost + review cost + regulatory/reputational cost |
| Expected value of the tool | Probability of avoiding a wrong policy × cost avoided + audit efficiency + regulatory defensibility |
| Pilot cost | Data prep + analyst time + audit labels + review |
| ROI | Expected value / pilot cost |

The numbers are illustrative until the partner provides their costs. Do not
invent a peso figure in a public document.

---

## 11. The model-risk package

A risk team will recognize this structure:

- **Model card:** purpose, intended use, out-of-scope use, inputs, outputs,
  assumptions, performance, limitations, ethical/regulatory notes.
- **Validation report:** conceptual soundness, data quality, implementation
  testing, outcomes analysis, sensitivity, benchmarks, independent review.
- **Monitoring:** drift, label maturity, weight/ESS, coverage, audit share,
  decision changes.
- **Change control:** versioning, review, approval, rollback.

The project has the raw material in `docs/METHODS.md`, `docs/RESULTS.md`,
`docs/THREATS.md`, `docs/TESTING.md`, and `docs/REPRODUCIBILITY.md`. The gap is
the packaging, not the analysis.

---

## 12. The hostile-reviewer response

1. **Pre-register** the pilot before running it.
2. **Report all scenarios**, including failures and negative results.
3. **Put the strongest counter-case first** in the paper and the README.
4. **Separate measured, assumed, and unverifiable** claims.
5. **Provide a one-command reproduction** and a data hash.
6. **Get independent replication** by someone with no stake.
7. **Write a reviewer's guide** with the 10 likely attacks and responses.
8. **Do not claim novelty** for standard estimators; claim the applied
   measurement layer.
9. **Do not claim production or causal effects.**
10. **Make the limitations section a first-class contribution.**

---

## 13. What not to do

- Do not add more estimators or scenarios before the pilot.
- Do not build a dashboard, database, or auth system.
- Do not claim production, GCash, or a specific bank.
- Do not hide the simulation.
- Do not run a random approval/rejection experiment.
- Do not use PII or proprietary data without a data-sharing agreement.
- Do not promise a risk team will run it without a sponsor.
- Do not chase a venue before the evidence.
- Do not let the README, one-pager, or paper drift from the claim ledger.

---

## 14. The one-page credibility test

A risk team or a hostile reviewer should be able to answer these from the
repository:

1. What decision does this change?
2. What is the estimand, and what is not identified?
3. What are the identification assumptions?
4. What is the observation model, and how was it validated?
5. What is the cost matrix, and how was it calibrated?
6. What is the audit design, and is it legal/operational?
7. What is the evidence on real data?
8. Who reviewed it independently?
9. What would change the conclusion?
10. Who owns it, and how is it maintained?

If the answer to any question is "the author says so," the project is not yet
review-ready. If every answer points to an artifact, the project is.

---

## 15. Reasoning check

- **Claim and tier:** This is a strategy, not a measured result. It is derived
  from the project's current artifacts and standard model-risk/adoption
  criteria.
- **Strongest counter-case:** A student may not be able to get a bank partner;
  the pilot may be infeasible. The fallback is a public real-action dataset, two
  external readers, and an independent replication — still a strong Level 2.
- **Not verified:** No risk team or hostile reviewer has been interviewed for
  this plan. The criteria are inferred from the project's docs and standard
  practice.
- **Next action:** Write the validation report, model card, pilot protocol, and
  business case; then contact five practitioners with a one-page pilot brief.

## 16. Related documents

- Methods: [`METHODS.md`](METHODS.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Claims: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Publication checklist: [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md)
- Open questions: [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
