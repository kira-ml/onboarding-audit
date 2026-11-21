# V1 Roadmap

**Status:** Planning, 2026-11-21.
**Release:** v1.0.0, 2026-12-31.
**Rule:** Finish-first. The package is frozen before the reviewer search begins.

---

## 1. Milestones

| Milestone | Date | Definition |
|---|---|---|
| **M0 — V1 plan** | 2026-11-21 | V1 docs created; scope and claim frozen for planning |
| **M1 — Credibility triage** | 2026-11-24 | Sweep run; F5 recorded; claim updated; red-team findings triaged |
| **M2 — Core fixes** | 2026-12-01 | Report gate; bounds F5; demo log; tests |
| **M3 — Package freeze** | 2026-12-05 | Model card, validation report, pilot protocol, business case; CI; v1.0.0-rc |
| **M4 — Review** | 2026-12-15 | Reviewer packet sent; two calls scheduled |
| **M5 — v1.0.0** | 2026-12-31 | Release tag; reviewer responses; January pilot plan |

---

## 2. Phase 0 — Credibility triage (Nov 21–24)

**Goal:** Establish what is true before changing the product.

**Tasks:**
- [x] Add `e_approve` and `kappa_review` overrides to `Scenario` and
      `run_scenario`.
- [x] Create `configs/obs_sweep.yaml` with 12 cells.
- [x] Run the sweep (50 reps per cell) and write `reports/obs_sweep/pilot.json`/`.md`.
- [x] Add `scripts/analyze_sweep.py` for a compact table.
- [ ] Compute F5 pass/fail for every policy; record the unconditional interval.
- [ ] Triage the six red-team findings: confirmed, rejected, or residual.
- [x] Update `docs/CLAIMS.md` and `docs/RESULTS.md` with the conditional claim.
- [x] Freeze the V1 claim.

**Deliverables:**
- `configs/obs_sweep.yaml`
- `reports/obs_sweep/pilot.json`, `reports/obs_sweep/obs_sweep.md`
- `docs/V1/EXPERIMENTS.md` result table
- `docs/CLAIMS.md` updated
- `docs/V1/PROGRESS.md` triage log

**Acceptance:** the V1 claim is stated with measured conditions; F5 is recorded;
no unresolved critical finding is left untriaged.

---

## 3. Phase 1 — Core fixes (Nov 25–Dec 1)

**Goal:** Make the product safe and the bounds honest.

**Tasks:**
- [ ] Add `src/onboarding_audit/gates.py` with `IdentificationReport`.
- [ ] Integrate the gate into `report.py`; remove the hardcoded "Measured."
- [ ] Add `examples/demo_log.csv` (no propensity, known truth).
- [ ] Add `test_gates.py` and the adversarial-log tests.
- [ ] Fix the 20-row demo so it no longer prints "Measured."
- [ ] Record F5 in `pilot.json`/`pilot.md`; use DR for both pilot and report
      bounds (or record both).
- [ ] Add `test_pilot.py` for F5 and bounds.
- [ ] Update `docs/REPORT_USAGE.md`, `docs/MEMO_TEMPLATE.md`, and
      `docs/THREATS.md`.

**Deliverables:**
- `gates.py`, updated `report.py`, `pilot.py`, `metrics.py`
- `examples/demo_log.csv`
- New tests
- Updated docs

**Acceptance:** five adversarial logs are refused or flagged; no "Measured" on
an unidentified log; F5 recorded; `pytest` passes.

---

## 4. Phase 2 — Reproducibility and package (Dec 2–5)

**Goal:** Make the release reproducible and review-ready.

**Tasks:**
- [ ] Add `scripts/prepare_baf.py` with the exact split and score provenance.
- [ ] Add `data/provenance.json` with hashes; update `docs/DATA.md` and
      `docs/DATA_DICTIONARY.md`.
- [ ] Add the leakage test; if the pipeline cannot be reproduced, narrow the
      Level 1 claim.
- [ ] Add `docs/MODEL_CARD.md`, `docs/VALIDATION_REPORT.md`,
      `docs/PILOT_PROTOCOL.md`, `docs/BUSINESS_CASE.md`.
- [ ] Add `docs/PRIVACY.md`, `docs/MAINTAINERS.md`, `docs/SUPPORT.md`.
- [ ] Add `.github/workflows/ci.yml` with tests, lint, smoke, link check.
- [ ] Add `ruff` to dev dependencies and fix lint.
- [ ] Add the one-command demo.
- [ ] Update the README and `docs/README.md`.
- [ ] Freeze v1.0.0-rc.

**Deliverables:**
- `scripts/prepare_baf.py`
- `data/provenance.json`
- Four review-package docs
- CI workflow
- v1.0.0-rc tag

**Acceptance:** a data scientist can run the demo in <10 minutes; CI is green;
the review package is complete; the claim ledger is consistent.

---

## 5. Phase 3 — Review (Dec 6–15)

**Goal:** Get external evidence before the release.

**Tasks:**
- [ ] Build the reviewer packet: one-pager, validation report, model card,
      pilot protocol, 10 credibility questions, 30-minute ask.
- [ ] Prepare a 10-person reviewer shortlist.
- [ ] Send the packet Dec 8–15.
- [ ] Schedule two calls.
- [ ] Record objections in `docs/EXTERNAL_REVIEW.md`.
- [ ] Fix only critical objections; no new features.
- [ ] Mid-point review Dec 15.

**Deliverables:**
- Reviewer packet
- `docs/EXTERNAL_REVIEW.md`
- Two calls scheduled or completed
- v1.0.0-rc2 if needed

**Acceptance:** at least one reviewer call by Dec 15; objections recorded; the
V1 claim survives or is narrowed.

---

## 6. Phase 4 — Release (Dec 16–31)

**Goal:** Ship v1.0.0 and set up V1.1.

**Tasks:**
- [ ] Incorporate reviewer feedback into the docs and claim ledger.
- [ ] Tag v1.0.0.
- [ ] Update `CHANGELOG.md`, `CITATION.cff`, and the README.
- [ ] Write the reviewer response and the V1.1 plan.
- [ ] Update `docs/V1/PROGRESS.md`.
- [ ] Optional: a blog post or a 10-minute walkthrough.

**Deliverables:**
- v1.0.0 tag
- Final docs
- Reviewer response
- V1.1 plan

**Acceptance:** v1.0.0 is tagged; the repo is clean; the claim ledger is
consistent; the reviewer packet is public or shared.

---

## 7. Weekly cadence

| Day | Activity | Output |
|---|---|---|
| Monday | Plan the week; pick the top three tasks | `PROGRESS.md` update |
| Wednesday | Mid-week check; unblock; cut scope if needed | Short note |
| Friday | Verify; update docs; commit; review the week | `PROGRESS.md`, commit |
| Sunday | Rest; no project work | — |

**Time cap:** 10–12 hours/week; 65–75 hours total. Stop if GPA, applications,
sleep, or health slip.

---

## 8. Dependencies

| Dependency | Needed for | Status |
|---|---|---|
| BAF `Base.csv` | FR4 pipeline | Public; available |
| LightGBM | FR4 candidate score | Add to dev dependencies |
| GitHub Actions | FR8 CI | Public repo; available |
| Two external reviewers | FR7/M4 | Not yet identified |
| Bank partner | V1.1/V2 pilot | Not needed for V1 |

---

## 9. Kill criteria

- **Nov 24:** sweep not run → use the existing single-scenario result and
  narrow the claim; do not call it robust.
- **Dec 5:** package not frozen → cut to validation report, model card, pilot
  protocol, and report gate; defer CI/adapter.
- **Dec 15:** no reviewer call → use the red-team + one strong peer; plan
  January.
- **Any time:** health/GPA/applications slip → stop.
- **Any time:** a partner asks for PII/proprietary data without a DPA → decline.

---

## 10. Definition of done

- [ ] Sweep run; claim conditional.
- [ ] F5 recorded; bounds honest.
- [ ] Report gate passes adversarial tests.
- [ ] Pipeline reproducible or claim narrowed.
- [ ] 50+ tests; CI green.
- [ ] Review package complete.
- [ ] Two external readers.
- [ ] v1.0.0 tagged.
- [ ] No unresolved critical red-team finding.

---

## 11. Related documents

- V1 index: [`README.md`](README.md)
- Vision: [`VISION.md`](VISION.md)
- Requirements: [`REQUIREMENTS.md`](REQUIREMENTS.md)
- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Decisions: [`DECISIONS.md`](DECISIONS.md)
- Experiments: [`EXPERIMENTS.md`](EXPERIMENTS.md)
- Evaluation: [`EVALUATION.md`](EVALUATION.md)
- Progress: [`PROGRESS.md`](PROGRESS.md)
