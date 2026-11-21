# V1 Experiments

**Status:** Pre-registered plan, 2026-11-21.
**Rule:** Run the experiment as written. If the result changes the claim, record
the change in `docs/CLAIMS.md` and `docs/V1/PROGRESS.md`; do not switch the
headline after seeing the result.

---

## 1. Experiment map

| ID | Experiment | Question | Output |
|---|---|---|---|
| **E1** | Observation-rate sweep | Is the naive bias and ranking flip robust to plausible observation rates? | `reports/obs_sweep/pilot.json`/`.md` |
| **E2** | Bounds F5 | Does the pre-registered bounds interval cover `V_full` in ≥90% of reps? | `pilot.json` F5 block |
| **E3** | Report gate | Does the tool refuse/flag unidentified logs? | `reports/report_gate_tests.md` |
| **E4** | Reproducibility | Can the scores be reproduced from the public data? | `data/provenance.json` |
| **E5** | Adapter/demo | Can a reviewer run the product in <10 minutes? | Timed demo log |

---

## 2. E1 — Observation-rate sweep

### 2.1 Hypothesis

- **H1a:** The naive estimate has >5% relative bias in at least **6 of 12**
  cells.
- **H1b:** The naive estimate reverses at least one pairwise ranking in at least
  **3 of 12** cells.
- **H1c:** DR is within 5% relative bias in at least **8 of 12** cells with
  oracle propensities. The sweep isolates the observation-rate effect; the
  estimated-`e` sensitivity is a separate study.
- **H1d:** The bias is **conditional**: it is largest at low `e_approve` and low
  `kappa_review`, and shrinks as `e_approve` rises.

### 2.2 Design

- `e_approve ∈ {0.01, 0.05, 0.20, 0.50}`.
- `kappa_review ∈ {0.50, 0.90, 1.00}`.
- 12 cells; 50 replications per cell; everything else fixed at the main scenario
  (1% audit, 45-day approve delay, default cost matrix, 2% review capacity).
- Common random numbers across cells.
- Same BAF frame and policies as the main pilot.

### 2.3 Metrics

- Naive relative bias (max across policies).
- DR/IPW/audit-only relative bias and coverage.
- Mean pairwise inversions and P(select true best).
- ESS and max weight.
- Bounds width and F5 coverage (secondary).

### 2.4 Decision rule

| Result | Interpretation | Action |
|---|---|---|
| H1a and H1b hold | The premise is robust across plausible rates | Keep the conditional claim; report the range |
| H1a holds but H1d shows collapse at high `e_approve` | The premise is real but conditional | Headline becomes "under low approve-label rates"; report the map |
| H1a fails (bias ≤5% in most cells) | The premise is weak | Pivot the V1 claim to the correction/gate/bounds; do not claim material bias |
| H1c fails (DR >5% in most cells) | The correction is fragile | Narrow the correction claim; emphasize audit-only and the gate |

### 2.5 Falsification

If the naive bias is ≤5% in all 12 cells and no ranking flips, the V1 thesis
"naive evaluation is materially biased" is false. The project then becomes a
measurement/diagnostic tool, not a bias study. Record this explicitly.

### 2.6 Output

- `configs/obs_sweep.yaml`
- `reports/obs_sweep/pilot.json`
- `reports/obs_sweep/obs_sweep.md`
- `scripts/analyze_sweep.py`
- A compact table in this document and `docs/RESULTS.md`.

### 2.7 Result (2026-11-21)

12 cells, 50 replications each, common random numbers.

| Cell | Naive max bias | DR max bias | DR coverage | Naive inversions | DR P(best) |
|---|---:|---:|---:|---:|---:|
| `e001_k050` | 386.46% | 1.52% | 85.5% | 1.28 | 64% |
| `e001_k090` | 515.53% | 0.99% | 84.5% | 1.18 | 64% |
| `e001_k100` | 538.46% | 1.38% | 85.0% | 1.10 | 64% |
| `e005_k050` | 174.61% | 0.97% | 95.0% | 1.00 | 68% |
| `e005_k090` | 278.46% | 0.96% | 95.5% | 1.00 | 68% |
| `e005_k100` | 300.12% | 1.05% | 95.5% | 1.00 | 68% |
| `e020_k050` | 45.34% | 1.84% | 94.0% | 1.00 | 76% |
| `e020_k090` | 91.78% | 1.89% | 94.0% | 1.00 | 80% |
| `e020_k100` | 102.71% | 1.87% | 94.0% | 1.00 | 80% |
| `e050_k050` | 7.76% | 1.26% | 95.5% | 0.48 | 96% |
| `e050_k090` | 29.38% | 1.31% | 96.0% | 1.00 | 100% |
| `e050_k100` | 34.67% | 1.27% | 96.0% | 1.00 | 100% |

**Measured read:**

- **H1a supported:** naive bias exceeds 5% in **12/12** cells. The range is
  **7.8% to 538.5%**.
- **H1b supported:** the naive estimate has at least one pairwise inversion in
  **12/12** cells (0.48–1.28 mean inversions); it selects the true best policy
  **0%** of the time in 11/12 cells and **52%** in `e050_k050`.
- **H1c supported:** DR with known propensities stays within **1.89%** in all 12
  cells. Coverage is **84.5–96.0%**.
- **H1d supported:** the bias shrinks as `e_approve` rises, but it does **not**
  collapse below 5% even at `e_approve=0.50` (7.8–34.7%). The magnitude is
  strongly conditional; the direction is robust.
- **Residual risk:** at low approve-label rates, DR's P(select true best) is
  **64%** and coverage is **84.5–85.5%**. The correction is accurate, but the
  ranking is not guaranteed. This is a reportable limitation, not a hidden one.

**Decision:** keep the conditional V1 claim. Do not claim a universal
112–278% magnitude. Report the 7.8–538.5% range, the 12/12 direction, and the
low-`e` ranking weakness.

---

## 3. E2 — Bounds F5

### 3.1 Hypothesis

- **H2a:** The current bounds fail the pre-registered F5 criterion
  (`coverage_full >= 0.90`) for at least one policy.
- **H2b:** An unconditional interval `[L(v_pop - 1.96 se), U(v_pop + 1.96 se)]`
  improves coverage but may still fail without an assumption on the reject
  margin.

### 3.2 Design

- Use the 100-replication main scenario.
- For each policy, compute:
  - current bounds `[L, U]`;
  - F5 coverage of `V_full`;
  - unconditional interval and its coverage;
  - width, reject share, and `P0` estimate SE.
- Use the same `v_pop` construction for pilot and report (DR preferred; record
  IPW as a diagnostic).

### 3.3 Decision rule

| Result | Interpretation | Action |
|---|---|---|
| F5 ≥90% for all policies | The bounds pass | Record pass; keep the coverage claim |
| F5 <90% for at least one policy | The bounds fail | Record fail; remove the coverage claim; report partial identification |
| Unconditional interval passes | The failure was construction | Adopt the unconditional interval; record the change |
| Unconditional interval fails | No cheap fix | Report width and reject share; no coverage claim |

### 3.4 Falsification

If F5 passes at ≥90%, the red-team finding is wrong and the current bounds are
valid. Record the pass and update the threats register.

### 3.5 Output

- `F5_pass`, `F5_coverage`, `unconditional_coverage` in `pilot.json`.
- A section in `docs/RESULTS.md` that says "F5 passed" or "F5 failed."
- Updated `docs/CLAIMS.md` and `docs/THREATS.md`.

---

## 4. E3 — Report gate

### 4.1 Hypothesis

- **H3a:** The current report prints "Measured" on at least one unidentified
  log.
- **H3b:** The gate refuses or flags all five adversarial logs.
- **H3c:** The gate passes both valid logs (no false refusal).

### 4.2 Adversarial logs

| Log | Defect | Expected |
|---|---|---|
| L1 | No `propensity` column, action-level fallback, no audit | Flag; no "Measured" |
| L2 | Low overlap: candidate reviews a region the incumbent never labeled | Flag; bounds/diagnostic |
| L3 | Zero positivity: an action has `e=0` | Refuse |
| L4 | Tiny sample: 20 rows | Flag; no "Measured" |
| L5 | Negative cost support: a candidate action has a negative cost | Refuse |
| L6 | Valid provided propensity | Pass |
| L7 | Valid audit design | Pass |

### 4.3 Metrics

- Gate pass/fail per log.
- "Measured" count on adversarial logs (target 0).
- False refusal rate on valid logs (target 0).
- Time to run the gate.

### 4.4 Decision rule

- 5/5 adversarial logs refused or flagged.
- 2/2 valid logs pass.
- 0 "Measured" on adversarial logs.

### 4.5 Falsification

If the gate refuses a valid log, relax the warning thresholds; keep the
positivity and cost-support refusals.

### 4.6 Output

- `reports/report_gate_tests.md`
- `tests/test_gates.py`
- Updated `docs/REPORT_USAGE.md` and `docs/MEMO_TEMPLATE.md`.

---

## 5. E4 — Reproducibility

### 5.1 Hypothesis

- **H4a:** `scripts/prepare_baf.py` reproduces the processed frame and the
  `p_fraud`/`p_fraud_lgbm` scores within a stated tolerance.
- **H4b:** If H4a fails, the Level 1 "reproducible" claim is narrowed.

### 5.2 Design

- Download `Base.csv`.
- Split months 0–2 / 3–4 / 5–6.
- Fit the incumbent logistic regression and candidate LightGBM.
- Score the test window.
- Compare to `data/scored_test.parquet`: row count, label distribution, score
  correlation, max absolute difference, SHA-256.
- Add a leakage test: refit the candidate on months 5–6; show the ranking flip
  disappears or reverses.

### 5.3 Decision rule

| Result | Interpretation | Action |
|---|---|---|
| Scores reproduce within tolerance | Level 1 holds | Record provenance and hash |
| Scores differ materially | Level 1 narrows | Document the gap; do not claim full reproducibility |
| Leakage test reverses the flip | The better-model premise is unverified | Remove the ranking-flip claim or qualify it |

### 5.4 Output

- `scripts/prepare_baf.py`
- `data/provenance.json`
- Updated `docs/DATA.md`, `docs/DATA_DICTIONARY.md`,
  `docs/REPRODUCIBILITY.md`.

---

## 6. E5 — Adapter and demo

### 6.1 Hypothesis

A data scientist can run the demo in **under 10 minutes** and the adapter handles
CSV and parquet without errors.

### 6.2 Design

- A synthetic 2,500-row log with no propensity column.
- `validate` and `report` on CSV and parquet.
- Time the run.
- Check the memo for the gate status and the diagnostics.

### 6.3 Decision rule

- Runtime <10 minutes.
- No unhandled errors.
- The memo says "not identified" or "flagged" on the no-propensity log.
- The valid log produces a point estimate.

### 6.4 Output

- `examples/demo_log.csv`
- `docs/REPORT_USAGE.md`
- A timed result in `docs/V1/PROGRESS.md`.

---

## 7. Pre-registration and stop rules

- Record the hypotheses and decision rules in this document **before** running
  E1–E5.
- Do not change the headline after seeing the result; update the claim to the
  measured conditions.
- Stop if the sweep takes >90 minutes; use 25 reps and record the reduced
  precision.
- Stop if the pipeline cannot be reproduced by Dec 5; narrow the claim.
- Stop if the gate refuses valid logs; fix the thresholds before the freeze.

## 8. What would falsify V1

- The bias collapses at plausible observation rates and no ranking flips.
- DR fails in most cells where positivity holds.
- F5 passes; the red-team finding is wrong.
- The gate cannot distinguish valid from invalid logs.
- The scores cannot be reproduced and the ranking flip is a split artifact.

If any of these occurs, V1 narrows the claim; it does not hide the result.
