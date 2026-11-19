# Communication Plan

**Purpose:** Make the project legible to a fintech research team, a risk
committee, and an internship interviewer without overclaiming.

---

## 1. One sentence

> I study whether a bank can trust its own onboarding-fraud policy evaluation
> when the current policy chooses which applicants get labeled, labels arrive
> late, and review capacity is finite — and I build the logging, audit, and
> memo layer that makes the answer defensible.

## 2. The 60-second version

> A fintech onboarding team wants to know whether a new approve/review/reject
> policy will catch more fraud without rejecting more good customers. The only
> labels they have were selected by the current policy: reviewed applications
> get a fast label, approved accounts are labeled late if at all, and rejected
> applicants are never observed. A naive backtest therefore measures the
> population the old policy chose, not the new policy's value.
>
> I formalize the problem, separate the identifiable approve/review margin from
> the unobserved reject margin, and test naive, IPW, doubly robust, audit-only,
> and bounds estimators on the public BAF account-opening benchmark. I also
> show when a random post-hoc verification audit helps and when it does not.
>
> In the pilot, naive evaluation overstated cost by **112–278%** and ranked the
> better model below the incumbent; doubly robust estimation recovered the
> identified value within **0.94%** with **96%** coverage. The audit-only
> estimator was unbiased but high-variance, and action-only weighting collapsed
> when approved fraud was more likely to be labeled than approved legitimate
> accounts. The reject margin required bounds, not a point estimate.
>
> The output is an open-source logging schema, audit design, and policy-change
> memo mapped to BSP Circular 1170 (eKYC), BSP Circular 1213 (FMS calibration
> and independent audit), and AFASA. It is a measurement layer, not another
> fraud detector.

## 3. The 10-minute walkthrough

1. **The decision (1 min).** Approve / review / reject a new account. Two-sided
   cost: fraud loss vs false rejection/inclusion harm.
2. **The measurement problem (2 min).** Selection, delay, capacity, and the
   unobserved reject margin. Use one concrete example: the reviewed applicants
   are not a random sample.
3. **The evidence (1 min).** BSP 1213 requires calibration/audit but its 11 log
   fields contain no decision/score/outcome; BSP Project Sapiens names sampling
   and labelling bias; AFASA s.6 ties inadequate controls to restitution.
4. **The method (2 min).** Primary estimand `P0`, IPW/DR, audit-only, bounds;
   why the reject margin is not point-identified.
5. **The pilot (2 min).** Naive bias and rank flips; corrected estimator
   performance; audit value; outcome-dependent failure; bounds width.
6. **The artifact (1 min).** Schema, validator, audit designer, memo, benchmark.
7. **The limits (1 min).** Simulation, BAF, assumed costs, oracle propensities,
   no PH data, no causal deployment claim.

## 4. Five hard questions

**Q1. Why not just optimize AUPRC/F1?**
A: The decision is cost-sensitive and capacity-constrained. AUPRC ignores the
false-reject cost, the review cost, and the review capacity. It also evaluates on
the selected labels, which is the bias the project studies.

**Q2. How is this different from reject inference?**
A: Reject inference is the closest analogue, but it is credit scoring, usually
without delayed labels, capacity-constrained review, or an audit design. The
project borrows the missing-data framing and tests it on account-opening fraud
with a public benchmark and a practical memo.

**Q3. Why not run a randomized experiment?**
A: A random approval of would-be-rejected applicants deliberately onboards
fraud; a random rejection excludes legitimate customers. A random post-hoc
verification of approved applications is the defensible audit. The project
designs that audit and quantifies what it buys.

**Q4. What would you deploy, and at what threshold?**
A: I would not deploy a point estimate from logs alone. I would deploy the
logging schema and the audit first; then use the memo to support a policy change
only if the overlap/ESS and the bounds support it. The threshold is a
cost-sensitive argmin, not a generic 0.5.

**Q5. What is the biggest weakness?**
A: The pilot's observation mechanism is simulated and the propensities are
oracle-known. A real bank's labels are outcome-dependent and its propensities are
estimated. The next step is a propensity-estimation and sensitivity study, plus
a bank partner for real logs. The corrected ranking is also good but not perfect:
DR selects the true best policy 72% of the time, with the residual instability
concentrated in the close better-model/incumbent gap. And the reject margin is
bounded, not point-identified; the incumbent's narrow interval covers the true
full value only 35% of the time. The project is explicit about all three.

## 5. What not to claim

- Do not claim production, GCash data, or a real bank deployment.
- Do not claim a causal deployment effect.
- Do not claim a point-identified full-population value.
- Do not claim a new fraud detector or a new OPE estimator.
- Do not claim the 1% audit detects small fraud-rate differences; it does not.
- Do not claim BSP mandates explainable AI; BSP's AI principles are voluntary,
  and the binding explainability/fairness duties come from the NPC.
- Do not claim BSP 1213 is a model-risk-management circular; it is an FMS
  circular, and the MRM guidelines are a draft.

## 6. Portfolio framing

**Title:** *Who Gets Onboarded? Audit-Ready Evaluation of Account-Opening Fraud
Policies under Selective and Delayed Labels.*

**One-line GitHub description:** An open-source measurement layer for
account-opening fraud policies: logging schema, selection/delay-aware
estimators, audit design, and an audit-ready policy-change memo.

**What a reviewer should remember:**
1. The problem is real and regulator-relevant.
2. The method is honest about what is identified and what is not.
3. The artifact is usable: schema, validator, pilot, memo.
4. The research is reproducible: pre-registration, tests, benchmark, claim ledger.
5. The person understands fintech operations, not just ML.
