# Roadmap

**Status:** Canonical roadmap for v0.2.1 (2026-11-20).

**Goal:** A public, research-grade measurement layer for account-opening fraud
policies, ready for the Summer 2027 fintech internship cycle.

**Rule:** Value before scope. Ship the smallest artifact a fintech team can use,
then add depth only where the pilot earns it.

---

## v0.1 — Pilot (November–December 2026)

- [x] Problem validation and evidence memo.
- [x] Account-opening reframing; archive V2.1.
- [x] Decision-log schema; audit design; BSP mapping.
- [x] Simulation, estimators, bounds, pilot CLI, schema validator.
- [x] Negative-control tests.
- [x] Full pilot results and claim ledger (`reports/pilot.md`,
  `reports/pilot.json`, `docs/CLAIMS.md`).
- [ ] Two external readers (fraud/KYC practitioner + researcher).
- [x] README/one-pager final pass; no placeholders.

**Pilot outcome:** premise supported and correction supported. Naive bias
**+111.6% to +278.5%**; naive rank inversion 1.00; DR max |relative bias|
**0.94%** with **96.0%** coverage; audit-only high variance at 1%; reject margin
requires bounds. H4 (audit value) is supported but modest in the main scenario and decisive
under outcome-dependent labels.

**Exit criterion:** the pilot shows a material naive bias and/or rank flips, and
at least one honest correction or bound; or a well-supported null. **Met.**

## v0.2 — Usable tool (January 2027)

- [x] Arbitrary-log `report` command (bring your own log and candidate scores).
- [x] Propensity estimation from logs/audit; sensitivity to estimated e.
  **Result:** DR survives estimated `e` when observation is action-dependent
  (**2.67% / 91.0%**); IPW does not (**11.19% / 73.0%**); outcome-dependent
  labels with estimated `e` require audit-only (**2.58% / 82.5%**).
- [x] Covariate-dependent observation: fitted per-action propensity model,
  `--propensity-model covariate`, and a 50-replication sensitivity.
  **Result:** action-level IPW **67.52%**, DR **21.25%**; covariate model
  **1.97% / 2.48%** (delay 0.5) and **3.35% / 3.68%** (delay 45); coverage
  **89–91.5%** (heavy tails).
- [ ] FiFAR capacity/analyst layer.
- [x] Markdown memo template with the measured/assumed/unverifiable ledger.
- [x] Example log and CLI walkthrough (`examples/`, `docs/REPORT_USAGE.md`).
- [x] Documentation index and reading path (`docs/README.md`).

**Exit criterion:** a data scientist can run the tool on a sample log and get a
memo in under 30 minutes.

## v0.2.1 — Documentation freeze (November 2026)

- [x] Consolidated methods reference (`docs/METHODS.md`).
- [x] Consolidated results and H1–H6 verdicts (`docs/RESULTS.md`).
- [x] Reproducibility guide (`docs/REPRODUCIBILITY.md`).
- [x] Architecture and testing guides (`docs/ARCHITECTURE.md`,
  `docs/TESTING.md`).
- [x] Data dictionary (`docs/DATA_DICTIONARY.md`).
- [x] Publication checklist (`docs/PUBLICATION_CHECKLIST.md`).
- [x] FAQ and open-questions register (`docs/FAQ.md`,
  `docs/OPEN_QUESTIONS.md`).
- [x] Paper workspace guide (`paper/README.md`), explicitly not a paper draft.
- [ ] Two external readers (fraud/KYC practitioner + researcher).

**Exit criterion:** every public number traces to a committed artifact, every
canonical document is current, and a new collaborator can start from
`docs/README.md` without reading the conversation history. **Met for the
author; external readers remain.**

## v0.3 — Research (February 2027)

- [ ] Paper draft (IMRaD) built from `docs/METHODS.md`, `docs/RESULTS.md`, and
  `docs/CLAIMS.md`; no new headline during drafting.
- [ ] Second public dataset or a transaction-fraud extension.
- [ ] Sensitivity: costs, capacity, delay, audit size.
- [ ] Bootstrap/randomization-inference interval for the heavy-weight scenarios.
- [ ] Independent review/red-team pass.

**Exit criterion:** a researcher can reproduce the headline and explain the
limitations.

## v1.0 — Release (March–April 2027)

- [ ] Public GitHub release, MIT license, CITATION.cff.
- [ ] Technical report / arXiv.
- [ ] Blog post or short talk for a fintech/ML audience.
- [ ] Application package: one-pager, 10-minute walkthrough, five hard questions.
- [ ] At least two external readers/practitioners have used it.

## What is explicitly out of scope

- A new fraud detector, classifier, or graph-mule model.
- A production integration or vendor replacement.
- A claim about GCash/Maya data or a specific bank.
- A random approval/rejection experiment.
- A general-purpose OPE library.
- A scam/APP intervention evaluation without a bank partner.

## Review dates

- **2026-11-20:** documentation freeze (canonical docs complete; paper not
  started). **Met for the author.**
- **2026-12-15:** external readers and pilot go/no-go.
- **2027-01-15:** v0.2 usable-tool gate.
- **2027-02-15:** paper draft gate.
- **2027-03-15:** release and application package.
