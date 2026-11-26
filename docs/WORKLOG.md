# Worklog

**Status:** Historical state log; past entries are not updated. The current
state is the last entry.

## 2026-11-27 — External credibility pre-review

**Verdict:** the problem is real; the project is worth pursuing as a
research/portfolio artifact and open applied benchmark, not as a validated
commercial product or a novel paper. The audit is in
[`EXTERNAL_CREDIBILITY_REVIEW.md`](EXTERNAL_CREDIBILITY_REVIEW.md) and the
tracked log is in [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md).

**Critical corrections:** removed the false “no peer-reviewed fraud-specific
policy evaluation” claim; added OSCAR, Beyond Holdout Error, and DOiT (ICAIF
2026) to the manuscript and bibliography; repositioned the contribution as the
applied account-opening combination; added a data-readiness note; added the
segment diagnostic and action-weighted baseline earlier in the release.

**Residual open issues:** no real log; no external readers; no model ablation;
the audit/legal feasibility is unverified; the paper is 7 pages and not
peer-reviewed; the vendor-gap matrix is not committed; the bounds are wide in
`frej_002`.

**Next:** decide whether to continue as a narrow research artifact; if yes,
close the open issues in the audit log before sending the reviewer packet.

## 2026-11-26 — Strategic review and full-policy check

**Decision:** `v1.0.0` is a **review release**, not a public flagship release.
The public-release gate (two external readers) is open. The next code release is
`v1.0.1`/`v1.1`, not a silent addition to the tag. See
[`STRATEGIC_REVIEW_v1.md`](STRATEGIC_REVIEW_v1.md), [`RELEASE_STATUS.md`](RELEASE_STATUS.md),
and D15 in [`DECISIONS.md`](DECISIONS.md).

**Product change:** `full_policy_difference` in `estimators.py` bounds the
candidate-vs-incumbent difference over the unobserved reject margin and reports
the break-even rejected-fraud rate. The memo labels the recommendation
`P0`-conditional, adds §4.1, and warns when the `P0` recommendation does not
survive the reject margin. Nine new tests (full-policy, action-weighted,
segment diagnostic); **101 passed**.

**Integrity fixes:** the vendor-review claim is downgraded from Measured to
Limitation; BSP 1213 is qualified as an FMS circular; the validation report's
sweep grid, test counts, claim-check count, and CI status are corrected; the
one-pager status is updated; `RELEASE_STATUS.md` and `EXTERNAL_REVIEW.md` are
added; the README and V1 status docs now say the external gate is open.

**Not verified:** no human external reader; no partner log; the paper PDF was
not rebuilt (no TeX toolchain); the benchmark hash was not re-run on another
stack.

**Next:** send the reviewer packet to 10 targeted practitioners/researchers;
record objections; fix or narrow critical/high findings; release the full-policy
check as `v1.0.1` or `v1.1`; do not add new methods before the external log has
entries.

## 2026-11-21 — Red-team corrections

**Found by the independent estimator review and adversarial pass:**

- `fit_outcome_model` divided by zero on a labelled reject row; fixed by
  dropping zero-propensity rows and returning NaN when none remain.
- `e_approve` omitted the resolution factor on the audit channel. After the
  fix, IPW under estimated action-level propensities is **2.92%**, not 11.19%;
  DR is **1.43%**. The "IPW is not robust" claim was a bug, not a finding.
- The HT variance is now the standard design form; the census case returns
  zero.
- `policy_bounds` now widens with the `P0` SE when there are no rejected rows.
- The gate now rejects `e > 1`, non-finite costs, unknown actions, and
  impossible propensity calibration; it flags a low observed/expected ratio.
- The memo's outside-`P0` count used a key that did not exist; fixed and
  regression-tested.
- Claims now carry Monte Carlo bounds; the sweep's "12/12" is labelled as the
  maximum across policies; the bounds width is reported for `frej_002`
  (**0.203**) as well as the main scenario (**0.009942**).

**Tests:** 80 pass. The pilot and sensitivity are being re-run to match the
corrected code.

## 2026-11-19 — Direction set, repo scaffolded

**Done:**

- Archived the origin repository as `v2.1.0` with `ARCHIVE.md`.
- Committed the evidence memo and six research reviews to the origin repo.
- Created `D:\onboarding-audit` as the new flagship repo.
- Wrote the public surface: `README.md`, `LICENSE`, `pyproject.toml`,
  `CITATION.cff`, `.gitignore`.
- Wrote the research contract: `docs/PROBLEM.md`, `docs/PILOT_SPEC.md`,
  `docs/SCHEMA.md`, `docs/AUDIT_DESIGN.md`, `docs/DATA.md`, `docs/CLAIMS.md`,
  `docs/DECISIONS.md`.
- Copied the processed BAF test file to `data/scored_test.parquet` for the
  local pilot.

**Next:**

1. Implement `src/onboarding_audit/`: config, data, policies, observation,
   estimators, metrics, pilot.
2. Add `configs/pilot.yaml`.
3. Add tests: policy capacity, observation propensities, full-observation
   identity, bounds, no leakage, metrics.
4. Run the pilot; write `reports/pilot.json` and `reports/pilot.md`.
5. Fill the claim ledger with measured results.
6. Add the CLI and a minimal report template.
7. External readers: one fraud/KYC practitioner, one researcher.
8. FiFAR capacity layer (follow-on).
9. Paper draft and release.

**Open questions:**

- What are the actual PH onboarding review rates, label delays, and
  false-rejection costs? No public data; elicit via interviews.
- Is post-hoc verification operationally feasible at a PH bank/e-wallet?
- What is the base-rate difference between BAF and PH e-wallet onboarding?
- Does FiFAR's analyst model add enough to justify the complexity in v0.1?
- What is the right cost model for a fraudulent account: credit-line exposure,
  expected draw-down, or a fixed loss?

**Blockers:** None.

**Health:** The research contract is complete; the pilot is the next decisive
test.

---

## 2026-11-19 — Full pilot complete

**Result:** the premise is real and the correction holds on the identified
population.

- Naive relative bias: **+111.6% to +278.5%** across four policies.
- Naive rank flip: mean **1.00** inversion, P(select true best) **0%**; the
  naive estimate would reject the better model.
- DR: max |relative bias| **0.94%**, mean coverage **96.0%**; IPW **1.18% /
  95.0%**.
- Audit-only at 1%: max **2.98%**, coverage **84.5%**, ESS **1,271**.
- Audit value: DR RMSE **0.001159 → 0.001068** (0% → 2%), ESS **6,610 → 9,126**;
  modest in the main scenario, decisive under outcome-dependent labels
  (audit-only **-2.4% to -2.0%** vs IPW **+44% to +368%** and DR **+596% to
  +1302%**).
- Reject margin: widest bounds **0.009942**; incumbent bounds coverage **35%**;
  bounds are not confidence intervals.
- Runtime: 1,114 s; 700 replications; 13 scenarios.

**Claim ledger and public artifacts updated:** `docs/CLAIMS.md`,
`docs/ONE_PAGER.md`, `paper/brief.md`, `paper/outline.md`, `README.md`,
`reports/pilot.md`, `reports/pilot.json`.

**Next:**

1. Recompute the final verdict with the corrected H2 (naive-only) and H3
   (IPW/DR-only) logic, and regenerate `reports/pilot.md` (done).
2. Two external readers: a fraud/KYC practitioner and a researcher.
3. FiFAR capacity/analyst layer (v0.2).
4. Propensity estimation from logs/audit and sensitivity (v0.2).
5. Paper draft from the outline; fill the claim ledger references.
6. Public release and application package.

**Open questions:** unchanged, plus:
- The naive bias is positive (overestimates cost), not "flattering the
  incumbent." The direction depends on the action mix and costs; test a logging
  policy with a different action mix.
- The corrected ranking still has ~0.29 mean inversions, concentrated in the
  close better-model/incumbent gap. Is that acceptable for a launch decision?
- The audit's marginal value is modest at a 5% approved-label base rate. What is
  the realistic base rate in a PH e-wallet?

**Health:** The pilot supports the premise and the correction; the project is
ready for external review and the v0.2 tool layer.

---

## 2026-11-20 — Arbitrary-log report + propensity sensitivity

**Done:**

- `onboarding-audit report`: validates a decision log, estimates or reads
  propensities, derives candidate actions, computes naive/IPW/DR/audit-only
  estimates and reject-margin bounds, reports overlap/ESS/label-maturity
  diagnostics, sizes an audit, and writes an audit-ready memo.
- `onboarding-audit sensitivity`: estimated, noisy (sigma 0.10/0.25), and
  outcome-dependent propensity scenarios.
- CLI now exposes `pilot`, `report`, `sensitivity`, `validate`.
- 39 tests pass, including the report's known-ground-truth check (DR closer to
  the true `P0` value than naive), missing-propensity estimation, no-audit
  behavior, missing candidate IDs, and invalid logs.
- Docs: `docs/REPORT_USAGE.md`, updated README quickstart, roadmap, examples.

**Sensitivity result (50 reps, complete):**

- Estimated action-level `e`: DR max **2.67%**, coverage **91.0%**; IPW max
  **11.19%**, coverage **73.0%**.
- Lognormal noise sigma 0.25: DR **1.58% / 96.5%**; IPW **7.01% / 93.5%**.
- Outcome-dependent labels with estimated `e`: audit-only **2.58% / 82.5%**;
  IPW **1350.8%**; DR **1627.9%**.

The claim gate is met for **DR**, not for IPW. The paper should claim DR
robustness, not IPW robustness. The tool should recommend DR when `e` is
estimated, and audit-only when the label-source mix suggests outcome-dependent
observation.

**Next:**

1. Update the paper draft and one-pager with the DR-only propensity claim (done
   in the brief/outline; paper draft remains).
2. FiFAR capacity/analyst layer.
3. Two external readers.
4. Public release and application package.

**Health:** The tool surface is usable on a real log, and the correction
survives estimated propensities with DR. The remaining scope is external
validity and the FiFAR capacity layer, not a new method.

---

## 2026-11-20 — Covariate sensitivity + documentation freeze

**Done:**

- Added covariate-dependent observation to the pilot:
  `logit(channel) = logit(base) + 0.75 * standardized log1p(amount)`.
- Added a cross-fitted per-action logistic propensity model
  (`propensity.fit_covariate_propensity`).
- Added five 50-replication scenarios: oracle, action-level, covariate model,
  and the two delay-45 variants.
- Added `--propensity-model covariate` and `--propensity-features` to the
  arbitrary-log report.
- Added observation-rate-by-amount-quintile and weight-tail diagnostics to the
  memo.
- 47 tests pass, including the covariate gradient recovery and the report's
  covariate path.

**Covariate result (50 reps):**

- Action-level: IPW **67.52% / 1.5%** coverage; DR **21.25% / 72.5%**
  (delay 0.5). With delay 45: IPW **51.72% / 21.5%**; DR **17.59% / 80.0%**.
- Covariate model: IPW **1.97% / 91.5%**; DR **2.48% / 89.5%** (delay 0.5).
  With delay 45: IPW **3.35% / 90.5%**; DR **3.68% / 89.5%**.
- Oracle: IPW **3.01% / 90.0%**; DR **2.63% / 89.0%**.
- The covariate model recovers the oracle; action-level weighting does not.
  Coverage is 89–91.5%, below nominal 95%, because the weights are heavy-tailed.

**Documentation freeze:**

- Added `docs/METHODS.md`, `docs/RESULTS.md`, `docs/REPRODUCIBILITY.md`,
  `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `docs/DATA_DICTIONARY.md`,
  `docs/PUBLICATION_CHECKLIST.md`, `docs/FAQ.md`, `docs/OPEN_QUESTIONS.md`,
  `docs/REFERENCES.md`, and `paper/README.md`.
- Rewrote `docs/README.md` as the map with reading paths, document status, and
  precedence/update rules.
- Updated `README.md`, `PROBLEM.md`, `DATA.md`, `SCHEMA.md`, `MEMO_TEMPLATE.md`,
  `CONTRIBUTING.md`, `ROADMAP.md`, `DECISIONS.md` (D11/D12), `CLAIMS.md`,
  `THREATS.md`, `PILOT_SPEC.md`, `ONE_PAGER.md`, `COMMUNICATION.md`,
  `paper/brief.md`, and `paper/outline.md`.
- The paper is intentionally not drafted; `paper/` contains research notes only.
- Regenerated `reports/pilot.{json,md}` under v0.2.1; the headline numbers are
  unchanged (H1 max 278.49%, DR 0.94% / 96.0%). The report header now matches the
  package version.

**Next:**

1. Two external readers: a fraud/KYC practitioner and a researcher.
2. FiFAR capacity/analyst layer.
3. Bootstrap/randomization-inference interval for the heavy-weight scenarios.
4. Paper draft from the canonical docs, not from a blank page.
5. Public release and application package.

**Health:** The documentation is research-ready. The scientific claim is now
model-specific: DR with an estimated action-level `e` for action-dependent
observation; a covariate propensity model for covariate-dependent observation;
audit-only for outcome-dependent labels. The remaining work is external validity,
uncertainty calibration, and the paper.

---

## 2026-11-20 — Credibility and adoption plan

**Done:**

- Wrote `docs/CREDIBILITY_PLAN.md`: credibility ladder, risk-team adoption
  checklist, hostile-reviewer attack table, minimum evidence package, 90-day
  plan, pilot protocol, business case, and model-risk package.
- Pushed the repo to `https://github.com/kira-ml/onboarding-audit` (public);
  corrected the GitHub URL from `keniralacson` to `kira-ml`.
- Recorded D13: prioritize a real-log pilot and external validation over more
  methods.

**State:**

- Level 1 (reproducible research artifact) is strong.
- Level 2 (review-ready tool) is the next target.
- Level 3 (pilot-proven) is the 2027 target; Level 4 requires a sponsor.

**Next:**

1. Write `docs/VALIDATION_REPORT.md`, `docs/MODEL_CARD.md`,
   `docs/PILOT_PROTOCOL.md`, `docs/BUSINESS_CASE.md`.
2. Add a real-log adapter, one-command demo, CI, and maintainer/security/privacy
   files.
3. Contact five practitioners; get two external readers.
4. Run a red-team review of the credibility plan.

**Health:** The scientific foundation is strong; the binding constraint is now
access and external validation, not code.

---

## 2026-11-20 — November–December strategic decision

**Decision:** D14 — C+ convex barbell: 80% Level 2 package, 20%
outreach/information, 0% new methods.

**Revision (same day):** switched to **C-seq, finish-first** — package freeze by
2026-12-05; reviewer shortlist in late November; reviewer search 2026-12-08 to
2026-12-23. The expected-value difference from C+ is within the subjective
noise; the focus constraint decides.

**Red-team review received:** six findings, verdict FAIL on the current framing;
saved to `docs/RED_TEAM_CREDIBILITY_PLAN.md`. Triage deferred to 2026-11-20
20:00. Do not change public claims until the findings are verified.

**Why:** The binding constraint is access to a real log and a risk-team
reviewer, not code. C is convex; D is a high-variance bet on a low-probability
partner.

**Next:**

1. Write the 1-page pilot brief; send it to 10 targeted practitioners.
2. Write the validation report, model card, pilot protocol, and business case.
3. Add the real-log adapter, one-command demo, CI, and maintainer/security/
   privacy files.
4. Mid-point review 2026-12-15; end-of-period review 2026-12-31.

**Health:** The project is at Level 1; the decision is to build the Level 2
package, not to add methods.

---

## 2026-11-21 — V1 credibility-first plan

**Done:**

- Created `docs/V1/`: README, VISION, REQUIREMENTS, ARCHITECTURE, DECISIONS,
  ROADMAP, EXPERIMENTS, EVALUATION, PROGRESS.
- Added scenario-level `e_approve`/`kappa_review` overrides to `Scenario` and
  `run_scenario`.
- Created `configs/obs_sweep.yaml` (12 cells) and `scripts/analyze_sweep.py`.
- 49 tests pass. The 1-rep smoke shows the expected pattern: naive bias
  ~388–527% at `e_approve=0.01`, ~4.7–30% at `e_approve=0.50`.
- Launched the full 50-rep observation sweep.
- Updated README, `docs/ROADMAP.md`, and `docs/CLAIMS.md` to the V1 plan.

**E1 sweep result (50 reps, 12 cells):**

- Naive bias **7.8–538.5%**, >5% in **12/12** cells.
- DR with known propensities max **1.89%**; coverage **84.5–96.0%**.
- DR P(select true best) **64%** at `e_approve=0.01`, **96–100%** at `0.50`.
- The premise survives; the universal magnitude does not. V1 claim updated.
- Identification gate implemented (`gates.py`): positivity, sample size, ESS,
  max weight, and cost support; the 20-row demo now withholds estimates. 57 tests
  pass.

**Next:**

1. Record F5; add the unconditional interval.
2. Build the review package (model card, validation report, pilot protocol,
   business case).

**Health:** V1 is a credibility release; the observation sweep is the first
evidence gate.
