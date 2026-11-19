# BSP / AFASA / NPC Mapping

**Purpose:** Show exactly which regulatory obligations the project supports, and
which it does not. This is the "why a bank or e-wallet cares" document. It is
not legal advice.

---

## 1. The obligations

| Instrument | What it requires | Status |
|---|---|---|
| **BSP Circular 1170 (2023)** | eKYC and digital identity proofing/authentication; anti-fraud and cyber-security processes for AML/CFT | Binding |
| **BSP Circular 1213 (2025)** | Automated, real-time fraud monitoring; a Fraud Management System (FMS); rule-based **and** machine-learning approaches; **constant calibration** through data analysis, risk assessment, adaptive rules, ML refinements, stress testing, **independent review and audits**; 5-year tamper-protected logs with 11 fields; 24-hour Transaction Pause Period; strong/adaptive authentication; customer notifications; kill switch; money lock; transaction limits | Binding; compliance deadline 25 June 2026 |
| **BSP Circular 1214 (2025)** | BSP inquiry into financial accounts; information sharing; audit trails | Binding |
| **BSP Circular 1215 (2025)** | Temporary holding of disputed funds: three lawful triggers (complaint, FMS finding, inter-bank request); initial hold <=5 days; total hold <=30 days; verification <=60 days if no funds held; improper holding is punishable | Binding |
| **RA 12010 (AFASA), s.6** | Institutions must employ adequate risk management systems and controls; failure can trigger **restitution**; conviction is not a prerequisite | Binding |
| **BSP Project Sapiens (2024)** | Thematic review: fraud/AML is the top AI use case; **sampling bias** and **labelling bias** are named; only 6/10 deep-dive institutions validate models during development and ongoing; some banks limit AI audit to credit/lending | Supervisory observation |
| **NPC Advisory 2024-04 / Circular 2022-04** | Transparency, explainability, human intervention, contestability, bias monitoring, automated-decision registration under the Data Privacy Act | Binding |
| **BSP draft Model Risk Management (June 2025)** | Model inventory, validation, documentation, lifecycle governance; outcomes analysis | **Draft, not final** |
| **BSP M-2026-031 AI principles (June 2026)** | AI governance principles | **Voluntary** |

## 2. The gap the project addresses

BSP 1213 mandates calibration, stress testing, and independent review/audit, and
mandates 5-year logs with 11 fields. **None of the 11 fields is the decision,
score, propensity, or outcome.** A team can satisfy the logging rule and still
be unable to evaluate its own onboarding policy.

The project supplies:

1. **A decision-log schema** that keeps the 11-field floor and adds the
   decision, observation, label, and eKYC fields needed for evaluation.
2. **Selection/delay-aware estimators** and **bounds** for the reject margin.
3. **An audit design** that respects the legal constraints.
4. **An audit-ready memo** separating measured, assumed, and unverifiable
   claims.

## 3. Mapping

| Requirement | Project artifact | What it supports | What it does not do |
|---|---|---|---|
| 1213: continuous calibration | Estimator comparison; label-maturity diagnostics; capacity/delay sweeps | A reproducible calibration check for a policy change | It does not calibrate the score itself; that is a separate model task |
| 1213: stress testing | `outcome_dependent` scenario; delay/capacity/cost sweeps | Stress tests the evaluation, not just the model | It is a simulation stress test; the bank must run its own |
| 1213: independent review and audits | Audit design; `policy_bounds`; measured/assumed/unverifiable memo | A structure an independent validator can review | It does not replace the validator or legal review |
| 1213: 5-year logs / 11 fields | `docs/SCHEMA.md`; schema validator | A concrete extension of the mandated log | It does not itself satisfy the retention/tamper requirements |
| 1170: eKYC / identity proofing | Schema eKYC fields; post-hoc verification audit | A way to audit identity decisions without changing them | It does not implement eKYC |
| AFASA s.6: adequate controls / restitution | The memo's measured/assumed/unverifiable ledger; bounds | Evidence that the policy was evaluated with stated assumptions | It does not establish legal adequacy; that is a legal/compliance judgment |
| 1215: hold triggers | The audit design rejects random holds; for account opening, it rejects random approvals/rejections | A legally defensible audit design | It does not cover transaction holds; that is a separate product decision |
| Project Sapiens: sampling/labelling bias | The entire estimand and bias decomposition | A direct response to the named risk | It cannot fix the bank's data if the fields are not logged |
| NPC 2024-04: explainability, contestability | Schema reason/decision fields; human-review tier; memo | Documentation for an automated decision | It does not implement the contest process |
| Draft MRM | The memo's validation structure | A head start if the MRM is finalized | Do not cite as binding |
| BSP AI principles (voluntary) | Transparency/audit memo | Alignment with the principles | Do not claim mandatory compliance |

## 4. The audit design under the law

- **Random holds are not available.** Circular 1215 closes the hold triggers to
  complaint, FMS finding, and inter-bank request; improper holding is punishable.
- **Random post-hoc verification of approved applications** is the recommended
  audit. It does not change the decision; it labels a random sample.
- **Shadow scoring** is the lowest-risk way to test coverage/overlap without
  customer impact.
- **Random approval of would-be-rejected applicants** deliberately onboards
  fraud; do not use it without explicit legal/risk approval.
- **Random rejection of would-be-approved applicants** deliberately excludes
  legitimate customers; do not use it.

For account opening, the analogous constraint is: do not randomize the
approval/rejection decision; randomize **post-hoc verification** and
**shadow scoring**.

## 5. What the memo should say to an auditor

1. The estimand (the logging non-rejected population).
2. The observation model and the propensities (known or estimated).
3. The overlap/ESS diagnostics.
4. The estimate or bounds, with uncertainty.
5. The reject-margin treatment.
6. The audit design and what it bought.
7. The measured / assumed / unverifiable ledger.
8. What would change the conclusion.

## 6. Caveats

- This is not legal advice. A bank's compliance and legal teams must review the
  audit design and the schema.
- The MRM circular is a draft; BSP's AI principles are voluntary. The binding
  explainability/fairness duties come from the NPC.
- BSP 1213 is an FMS circular, not an MRM circular.
- The project uses public/synthetic data and makes no claim about a specific
  institution.
