# V1 Evaluation Methodology

**Status:** Planning, 2026-11-21.
**Purpose:** Define how V1 decides what is true, what is claimable, and what is
ready for release. The rule is simple: **no claim above its evidence tier.**

---

## 1. Evidence tiers

| Tier | Meaning | Example |
|---|---|---|
| **E0** | Assertion or opinion | "A risk team would run this" without a partner |
| **E1** | Code/doc inspection or a single example | A 20-row demo; a unit test |
| **E2** | Simulation or benchmark with known ground truth | BAF pilot; observation sweep |
| **E3** | External real-world data or review | A real log; an external reader; a legal review |
| **E4** | Independent replication or production use | Another team reproduces the result |

**V1 rule:** a public claim must be at least E2, and its tier must be stated.
V1 does not claim E3 or E4 for the pilot.

---

## 2. Claim matrix

| Claim | Current tier | V1 target tier | Test | Status |
|---|---|---|---|---|
| Naive evaluation is biased under plausible observation rates | E2 (one scenario) | E2 (12-cell sweep) | E1 | **Supported** |
| The naive estimate can reverse the policy ranking | E2 (one scenario) | E2 (12-cell sweep) | E1 | **Supported** |
| The bias magnitude is conditional on observation rates | E0 | E2 (12-cell sweep) | E1 | **Supported** |
| DR recovers `P0` when positivity and the observation model hold | E2 (oracle/estimated) | E2 (sweep + sensitivity) | E1 | **Supported with oracle `e`; estimated `e` separate** |
| The corrected ranking weakens at low approve-label rates | E0 | E2 (12-cell sweep) | E1 | **Supported** |
| Audit-only is honest under outcome-dependent labels | E2 | E2 | Existing sensitivity | Supported |
| The reject margin is not point-identified | E2 | E2 | E2 | Open |
| The bounds are a partial-identification interval, not a CI | E0/E2 | E2 with F5 record | E2 | Open |
| The tool refuses to report an unidentified estimate | E1 | E1/E2 (gate tests) | E3 | Open |
| The benchmark is reproducible | E0/E1 | E1/E2 | E4 | Open |
| A risk team can review the package | E0 | E1/E2 | Review package + readers | Open |
| A risk team has run it on a real log | E0 | Not claimed in V1 | — | Deferred |

---

## 3. Metrics

### 3.1 Estimator metrics

| Metric | Definition | Use |
|---|---|---|
| Relative bias | `(mean estimate - true) / true` | Is the estimator centered? |
| RMSE | `sqrt(mean((estimate - true)^2))` | Accuracy including variance |
| Coverage | Share of 95% intervals containing the truth | Is uncertainty calibrated? |
| ESS | `(sum w)^2 / sum w^2` | Weight concentration |
| Max weight | `max w_i` | Single-row dominance |
| Rank inversion | Pairwise disagreement with the true ranking | Decision quality |
| P(select true best) | Share selecting the true lowest-cost policy | Decision quality |
| Cost of misranking | True cost of selected minus true best | Economic size |

### 3.2 Bounds metrics

| Metric | Definition | Use |
|---|---|---|
| Width | `U - L` | Precision cost of the reject margin |
| F5 coverage | Share of intervals containing `V_full` | Pre-registered control |
| Unconditional coverage | Coverage of `[L(v_pop ± 1.96 se), U(...)]` | Diagnostic |
| Reject share | Share of logging-rejected rows | Materiality |

### 3.3 Gate metrics

| Metric | Definition | Target |
|---|---|---|
| Adversarial refusal rate | Share of invalid logs refused/flagged | 5/5 |
| False refusal rate | Share of valid logs refused | 0/2 |
| "Measured" on invalid logs | Count | 0 |
| Time to run | Wall-clock | <1 min for 20k rows |

### 3.4 Reproducibility metrics

| Metric | Definition | Target |
|---|---|---|
| Row count | Processed vs source | Exact |
| Label distribution | Fraud rate | Exact/tolerance |
| Score correlation | Reproduced vs committed | >0.99 |
| Max absolute score difference | Reproduced vs committed | <1e-3 |
| SHA-256 | Processed file/score columns | Match or documented gap |

---

## 4. Gates

### G1 — No claim above its evidence tier

A public claim must be at least E2 and state its tier. E0/E1 claims are labeled
"assumption" or "demo," not "measured."

### G2 — No "Measured" without an identification pass

The memo claim ledger uses the gate result. If positivity or cost support fails,
the memo says "not identified" and does not print a point estimate.

### G3 — No bounds coverage claim if F5 fails

If F5 coverage is <90%, the docs say "F5 failed" and report the bounds as a
partial-identification interval. No "95% CI" language.

### G4 — No Level 3 claim without a real log

The README, paper, and model card may claim Level 2 (review-ready) but not Level
3 (pilot-proven) without a real historical log and a risk-team review.

### G5 — No release with an unresolved critical red-team finding

Every critical finding must be closed, narrowed, or explicitly residual in
`docs/RED_TEAM_CREDIBILITY_PLAN.md` and `docs/CLAIMS.md`.

### G6 — No public number without an artifact

Every number in the README, one-pager, or paper traces to a committed JSON or a
cited primary source.

---

## 5. Review protocol

### 5.1 Internal red team

- Run an independent red-team review of the V1 package.
- Record findings with severity, evidence, and a disconfirming test.
- Close or narrow every critical finding.

### 5.2 External readers

- Two readers: a fraud/KYC practitioner and a researcher.
- 30-minute call; show the one-pager, validation report, and pilot protocol.
- Ask: "Where would you reject this? What would you need to believe?"
- Record objections in `docs/EXTERNAL_REVIEW.md`.

### 5.3 Claim ledger audit

- Every public claim appears in `docs/CLAIMS.md`.
- Every measured number traces to `reports/pilot.json`,
  `reports/propensity_sensitivity.json`, or `reports/obs_sweep/pilot.json`.
- No derived document introduces a new claim.

### 5.4 Link and stale-number check

- Run the relative-link check; target 0 missing.
- Search for stale headline numbers and "v0.1" markers.
- Check the README, one-pager, and model card for consistency.

---

## 6. Release gate

V1 is releasable only when:

- [ ] E1 sweep complete; claim conditional.
- [ ] E2 F5 recorded; bounds language corrected.
- [ ] E3 gate tests pass; no "Measured" on invalid logs.
- [ ] E4 pipeline reproduced or claim narrowed.
- [ ] E5 demo runs in <10 minutes.
- [ ] 50+ tests; CI green.
- [ ] Review package complete.
- [ ] Two external readers (or a documented fallback).
- [ ] No unresolved critical red-team finding.
- [ ] `docs/CLAIMS.md`, `README.md`, and the model card agree.
- [ ] v1.0.0 tag.

---

## 7. What counts as success

**Scientific success:** the V1 claim is conditional and measured; the failed
controls are recorded; the tool refuses to overclaim.

**Engineering success:** a reviewer can install, run, and inspect the demo and
the report without the author.

**Portfolio success:** the release demonstrates research discipline, engineering
discipline, and communication discipline, with a defensible interview story.

## 8. What counts as failure

- The headline remains a single-scenario claim.
- F5 is still reinterpreted rather than recorded.
- The report still prints "Measured" on unidentified logs.
- The benchmark cannot be reproduced and the claim is not narrowed.
- The package is incomplete and no reviewer is engaged.
- A public claim exceeds its evidence tier.

## 9. Evidence log template

| Date | Claim | Tier | Artifact | Test | Status | Residual risk |
|---|---|---|---|---|---|---|
| | | E0–E4 | | | | |

## 10. Related documents

- Experiments: [`EXPERIMENTS.md`](EXPERIMENTS.md)
- Requirements: [`REQUIREMENTS.md`](REQUIREMENTS.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Current claim ledger: [`../CLAIMS.md`](../CLAIMS.md)
- Current threats: [`../THREATS.md`](../THREATS.md)
