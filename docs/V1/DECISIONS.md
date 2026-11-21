# V1 Technical Decisions

**Status:** Planning, 2026-11-21.
**Purpose:** Record the six decisions that define V1. Each entry states the
options, the decision, the reasoning, the expected outcome, the assumptions, the
review date, and the kill criteria.

The canonical project journal is [`../DECISIONS.md`](../DECISIONS.md); these V1
decisions extend it for the v1.0.0 release.

---

## D15 — V1 is a credibility release, not a feature release

**Date:** 2026-11-21.
**Status:** Accepted.

**Options:**
1. Add estimators, scenarios, FiFAR, or a transaction extension.
2. Fix the credibility gaps: conditional claim, bounds F5, report gate,
   reproducible pipeline, review package.
3. Pause the project and wait for a bank partner.

**Decision:** Option 2. V1 freezes the method set and spends the release on
credibility, safety, and packaging.

**Why:**
- The red-team review found six credibility gaps; more features would not close
  them.
- A risk team adopts a tool it can audit, not another estimator.
- The project already has enough methods for a pilot.
- The time budget is six weeks; adding features would crowd out the evidence.

**Expected outcome:** A Level 2 review-ready release by 2026-12-31.

**Assumptions:** 65–75 hours available; no new partner; public/synthetic data
only.

**Review date:** 2026-12-05.
**Kill criteria:** If the credibility work cannot be completed by Dec 5, cut
scope to the validation report, model card, pilot protocol, and report gate.

---

## D16 — The headline claim becomes conditional on the observation sweep

**Date:** 2026-11-21.
**Status:** Accepted.

**Options:**
1. Keep the single-scenario headline (+111.6% to +278.5%).
2. Report the bias as a function of plausible observation rates.
3. Drop the bias claim entirely.

**Decision:** Option 2. The V1 claim is conditional: the naive estimate is biased
and can reverse the ranking under a range of plausible observation rates; the
sweep reports where it holds and where it collapses.

**Why:**
- The current headline is set by two hand-set parameters (`e_approve=0.05`,
  `kappa_review=0.90`) and a 2% review band.
- A hostile reviewer will ask whether the bias survives plausible changes.
- A conditional claim is smaller but survives review; a universal claim does
  not.

**Expected outcome:** A 12-cell sweep with naive bias, DR/IPW/audit-only bias,
coverage, rank inversion, and P(select true best). The claim is updated to the
measured conditions.

**Assumptions:** The sweep is feasible in ~30 minutes; the BAF frame is fixed;
the cost matrix is unchanged.

**Review date:** 2026-11-24.
**Kill criteria:** If the bias collapses at plausible rates, the headline becomes
"the naive estimate is biased only under low approve-label rates"; the tool's
value shifts to the correction and the gate.

---

## D17 — The report gate is mandatory

**Date:** 2026-11-21.
**Status:** Accepted.

**Options:**
1. Keep the current report behavior and add a warning.
2. Refuse to print a point estimate when identification fails.
3. Print the point estimate but label it "not identified."

**Decision:** Option 2 for positivity and cost-support failures; option 3 for
overlap, ESS, and small-sample warnings. The memo must never print "Measured"
when the estimate is unidentified.

**Why:**
- The current report can print "Measured" on a 20-row log with a negative-cost
  CI.
- This is the project's own strongest counter-case: "a confident-looking memo
  that is not identified."
- A risk team needs the tool to say "no" clearly.

**Expected outcome:** A gate with reasons and metrics; five adversarial logs
refused or flagged; no "Measured" on unidentified logs.

**Assumptions:** The gate thresholds are configurable; the memo can print a
diagnostic without a point estimate.

**Review date:** 2026-12-05.
**Kill criteria:** If the gate is too strict for legitimate small logs, relax the
warning thresholds but keep the positivity and cost-support refusal.

---

## D18 — F5 is recorded as pass/fail; bounds are partial identification

**Date:** 2026-11-21.
**Status:** Accepted.

**Options:**
1. Keep the current bounds and call the 34% coverage "a diagnostic."
2. Record F5 pass/fail explicitly and drop the coverage claim if it fails.
3. Replace the bounds with a different construction.

**Decision:** Option 2. Record F5 for every policy; compute the unconditional
interval and its own F5. If the narrow F5 fails, report the narrow interval as a
partial-identification range and describe the widened interval as a conservative
95% interval only where its own F5 passes.

**Why:**
- The pre-registered F5 criterion is ≥90%; the reported coverage is 35–85%.
- Reinterpreting a failed pre-registered test is the fastest hostile-reviewer
  dismissal.
- A recorded failure is more credible than a renamed success.

**Expected outcome:** `F5_pass` and `F5_coverage` in `pilot.json`; explicit
language in `RESULTS.md` and `CLAIMS.md`; no "95% CI" for the narrow interval.

**Assumptions:** The F5 computation is correct; the unconditional interval is a
useful diagnostic; the bounds remain decision-relevant even if F5 fails.

**Review date:** 2026-11-28.
**Kill criteria:** If F5 cannot be computed reliably, remove the coverage metric
and report only the interval width and the reject share.

---

## D19 — Include the benchmark pipeline or narrow the Level 1 claim

**Date:** 2026-11-21.
**Status:** Accepted.

**Options:**
1. Add `scripts/prepare_baf.py` and reproduce the scores.
2. Keep the scores as a local artifact and narrow the Level 1 claim.
3. Replace the scores with a public, pre-trained model.

**Decision:** Option 1 if the pipeline can be reproduced within the time budget;
otherwise option 2 with an explicit gap statement and a data hash.

**Why:**
- The headline ranking depends on scores that are not in the repository.
- A hostile reviewer cannot rule out leakage.
- A reproducible pipeline is a core Level 1 requirement.

**Expected outcome:** A script, a provenance file, score hashes, and a leakage
test; or a narrowed claim that says "the scores are not reproducible from this
repository."

**Assumptions:** The public BAF data is available; the original split is known;
the LightGBM dependency is acceptable.

**Review date:** 2026-12-05.
**Kill criteria:** If the pipeline cannot be reproduced by Dec 5, narrow the
claim and publish the gap; do not claim full reproducibility.

---

## D20 — V1 targets Level 2, not Level 3

**Date:** 2026-11-21.
**Status:** Accepted.

**Options:**
1. Chase a real bank pilot in 2026.
2. Build the Level 2 review package and defer the pilot to V1.1/V2.
3. Drop the project.

**Decision:** Option 2. V1 is review-ready; the pilot is V1.1/V2.

**Why:**
- No partner, DSA, legal review, or named business owner exists.
- A six-week pilot push is a low-probability bet that would crowd out the
  package.
- A review-ready package is the enabling asset for a 2027 pilot.

**Expected outcome:** A Level 2 package by Dec 31; reviewer packet; two external
readers; a January pilot plan.

**Assumptions:** The package can be built in six weeks; reviewers can be found
in December; the public/synthetic path is acceptable for V1.

**Review date:** 2026-12-15.
**Kill criteria:** If a warm partner appears, shift 30–40% of time to a scoped
pilot, but keep the package. If no reviewer by Dec 15, use the red-team + one
peer and plan January.

---

## Decision summary

| ID | Decision | Review | Kill criterion |
|---|---|---|---|
| D15 | Credibility release, not features | Dec 5 | Cut scope if not frozen |
| D16 | Conditional bias claim | Nov 24 | Narrow to low-label-rate regime |
| D17 | Mandatory report gate | Dec 5 | Relax warnings, keep refusals |
| D18 | Record F5; bounds are partial ID | Nov 28 | Drop coverage metric if unreliable |
| D19 | Reproducible pipeline or narrow claim | Dec 5 | Publish gap; no full repro claim |
| D20 | Level 2, not Level 3 | Dec 15 | Shift to pilot only with a warm partner |
