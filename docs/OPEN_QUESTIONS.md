# Open Questions

**Status:** Canonical research backlog for v0.2.1 (2026-11-20).
**Purpose:** Record what the project does **not** answer, why it matters, and how
to resolve it. This is the source for the paper's future-work section and for
the next round of experiments.

An open question is not a weakness to hide. It is a boundary of the claim.

---

## 1. Priority questions

### Q1. What are the real Philippine onboarding review rates, label delays, and false-reject costs?

**Why it matters.** The pilot's capacity (1–10%), delay (0.5–90 days), and
false-reject cost (0.02–0.50) are plausible ranges, not measured values. A
different operating point could change the ranking or the audit recommendation.

**Current evidence.** The BSP/industry evidence supports the *problem*, not the
calibration. There is no public Philippine account-opening log with actions,
propensities, or label timestamps.

**How to resolve.** Interviews with 2–3 PH fintech fraud/KYC teams; a data-sharing
agreement; a small audit pilot. Record the answers in `DATA.md` and the decision
journal.

**Priority.** High. This is the largest external-validity gap.

### Q2. Is post-hoc verification operationally feasible at a PH bank/e-wallet?

**Why it matters.** The audit design is the identification device for the
approved margin and the fallback under outcome-dependent labels. If it cannot be
run, the tool's recommendation is weaker.

**Current evidence.** The design is legally defensible (no random
approvals/rejections), but the operational cost, customer friction, and
turnaround time are not measured.

**How to resolve.** A process interview with an onboarding/ops team; a small
time-and-motion study; a legal review of the verification script.

**Priority.** High.

### Q3. How does the correction behave on a real log with covariate-dependent observation?

**Why it matters.** The covariate sensitivity uses a simulated logistic
mechanism on `log1p(amount)`. A real log may have a different gradient, multiple
covariates, or unmeasured confounding.

**Current evidence.** The 50-replication result: action-level IPW **67.52%**,
action-level DR **21.25%**; the fitted covariate model **1.97% / 2.48%** (delay
0.5) and **3.35% / 3.68%** (delay 45); coverage **89–91.5%**. The covariate
model recovers the oracle, but heavy weights undercover. See
[`RESULTS.md`](RESULTS.md) §9.

**How to resolve.** A partner log; a prespecified propensity model; a
pre-registered sensitivity band; a bootstrap interval.

**Priority.** High.

### Q4. Is the cost matrix defensible?

**Why it matters.** The false-reject cost is the inclusion parameter. A different
value can reverse a close ranking.

**Current evidence.** The normalized values are transparent and
sensitivity-tested (0.02–0.50). They are not a bank's accounting.

**How to resolve.** Elicit the cost of a false rejection (complaint handling,
lost lifetime value, inclusion harm) and the fraud loss given approval from a
partner. Report the ranking as a function of the false-reject cost.

**Priority.** Medium-high.

### Q5. What is the right audit size for a decision, not a generic 1%?

**Why it matters.** The pilot shows the audit's marginal value is modest in the
main scenario and decisive under outcome-dependent labels. A team needs a
decision-specific sample size, not a rule of thumb.

**Current evidence.** [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md) gives proportion and
two-policy formulas; the pilot gives realized RMSE/ESS at 0–2%.

**How to resolve.** A power calculator that takes the candidate's effect size,
the approved-label base rate, and the review cost; validate it on the pilot.

**Priority.** Medium.

### Q6. Does the ranking instability matter for a launch decision?

**Why it matters.** DR selects the true best policy 72% of the time; the residual
inversions are concentrated in the close better-model/incumbent gap. A launch
decision may tolerate that, or it may not.

**Current evidence.** Mean inversions 0.29, cost of misranking 0.000093 (naive
0.000333). The gap is small relative to the cost of a wrong reject.

**How to resolve.** A decision-theoretic threshold: how much misranking cost is
acceptable relative to the audit cost? Elicit from a risk committee.

**Priority.** Medium.

### Q7. Does the audit introduce a fairness or gaming risk?

**Why it matters.** A random post-hoc verification sample could be gamed if
customers/fraudsters learn the pattern; a segment with more audits could face
more friction.

**Current evidence.** The design is random within approved applications; the
schema has `segment`/`region` fields, but the pilot does not evaluate fairness.

**How to resolve.** A fairness diagnostic by segment; a review of the audit
script for disparate impact; a test for audit-aware behavior.

**Priority.** Medium.

### Q8. How does performativity change the result?

**Why it matters.** A deployed policy changes fraudster and customer behavior.
The pilot estimates policy value under a fixed observation model.

**Current evidence.** The project explicitly does not claim a causal deployment
effect. Pombal et al. (2022) is the closest work on performativity in this
setting.

**How to resolve.** A dynamic model or a live experiment with a compliant audit
arm; a sensitivity analysis over behavioral response.

**Priority.** Medium-low for v0.3; high for a production claim.

### Q9. Does FiFAR add enough to justify the capacity layer?

**Why it matters.** The pilot models review capacity as a hard cap with a
cost-based queue. FiFAR models analyst behavior and learning-to-defer. A more
realistic capacity layer could change the review policy's value.

**Current evidence.** The capacity sweep 1–10% does not break the correction. The
FiFAR layer is not implemented.

**How to resolve.** A small FiFAR integration; compare the queue value with and
without analyst heterogeneity.

**Priority.** Medium (v0.2/v0.3 scope).

### Q10. Can the tool evaluate a transaction-fraud policy?

**Why it matters.** The estimator layer is general, but the schema, delays,
actions, and audit design are account-opening specific.

**Current evidence.** The project explicitly scopes to account opening; BAF is
account-opening data.

**How to resolve.** A separate transaction-fraud dataset (IEEE-CIS, PaySim) and a
new schema/audit design; do not reuse the account-opening claims.

**Priority.** Low for the current flagship; possible v0.3 extension.

### Q11. What is the right interval under heavy weights?

**Why it matters.** The covariate sensitivity shows below-nominal coverage
(80–88%) even with oracle propensities. The point estimate can be close while
the interval is too narrow.

**Current evidence.** The influence-function SE undercovers under heavy-tailed
weights; the covariate scenarios show **89–91.5%** coverage for the covariate
model and **89–90%** for the oracle, against nominal 95%. ESS and max weight are
reported.

**How to resolve.** A bootstrap or randomization-inference interval; a
comparison on the pilot's covariate scenarios; a coverage test.

**Priority.** Medium-high for the paper's uncertainty claims.

### Q12. Can the project get two external readers?

**Why it matters.** The roadmap and the publication checklist require a
fraud/KYC practitioner and a researcher. Their objections are the best
red-team.

**Current evidence.** No external reader has reviewed the artifact yet.

**How to resolve.** Send the one-pager and the report usage guide to 2–3
practitioners; ask for a 30-minute critique; record the objections.

**Priority.** High for release readiness.

---

## 2. Questions the project has already answered

| Question | Answer | Evidence |
|---|---|---|
| Is the naive evaluation materially biased? | Yes, +111.6% to +278.5% in the main scenario | `reports/pilot.json`; [`RESULTS.md`](RESULTS.md) |
| Does the naive estimate reverse the ranking? | Yes, better-model/incumbent | [`RESULTS.md`](RESULTS.md) |
| Does DR recover the identified value? | Yes, 0.94% max bias, 96.0% coverage | [`RESULTS.md`](RESULTS.md) |
| Is the audit a universal fix? | No; modest in the main scenario, decisive under outcome-dependent labels | [`RESULTS.md`](RESULTS.md) |
| Is the reject margin point-identified? | No; bounds only | [`THREATS.md`](THREATS.md) |
| Does DR survive estimated action-level propensities? | Yes, 2.67% / 91.0% when observation is action-dependent; no under covariate dependence | [`RESULTS.md`](RESULTS.md) |
| Does IPW survive estimated propensities? | No, 11.19% / 73.0% | [`RESULTS.md`](RESULTS.md) |
| Does action-level IPW survive covariate-dependent observation? | No; the covariate model is needed | [`RESULTS.md`](RESULTS.md) |
| Is BSP 1213 a model-risk circular? | No; it is an FMS circular; the MRM guidelines are a draft | [`BSP_MAPPING.md`](BSP_MAPPING.md) |

---

## 3. How to add a question

1. State the question as a decision or a measurement, not a topic.
2. State why it matters for the claim.
3. State the current evidence and its limit.
4. State the smallest study that would resolve it.
5. Assign a priority and a review date.
6. If it changes a public claim, add it to [`CLAIMS.md`](CLAIMS.md) and
   [`DECISIONS.md`](DECISIONS.md).

## 4. Related documents

- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Threats: [`THREATS.md`](THREATS.md)
- Decisions: [`DECISIONS.md`](DECISIONS.md)
- Worklog: [`WORKLOG.md`](WORKLOG.md)
- Publication checklist: [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md)
