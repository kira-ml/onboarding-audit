# Changelog

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
