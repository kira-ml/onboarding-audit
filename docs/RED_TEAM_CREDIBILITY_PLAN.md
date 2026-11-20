# Red-Team Review — Credibility and Adoption Plan

**Status:** Open adversarial review, 2026-11-20. Findings are **unverified** and
must be triaged before changing claims. This is not a final judgment.
**Reviewer:** independent red-team subagent.
**Scope:** `docs/CREDIBILITY_PLAN.md`, `docs/CLAIMS.md`, `docs/THREATS.md`,
`docs/RESULTS.md`, `docs/METHODS.md`, `README.md`, `docs/ROADMAP.md`.
**Verdict from the reviewer:** FAIL on the current framing. The most likely
illusion is that the headline bias is manufactured by the observation-rate gap,
and the product defaults to the estimator the project itself shows to be biased.

---

## Steelman

The strongest version of the claim: a bank's ordinary backtest of an onboarding
policy is badly biased because the incumbent chooses which applications get
labels, approved labels arrive late and incompletely, and rejected applications
never get outcomes. A doubly robust estimator using the log's observation
propensities recovers the policy value on the non-rejected population, and a
small random post-hoc audit plus partial-identification bounds makes the
remaining reject margin honest. If true, a bank could evaluate a challenger
policy on its existing decision log, quantify the error in its current
champion–challenger process, and defend the result to model risk with a
documented observation model and audit design. The plan claims this is already a
strong research artifact and the remaining gap to a risk-team pilot is
packaging, access, and two external readers — not more analysis.

## Claim inventory

| Claim | Tier present | Tier required | Status |
|---|---|---|---|
| Naive evaluation is materially biased (+112–278%) | E2 simulation | E3 sweep or real log | Unverified as a general claim |
| DR recovers `P0` within 0.94% / 96% coverage | E2 with oracle `e` | E2 with estimated `e` + E3 real log | Partially supported |
| The audit is decisive under outcome-dependent labels | E2 simulation | E3 operational audit | Unverified operationally |
| Reject margin is not point-identified; bounds are honest | E2 / E0 | E2 with F5 passing | F5 reportedly failed |
| The tool is review-ready (Level 2) | E1 code + 20-row demo | E3 real log + external review | Not yet |
| A 90-day partner pilot is feasible | E0 assumption | E3 signed term sheet | Unverified |

---

## Finding 1 — Critical (blocker)

**Claim:** The headline bias (+111.6% to +278.5%) is a property of two hand-set
observation parameters (`e_approve=0.05`, `kappa_review=0.90`) and a 2% review
band that no scenario varies. The central premise may be an arithmetic identity
on a chosen simulation, not a measured fact about onboarding logs.

**Why it matters:** This is the premise for the risk team's interest, the first
line of the README, and the pilot's success metric. If the bias collapses when
the observation rates are plausible, the "material bias" story is not evidence
about a bank.

**Failure mechanism (reviewer's):** In the main scenario the logging policy
reviews 4,550 of 227,491 applications (2.0%) at `kappa_review=0.90`, but approves
219,344 (96.4%) at `e_approve=0.05` with a 45-day median delay. The observed
sample is 12,171 labels: 4,097 review (33.7%), 6,715 post-approval reports
(55.2%), 1,359 audit (11.2%). The review band is over-weighted ~17× relative to
its population share, and every review row carries a cost floor of 0.02
(0.02 + 0.30 for fraud), 2.4× the true `P0` value of 0.00845. The naive mean is
the mean of a sample that is one-third review-band rows with a cost floor, so it
must overstate cost; the exact +111–278% is set by the 0.05/0.90 ratio and the
review cost. The stated mechanism in `docs/RESULTS.md` — "approved fraud is more
likely to be labeled than approved legitimate accounts" — is false in the main
scenario: `draw_observation` uses an outcome-independent approve channel. That
mechanism exists only in the `outcome_dependent` scenario. No scenario varies
`e_approve`, `kappa_review`, `review_cost`, or the review capacity's effect on
the observed mix; the 11 sensitivity scenarios vary how `e` is known or
estimated, not its level. The 1,150 replications are 22 analyses of one fixed
frame under one seed with common random numbers, not independent evidence.

**Disconfirming test:** Add a one-factor sweep:
`e_approve ∈ {0.01, 0.05, 0.20, 0.50}` × `kappa_review ∈ {0.5, 0.9, 1.0}`,
50 reps, everything else fixed. Report naive relative bias and P(select true
best) for each cell. If the bias stays >50% and the flip persists, the claim
survives; if it falls below 5% once `e_approve ≥ 0.20` or `kappa_review ≤ 0.9`,
the headline is a parameter choice.

**Confidence:** high.

---

## Finding 2 — Critical (blocker)

**Claim:** The pre-registered F5 falsification control — "the full-population
interval contains `V_full` in ≥90% of reps" — failed for all four policies
(84%, 35%, 85%, 65%), and the documentation reinterprets the failure as "not a
CI" instead of recording a failed test.

**Why it matters:** This is the fastest hostile-reviewer dismissal: the project's
own pre-registered control failed and the failure was renamed. The bounds are not
decision-grade for a risk team.

**Failure mechanism (reviewer's):** `docs/PILOT_SPEC.md` sets the F5 pass
criterion at ≥90%; `reports/pilot.md` reports coverage of 84.0%, 35.0%, 85.0%,
65.0%. `docs/RESULTS.md` and `docs/DECISIONS.md` reframe 35% as "a diagnostic,"
but no document says "F5 failed." The interval is centered on the midpoint of the
min/max cost range while the true full value sits near the boundary, and the
`P0` estimate is noisy, so coverage is mechanically low. The pilot bounds use
`v_pop=ipw_ht`, while the product's `policy_bounds` uses DR, so the pilot and
the shipped tool use different constructions.

**Disconfirming test:** Add F1–F8 pass/fail to the `verdict` block in
`pilot.json` and `RESULTS.md`; compute the unconditional interval
`[L(v_pop - 1.96 se), U(v_pop + 1.96 se)]` for the incumbent; check coverage of
`V_full` over the 100 main reps. If it covers ≥90%, the failure was a
construction error; if not, no cheap construction fixes it without an
assumption on the reject margin.

**Confidence:** high.

---

## Finding 3 — Critical (blocker)

**Claim:** The shipped `report` path defaults to action-level propensities — the
estimator the project's own sensitivity shows fails (IPW 11.19% bias / 73%
coverage) — has no minimum-sample or positivity refusal gate, and its only demo
log pre-loads oracle propensities. A risk team's first run can produce a
"Measured" memo on an unidentified quantity.

**Why it matters:** This is the artifact a risk team will run first, and it is
the exact failure `docs/THREATS.md` names as the strongest counter-case: "a
confident-looking memo that is not identified."

**Failure mechanism (reviewer's):** `run_report` defaults to
`propensity_model="action"`. When the log has no `propensity` column,
`estimate_propensities` computes `e_review` and `e_approve` from the observed
rates in the same data. The closest pilot analogue, `propensity_estimated`, gives
IPW 11.19%/73.0% and DR 2.67%/91.0%. The demo log ships a `propensity` column
with simulated values 0.051/0.050/0.900, so the demo never exercises the
fallback. There is no minimum-n, ESS, max-weight, or cost-support gate. The
committed 20-row memo reports DR 1.534616 with a 95% CI of [-3.033335, 6.102568]
(negative costs are impossible), `audit_only` 0.000000 with SE 0 and CI [0,0],
and "`P0` policy value is estimated | Measured." It also recommends "113 labels
needed" from 11 approved rows. The positivity line is hardcoded to say "FAILED —
no point estimate" while the table still shows point estimates. The one
end-to-end test generates data with the assumed observation mechanism and
asserts DR beats naive, so it cannot catch this.

**Disconfirming test:** Drop the `propensity` column from
`examples/sample_log.csv` and run `onboarding-audit report`; then run it on a
2,500-row synthetic log with no propensity column and a 5% approve-label rate,
with a known true `P0`; compare the memo's point estimate and claim ledger to the
truth. If the tool refuses or flags and does not print "Measured" when the
estimate is unidentified, the finding is closed.

**Confidence:** high.

---

## Finding 4 — High (major; blocker for the Level 1 claim)

**Claim:** The two scores that determine the headline ranking and the 227k-row
frame are produced by a pipeline that is not in the repository, so the "better
model" premise and the Level 1 "reproducible" claim are unverifiable.

**Why it matters:** The headline is a ranking flip between `p_fraud` and
`p_fraud_lgbm`; if the candidate score was fit on months 5–6, or the advantage is
a split artifact, the flip is not evidence. A hostile reviewer cannot rule out
leakage; a risk team cannot validate the model it is being asked to prefer.

**Failure mechanism (reviewer's):** `data/scored_test.parquet` is gitignored.
`docs/DATA.md` and `docs/REPRODUCIBILITY.md` state that the V2 pipeline is not
part of the repository and `scripts/prepare_baf.py` is not included. The training
split (months 0–2) is asserted, not shown. The 18-vendor capability matrix cited
in `docs/CLAIMS.md` does not exist in the repo. `docs/RELATED_WORK.md` points the
full bibliography at a private path. `docs/PUBLICATION_CHECKLIST.md` requires
`REPRODUCIBILITY.md` to reproduce the headline from a clean checkout, which it
does not.

**Disconfirming test:** Commit `scripts/prepare_baf.py`, the exact month split,
and a hash of the score columns; retrain on months 0–2 and reproduce the scores
within tolerance; add a leakage test that refits the candidate on months 5–6 and
shows the ranking flip disappears or reverses.

**Confidence:** high.

---

## Finding 5 — High (major; blocker for Level 3)

**Claim:** The Level 3 target and 90-day pilot schedule are infeasible without a
bank partner, the "public real-action dataset" fallback does not exist, and 7 of
the 10 checklist items require an institution to sign.

**Why it matters:** The plan's stated goal is Level 3 by Summer 2027, and its
weeks 5–8 acceptance criterion is "a real log, a real reviewer, a real memo." If
no partner exists, the target is unreachable and the acceptance criteria are
hopes, not tests.

**Failure mechanism (reviewer's):** No partner, DSA, legal review, or named
business owner exists; the plan admits no risk team has been interviewed. The
weeks 5–8 pilot is scheduled before the plan's own partner kill-criterion. The
fallback datasets named in the repo are synthetic or transaction-fraud, not
account-opening with reject outcomes. Seven of the ten checklist items require an
institution. "Two external readers" is proofreading, not validation; an
independent replication of a seeded simulation with the same repo and data will
reproduce the same numbers because the only randomness is the seeded observation
draw. The audit's target is the logging-approved population, not the candidate's
approved population; a label sample is not an independent model validation.

**Disconfirming test:** Produce a dated partner pipeline with 5 named
institutions, contact dates, and a one-page brief; the test is a signed letter of
intent or data-access term sheet by 2026-12-15. If none signs, relabel the Summer
2027 target as Level 2 with a simulated case study.

**Confidence:** high.

---

## Finding 6 — High (major)

**Claim:** The business case is an unfillable template, and the pilot's own
numbers imply the audit costs about 58% of the value of the policy switch it is
meant to inform.

**Why it matters:** The risk team's "what does it save?" question has no answer.
The plan's answer is a template that cannot be filled without the partner.

**Failure mechanism (reviewer's):** The plan says "Do not invent a peso figure,"
so the week 1–2 deliverable cannot be completed; the EV formula has no estimator
for the probability. From the committed values: true `P0` is 0.008452
(`better_model`) vs 0.008785 (`incumbent`), a gap of 0.000333 per application, or
75.75 cost units over 227,491 applications. A 1% audit of 219,344 approved rows
is 2,193 labels × 0.02 = 43.87 cost units, ~58% of the 75.75-unit value. The
reported cost of misranking (0.000093 per application) is 21.16 units, ~28% of
the value; net of the audit and residual misranking, the expected value is
~10.7 units, or 0.000047 per application. That is a back-of-envelope from the
committed numbers, but it is the calculation a risk team will do.

**Disconfirming test:** Fill `docs/BUSINESS_CASE.md` with the per-application
value of switching (0.000333) and the per-application audit cost
(0.02 × 1% × 219,344 / 227,491 = 0.000193), then repeat at the bank's stated
volume and cost matrix; compute the ratio and the net expected value after the
residual misranking cost.

**Confidence:** medium-high.

---

## Verdict

**FAIL — the single most likely reason the work is an illusion is that the
"material bias" is manufactured by the 0.90-vs-0.05 observation-rate gap and the
2% review band's cost floor, never swept, and the product then defaults to the
estimator the project itself shows to be biased while printing "Measured."**

## Triage status

- **Status:** open.
- **Next session:** 2026-11-20 20:00.
- **First two checks:** Finding 1 (observation-rate sweep) and Finding 2 (F5
  pass/fail). These determine whether the headline and the bounds survive.
- **Do not change public claims until the findings are verified.**

## Related documents

- Credibility plan: [`CREDIBILITY_PLAN.md`](CREDIBILITY_PLAN.md)
- Claims: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Decision memo: [`DECISION_MEMO_2026-11.md`](DECISION_MEMO_2026-11.md)
