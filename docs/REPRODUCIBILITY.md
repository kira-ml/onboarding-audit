# Reproducibility

**Status:** Canonical reproduction guide for v0.2.1 (2026-11-20).
**Purpose:** Let a reader rebuild the environment, the data frame, the pilot, the
sensitivity studies, and the report from a clean checkout. If a number cannot be
reproduced from this document, it should not be in the paper.

---

## 1. Environment

| Item | Value |
|---|---|
| Python | 3.10+ (tested on 3.12) |
| OS | Windows 11 (the commands below use PowerShell; the Python code is portable) |
| Hardware | CPU only; no GPU |
| Package manager | `pip` with `pyproject.toml` |
| Core dependencies | `numpy`, `pandas`, `scipy`, `scikit-learn`, `pyarrow`, `PyYAML` |
| Dev dependencies | `pytest`, `matplotlib` |

The exact version bounds are in [`../pyproject.toml`](../pyproject.toml). The
package is installed in editable mode for development.

## 2. Install

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev,baf]"
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,baf]"
```

Verify:

```bash
python -c "import onboarding_audit; print(onboarding_audit.__version__)"
pytest -q
```

Expected: the version string and **85 passed**.

## 3. Data

The pilot uses `data/scored_test.parquet`:

- 227,491 rows, months 5–6 of the BAF account-opening data;
- 39 columns;
- SHA-256:
  `f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593`.

The file is **not committed** (see `.gitignore`). Its provenance, column roles,
and limitations are in [`DATA.md`](DATA.md) and
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

The raw BAF data is public (Jesus et al., NeurIPS 2022). Rebuild the processed
file from `Base.csv`:

```bash
pip install -e ".[baf]"
python scripts/prepare_baf.py --raw /path/to/Base.csv --verify
```

The script:

1. loads `Base.csv`, adds `transaction_id` and `amount_proxy`, and sorts by
   `month`;
2. simulates the one-month label delay;
3. splits months 0–2 (train), 3–4 (validation), 5–6 (test);
4. fits the incumbent logistic regression (`C=10`) and the candidate LightGBM
   (300 trees, learning rate 0.05), and refits the random forest as a
   diagnostic;
5. writes the 39-column test frame and `data/scored_test.provenance.json` with
   the input hash, the output hash, the model parameters, the library versions,
   and per-score column hashes.

`--verify` exits non-zero if the output SHA-256 differs from
`f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593`. A library
upgrade that changes the scores is therefore visible, not silent. The verified
rebuild record is in [`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md).

Do not fabricate the processed file from a different split; the scores and the
test window are part of the benchmark.

## 4. Commands

### 4.1 Tests

```bash
pytest -q
```

### 4.2 Demo

```bash
onboarding-audit demo --out reports/demo
```

Uses `examples/demo_log.csv` (2,500 rows, no propensity column) and
`examples/demo_candidate.csv`; exercises the estimated-propensity path and the
identification gate. Not a research result.

### 4.3 Pilot

```bash
onboarding-audit pilot --config configs/pilot.yaml --out reports
```

This runs the 22 configured scenarios (1,150 replications). It writes:

- `reports/pilot.json` — the source of truth;
- `reports/pilot.md` — the human-readable report;
- `reports/pilot_rows.parquet` — row-level results (gitignored, local).

### 4.4 Observation-rate sweep

```bash
onboarding-audit pilot --config configs/obs_sweep.yaml --out reports/obs_sweep
python scripts/analyze_sweep.py
```

This runs the 12-cell sweep (50 replications per cell) and writes the committed
summary in `reports/obs_sweep/`.

### 4.5 Propensity and covariate sensitivity

```bash
onboarding-audit sensitivity --config configs/pilot.yaml --out reports --reps 50
```

This runs the 11 sensitivity scenarios (550 replications): main, action-level
estimated, noisy (0.10/0.25), outcome-dependent, outcome-dependent with
estimated `e`, and the five covariate scenarios. It writes:

- `reports/propensity_sensitivity.json`;
- `reports/propensity_sensitivity.md`.

### 4.6 Arbitrary-log report

```bash
onboarding-audit report \
  --log examples/sample_log.csv \
  --candidate examples/sample_candidate.csv \
  --config configs/pilot.yaml \
  --capacity 0.10 \
  --out reports/sample_report
```

Covariate propensity model:

```bash
onboarding-audit report \
  --log examples/sample_log.csv \
  --candidate examples/sample_candidate.csv \
  --config configs/pilot.yaml \
  --capacity 0.10 \
  --propensity-model covariate \
  --propensity-features customer_age,credit_risk_score \
  --out reports/sample_covariate
```

The sample log is a 20-row schema/CLI smoke example, not a research result.

### 4.7 Schema validation

```bash
onboarding-audit validate --log examples/sample_log.csv
```

## 5. Seeds and common random numbers

- `configs/pilot.yaml` sets `seed: 20261120`.
- `data.load_eval_data` uses the seed to assign decision days.
- `pilot.run_scenario` creates one `numpy.random.Generator` per scenario from the
  seed and draws replications sequentially. The same seed is used across
  scenarios, so the scenarios share the evaluation frame and the decision days
  (common random numbers).
- `fit_outcome_model` uses `seed + rep` for the cross-fitting folds.
- `fit_covariate_propensity` uses `seed + rep` for its folds.
- The noisy propensity uses `seed + 7000 + rep`.

Do not change the seed when comparing a new run to the committed results. If you
must change it, report both runs and explain why.

## 6. Outputs and source of truth

| Artifact | Committed? | Role |
|---|---|---|
| `reports/pilot.json` | yes | Pilot summary, ranking, bounds, verdict; source of truth |
| `reports/pilot.md` | yes | Human-readable pilot report |
| `reports/pilot_rows.parquet` | no | Row-level results; large and reproducible |
| `reports/propensity_sensitivity.json` | yes | Sensitivity summary; source of truth |
| `reports/propensity_sensitivity.md` | yes | Human-readable sensitivity report |
| `reports/obs_sweep/pilot.json` | yes | Observation sweep; source of truth |
| `reports/obs_sweep/obs_sweep.md` | yes | Sweep summary |
| `reports/obs_sweep/obs_sweep_summary.csv` | yes | Sweep summary table |
| `reports/demo/` | no | Generated demo memo; usability fixture |
| `data/scored_test.provenance.json` | no | Benchmark input/output hashes and library versions |

A public number must trace to one of the committed JSON files or a cited primary
source. The claim ledger is [`CLAIMS.md`](CLAIMS.md).

## 7. How to reproduce each table

| Table | Command | JSON key |
|---|---|---|
| Pilot headline | `onboarding-audit pilot ...` | `summary` |
| Policy ranking | same | `ranking` |
| Bounds | same | `bounds` |
| H1–H6 verdict | same | `verdict` |
| Propensity sensitivity | `onboarding-audit sensitivity ...` | `aggregate` |
| Covariate sensitivity | same | `aggregate` filtered to `covariate_*` |
| Arbitrary-log memo | `onboarding-audit report ...` | `report.json` |
| Headline claim check | `python scripts/check_claims.py` | all of the above |

## 8. Runtime

Reference machine: Windows 11, CPU-only, 16 GB RAM.

| Run | Replications | Approx. runtime |
|---|---:|---:|
| `pytest -q` | — | < 15 s |
| Demo (2,500 rows) | — | < 10 s |
| Pilot (22 scenarios) | 1,150 | ~19 min CPU; ~31 min wall-clock on the reference run |
| Sensitivity (11 scenarios) | 550 | ~16 min (reference run; covariate model fits dominate) |
| Report on the 20-row sample | — | < 5 s |
| Report on a 227k-row log | — | seconds to a few minutes, depending on features |

The sensitivity runtime depends on the number of covariate-model folds and the
machine. Wall-clock time also depends on concurrent load; the reference pilot
run took ~31 minutes while other work was running, with ~19 minutes of CPU time.
The exact wall-clock time is not part of the scientific result; the replication
count and seed are.

## 9. Determinism and version drift

- The code uses fixed seeds, but BLAS, `scikit-learn`, and solver versions can
  change the last digits of a fit. Pin the versions in `pyproject.toml` if exact
  bit-for-bit reproduction matters.
- The pilot JSON is the committed record. If a dependency upgrade changes a
  number, report the old and new values and the version change; do not silently
  overwrite the claim.
- `pandas`/`pyarrow` parquet reading is stable for the committed schema, but a
  different pyarrow version may change dtypes or compression. The data hash in
  §3 is the check.

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `missing required columns` | The processed frame or log is incomplete | Check `DATA_DICTIONARY.md` / `SCHEMA.md` |
| `evaluation months must be 5 and 6` | Wrong split | Use the BAF test window, not the full file |
| `positivity failure` | A non-rejected row has `e=0` | Increase `kappa_review`, `e_approve`, or `audit_rate` |
| `covariate propensity model requires at least one numeric feature` | The log has no numeric features | Pass `--propensity-features` or use the action-level model |
| `candidate score missing for N applications` | The candidate file does not cover the log | Export a score for every application |
| `DR is n/a` | No usable outcome-model features | Pass `--features`; IPW/audit-only still run |
| `MemoryError` on the pilot | The full frame plus fold predictions is large | Run on a machine with more RAM or reduce the feature set |

## 11. What cannot be reproduced from this repository alone

- The raw BAF download (public, but not redistributed).
- A Philippine bank log (none is public; the project does not use one).
- A production cost matrix (the configured values are normalized assumptions).
- A legal/risk sign-off on the audit design.

The V2 model scores **can** be rebuilt from the public raw file with
`scripts/prepare_baf.py`; the script records the hashes and the library versions
so a mismatch is visible. Exact bit-for-bit agreement across a library upgrade is
not guaranteed.

These are stated as limitations, not hidden.

## 12. Related documents

- Data card: [`DATA.md`](DATA.md)
- Data dictionary: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)
- Methods: [`METHODS.md`](METHODS.md)
- Testing: [`TESTING.md`](TESTING.md)
- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Publication checklist: [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md)
