# Testing

**Status:** Canonical test guide for v0.2.1 (2026-11-20).
**Purpose:** Explain what the test suite protects, how to run it, and which
failure modes are not covered. Tests are part of the research claim: a
correction that cannot pass a known-truth identity is not evidence.

---

## 1. Run the suite

```bash
pytest -q
```

Expected: **92 passed** on the v0.2.1 tree. The suite uses only synthetic or
small in-memory data; it does not require `data/scored_test.parquet`.

The headline numbers are also checked directly against the committed JSON:

```bash
python scripts/check_claims.py
```

Expected: **27/27 checks passed**. This is the executable form of the claim
ledger's rule: every public number traces to a committed artifact.

Optional:

```bash
pytest -q tests/test_estimators.py
pytest -q -k "covariate or propensity"
pytest -q --maxfail=1
```

## 2. Test philosophy

The suite uses four kinds of checks:

1. **Identities.** When the observation probability is 1, IPW/DR must equal the
   full-sample mean. When the audit covers everyone, audit-only must equal the
   approved mean. When the action is reject and the outcome is fraud, the cost
   is zero.
2. **Known ground truth.** The report test compares DR and naive against a
   computed true `P0` value. The covariate test recovers a known logistic
   gradient.
3. **Negative controls.** The no-leakage test permutes labels and checks that the
   policy actions do not change. The schema tests reject inconsistent logs.
4. **Boundary and failure behavior.** Capacity is never exceeded; negative
   amounts fail; missing candidate IDs fail; invalid actions fail.

The tests are not a substitute for the 50–100 replication Monte Carlo studies.
They protect the implementation, not the external validity of the simulation.

## 3. What each file protects

### `tests/test_estimators.py`

| Test | What it proves |
|---|---|
| `test_full_observation_identity` | With `e=1` for all observed rows, IPW/DR equal the full mean |
| `test_ess_bounds` | ESS is between 1 and `n`; weights are finite |
| `test_bounds_contain_true_full_value` | The min/max cost bounds contain the true full value in a constructed case |
| `test_audit_only_full_audit_is_unbiased` | A full audit recovers the approved mean |
| `test_expected_cost_matches_realized_for_extremes` | The outcome-model expected cost agrees with realized cost at `p=0` and `p=1` |
| `test_outcome_model_returns_probabilities` | Cross-fitted predictions are in `(0,1)` |
| `test_ipw_weights_large_for_low_propensity` | Low propensity produces large weights, as expected |

### `tests/test_observation.py`

| Test | What it proves |
|---|---|
| `test_p_resolved_is_monotone_in_decision_day` | Later decision days have lower resolution probability |
| `test_zero_delay_resolves_everything` | A near-zero delay resolves all rows |
| `test_propensity_positive_for_non_rejected` | Positivity holds for a mixed action vector |
| `test_empirical_observation_frequency_matches_propensity` | The draw matches the modeled propensity |
| `test_full_observation_observes_all_non_rejected` | `kappa=1`, `e=1`, `audit=1` observes every non-rejected row |
| `test_outcome_dependent_approved_fraud_is_more_observed` | Fraud is observed at `e_approve_fraud`; legitimate only by audit |
| `test_covariate_observation_has_a_gradient_and_positive_propensity` | The covariate mechanism creates a gradient and stays positive |
| `test_covariate_observation_requires_a_covariate` | The covariate mode fails loudly without a covariate |

### `tests/test_policies.py`

| Test | What it proves |
|---|---|
| `test_actions_are_valid_and_capacity_is_respected` | Actions are in the enum; review count <= capacity |
| `test_review_capacity_never_exceeded` | The cap holds across a range of capacities |
| `test_realized_cost_identities` | Cost identities for approve/review/reject and fraud/legit |
| `test_rejecting_fraud_costs_zero` | Rejecting fraud has zero fraud loss |
| `test_choose_actions_extremes` | `p=0` approves, `p=1` rejects |
| `test_apply_capacity_overflow_is_rerouted` | Overflow goes to the cheaper of approve/reject |
| `test_negative_amount_rejected` | Invalid amounts fail |

### `tests/test_metrics.py`

- Pairwise inversions on a known ranking.
- Ties are not counted as inversions.

### `tests/test_no_leakage.py`

- Permutes the labels and checks that policy actions are unchanged. This is the
  no-leakage control: the policy must not depend on the evaluation outcome.

### `tests/test_schema.py`

- A valid log passes.
- Missing required columns fail.
- Invalid actions fail.
- `reviewed=1` requires `action=review`.
- `audit_flag=1` requires `action=approve`.
- A missing label breaks the naive estimator.

### `tests/test_report.py`

| Test | What it proves |
|---|---|
| `test_report_runs_and_dr_beats_naive` | The report runs end to end; DR is closer to the true `P0` value than naive on a synthetic log with known ground truth |
| `test_report_estimates_propensity_when_missing` | Action-level estimation runs when the log has no propensity column |
| `test_report_without_audit_has_no_audit_only_estimate` | No audit labels means `audit_only` is `n/a` |
| `test_report_rejects_missing_candidate_ids` | The candidate file must cover every application |
| `test_report_rejects_invalid_log` | The report refuses an invalid log |
| `test_covariate_propensity_model_varies_within_action` | The covariate model recovers a known within-action gradient |
| `test_report_covariate_propensity_model_runs` | The covariate report path writes the memo and exposes the model |

### `tests/test_gates.py`

- A valid log passes the identification gate.
- Positivity, negative cost, small sample, and low ESS fail with reasons.
- A declared outcome-dependent mechanism refuses; an undeclared mechanism warns.
- Candidate actions outside `P0` and estimated propensities without an audit
  warn without blocking a valid `P0` estimate.

### `tests/test_demo.py`

- The end-to-end demo passes the gate, uses the estimated-propensity path, writes
  a memo with “Measured,” and DR is closer to the known true `P0` than naive.

### `tests/test_propensity.py`

- Action-level review and approve estimates, including the audit-aware approve
  form.
- Reject rows stay at zero.
- Lognormal noise has mean near one, preserves zeros, and is identity at
  `sigma=0`.
- The covariate model recovers a known logistic gradient and keeps reject rows
  at zero.

### `tests/test_config.py`

- The pilot YAML parses the covariate scenarios with the expected
  `propensity_mode`, `observation_mode`, and `covariate_beta`.

### `tests/test_sweep.py`

- The observation sweep YAML parses 12 cells with the expected `e_approve` and
  `kappa_review` values.
- `Observation.with_overrides` accepts the two parameters.

### `tests/test_sensitivity.py`

- `write_markdown` renders the measured read from a payload.
- The rendered text contains the table values, not a stale hard-coded number.
- The renderer is the path used to regenerate the committed report from the
  JSON without rerunning the study.

## 4. What is not tested

| Gap | Why it matters | Next step |
|---|---|---|
| **No end-to-end CLI test on the full BAF file** | The pilot path is tested in pieces; a config or output-format regression could slip | Add a 1-replication CLI smoke test gated on the data file |
| **No bootstrap or randomization inference** | Influence-function intervals can undercover under heavy weights | Add a bootstrap option and a coverage test |
| **No property-based tests** | Hand-written cases may miss edge combinations | Add Hypothesis for action/capacity/cost invariants |
| **No fairness test** | The schema has segment fields but the pilot does not evaluate fairness | Add a segment-level diagnostic and a test |
| **No real-log test** | The report is tested on a synthetic 2,500-row log | Add a partner log or a public transaction log |
| **No performance test** | The pilot is ~1.1k s for 700 replications; the report is fast | Add a timing smoke test if the CLI grows |
| **No test that the memo numbers match the JSON** | The memo is generated from the same objects, but a formatting bug is possible | Add a snapshot test on a small log |
| **CI is basic** | The workflow runs tests, the demo, and the link check on 3.10–3.12; it does not lint or type-check yet | Add `ruff` and `mypy` |

## 5. Adding a test

1. Put the test in the file that matches the module under test.
2. Prefer an identity or a known ground truth over a snapshot of a random draw.
3. Use a fixed seed for any stochastic test.
4. Keep the test fast: the full suite should run in seconds.
5. If the test protects a claim, add the claim to `docs/CLAIMS.md`.
6. Run `pytest -q` and report the exact output.

## 6. Test data

- `tests/conftest.py` builds a small synthetic frame for policy tests.
- `tests/test_report.py` builds a synthetic decision log with known `P0` value.
- No test reads `data/scored_test.parquet`; the data file is local and
  gitignored.

## 7. Related documents

- Code map: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Claims: [`CLAIMS.md`](CLAIMS.md)
- Contributing: [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
