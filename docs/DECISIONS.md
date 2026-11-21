# Decision Journal

**Status:** Canonical decision journal for v0.2.1 (2026-11-20).

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

**Result (2026-11-20):** The gate is met for **DR**, not for IPW.
- Estimated e: DR max **2.67%**, coverage **91.0%**; IPW max **11.19%**,
  coverage **73.0%**.
- Noise sigma 0.25: DR **1.58% / 96.5%**; IPW **7.01% / 93.5%**.
- Outcome-dependent labels with estimated e: audit-only **2.58% / 82.5%**;
  IPW **1350.8%**; DR **1627.9%**.

**Decision update:** The paper claims DR robustness, not IPW robustness. The tool
recommends DR when e is estimated, and audit-only when the label-source mix
suggests outcome-dependent observation.

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
  With delay 45: IPW **51.72% / 21.5%**; DR **17.59% / 80.0%**.
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
