# Validation Report — V1

**Status:** V1 validation record, updated 2026-11-28.
**Subject:** `onboarding-audit` v1.1.0, the Decision Reliability pre-release
(evidence baseline v1.0.0).
**Verdict:** Level 2 (review-ready). Level 3 (partner pilot) is not claimed.

> **Release status (2026-11-28):** `v1.1.0` is a Decision Reliability pre-release;
> the public-release gate — two external readers or a documented fallback — is
> still open. See
> [`RELEASE_STATUS.md`](RELEASE_STATUS.md). This report records the evidence at
> the tag; [`CLAIMS.md`](CLAIMS.md) is the live claim ledger.

This report is the reviewer's index to the evidence. It does not replace the
claim ledger, the model card, or the generated artifacts; it states what was
run, what passed, what failed, and what remains unverified.

---

## 1. Scope

| Item | Statement |
|---|---|
| System | Offline policy-evaluation layer for account-opening fraud decisions |
| Version | `1.0.0` |
| Data | BAF `Base.csv` (public, synthetic), test months 5–6 |
| Primary estimand | Mean realized cost per application on `P0` |
| Review level targeted | Level 2: a fintech model-risk reviewer can audit the code, the evidence, and the claims |
| Not claimed | Level 3 pilot, production estimate, causal effect of a live policy change |

## 2. Environment

| Item | Value |
|---|---|
| Python | 3.10 (local run) |
| OS | Windows 11 (local run) |
| Package | `pip install -e ".[dev,baf]"` |
| Test command | `pytest -q` |
| Test result | **119 passed** in the current tree (92 at the `v1.0.0` tag) |
| Link check | `python scripts/check_links.py` → **0 missing links** |
| CI | `.github/workflows/ci.yml`, Python 3.10–3.12; run 44918141562 green |

The CI workflow runs the tests, the demo, the claim check, and the link check.

## 3. Code-level evidence

| Check | Evidence | Result |
|---|---|---|
| Full-observation identity | `tests/test_estimators.py::test_full_observation_identity` | pass |
| Full-audit identity | `tests/test_estimators.py` | pass |
| Negative controls | `tests/test_estimators.py`, `tests/test_propensity.py` | pass |
| Identification gate | `tests/test_gates.py` (15 tests) | pass |
| Gate integration in the report | `tests/test_report.py` | pass |
| 20-row demo withholds estimates | `tests/test_report.py::test_report_withholds_point_estimate_on_small_log` | pass |
| End-to-end demo | `tests/test_demo.py` | pass |
| Headline numbers match the committed JSON | `scripts/check_claims.py`, `tests/test_claims.py` | pass (62/62) |
| Double robustness | `scripts/double_robustness.py`, `tests/test_double_robustness.py` | pass |
| Temporal stability | `scripts/temporal_stability.py`, `reports/temporal_stability.json` | pass (both months) |
| Bounds widen with the `P0` standard error | `tests/test_estimators.py` | pass |
| Decision reliability profile | `tests/test_reliability.py`, `tests/test_report.py`; memo §4.2 | pass |
| F5 fields in the summary | `tests/test_metrics.py` | pass |

## 4. Identification gate

The report refuses a point estimate unless all of the following hold:

| Check | Threshold | Test |
|---|---|---|
| Positivity | every observed `P0` row has `e > 0` (provided column); every `P0` row (estimated) | `test_positivity_failure_refuses` |
| Observed labels | ≥ 100 | `test_small_sample_refuses` |
| Labels per non-rejected action | ≥ 30 | `test_small_sample_refuses` |
| Effective sample size | ≥ 100 | `test_low_ess_refuses` |
| Max weight | ≤ 100 | `test_low_ess_refuses` |
| Cost support | no negative cost | `test_negative_cost_refuses` |
| Declared outcome-dependent observation | refuse | `test_declared_outcome_dependent_refuses` |
| Undeclared observation mechanism | warn; memo marks the estimate unverified | `test_undeclared_observation_mechanism_warns` |

Warnings (not refusals): candidate actions outside `P0` above 10%, observed
sample below 500, ESS below 500, max weight above 50, `e_min < 0.01`, and
estimated propensities without an audit.

**Observed behavior.** On the committed 20-row `examples/sample_log.csv`, the
gate reports **“Not identified”** with four reasons and withholds the point
estimates from both the memo and the CLI. The JSON keeps the diagnostic numbers
for debugging; the `policy_value_target_5pct` sizing is omitted because it would
be computed from an unidentified point estimate.

## 5. Observation-rate sweep (E1)

| Item | Value |
|---|---|
| Design | 12 cells: `e_approve` ∈ {0.01, 0.05, 0.20, 0.50} × `kappa_review` ∈ {0.50, 0.90, 1.00} |
| Replications | 50 per cell |
| Command | `onboarding-audit pilot --config configs/obs_sweep.yaml` |
| Artifact | `reports/obs_sweep/pilot.json` |
| Summary | `reports/obs_sweep/obs_sweep.md`, `reports/obs_sweep/obs_sweep_summary.csv` |

| Result | Value |
|---|---|
| Naive relative bias | **7.8% to 538.5%** (max across policies) |
| Cells with naive bias > 5% | **12/12** for at least one policy; incumbent **11/12** |
| DR mean relative bias (known `e`) | **1.89%**; 95% MC upper bound **4.3%** (`e>=0.05`), **9.6%** (`e=0.01`) |
| DR coverage (known `e`) | **84.5% to 96.0%** |
| DR P(select the true best policy) | **64%** at `e_approve=0.01`; **96–100%** at `e_approve=0.50` |
| Naive P(select the true best policy) | **0%** in 11/12 cells; **52%** at `e050_k050` |

Interpretation: the premise (naive evaluation is biased) holds in every cell;
the magnitude is conditional on the observation rates. The main-scenario
**112–278%** is one point in the sweep, not a universal number.

## 6. Bounds (F5)

Recorded by the pilot in `reports/pilot.json` and `reports/pilot.md`:

| Field | Meaning |
|---|---|
| `coverage_full` | Share of replications where the narrow (conditional) partial-identification interval covers the true full-population value |
| `f5_pass` | `coverage_full >= 90%` |
| `lower_unconditional`, `upper_unconditional` | The interval widened by the `P0` standard error, scaled by the `P0` share |
| `unconditional_coverage` | Coverage of the widened interval |
| `f5_pass_unconditional` | `unconditional_coverage >= 90%` |

F5 status: **failed for the narrow interval, passed for the widened interval.**

| Interval | F5 pass | Main-scenario coverage |
|---|---:|---:|
| Narrow | **15/88** | 34–87% |
| Widened | **77/88** | 99–100% |

The 11 widened-interval failures are exactly the cells where the `P0` estimate
is biased (outcome-dependent labels, action-level covariate misspecification,
`delay_90`). The coverage claim for the narrow interval is removed; the widened
interval is reported as a valid (conservative) 95% interval under the
identification assumptions, with its width.

The narrow interval is
**conditional on the `P0` estimate**, not a confidence interval. A narrow
interval on a noisy `P0` estimate can miss; the incumbent's narrow interval is
the case that fails.

## 7. Benchmark reproducibility

`scripts/prepare_baf.py` rebuilds `data/scored_test.parquet` from the public
`Base.csv`:

1. Load, add `transaction_id` and `amount_proxy`, sort by month.
2. Simulate the one-month label delay.
3. Split months 0–2 (train), 3–4 (validation), 5–6 (test).
4. Fit the incumbent logistic regression (C=10) and the candidate LightGBM
   (300 trees, 0.05 learning rate); refit the random forest as a diagnostic.
5. Write the 39-column test frame and a provenance sidecar with the input hash,
   the output hash, the model parameters, the library versions, and per-score
   column hashes.

`--verify` compares the output to the recorded SHA-256
(`f5efd678…f331593`) and exits non-zero on a mismatch.

**Verified on 2026-11-21.** The rebuild produced 227,491 rows with SHA-256
`f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593` — an exact
match. scikit-learn 1.7.2, lightgbm 4.7.0. The record, including the raw-file
hash and the per-score column hashes, is in
[`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md).

## 8. What is not verified

| Item | Status |
|---|---|
| The rebuilt benchmark reproduces the recorded hash on this machine | **verified** (exact match) |
| The same hash on a different library version | not verified; provenance records versions |
| A partner-institution log | not available |
| The cost matrix | assumed, not measured |
| The Level 3 pilot | not run |
| External readers | not yet engaged; the public-release gate is open |
| Unmeasured confounding in a real log | not testable from the log alone |

## 9. Release gates

| Gate | Status |
|---|---|
| Tests pass | **pass** (119 in the current tree; 92 at the tag) |
| Link check | **pass** (0) |
| Identification gate integrated and tested | **pass** |
| Observation sweep committed | **pass** |
| F5 recorded | **narrow: fail (15/88); widened: pass (77/88)** |
| Benchmark reproducible | **pass** (exact SHA-256 match) |
| Model card | **pass** |
| Pilot protocol | **pass** |
| Business case | **pass** |
| CI green on GitHub | **pass** (run [44918141562](https://github.com/kira-ml/onboarding-audit/actions/runs/44918141562)) |

## 10. Reviewer checklist

1. Read [`MODEL_CARD.md`](MODEL_CARD.md) and [`CLAIMS.md`](CLAIMS.md).
2. Run `pytest -q`.
3. Run `onboarding-audit demo --out reports/demo`.
4. Inspect the gate refusal on `examples/sample_log.csv`.
5. Re-run `scripts/prepare_baf.py --verify` if you have `Base.csv`.
6. Re-run the sweep and compare to `reports/obs_sweep/pilot.json`.
7. Challenge §8. If an item there matters to your decision, it is not yet
   answered.

## 11. Related documents

- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Model card: [`MODEL_CARD.md`](MODEL_CARD.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Testing: [`TESTING.md`](TESTING.md)
- Pilot protocol: [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md)
