# V1 Requirements

**Status:** Planning, 2026-11-21.
**Scope:** v1.0.0, credibility-first release.
**Rule:** A requirement is not done until its acceptance test passes and the
result is recorded in the V1 progress tracker.

---

## 1. Functional requirements

### FR1 — Observation-rate robustness sweep

**What:** Run a pre-registered sweep over plausible observation rates:
`e_approve ∈ {0.01, 0.05, 0.20, 0.50}` and
`kappa_review ∈ {0.5, 0.9, 1.0}`, 50 replications per cell, everything else
fixed. Report naive bias, DR/IPW/audit-only bias, coverage, rank inversion, and
P(select true best) per cell.

**Why:** The current headline is a single-scenario result. The sweep determines
whether the bias and the ranking flip are robust or parameter-dependent.

**Acceptance:**
- `configs/obs_sweep.yaml` exists with 12 cells.
- `reports/obs_sweep/pilot.json` and `.md` are generated.
- The V1 claim in `docs/CLAIMS.md` is updated to the measured conditions.
- The sweep result is summarized in `docs/RESULTS.md`.

### FR2 — Bounds validity and F5 record

**What:** Record the pre-registered F5 pass/fail for every policy. Compute an
unconditional interval `[L(v_pop - 1.96 se), U(v_pop + 1.96 se)]` and compare its
coverage with the current bounds. If F5 fails, remove the coverage claim and
report the bounds as a partial-identification interval.

**Why:** The current F5 criterion is ≥90%, but the reported coverage is 35–85%.
The documentation reinterprets the failure instead of recording it.

**Acceptance:**
- `pilot.json` has `F5_pass` and `F5_coverage` per policy.
- `docs/RESULTS.md` says "F5 failed" or "F5 passed" explicitly.
- If F5 fails, `docs/CLAIMS.md` and the README remove any implication that the
  bounds are a confidence interval.
- A test covers the F5 computation.

### FR3 — Identification gate in the report

**What:** Before printing a point estimate or "Measured," check:
- positivity on `P0`;
- overlap/ESS and max weight;
- minimum observed sample per action;
- cost support (no negative costs);
- candidate actions outside `P0`.

If a gate fails, the memo must say "not identified" and must not print
"Measured."

**Why:** The current `report` can print "Measured" on a 20-row log with a
negative-cost CI. This is the strongest counter-case in the project's own threats
register.

**Acceptance:**
- A new `IdentificationReport` with `passed`, `reasons`, and `metrics`.
- The memo claim ledger uses the gate status, not a hardcoded "Measured."
- Five adversarial logs (no propensity, low overlap, zero positivity, tiny n,
  negative cost support) are refused or flagged.
- A test asserts no "Measured" on an unidentified log.
- The 20-row demo no longer prints "Measured."

### FR4 — Reproducible benchmark pipeline

**What:** Add a script that reproduces the processed BAF frame and the
`p_fraud`/`p_fraud_lgbm` scores: exact month split, training, validation, test,
and hashes. If the original pipeline cannot be reproduced, narrow the Level 1
claim and document the gap.

**Why:** The headline ranking depends on scores that are not in the repository.
A hostile reviewer cannot rule out leakage.

**Acceptance:**
- `scripts/prepare_baf.py` exists and runs on the public BAF data.
- The processed frame and score columns are reproduced within a stated
  tolerance, or the gap is documented.
- The data dictionary includes the score provenance and hash.
- A leakage test refits the candidate on the evaluation window and shows the
  ranking flip disappears or reverses.
- `docs/REPRODUCIBILITY.md` reproduces the headline from a clean checkout, or
  explicitly states what cannot be reproduced.

### FR5 — Real-log adapter and data-quality report

**What:** Add a CSV/parquet adapter that maps a team's log to the schema,
reports missing fields, label maturity, action mix, and the observation-rate
diagnostic by amount quintile. The adapter must not require PII.

**Why:** A risk team's first run will be on its own log, not the BAF frame.

**Acceptance:**
- `onboarding-audit validate` reports the schema mapping and missing fields.
- The adapter handles CSV and parquet.
- The data-quality report includes label maturity, action mix, and the
  observation-rate-by-amount-quintile diagnostic.
- A synthetic 2,500-row log with no propensity column is included as a test
  fixture.

### FR6 — One-command demo

**What:** A single command that runs validate, report, and a memo on a synthetic
log, with no external data.

**Why:** A reviewer should be able to see the product in under 10 minutes.

**Acceptance:**
- `python -m onboarding_audit.cli demo` or a documented `make demo` runs
  end-to-end.
- The demo log has no pre-loaded propensity column.
- The output includes a memo and a JSON report.
- The demo is documented in `README.md` and `docs/REPORT_USAGE.md`.

### FR7 — Review package

**What:** Add four artifacts:
- `docs/MODEL_CARD.md`: intended use, out-of-scope use, inputs, outputs,
  assumptions, performance, limitations, regulatory notes.
- `docs/VALIDATION_REPORT.md`: claim → evidence → test → status → residual risk.
- `docs/PILOT_PROTOCOL.md`: scope, data, success metrics, privacy/legal,
  rollback.
- `docs/BUSINESS_CASE.md`: cost of the current evaluation, cost of a wrong
  policy, expected value, audit cost, pilot ROI.

**Why:** These are the artifacts a risk team expects. Their absence is an
adoption blocker.

**Acceptance:** all four exist and are linked from `docs/README.md`; no
placeholder text remains.

### FR8 — Tests and CI

**What:** Add tests for the sweep, F5, report gate, adapter, and demo. Add
GitHub Actions CI for tests, lint, and a smoke run.

**Why:** A review-ready tool must be testable by someone else.

**Acceptance:**
- `pytest -q` passes with at least 50 tests.
- CI is green on Python 3.10–3.12.
- The CI includes a smoke run on the demo log.
- A broken link check runs in CI.

### FR9 — Documentation and claim ledger

**What:** Update the README, `docs/README.md`, `docs/CLAIMS.md`,
`docs/RESULTS.md`, `docs/THREATS.md`, and the V1 docs. Every public number traces
to an artifact.

**Why:** The project's credibility depends on the claim ledger being the source
of truth.

**Acceptance:**
- No broken relative links.
- No stale headline in the README or one-pager.
- Every V1 claim appears in `docs/CLAIMS.md` with an evidence tier.
- The red-team findings are either closed or explicitly residual.

### FR10 — Release packaging

**What:** Tag v1.0.0, update `CHANGELOG.md`, `CITATION.cff`, and the README
status. Include a reviewer packet.

**Why:** The release is the portfolio artifact.

**Acceptance:**
- `v1.0.0` tag.
- `CHANGELOG.md` has a v1.0.0 entry.
- `CITATION.cff` version is 1.0.0.
- The README says "v1.0.0 credibility-first release."
- The reviewer packet is ready.

---

## 2. Non-functional requirements

| ID | Requirement | Acceptance |
|---|---|---|
| **NFR1** | Honesty: no claim above its evidence tier | Claim ledger review; no "Measured" without a gate |
| **NFR2** | Reproducibility: seeds, hashes, commands, environment | `docs/REPRODUCIBILITY.md`; CI; data hash |
| **NFR3** | Privacy/security: no PII; public/synthetic only until a DPA | Schema warnings; examples; `PRIVACY.md` |
| **NFR4** | Usability: a data scientist can run the demo in <10 min | Timed demo test |
| **NFR5** | Performance: report on 227k rows in <5 min | Timing check |
| **NFR6** | Maintainability: typed public functions; small pure estimators | Code review; tests |
| **NFR7** | Compatibility: Python 3.10+; pinned dependencies | CI matrix |
| **NFR8** | No production or causal claims | README, memo, model card |

---

## 3. Out of scope for V1

- A real bank pilot or data-sharing agreement (V1.1/V2).
- FiFAR capacity/analyst layer (V2).
- Transaction-fraud extension (V2).
- A dashboard, database, or auth system.
- A new estimator or theoretical result.
- Production integration or vendor replacement.
- A causal deployment effect.
- A point-identified full-population value.

---

## 4. Risks and mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Sweep shows the bias is parameter-dependent | Medium-high | The headline narrows | Report the conditional claim; keep the correction and the gate as the contribution |
| F5 cannot be fixed cheaply | High | The bounds are weaker | Record the failure; drop the coverage claim; report partial identification |
| Report gate is too strict for small logs | Medium | Usability | Make it a clear warning with "not identified," not a silent pass |
| Score pipeline cannot be reproduced | Medium | Level 1 claim weakens | Narrow the claim; publish the gap and the hash |
| No external reader by Dec 15 | Medium | Review package incomplete | Use the red-team + one strong peer; plan January |
| Six weeks too short | Medium | Scope cut | Cut to validation report, model card, pilot protocol, report gate |
| A partner asks for PII/proprietary data | Low | Catastrophic | Decline without a DPA and sandbox |
| Overclaiming in derived docs | Medium | Reputational | Claim ledger; red team; external review |

---

## 5. Traceability

| Requirement | Experiment | Evaluation | Roadmap |
|---|---|---|---|
| FR1 | E1 observation sweep | Evidence tier E2 | Phase 0 |
| FR2 | E2 bounds F5 | F5 gate | Phase 0–1 |
| FR3 | E3 report gate | Gate pass/fail | Phase 1 |
| FR4 | E4 reproducibility | Score/hash check | Phase 2 |
| FR5 | E5 adapter | Data-quality report | Phase 2 |
| FR6 | Demo | Timed run | Phase 2 |
| FR7 | Review package | Artifact checklist | Phase 2–3 |
| FR8 | Tests/CI | CI green | Phase 2 |
| FR9 | Docs/claim ledger | Link/claim audit | Phase 3 |
| FR10 | Release | v1.0.0 tag | Phase 4 |
