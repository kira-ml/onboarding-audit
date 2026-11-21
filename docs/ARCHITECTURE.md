# Architecture

**Status:** Canonical code map for v0.2.1 (2026-11-20).
**Purpose:** Explain how the package is organized, how data flows from a
decision log or the BAF frame to a report, and which invariants the code
protects. This is the document to read before changing the implementation.

---

## 1. Package layout

```
src/onboarding_audit/
  config.py       Typed configuration and YAML loading
  data.py         BAF frame loading, decision-day assignment, feature scaling
  policies.py     Cost-sensitive actions, review capacity, realized cost
  observation.py  Observation model, delay resolution, audit, label draws
  propensity.py   Action-level, noisy, and covariate propensity estimation
  estimators.py   Naive, IPW-HT, IPW-Hajek, DR, audit-only, bounds
  metrics.py      Bias, RMSE, coverage, ESS, ranking, bounds summaries, verdict
  pilot.py        Scenario runner, pilot report writer, CLI entry point
  sensitivity.py  Propensity/covariate sensitivity runner and report
  report.py       Arbitrary-log validation, evaluation, memo, JSON
  schema.py       Decision-log schema validation
  cli.py          `pilot`, `report`, `sensitivity`, `validate`
```

The package is intentionally small and flat. There is no service, database, or
web layer. The artifact is a reproducible evaluation library and CLI.

## 2. Data flow

### 2.1 Pilot path

```
configs/pilot.yaml
        |
        v
config.load_config  --->  PilotConfig
        |
        v
data.load_eval_data  --->  EvalData (df, y, amount, month, decision_day, X)
        |
        v
pilot.build_policy_set  --->  PolicySpec[]
policies.build_policy   --->  PolicyActions (actions, cost components)
        |
        v
observation.build_observation_model  --->  ObservationModel (propensity, p_resolved)
        |
        v
for each replication:
    observation.draw_observation  --->  ObservationDraw (observed, audit, source)
    propensity.<mode>             --->  e_est
    estimators.fit_outcome_model  --->  phat
    estimators.{naive, ipw_ht, ipw_hajek, dr, audit_only, policy_bounds}
        |
        v
metrics.summarize / ranking_metrics / bounds_summary / verdict
        |
        v
reports/pilot.json + reports/pilot.md
```

### 2.2 Arbitrary-log report path

```
log file (CSV/parquet) ---> schema.validate_log ---> errors or ok
        |
        v
report.estimate_propensities
    provided column, action-level estimate, or covariate model
        |
        v
report._candidate_actions (score -> actions, capacity cap)
        |
        v
report.evaluate_report
    naive/IPW/DR/audit-only, diagnostics, bounds, audit recommendation
        |
        v
report.write_memo + report.json
```

### 2.3 Sensitivity path

```
configs/pilot.yaml ---> config.load_config
        |
        v
data.load_eval_data
        |
        v
for each selected scenario:
    pilot.run_scenario  --->  row-level results
        |
        v
metrics.summarize ---> reports/propensity_sensitivity.json + .md
```

## 3. Module responsibilities

### `config.py`

- Frozen dataclasses: `Costs`, `Observation`, `OutcomeModel`, `PolicySpec`,
  `Scenario`, `PilotConfig`.
- `load_config` validates types, unique scenario IDs, capacity bounds, propensity
  modes, observation modes, and the covariate parameters.
- The first policy must be named `incumbent`; it is the logging policy.

### `data.py`

- Loads a scored BAF parquet.
- Validates the label, amount, month, and feature columns.
- Assigns a uniform decision day within months 5 and 6 (cutoff day 90).
- Standardizes the outcome-model matrix with `StandardScaler` on the evaluation
  window. The scaler uses features only, not labels; this is an unsupervised
  preprocessing choice, not target leakage.
- Adds `log1p(amount)` and `month` to the feature matrix.

### `policies.py`

- `fraud_loss`: amount-scaled or flat fraud loss.
- `choose_actions`: argmin of expected cost over approve/review/reject.
- `apply_capacity`: caps review at `K` by ranking the savings from review; routes
  overflow to approve or reject.
- `build_policy`: builds a policy from a score column and a `PolicySpec`.
- `realized_cost`: the evaluation cost of a realized action and outcome.

The policy's decision cost may differ from the evaluation cost through
`decision_false_reject_cost`; the evaluation cost is common across policies.

### `observation.py`

- `p_resolved`: lognormal delay resolution probability.
- `build_observation_model`: action-dependent or covariate-dependent channel
  probabilities; audit mixture; positivity check.
- `draw_observation`: resolves labels, draws review/report/audit channels, and
  records `label_source`.
- `ObservationModel` stores `propensity`, `p_resolved_review`,
  `p_resolved_approve`, `kappa_review_vec`, and `e_report_vec`.
- `ObservationDraw` stores `observed`, `audit`, `resolved_*`, `observed_*`, and
  `label_source`.

### `propensity.py`

- `estimate_from_draw`: action-level marginal `e` from one draw, audit-aware.
- `noisy_copy`: mean-one lognormal noise, clipped, zeros preserved.
- `fit_covariate_propensity`: per-action logistic `P(observed | action, X)` with
  cross-fitting. Reject rows stay at zero.

### `estimators.py`

- `naive`, `ipw_ht`, `ipw_hajek`, `dr`, `audit_only`, `policy_bounds`.
- `fit_outcome_model`: cross-fitted weighted logistic regression.
- `expected_cost`: outcome-model expected cost per action.
- `effective_sample_size`, `coverage`.
- Every estimator returns `Estimate(value, se, n_used, ess, max_weight)`.

### `metrics.py`

- `summarize`: bias, relative bias, RMSE, coverage, mean SE, MC SE, ESS, max
  weight, per scenario/policy/estimator.
- `ranking_metrics`: Spearman, pairwise inversions, P(select true best), cost of
  misranking.
- `bounds_summary`: width and full-population coverage.
- `verdict`: H1–H6 checks from the pilot output.

### `pilot.py`

- `build_policy_set`: the four policies and the scenario capacity override.
- `run_scenario`: the replication loop; builds the observation model, draws
  labels, selects the propensity mode, fits the outcome model, runs every
  estimator and bounds, and returns rows plus diagnostics.
- `run_pilot`: loads data, filters scenarios, runs, writes JSON/Markdown.
- `write_report`: the pilot report with headline, rankings, audit sweep, bounds,
  and verdicts.

### `sensitivity.py`

- Runs the pre-declared propensity sensitivity scenarios: action-level,
  noisy, outcome-dependent, and covariate-dependent.
- Writes `reports/propensity_sensitivity.json` and `.md`.
- `write_markdown` can re-render the Markdown from the committed JSON without
  rerunning the study, so the prose and table stay in sync.

### `report.py`

- `validate_log` via `schema.py`.
- `estimate_propensities`: provided, action-level, or covariate.
- `_candidate_actions`: derives candidate actions from a score and capacity.
- `evaluate_report`: estimates, diagnostics, bounds, audit recommendation.
- `write_memo`: the audit-ready memo.
- `run_report`: the orchestration entry point.

### `schema.py`

- Validates the required fields, action enum, score range, reviewed/audit
  consistency, label/timestamp consistency, and propensity range.
- Reports which estimators the log can support.

### `cli.py`

- `pilot`: run the pre-registered pilot.
- `report`: evaluate a candidate from a log and candidate scores.
- `sensitivity`: run the propensity/covariate sensitivity.
- `validate`: validate a log schema.

## 4. Invariants

1. **No label leakage.** The outcome model and policy use pre-decision features
   only. The schema validator warns about post-decision fields. The
   `test_no_leakage` permutation test protects the split.
2. **Deterministic policies.** Actions are a deterministic function of the score,
   amount, cost matrix, and capacity. The candidate policy never sees the
   evaluation labels.
3. **Positivity on `P0`.** `build_observation_model` raises if a non-rejected row
   has zero observation probability.
4. **Capacity is enforced.** `build_policy` asserts that the review count does
   not exceed `K`.
5. **Audit is post-approval only.** `audit_flag=1` implies `action=approve`; the
   validator rejects inconsistent logs.
6. **Bounds are conditional.** `policy_bounds` takes the `P0` estimate as input;
   it does not pretend to be a confidence interval.
7. **Reject rows have `e=0`.** The propensity model and estimators exclude them
   from `P0`; they enter only the bounds.
8. **One source of truth for numbers.** Public numbers trace to
   `reports/pilot.json`, `reports/propensity_sensitivity.json`, or a cited
   primary source, and appear in `docs/CLAIMS.md`.

## 5. Extension points

### Add an estimator

1. Add a pure function to `estimators.py` returning `Estimate`.
2. Add it to the `estimates` dict in `pilot.run_scenario` and
   `report.evaluate_report`.
3. Add a metric/target mapping in `metrics.summarize` if needed.
4. Add a test with a known identity or ground truth.
5. Add a claim to `docs/CLAIMS.md` and a decision if it changes the estimand.

### Add a scenario

1. Add a row to `configs/pilot.yaml` with a unique `id`.
2. State the purpose in `docs/PILOT_SPEC.md` §8.
3. Run a 5-replication smoke test.
4. Run the full scenario.
5. Add the result to `docs/CLAIMS.md` and `docs/RESULTS.md`.

### Add a dataset

1. Add a loader that produces the `EvalData` fields (`df`, `y`, `amount`,
   `month`, `decision_day`, `X`, `feature_names`, `n`).
2. Keep the policy/estimator layer unchanged.
3. Add a data card and update `docs/DATA.md`.
4. Re-run the negative controls and the main scenario.

### Add a report field

1. Add the field to `schema.py` and `docs/SCHEMA.md`.
2. Add it to `report.estimate_propensities` or `evaluate_report`.
3. Add a memo line and a JSON key.
4. Add a test for missing/invalid values.

## 6. Testing map

| Test file | Protects |
|---|---|
| `test_estimators.py` | Full-observation identity, full-audit identity, propensity recovery, bounds validity |
| `test_observation.py` | Delay monotonicity, positivity, empirical frequency, outcome-dependent labels, covariate gradient |
| `test_policies.py` | Capacity, cost accounting, action construction |
| `test_metrics.py` | Bias, coverage, ranking, bounds summaries |
| `test_no_leakage.py` | Permutation/no-leakage control |
| `test_schema.py` | Required fields, action/flag consistency, invalid logs |
| `test_report.py` | Known-truth report, missing propensity, no audit, missing IDs, covariate model |
| `test_gates.py` | Positivity, overlap/ESS, sample size, cost support, candidate outside P0 |
| `test_propensity.py` | Action-level estimate, noise, covariate recovery, reject zeros |
| `test_sensitivity.py` | Markdown rendering from the committed JSON; no invented numbers |
| `test_config.py` | Scenario parsing and covariate fields |

See [`TESTING.md`](TESTING.md) for the strategy and gaps.

## 7. Design decisions

The architecture follows the decision journal:

- D1: account-opening reframing.
- D2: primary estimand `P0`.
- D3: audit design (post-hoc verification, shadow scoring).
- D4: cost matrix normalization.
- D5: pilot uses oracle propensities.
- D6: H2/H3 evaluation split.
- D7/D8: bounds are not confidence intervals.
- D9: action-level propensities when absent.
- D10: propensity sensitivity is a claim gate.
- D11: covariate propensity model when observation depends on the application.

See [`DECISIONS.md`](DECISIONS.md).

## 8. Known architectural limits

- The pilot is a single-process NumPy/scikit-learn loop. It is reproducible but
  not optimized for very large logs; the arbitrary-log report is the scalable
  path.
- The covariate propensity model is a logistic approximation. A real log may
  need a more flexible model, splines, or a domain-specific design.
- The variance estimators are influence-function approximations. Heavy-tailed
  weights can undercover; the report exposes ESS and weight tails but does not
  bootstrap.
- The package does not include a database, API, or dashboard. That is
  intentional: the artifact is the measurement layer, not a platform.
