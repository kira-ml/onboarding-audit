# Changelog

**Status:** Canonical version history.

## [Unreleased] — V1 review candidate (2026-11-21)

### Added

- Observation-mechanism declaration on `report` (`--observation-assumption`):
  `outcome` refuses, `unknown` marks the memo "assumption unverified".
- Propensity calibration diagnostic: observed/expected ratio, refusal when the
  observed count exceeds what the stated `e` allows, and a flag below 0.5.
- Monte Carlo bounds on every headline bias; Wilson intervals on the sweep.
- `scripts/check_claims.py`: 27 headline numbers recomputed from the committed
  JSON; runs in CI.
- `docs/AUDIT_REPORT.md`, `docs/MODEL_CARD.md`, `docs/VALIDATION_REPORT.md`,
  `docs/PILOT_PROTOCOL.md`, `docs/BUSINESS_CASE.md`,
  `docs/BENCHMARK_PROVENANCE.md`.
- `scripts/prepare_baf.py`: rebuilds the benchmark from `Base.csv`; reproduced
  the recorded SHA-256 exactly.
- End-to-end `demo` command and a no-propensity demo log.

### Fixed

- `fit_outcome_model` divided by zero on a labelled reject row.
- `e_approve` omitted the resolution factor on the audit channel.
- HT variance centred on the estimate; the census case now returns zero.
- `policy_bounds` dropped the `P0` SE when there were no rejected rows.
- The memo's outside-`P0` line read a non-existent key and printed 0.
- Gate silent-pass paths: NaN cost, `e > 1`, unknown action strings.
- NaN bounds were counted as coverage failures.

### Changed claims

- IPW under estimated action-level `e` is **2.92%**, not 11.19%; the old result
  was a propensity bug. DR is **1.43%**.
- DR's **0.94%** and **≤1.89%** are means; the 95% MC upper bound on |bias| is
  **3.8%** (main) and **4.3–9.6%** (sweep).
- "12/12 cells >5%" is the maximum across policies; the incumbent is **11/12**.
- The bounds are **0.009942** in the main scenario and **0.203** in `frej_002`.
- F5: the narrow interval passes **15/88**, the widened interval **77/88**.

## [0.2.1] — 2026-11-20

### Added

- Covariate-dependent observation in the pilot:
  `logit(channel) = logit(base) + beta * standardized log1p(amount)`, with
  `observation_mode: covariate` and `covariate_beta`.
- `propensity.fit_covariate_propensity`: a cross-fitted per-action logistic
  model `P(observed | action, X)`.
- Five 50-replication covariate scenarios: oracle, action-level, fitted model,
  and the two delay-45 variants.
- `--propensity-model covariate` and `--propensity-features` on
  `onboarding-audit report`.
- Observation-rate-by-amount-quintile and weight-tail diagnostics in the memo.
- Canonical documentation: `docs/METHODS.md`, `docs/RESULTS.md`,
  `docs/REPRODUCIBILITY.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`,
  `docs/DATA_DICTIONARY.md`, `docs/PUBLICATION_CHECKLIST.md`, `docs/FAQ.md`,
  `docs/OPEN_QUESTIONS.md`, `docs/REFERENCES.md`, and `paper/README.md`.
- A documentation map with reading paths, status, precedence, and update rules
  in `docs/README.md`.

### Changed

- `README.md`, `PROBLEM.md`, `DATA.md`, `SCHEMA.md`, `MEMO_TEMPLATE.md`,
  `CONTRIBUTING.md`, `ROADMAP.md`, `DECISIONS.md` (D11/D12), `CLAIMS.md`,
  `THREATS.md`, `PILOT_SPEC.md`, `ONE_PAGER.md`, `COMMUNICATION.md`,
  `paper/brief.md`, and `paper/outline.md` updated with the covariate results
  and the documentation freeze.
- Version bumped to 0.2.1.

### Results

- Action-level covariate observation: IPW **67.52% / 1.5%** coverage; DR
  **21.25% / 72.5%** (delay 0.5). With delay 45: IPW **51.72% / 21.5%**; DR
  **17.59% / 80.0%**.
- Covariate model: IPW **1.97% / 91.5%**; DR **2.48% / 89.5%** (delay 0.5).
  With delay 45: IPW **3.35% / 90.5%**; DR **3.68% / 89.5%**.
- Oracle: IPW **3.01% / 90.0%**; DR **2.63% / 89.0%**.
- The covariate model recovers the oracle; action-level weighting does not.
  Coverage is 89–91.5%, below nominal 95%, because the weights are heavy-tailed.

### Notes

- The paper is not drafted. The canonical documentation is the source of truth;
  `paper/` contains research notes only.
- 47 tests pass, including the covariate gradient recovery and the report's
  covariate path.

## [0.2.0] — 2026-11-20

### Added

- `onboarding-audit report`: arbitrary-log policy evaluation. It validates the
  decision log, uses a provided propensity or estimates an action-level
  propensity, derives candidate actions, computes naive/IPW/DR/audit-only
  estimates and reject-margin bounds, reports overlap/ESS/label-maturity
  diagnostics, sizes a post-hoc verification audit, and writes an audit-ready
  memo (`report.md`) and JSON.
- `onboarding-audit sensitivity`: pre-declared propensity sensitivity with
  estimated, noisy (sigma 0.10/0.25), and outcome-dependent-label scenarios.
- `src/onboarding_audit/propensity.py`: action-level propensity estimation and
  lognormal noise for the sensitivity.
- `docs/REPORT_USAGE.md`: how to run and read the arbitrary-log report.
- `examples/sample_candidate.csv` and an updated CLI walkthrough.
- Tests for the report's known-ground-truth check, missing-propensity
  estimation, no-audit behavior, missing candidate IDs, invalid logs, and the
  propensity helpers. 39 tests pass.

### Changed

- README quickstart now covers `pilot`, `report`, `sensitivity`, and `validate`.
- Roadmap v0.2 items updated: the report and propensity sensitivity are
  implemented; FiFAR remains the next capacity layer.
- Version bumped to 0.2.0.

### Notes

- The report is still a pilot: it does not prove the observation model is
  correct, and the reject margin is bounded, not point-identified.
- The sensitivity uses action-level propensities; a covariate propensity model
  is the v0.3 extension. (Implemented in 0.2.1.)
- Sensitivity result: DR survives estimated `e` (**2.67% / 91.0%**); IPW does
  not (**11.19% / 73.0%**); outcome-dependent labels with estimated `e` require
  audit-only (**2.58% / 82.5%**). The paper claims DR robustness, not IPW
  robustness.

## [0.1.0] — 2026-11-19

### Added

- Account-opening reframing of the flagship: audit-ready evaluation of
  approve/review/reject policies under selective and delayed labels.
- Decision-log schema (`docs/SCHEMA.md`) extending BSP Circular 1213's 11
  mandated fields with decision/observation/label/eKYC fields.
- Audit design (`docs/AUDIT_DESIGN.md`): random post-hoc verification of
  approved applications and shadow scoring; no random approvals/rejections.
- BSP/AFASA/NPC mapping (`docs/BSP_MAPPING.md`).
- Pre-registered pilot (`docs/PILOT_SPEC.md`): estimand on the logging
  non-rejected population, full-population bounds, estimators, scenarios,
  negative controls, kill criteria.
- Simulation and estimators: policy construction, review capacity, observation
  model, naive/IPW/DR/audit-only, partial-identification bounds, metrics.
- Pilot CLI and schema validator (`onboarding-audit pilot`,
  `onboarding-audit validate`).
- Negative-control tests: full observation, full audit, propensity recovery,
  bounds validity, capacity, no leakage, schema validation.
- Data card, claim ledger, decision journal, threats to validity, related-work
  map, communication plan, one-pager, glossary, memo template, roadmap.

### Changed

- Archived the origin repository as `v2.1.0` with `ARCHIVE.md`.
- Marked the transaction-framed V3 proposal/pilot as superseded.

### Notes

- The pilot uses public BAF account-opening data; no proprietary bank data.
- The cost matrix is a normalized assumption, not a production estimate.
- The pilot uses oracle propensities to isolate estimator behavior; estimated
  propensities are the v0.2 study.
