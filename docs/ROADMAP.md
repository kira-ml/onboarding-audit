# Roadmap

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

- [ ] Arbitrary-log `report` command (bring your own log and candidate scores).
- [ ] Propensity estimation from logs/audit; sensitivity to estimated e.
- [ ] FiFAR capacity/analyst layer.
- [ ] HTML/Markdown memo template with the measured/assumed/unverifiable ledger.
- [ ] Example notebook on the public sample log.
- [ ] Documentation site or a clean `docs/` reading path.

**Exit criterion:** a data scientist can run the tool on a sample log and get a
memo in under 30 minutes.

## v0.3 — Research (February 2027)

- [ ] Paper draft (IMRaD) with the claim ledger.
- [ ] Second public dataset or a transaction-fraud extension.
- [ ] Sensitivity: costs, capacity, delay, audit size.
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

- **2026-12-15:** pilot result and go/no-go.
- **2027-01-15:** v0.2 usable-tool gate.
- **2027-02-15:** paper draft gate.
- **2027-03-15:** release and application package.
