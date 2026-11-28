# Decision Journal

**Status:** Canonical decision journal for v1.0.0 (2026-11-22; updated 2026-11-26).

**Rule:** Record material, hard-to-reverse decisions with options, expected
outcome, assumptions, review date, and kill criteria.

---

## D1 — Adopt account-opening as the decision unit

**Date:** 2026-11-19.
**Status:** Accepted.

**Options considered:**
1. Continue transaction approve/review/block on BAF.
2. Switch to a transaction dataset (IEEE-CIS/PaySim) for transaction triage.
3. Reframe to account-opening approve/review/reject on BAF.
4. Scam/APP intervention evaluation.

**Decision:** Option 3, with the transaction-triage and scam-intervention
framings kept as fallbacks/extensions.

**Why:**
- BAF is one million **account-opening applications**, not transaction data.
  Option 1 has a fatal domain mismatch.
- Option 2 is feasible but less locally distinctive and requires a new pipeline.
- Option 4 has the strongest problem evidence but no public intervention logs;
  it would be a simulation/design study.
- Option 3 matches the data, the decision, the label structure, and the
  regulatory hooks (BSP 1170 eKYC, BSP 1213 FMS, AFASA). It also preserves the
  V1/V2 cost-sensitive and capacity work.

**Expected outcome:** A defensible pilot showing naive bias/rank flips and at
least one honest correction or bound on BAF, plus a usable logging/audit
protocol.

**Assumptions:** BAF's account-opening labels are a reasonable proxy for
account-opening fraud; the cost matrix can be normalized and sensitivity-tested;
the reject margin will require bounds.

**Review date:** 2026-12-15 (after the pilot).
**Kill criteria:** The pilot shows negligible bias and no rank flips; the
account-opening reframing cannot be defended; or a bank partner provides
transaction data that changes the ranking.

---

## D2 — Primary estimand is the logging non-rejected population

**Date:** 2026-11-19.
**Status:** Accepted.

**Options:**
1. Full-population policy value (including logging-rejected applicants).
2. Logging non-rejected population (`P0`) + full-population bounds.
3. Only the reviewed population.

**Decision:** Option 2.

**Why:**
- Rejected applicants have no outcome; a full-population point estimate is not
  identified from logs alone.
- `P0` is the population the institution would still consider; it answers the
  practical decision and has positivity.
- Bounds preserve the full-population question without pretending to identify
  it.
- Option 3 is too narrow; it ignores the approved margin and the audit.

**Expected outcome:** An identified estimate for `P0` and an honest bounds
interval for the full population.

**Assumptions:** Positivity holds in `P0` (review and approve channels have
positive probability); the label channels are correctly specified for the
primary scenario.

**Review date:** 2026-12-15.
**Pilot update (2026-11-19):** The `P0` estimate is identified and the corrected
estimators recover it (DR max |relative bias| 0.94%, mean coverage 96.0%). The
reject-margin bounds are not confidence intervals: the incumbent's narrow
interval covers the true full value in only 34% of replications. The `P0`
decision stands, with the bounds caveat recorded in D8.
**Kill criteria:** The bounds are so wide that no decision is possible; or the
`P0` estimand is not the decision the buyer cares about.

---

## D3 — Audit design: post-hoc verification and shadow scoring, not random approvals/rejections

**Date:** 2026-11-19.
**Status:** Accepted, subject to legal/risk review.

**Options:**
1. Randomly approve a sample of would-be-rejected applicants.
2. Randomly reject a sample of would-be-approved applicants.
3. Randomly verify a sample of approved applications after approval.
4. Shadow-score a challenger policy without changing decisions.

**Decision:** Options 3 and 4; reject 1 and 2.

**Why:**
- Option 1 deliberately onboards fraud/mule accounts; it conflicts with eKYC and
  AFASA duties and the institution's risk appetite.
- Option 2 deliberately excludes legitimate customers; it creates inclusion harm
  and complaints.
- Option 3 yields unbiased labels for the approved population without changing
  the decision.
- Option 4 yields overlap/coverage diagnostics with no customer impact.

**Expected outcome:** A defensible audit arm that improves the approved-margin
estimate; the reject margin remains bounded.

**Assumptions:** Post-hoc verification is operationally feasible and legally
permissible; the verification outcome is a valid fraud proxy; the audit sample
is random within the approved population.

**Review date:** Before any external pilot with a bank partner.
**Kill criteria:** Legal/risk review rejects post-hoc verification; or the audit
sample cannot be made random/representative.

---

## D4 — Cost matrix is a normalized assumption

**Date:** 2026-11-19.
**Status:** Accepted.

**Decision:** Use the V2 normalized cost values for comparability:
`fraud_loss_rate=0.0019187869` (amount-scaled), `review_cost=0.02`,
`false_reject_cost=0.10`, `residual_fraud_loss=0.30`. Sweep the false-reject
cost (0.02, 0.10, 0.50).

**Derivation of `fraud_loss_rate`:** it is the normalizer
`1 / mean(amount_proxy on the training window)` =
`1 / 521.1626` = `0.0019187869`. It makes the mean fraud loss equal to one
normalized cost unit on the training window. It is computed on months 0–2 only;
the test window is not used. It is not a peso loss-given-fraud estimate and it is
not tuned to the evaluation result.

**Why:** The project needs a common cost unit to compare policies; the V2 values
are already documented and sensitivity-tested. They are not production
estimates.

**Expected outcome:** Policy rankings and bias results are reported as
cost-model-conditional; the false-reject sweep shows the inclusion trade-off.

**Assumptions:** The normalized values preserve the qualitative cost ordering;
the credit-line proxy is a reasonable exposure measure.

**Review date:** After the pilot; before any external claim.
**Kill criteria:** A bank-provided cost study shows the qualitative ordering is
different; or the results are driven entirely by the cost assumption.

---

## D5 — BAF primary, FiFAR follow-on

**Date:** 2026-11-19.
**Status:** Accepted.

**Decision:** Use BAF as the primary account-opening benchmark. Add FiFAR's 50
synthetic analysts and 30K alerts as the capacity layer in a follow-on, not in
the first pilot.

**Why:** BAF matches the decision; FiFAR adds the review-capacity/analyst
heterogeneity layer but is a derived synthetic dataset. The first pilot should
test the selective-label premise before adding analyst complexity.

**Expected outcome:** A clean BAF pilot; a FiFAR capacity study if the premise
holds.

**Assumptions:** FiFAR remains available and its synthetic analysts are a
reasonable capacity abstraction, not a claim about real analyst behavior.

**Review date:** 2026-12-31.
**Kill criteria:** The BAF pilot fails its premise; or FiFAR is unavailable.

---

## D6 — Archive V2.1.0 and start a new repository

**Date:** 2026-11-19.
**Status:** Accepted and executed.

**Decision:** Tag the old repository `v2.1.0` (already present), add
`ARCHIVE.md`, commit the evidence and superseded V3 artifacts, and start
`D:\onboarding-audit` as the new flagship.

**Why:** Preserve the origin, avoid rewriting V1/V2, and give the new project a
clean public surface.

**Expected outcome:** The old repo is an auditable origin; the new repo is the
flagship.

**Review date:** At public release.
**Kill criteria:** None; this is reversible by reverting the commit.

---

## D7 — H2 is naive-only; H3 is IPW/DR-only

**Date:** 2026-11-19.
**Status:** Accepted before the final pilot verdict.

**Options:**
1. Let H2 use the maximum inversion across all estimators.
2. Let H3 include audit-only, whose target is the approved population.
3. Define H2 on the naive estimator only, and H3 on the `P0` estimators
   (IPW/DR), with audit-only reported separately.

**Decision:** Option 3.

**Why:**
- H2 is a claim about the **naive** estimate; using the maximum across corrected
  estimators would let estimator noise satisfy a hypothesis about naive
  evaluation.
- Audit-only targets the **approved population**, not `P0`. Mixing it into H3
  would compare an approved-population estimate against a `P0` truth.
- The fixed definitions are stricter and easier to defend.

**Expected outcome:** H2 = 1.00 naive inversion; H3 = DR max |relative bias|
0.94%, mean coverage 96.0%; IPW 1.18%/95.0%.

**Assumptions:** The `P0` estimand is the decision-relevant one; audit-only is a
separate approved-margin diagnostic.

**Review date:** 2027-01-15 (with the paper draft).
**Kill criteria:** A reviewer shows the H2/H3 definitions are inconsistent with
the pre-registration; then report both versions and explain the change.

---

## D8 — Bounds are partial-identification intervals, not confidence intervals

**Date:** 2026-11-19.
**Status:** Accepted after the pilot.

**Options:**
1. Report the full-population bounds as a 95% interval.
2. Report them as partial-identification intervals conditional on the `P0`
   estimate, with coverage as a diagnostic.
3. Do not report full-population bounds; report only `P0`.

**Decision:** Option 2.

**Why:**
- The bounds combine the `P0` estimate with the min/max cost of the unobserved
  rejected rows. They are not sampling intervals for the full-population value.
- The pilot shows the incumbent's narrow interval covers the true full value in
  only 34% of replications. Calling it a 95% CI would be false.
- Option 3 would hide the reject-margin problem.

**Expected outcome:** The memo reports the interval, its width, and the
assumption; it says "partial identification" and does not claim 95% coverage.

**Assumptions:** The cost model is correct enough to bound the rejected rows;
the `P0` estimate is the identified part.

**Review date:** 2027-01-15.
**Kill criteria:** A reviewer proposes a valid confidence-interval construction
for the full-population value under weaker assumptions; then adopt it and
compare.

---

## D9 — Arbitrary-log report uses action-level propensities when absent

**Date:** 2026-11-20.
**Status:** Accepted.

**Options:**
1. Require a per-row propensity column and refuse to run without it.
2. Estimate action-level propensities from the log and run with a warning.
3. Estimate a covariate-conditional propensity model.

**Decision:** Option 2 for v0.2; option 3 is a follow-on.

**Why:**
- Most real logs do not have a per-row observation propensity; requiring one
  would make the tool unusable on the logs teams actually have.
- The action-level estimate is the minimum viable correction:
  `e_review = observed/reviewed`, and
  `e_approve = audit_rate + (1-audit_rate) * observed/(approved, not audited)`.
- The tool reports the propensity source, the observed e range, the ESS, and a
  positivity failure. It never hides that the propensities are estimated.
- A covariate propensity model is the right v0.3 extension, but it needs enough
  audit labels per cell and a model-validation step.

**Expected outcome:** The report runs on a log without propensities, but the
memo labels the source as `estimated` and reports the sensitivity band.

**Assumptions:** The observation mechanism is action-level in the main use case;
the audit is random within approved applications; the audit flag is present when
possible.

**Review date:** 2027-01-15.
**Kill criteria:** The action-level estimate produces materially different
decisions from a covariate model; then require the covariate model.

---

## D10 — The propensity sensitivity is a pre-declared claim gate

**Date:** 2026-11-20.
**Status:** Accepted.

**Decision:** The paper may claim that the correction works on the identified
population only if it survives (a) action-level estimated propensities in the
main scenario and (b) a moderate noise band. If it fails, the paper narrows to a
propensity-sensitivity diagnostic and bounds, not a point-estimate claim.

**Why:**
- The main pilot uses oracle propensities. That is a deliberate isolation, not a
  production assumption.
- A correction that only works with oracle propensities is not useful to a bank.
- The sensitivity is the cheapest test of external validity before the paper.

**Expected outcome:** Estimated propensities should be close to the oracle in
the main action-dependent scenario; noisy propensities should degrade gracefully;
the outcome-dependent scenario should break action-only weighting and favor
audit-only.

**Assumptions:** The estimated e is action-level; the noise is a stress test,
not a calibrated error model.

**Result (2026-11-20; corrected 2026-11-21):** The gate is met for both **DR**
and **IPW** after the `e_approve` correction.
- Estimated e: DR mean **1.43%**, coverage **93.5%**; IPW **2.92%**, **92.0%**.
  The old 2.67% / 11.19% values came from an `e_approve` formula that omitted
  the resolution factor on the audit channel.
- Noise sigma 0.25: DR **1.58% / 96.5%**; IPW **7.01% / 93.0%**.
- Outcome-dependent labels with estimated e: audit-only **2.58% / 82.5%**;
  IPW **2064.9%**; DR **1737.0%**.

**Decision update:** The paper claims DR is more robust under noise and
covariate-dependent observation, not that IPW fails under action-level
estimation. The tool recommends DR when `e` is noisy or covariate-dependent,
and audit-only when the label-source mix suggests outcome-dependent observation.

**Review date:** 2027-01-15.
**Kill criteria:** The correction fails under estimated e in the main scenario;
then the claim narrows to bounds/diagnostic and the tool recommends an audit
before a point estimate.

---

## D11 — Covariate propensity model when observation depends on the application

**Date:** 2026-11-20.
**Status:** Accepted.

**Options:**
1. Keep action-level `e` and report the covariate-dependent case as an open
   threat.
2. Add a per-action logistic `P(observed | action, X)` with cross-fitting, and
   compare it with action-level and oracle propensities in a pre-declared
   scenario.
3. Build a fully nonparametric propensity model.

**Decision:** Option 2 for v0.2.1; option 3 is not justified at this sample size.

**Why:**
- The action-level sensitivity answers "what if `e` is estimated?" but not "what
  if `e` depends on the application?"
- A real log's observation rate plausibly depends on amount, product, or
  segment. If so, action-level IPW is misspecified even with a large sample.
- The covariate model is the minimum credible correction: it uses the same
  pre-decision features as the outcome model, is cross-fitted, and reports the
  feature list and weight diagnostics.
- DR already includes the covariates in the outcome model, so it may be
  partially robust. The experiment tests whether that is enough.

**Expected outcome:** Action-level IPW fails; the covariate model recovers most
of the oracle; DR is more robust than IPW but not necessarily within 5%.

**Assumptions:** The observation mechanism is a function of observed,
pre-decision features; the audit is random; the logistic form is an
approximation; the features are available at decision time.

**Result (2026-11-20):** The gate is met by the covariate model, not by
action-level weighting.
- Action-level: IPW **67.52% / 1.5%** coverage; DR **21.25% / 72.5%** (delay 0.5).
  With delay 45: IPW **64.27% / 10.0%**; DR **20.27% / 79.0%**.
- Covariate model: IPW **1.97% / 91.5%**; DR **2.48% / 89.5%** (delay 0.5).
  With delay 45: IPW **3.35% / 90.5%**; DR **3.68% / 89.5%**.
- Oracle: IPW **3.01% / 90.0%**; DR **2.63% / 89.0%**.

**Decision update:** The report supports `--propensity-model covariate`; the
paper claims covariate-model robustness under covariate-dependent observation,
not action-level DR robustness. The report exposes the
observation-rate-by-amount-quintile diagnostic so a team can decide which model
to use. Heavy weights still undercover (89–91.5% vs 95%); a bootstrap interval is
the v0.3 extension.

**Review date:** 2027-01-15.
**Kill criteria:** The covariate model does not improve on action-level `e`, or
its weights are so heavy that the interval is uninformative; then the tool
reports bounds/diagnostics and recommends an audit, not a point estimate.

---

## D12 — Documentation is the source of truth; the paper is a rendering

**Date:** 2026-11-20.
**Status:** Accepted.

**Options:**
1. Start the paper draft first and fill the documentation later.
2. Freeze the canonical documentation first, then write the paper from it.
3. Keep a single long document and split it at submission time.

**Decision:** Option 2. The canonical documentation is finalized before the
paper draft. The paper is a rendering of `METHODS.md`, `RESULTS.md`,
`CLAIMS.md`, `THREATS.md`, and `RELATED_WORK.md`, not a separate source of truth.

**Why:**
- The project has measured results, a claim ledger, a decision journal, and a
  validity register. Writing the paper first would re-derive or, worse,
  contradict them.
- A paper is a snapshot; the documentation is the durable artifact. A reader
  should be able to reproduce and audit the work without reading the paper.
- The user's priority is a complete documentation foundation, not a premature
  PDF.
- A clear precedence rule prevents the README, one-pager, and paper from
  drifting into different claims.

**Artifacts:**
- `docs/README.md` — map, status, precedence, update rules.
- `docs/METHODS.md`, `docs/RESULTS.md`, `docs/CLAIMS.md`, `docs/THREATS.md`,
  `docs/RELATED_WORK.md` — the canonical research set.
- `docs/REPRODUCIBILITY.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md` — the
  technical set.
- `docs/PUBLICATION_CHECKLIST.md`, `docs/FAQ.md`, `docs/OPEN_QUESTIONS.md` — the
  release and question set.
- `paper/README.md` — the paper workspace guide, explicitly not a draft.

**Expected outcome:** A new collaborator can start from `docs/README.md`, trace
every number to a committed artifact, and draft the paper without re-running the
analysis or inventing a claim.

**Assumptions:** The measured results are stable enough to document; the
covariate 50-replication run is the last measurement before the freeze.

**Review date:** 2027-01-15, or when the paper draft starts.
**Kill criteria:** A documentation change forces a new measurement or a headline
change; then update the claim ledger and the pre-registration first, and delay
the freeze.

---

## D13 — Prioritize a real-log pilot and external validation over more methods

**Date:** 2026-11-20.
**Status:** Accepted.

**Options:**
1. Add more estimators, scenarios, and simulation depth.
2. Build the Level 2 review package (validation report, model card, pilot
   protocol, business case) and pursue a real-log pilot in parallel.
3. Wait for a bank partner before building anything else.

**Decision:** Option 2. Freeze the method set; build the review package; pursue a
historical-log pilot or a public real-action fallback. Do not add another
estimator or simulation scenario before the pilot.

**Why:**
- The binding constraint is access to a real log and a risk-team sponsor, not
  code.
- A hostile reviewer can dismiss another simulation; a pre-registered real-log
  pilot with external review is a much larger likelihood ratio.
- The project already has enough methods, tests, and scenarios for a pilot
  (47 tests; 22 configured scenarios; 11 sensitivity scenarios).
- Adding features now is optimizing a non-bottleneck.

**Expected outcome:** A review-ready package in 4 weeks; two external readers in
8 weeks; a historical-log pilot or a public real-action case study in 12 weeks.

**Assumptions:** A partner can be found; the log has the required fields;
legal/privacy can approve a read-only sandbox; the cost matrix can be elicited.

**Review date:** 2026-12-15.
**Kill criteria:** No partner by 2027-01-15, or the log lacks the required
fields, or the risk team finds the assumptions untenable; then narrow to a
public real-action case study and a methodological paper, and do not claim a
pilot.

---

## D14 — The November–December 2026 move is the Level 2 package plus an outreach probe

**Date:** 2026-11-20.
**Status:** Accepted.

**Options:**
- A. Do nothing / maintain.
- B. Research polish only.
- C. Level 2 package + outreach probe.
- C+. Convex barbell: C plus a public real-action fallback and 20% pilot
  scouting.
- D. Full pilot push.
- E. Pivot / new project.
- F. Application package only.

**Decision:** C-seq, finish-first. Allocate 100% to the Level 2 package until
2026-12-05; prepare a reviewer shortlist in late November; run the reviewer
search 2026-12-08 to 2026-12-23; 0% to new methods.

**Why:**
- The binding constraint is access to a real log and a risk-team reviewer, not
  code.
- C-seq is convex: the package is valuable in every state; the reviewer search
  is the December information purchase; the pilot is upside.
- C+ is marginally higher in the model, but it assumes parallel attention. The
  difference is within the subjective noise; the explicit focus constraint
  decides for C-seq.
- D is a high-variance bet on a low-probability partner; B has diminishing
  returns; A leaves the project at Level 1.

**Expected value (subjective):** C-seq **78.4** (net 71.9); C **79.7** (net
73.2); C+ **81.3** (net 73.8); D **60.4** (net 53.9); F **63.2** (net 60.2); B
**60.0** (net 55.0); A **50.0** (net 49.5). Sensitivity: C-seq is within about
two points of C+ across P(S3) 0.05–0.40. D only becomes competitive with a warm
partner.

**Assumptions:** 65–75 hours available over six weeks; 10–12 hours/week cap; no
warm partner at the start; public/synthetic data only until a DPA; the package
is reusable.

**Expected outcome:** Level 2 package frozen by 2026-12-05; reviewer packet sent
2026-12-08 to 2026-12-15; two reviewer calls by 2026-12-23; a pilot lead or a
public real-action fallback.

**Review dates:** 2026-12-05 (package freeze), 2026-12-15 (reviewer status), and
2026-12-31 (end-of-period).
**Kill criteria:** Package not frozen by 2026-12-05 → cut scope to the validation
report, model card, and pilot protocol. No reviewer call by 2026-12-15 → use the
red-team plus one strong peer, and plan January. Package work exceeds 75 hours
or GPA/applications/health slip → stop. A partner asks for PII/proprietary data
without a DPA/sandbox → decline. The risk team finds the assumptions untenable
→ narrow the claim to a methods paper; do not claim a pilot.

---

## D15 — V1.1 is a decision-reliability release, not a methods release

**Date:** 2026-11-26.
**Status:** Accepted for the full-policy check; positioning is proposed for
external review.

**Context:** The V1 strategic review (`STRATEGIC_REVIEW_v1.md`) found that the
`P0` recommendation can reverse once the unobserved reject margin is included.
The current memo prints a directional `P0` recommendation and a later
"full-policy: not identified" row; a reader can act on the first and miss the
second. The review also found that the release gate is open, the validation
report contradicted itself, and a "Measured" vendor claim had no artifact.

**Options:**
1. Keep the current framing; add more simulation evidence.
2. Reposition around decision reliability; add a full-policy difference bound and
   break-even; complete the external review before a public release.
3. Drop the reject margin from the product and sell only the `P0` estimate.

**Decision:** Option 2. The full-policy check is implemented in the working tree
(`full_policy_difference`, memo §4.1, tests). The public-release gate stays open
until two external readers (or a documented fallback) are recorded. No new
estimator or simulation scenario before that review.

**Why:**
- Option 1 optimizes the non-binding constraint (internal evidence) and leaves
  the decision-surface defect.
- Option 3 is narrower but abandons the buyer's actual question; the honest
  answer is to bound the full-policy difference, not to ignore it.
- The full-policy check is a small, testable extension of the existing cost
  model; it does not require a new estimator.
- The decision-reliability framing (point accuracy ≠ ranking; structural
  fragility; conditional audit value) is a stronger scientific contribution than
  the bias magnitude.

**Expected outcome:** A `v1.0.1`/`v1.1` release that states the `P0` estimate,
the full-policy bound, and the break-even; a memo that warns when the
recommendation does not survive the reject margin; an external review log with
two entries; a paper framed around decision reliability.

**Assumptions:** The common-fraud-rate break-even is a useful sensitivity, not a
claim; the external review can be obtained in December; the model-risk buyer is
the beachhead.

**Review date:** 2026-12-15.
**Kill criteria:** No external reader by 2026-12-15 → the public release slips
and the project stays at Level 2; the full-policy check reverses the flagship
case recommendation → rewrite the headline and case study; a reviewer finds a
false "Measured" claim → fix the ledger before any release.

---

## D16 — Project future: research artifact plus outreach probe, not a commercial push or paper submission now

**Date:** 2026-11-27.
**Status:** **Proposed; owner decision.**

**Decision:** Choose **B**: finish the project as a narrow research/portfolio
artifact and run a small external-outreach probe (5 asks, 2 reader calls, 1
real-log conversation). Do **not** push a commercial pilot (C), submit the paper
now (D), freeze (E), or pivot (F) unless the stop/upgrade conditions below are
met.

**Options considered:**
- A. Finish as a research artifact (40–60 h).
- B. A + small outreach probe (50–70 h).
- C. Commercial/model-risk pilot push (120–200 h).
- D. Submit paper now (10–20 h).
- E. Freeze/stop (5 h).
- F. Pivot to a new project (60–100 h).

**Why:**
- The binding constraint is external evidence, not code.
- B has the highest subjective expected value (81.6 vs A 76.4, C 59.7, D 59.5,
  E 58.0, F 51.1) **and** bounded downside.
- B buys the cheapest option on the fat-tailed external outcome (one reader or
  one real-log lead can change the trajectory).
- C risks absorbing barriers (health/GPA, PII/legal, application window) for a
  0.20 partner probability; the expected gain does not justify the tail.
- D has a high rejection probability and a repeated reputational drawdown after
  the v1.0.1 false-claim near-miss.
- A is safe but leaves the binding constraint unaddressed; E/F are fallbacks,
  not first choices.

**Expected outcome:** A trimmed/repositioned paper or technical report, a
holdout/ablation result, 2 reader calls or 1 real-log lead, an updated audit log,
and a clear go/no-go on a 2027 pilot.

**Assumptions:** 10–12 h/week cap; no warm partner at the start; no PII without a
DPA/sandbox; the external review can be obtained in December–January.

**Review dates:** 2026-12-15 (paper/trim/outreach), 2027-01-15 (reader/lead),
2027-02-15 (end-of-period).

**Kill/upgrade criteria:** No reader/lead by 2027-01-15 → freeze outreach. Paper
not trimmed by 2026-12-31 → do not submit. Health/GPA/applications slip → stop.
PII request without DPA → decline. Holdout baseline collapses the effect →
narrow the claim. Upgrade to C only with a warm partner, a log, a DPA/sandbox,
legal/ops review, an agreed cost matrix, and a respected time cap. Upgrade to D
only after a reader says the paper is competitive and it is venue-trimmed.

---

## D17 — Decision Reliability Profile is the product spine

**Date:** 2026-11-28.
**Status:** Implemented; shipped in the `v1.1.0` pre-release. No external validation.

**Context:** The project already had an identification gate, a `P0`/reject-margin
split, a full-policy break-even, and a decision layer. Those are reliability
ingredients but not a reliability product: the memo still led with a point
estimate and treated stability, calibration, and cost stress as separate
diagnostics.

**Options:**
1. Keep the existing gate + decision layer; add no new reliability metrics.
2. Add more estimators or scenarios.
3. Make decision reliability the product spine: a profile with identification,
   bootstrap decision stability, calibration, cost-stress stability, structural
   reject-margin reliability, operational readiness, and an explicit A–D grade.

**Decision:** Option 3. Add `reliability.py`, integrate it into `report.py` and
the memo (§4.2), and make the README/docs describe the specialization. No new
estimators or simulation scenarios.

**Why:**
- The specialization is Decision Reliability for Financial ML; the product
  should measure the reliability of the decision, not just the estimate.
- The existing assets (gate, full-policy check, action-weighted/holdout
  baselines) are the foundation; the profile unifies them.
- The new metrics are testable and reproducible: bootstrap stability,
  Brier/ECE, observed/expected, cost-stress share, grade rules.
- Adding more estimators would optimize a non-bottleneck.

**Expected outcome:** A memo that a risk team can read as a decision-reliability
report: grade first, dimensions second, point estimate conditional. The profile
refuses to call a decision A when the gate, stability, calibration, cost stress,
or structural dimension is weak.

**Assumptions:** The grade thresholds are conventions; the bootstrap fixes
nuisance models; calibration is observed-label only; the cost grid is local.

**Review date:** 2026-12-15.
**Kill criteria:** The profile is decorative (always A/B, never C/D) → tighten
thresholds or remove the grade. The bootstrap is too slow for a 100k log →
optimize or reduce `n_boot`. A risk team finds the grade misleading → rename it
to a profile and drop the letter grade.

## D18 — Publish v1.1.0 as a pre-release, not a validated 1.0

**Date:** 2026-11-28.
**Status:** Accepted; owner decision. Public-release gate remains **not met**.

**Context:** The Decision Reliability Profile is implemented and tested, and the
paper is refocused. Two external readers have not reviewed the package. The
choice is to hold the artifact, tag it as a pre-release, or call it a public 1.0.

**Options:**
1. Hold all tags until two external readers finish.
2. Tag `v1.1.0` as a pre-release and keep the gate open.
3. Publish as `1.0` and treat the tag as validation.

**Decision:** Option 2.

**Why:**
- Reviewers need a stable commit to inspect; an untagged `main` moves.
- The release notes, README, and `RELEASE_STATUS.md` state that the gate is
  waived, not met, so the tag cannot be mistaken for external validation.
- Option 3 would repeat the overclaim the audit removed.

**Expected outcome:** A frozen Decision Reliability artifact with an explicit
open gate; no claim of production or external validation.

**Assumptions:** The owner accepts the reputational cost of another pre-1.0 tag.
The reliability audit is post-hoc and small.

**Review date:** 2026-12-15.
**Kill criteria:** A reviewer finds the profile misleading, the audit
irreproducible, or the paper's reliability claims unsupported → deprecate the
tag, issue a corrective release, and record the finding in `CLAIMS.md` and
`EXTERNAL_REVIEW.md`.

## D19 — Use BAF only for non-commercial research; no raw redistribution

**Date:** 2026-11-28.
**Status:** Proposed; use is blocked pending the gates in `DATA_USE_PLAN.md`.
Not a legal opinion.

**Context:** The BAF suite is the project's primary public benchmark. The Kaggle
metadata states **CC BY-NC-SA 4.0**; the Feedzai repository code is Apache-2.0
with a separate commercial-use contact. The dataset is synthetic and
privacy-preserving, but it is not a real bank log and the license is
non-commercial.

**Options:**
1. Treat “public” as unrestricted and use BAF for any purpose.
2. Use BAF for non-commercial research, keep raw data local, cite the source,
   and obtain separate permission for commercial use.
3. Stop using BAF entirely.

**Decision:** Option 2.

**Rules:**
- Use BAF for non-commercial research only; do not assume “portfolio” or
  “internal evaluation” is non-commercial without counsel or permission.
- Do not redistribute raw BAF files; `data/` stays local.
- Publish aggregate results, code, and derived diagnostics, not applicant rows.
- Cite the BAF paper and Kaggle dataset; retain the license notice.
- Pin the Kaggle version and raw SHA before a public release.
- Call BAF **synthetic**; never a real bank log or external validation.
- A commercial pilot requires separate permission or licensed data.
- Do not run the BAF-suite audit until the protected-attribute conflict
  (`customer_age`, `employment_status`, `income`) in `DATA_USE_PLAN.md` §6.1 is
  resolved and recorded.

**Why:** It preserves the strongest public benchmark while avoiding the two
credibility failures: a license violation and a synthetic-to-real overclaim.

**Assumptions:** The Kaggle license metadata is authoritative for the dataset;
the code license does not relicense the data. This note is not legal advice.

**Review date:** 2026-12-15.
**Kill criteria:** The license changes, the raw version cannot be pinned, or a
commercial use is proposed without permission → stop and re-review before use.

## D20 — Hold the BAF suite after the restricted-feature failure

**Date:** 2026-11-28.
**Status:** Accepted. The BAF-suite audit is stopped.

**Context:** Removing `customer_age`, `employment_status`, and `income` from the
score features preserved the main point-estimate conclusions (DR max bias 1.33%,
coverage 92–95%, P(best) 60%), but the reliability audit failed: in
`frej_050`, **5 of 5 A/B releases were wrong**. The true candidate advantage was
about 0.53% of cost; the estimate put the candidate about 7% worse, and the
bootstrap, cost stress, and full-policy check all agreed with the wrong sign.

**Decision:** Do not run the BAF-suite audit as a success test. Do not claim the
profile is safe, and do not tune a threshold until the five failures disappear.
Redesign a materiality/bias guard, pre-register it, and test it on the restricted
feature set with the failures included.

**Why:** This is the project's central distinction: a stable, calibrated-looking
profile can still release a confident wrong decision when the effect is small and
the outcome model is biased.

**Kill criteria:** A proposed guard is evaluated only after seeing the audit
result; or the restricted failures are excluded; or the paper continues to claim
zero false certifications without qualification.

**Review date:** 2026-12-15.
