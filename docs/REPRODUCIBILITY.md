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
pip install -e ".[dev]"
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Verify:

```bash
python -c "import onboarding_audit; print(onboarding_audit.__version__)"
pytest -q
```

Expected: the version string and **57 passed**.

## 3. Data

The pilot uses `data/scored_test.parquet`:

- 227,491 rows, months 5–6 of the BAF account-opening data;
- 39 columns;
- SHA-256:
  `f5efd6781431f229685df6c154f1a6e124849a323e3c45d258a09cf10f331593`.

The file is **not committed** (see `.gitignore`). Its provenance, column roles,
and limitations are in [`DATA.md`](DATA.md) and
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

The raw BAF data is public (Jesus et al., NeurIPS 2022). The processed file was
produced by the archived V2 pipeline, which is not part of this repository. A
standalone `scripts/prepare_baf.py` is not included in v0.2.1; the honest
reproduction path is:

1. obtain `Base.csv` from the BAF repository;
2. use the archived V2 pipeline for the month 0–2 / 3–4 / 5–6 split and the
   `p_fraud` / `p_fraud_lgbm` scores;
3. write the 39-column test frame described in `DATA_DICTIONARY.md`.

Do not fabricate the processed file from a different split; the scores and the
test window are part of the benchmark.

## 4. Commands

### 4.1 Tests

```bash
pytest -q
```

### 4.2 Pilot

```bash
onboarding-audit pilot --config configs/pilot.yaml --out reports
```

This runs the 13 pre-registered scenarios (700 replications). It writes:

- `reports/pilot.json` — the source of truth;
- `reports/pilot.md` — the human-readable report;
- `reports/pilot_rows.parquet` — row-level results (gitignored, local).

### 4.3 Propensity and covariate sensitivity

```bash
onboarding-audit sensitivity --config configs/pilot.yaml --out reports --reps 50
```

This runs the 11 sensitivity scenarios (550 replications): main, action-level
estimated, noisy (0.10/0.25), outcome-dependent, outcome-dependent with
estimated `e`, and the five covariate scenarios. It writes:

- `reports/propensity_sensitivity.json`;
- `reports/propensity_sensitivity.md`.

### 4.4 Arbitrary-log report

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

### 4.5 Schema validation

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
| `reports/sample_report/` | no | Generated sample memo; smoke example |
| `reports/sample_covariate/` | no | Generated covariate sample memo; smoke example |

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

## 8. Runtime

Reference machine: Windows 11, CPU-only, 16 GB RAM.

| Run | Replications | Approx. runtime |
|---|---:|---:|
| `pytest -q` | — | < 10 s |
| Pilot (13 scenarios) | 700 | ~19 min CPU; ~31 min wall-clock on the reference run |
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
- The V2 model training pipeline that produced `p_fraud` and `p_fraud_lgbm`
  (archived in the origin repository).
- A Philippine bank log (none is public; the project does not use one).
- A production cost matrix (the configured values are normalized assumptions).
- A legal/risk sign-off on the audit design.

These are stated as limitations, not hidden.

## 12. Related documents

- Data card: [`DATA.md`](DATA.md)
- Data dictionary: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)
- Methods: [`METHODS.md`](METHODS.md)
- Testing: [`TESTING.md`](TESTING.md)
- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Publication checklist: [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md)
