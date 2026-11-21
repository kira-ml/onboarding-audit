# V1 Architecture

**Status:** Planning, 2026-11-21.
**Purpose:** Define the target architecture for v1.0.0: the modules, data flows,
interfaces, invariants, and trade-offs needed for a review-ready release.

---

## 1. Current architecture

The package is a small, flat Python library and CLI:

```
src/onboarding_audit/
  config.py       Typed YAML configuration
  data.py         BAF frame loading, decision days, feature scaling
  policies.py     Cost-sensitive actions, review capacity, realized cost
  observation.py  Observation model, delay, audit, label draws
  propensity.py   Action-level, noisy, and covariate propensity estimation
  estimators.py   Naive, IPW-HT, IPW-Hajek, DR, audit-only, bounds
  metrics.py      Bias, RMSE, coverage, ESS, ranking, bounds, verdict
  pilot.py        Scenario runner, pilot report writer
  sensitivity.py  Propensity/covariate sensitivity
  report.py       Arbitrary-log validation, evaluation, memo
  schema.py       Decision-log schema validation
  cli.py          `pilot`, `report`, `sensitivity`, `validate`
```

There is no service, database, or web layer. The artifact is a reproducible
evaluation library and CLI.

## 2. V1 target architecture

```
onboarding-audit/
├── configs/
│   ├── pilot.yaml              # existing benchmark
│   └── obs_sweep.yaml          # NEW: 12-cell observation-rate sweep
├── scripts/
│   ├── prepare_baf.py          # NEW: reproducible BAF frame + scores
│   └── analyze_sweep.py        # NEW: compact sweep table from pilot.json
├── src/onboarding_audit/
│   ├── gates.py                # NEW: identification gate
│   ├── sweep.py                # NEW: sweep runner/summary (optional)
│   ├── report.py               # MODIFIED: gate integration, claim ledger
│   ├── pilot.py                # MODIFIED: F5 verdict, bounds construction
│   ├── metrics.py              # MODIFIED: F5, sweep summaries
│   └── ...                     # existing modules unchanged
├── examples/
│   ├── sample_log.csv          # existing demo (has propensity)
│   └── demo_log.csv            # NEW: no propensity, known truth
├── docs/V1/                    # NEW: this plan
├── .github/workflows/ci.yml    # NEW: tests, lint, smoke, link check
└── ...
```

### 2.1 New module: `gates.py`

The identification gate is the core product change. It answers:

> Is this log sufficient to report a point estimate for `P0`?

```python
@dataclass
class IdentificationReport:
    passed: bool
    reasons: list[str]
    metrics: dict[str, float]
    source: str  # "provided" | "action" | "covariate"
```

Checks:

| Check | Fail condition | Action |
|---|---|---|
| Positivity | `e <= 0` for any `P0` row | Refuse point estimate |
| Overlap/ESS | `ESS < 100` or `max weight > 100` | Flag; report diagnostic |
| Minimum sample | `< 30` observed rows per action | Flag; report diagnostic |
| Cost support | Any cost `< 0` | Refuse; fix the cost model |
| Candidate outside `P0` | Material share of candidate actions outside `P0` | Flag; report bounds only |
| Propensity source | `action` with no audit flag | Flag; recommend covariate/audit |

The gate returns reasons, not a single boolean. The memo prints the reasons.

### 2.2 Modified `report.py`

- Call `gates.check_identification` before `evaluate_report`.
- Pass the gate result into the memo.
- Replace the hardcoded
  `| P0 policy value is estimated | Measured | ... |` with:
  - `Measured` only if the gate passes and the estimator is finite;
  - `Not identified` with reasons if the gate fails.
- Refuse to print a point estimate when positivity or cost support fails.
- Add the observation-rate-by-amount-quintile diagnostic to the memo.
- Fix the 20-row demo so it no longer prints "Measured."

### 2.3 Modified `pilot.py` and `metrics.py`

- Compute F5 for every policy:
  - `F5_pass = coverage_full >= 0.90`;
  - `F5_coverage = coverage_full`.
- Record F5 in `pilot.json` and `pilot.md`.
- Use the same `v_pop` construction for pilot bounds and report bounds:
  - Option A: use DR for both.
  - Option B: record both IPW and DR bounds and report the difference.
- Add a `bounds_validation` block with the unconditional interval and its
  coverage.

### 2.4 New `configs/obs_sweep.yaml`

The sweep config reuses the pilot config and varies two observation parameters
per scenario. This requires `Scenario` to accept `e_approve` and `kappa_review`
overrides.

```yaml
# 12 cells: e_approve x kappa_review
scenarios:
  - {id: e001_k050, reps: 50, e_approve: 0.01, kappa_review: 0.50, ...}
  - ...
```

`run_scenario` overrides the observation config:

```python
obs_cfg = config.observation.with_overrides(
    audit_rate=scenario.audit_rate,
    approve_delay_median=scenario.approve_delay_median,
    outcome_dependent=scenario.outcome_dependent,
    e_approve=scenario.e_approve or config.observation.e_approve,
    kappa_review=scenario.kappa_review or config.observation.kappa_review,
)
```

### 2.5 New `scripts/prepare_baf.py`

The script must:

1. Load `Base.csv`.
2. Sort by month; split 0–2 / 3–4 / 5–6.
3. Fit the incumbent logistic regression and the candidate LightGBM.
4. Score the test window.
5. Write `data/scored_test.parquet`.
6. Write a `data/provenance.json` with the split, seed, row counts, and SHA-256
   hashes of the score columns and the processed file.

If the original pipeline cannot be reproduced exactly, the script must say so
and the Level 1 claim must narrow.

### 2.6 New `examples/demo_log.csv`

A synthetic 2,500-row log with:

- no `propensity` column;
- known true `P0` value;
- a realistic action mix;
- an audit flag;
- a post-approval label channel.

The demo runs `validate` and `report` and shows the gate flagging the estimated
propensity path.

### 2.7 New `.github/workflows/ci.yml`

- Python 3.10, 3.11, 3.12.
- `pip install -e ".[dev]"`.
- `pytest -q`.
- `ruff check` (add `ruff` to dev dependencies).
- `python -m onboarding_audit.cli demo` smoke test.
- Link check script.

## 3. Data flows

### 3.1 Observation sweep

```
configs/obs_sweep.yaml
  -> config.load_config
  -> data.load_eval_data
  -> for each cell: pilot.run_scenario
  -> reports/obs_sweep/pilot.json
  -> scripts/analyze_sweep.py
  -> reports/obs_sweep/obs_sweep.md
  -> docs/V1/EXPERIMENTS.md result table
  -> docs/CLAIMS.md conditional claim
```

### 3.2 Report with gate

```
log file -> schema.validate_log
  -> report.estimate_propensities
  -> gates.check_identification
       | pass -> evaluate_report -> memo with "Measured"
       | fail -> memo with "Not identified" + reasons; no point estimate
  -> report.json
```

### 3.3 Bounds validation

```
pilot.run_scenario
  -> policy_bounds (DR and IPW variants)
  -> metrics.bounds_summary
  -> F5 pass/fail + unconditional interval
  -> reports/pilot.json
  -> docs/RESULTS.md
```

## 4. Invariants

1. **No "Measured" without a gate pass.** The memo claim ledger uses the gate
   status, not a hardcoded string.
2. **No point estimate when positivity or cost support fails.** Report the
   reasons and the bounds.
3. **F5 is recorded.** The pilot JSON and Markdown say pass/fail explicitly.
4. **The bounds are not a confidence interval.** The docs and memo say
   partial-identification interval.
5. **Scores are reproducible or the claim is narrowed.** The provenance file and
   hash are mandatory.
6. **No PII or proprietary data.** Public/synthetic only until a DPA and sandbox.
7. **No production or causal claim.** The model card and README state this.
8. **No new methods in V1.** The scope is credibility, not features.

## 5. Trade-offs

| Decision | Option A | Option B | V1 choice | Why |
|---|---|---|---|---|
| Sweep runner | New `sweep` CLI | Config + existing `pilot` | B | Less code; the pilot already handles scenarios |
| Bounds construction | Use DR for both pilot and report | Record IPW and DR | A, with B as a diagnostic | Consistency; the difference is a finding |
| Report gate | Hard refusal | Warning + "not identified" | B for small logs; A for positivity/cost | Usability without overclaiming |
| Score pipeline | Include full training | Narrow the Level 1 claim | Include if feasible; otherwise narrow | A hostile reviewer needs provenance |
| V1 target | Level 3 pilot | Level 2 review-ready | Level 2 | No partner; Level 3 is V1.1/V2 |
| External review | Block release | Release + reviewer packet | Release + reviewer packet | The calendar is fixed; review continues in January |

## 6. Testing strategy

| Test | Protects |
|---|---|
| `test_gates.py` | Positivity, overlap, min-n, cost support, candidate outside `P0` |
| `test_report.py` | No "Measured" on unidentified logs; demo log; known truth |
| `test_pilot.py` | F5 pass/fail; bounds construction |
| `test_sweep.py` | Sweep config parsing; 12 cells; summary |
| `test_prepare_baf.py` | Split, score hashes, leakage check (if data available) |
| `test_ci_smoke.py` | Demo runs end-to-end |
| Existing tests | Estimators, observation, policies, metrics, schema, no leakage |

## 7. Non-goals

- No service, database, dashboard, or auth.
- No new estimator theory.
- No real bank pilot in V1.
- No FiFAR or transaction extension.
- No production integration.

## 8. Related documents

- Requirements: [`REQUIREMENTS.md`](REQUIREMENTS.md)
- Decisions: [`DECISIONS.md`](DECISIONS.md)
- Experiments: [`EXPERIMENTS.md`](EXPERIMENTS.md)
- Current architecture: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
