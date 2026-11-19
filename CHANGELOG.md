# Changelog

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
  is the v0.3 extension.
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
