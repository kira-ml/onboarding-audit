# Release Notes — v1.0.0

**Date:** 2026-11-22.
**Tag:** `v1.0.0`.
**Nature:** a review-ready measurement layer, not a production system.

> **Post-release note (2026-11-26):** the ranking result is cost-dependent. In
> the main scenario naive P(best) is 0%, but at `frej_050` it is **100%** while
> DR is **58%**; see `RESULTS.md` §5 and `STRATEGIC_REVIEW_v1.md` C1. The point
> estimate remains biased at `frej_050`; this is a ranking counterexample, not a
> case where naive is accurate.

---

## 1. What this release is

`onboarding-audit` v1.0.0 evaluates an account-opening fraud policy from a
historical decision log with selective and delayed labels. It estimates the
policy's cost on the population the incumbent did not reject (`P0`), bounds the
reject margin, compares a candidate with the incumbent, and writes an
audit-ready memo.

The release is deliberately scoped:

- **Level 2 (review-ready).** A model-risk team can audit the code, the evidence,
  the claims, and the failure modes.
- **Not Level 3 (pilot-proven).** There is no partner log and no independent
  validator. The production claim is **INCONCLUSIVE**.
- **Not a fraud detector.** The layer evaluates policies; it does not score
  applicants.

## 2. What is in it

### Method

- Naive, IPW-HT, IPW-Hájek, doubly robust, audit-only, and partial-identification
  bounds.
- An identification gate: positivity, sample size, ESS, max weight, cost
  support, observation-mechanism declaration, and propensity calibration.
- A paired candidate-vs-incumbent decision: difference, 95% interval,
  P(candidate cheaper), expected regret, and labels-needed at 80% power.
- Post-stratified audit-only correction for delayed resolution.

### Evidence

| Result | Value |
|---|---|
| Naive bias, main / sweep | **111.6–278.5% / 7.8–538.5%** |
| Naive bias above 5% | **12/12** cells (max across policies); incumbent **11/12** |
| DR mean bias, main / sweep | **0.94% / ≤1.89%**; 95% MC upper **3.8% / 4.3–9.6%** |
| DR coverage | **84.5–96.0%** |
| DR P(select true best) | **64% [50, 76]** at low `e`; **96–100%** at high `e` |
| Double robustness | DR **+0.14%** (wrong outcome), **+0.36%** (wrong propensity) |
| Estimated action-level `e` | DR **1.43% / 93.5%**; IPW **2.92% / 92.0%** |
| Outcome-dependent labels | audit-only **2.58% / 82.5%**; DR **1,737.0%** |
| Bounds, main / `frej_002` | **0.009942 / 0.203** |
| F5 | narrow **15/88**, widened **77/88** |
| Temporal stability | naive **230% / 255%**; DR **0.89% / 0.43%**; naive P(best) **0% / 0%** |
| Case study | naive **+6.3% worse**; true **−12.4% better**; report **P = 0.984** |

### Artifacts

- `reports/pilot.json`, `reports/obs_sweep/`, `reports/propensity_sensitivity.json`,
  `reports/double_robustness.json`, `reports/temporal_stability.json`.
- `scripts/prepare_baf.py`: rebuilds the benchmark from `Base.csv`; reproduced
  the recorded SHA-256 exactly.
- `scripts/check_claims.py`: 43 headline numbers recomputed from the committed
  JSON; runs in CI.
- `docs/AUDIT_REPORT.md`: the adversarial audit, including the findings that
  changed the claims.
- `docs/TECHNICAL_NOTE.md`: identification, influence functions, bounds proof.
- `docs/CASE_STUDY.md`: a reproducible decision flip.
- `docs/MODEL_CARD.md`, `docs/VALIDATION_REPORT.md`, `docs/PILOT_PROTOCOL.md`,
  `docs/BUSINESS_CASE.md`.

## 3. What changed in the review

The independent audit returned **FAIL on the claims as stated**. The release
fixes or discloses every finding:

- DR precision now carries Monte Carlo bounds (**3.8%**, not 0.94%).
- "12/12 cells" is labeled as the maximum across policies; the incumbent is
  **11/12**.
- The bounds width is reported for `frej_002` (**0.203**) as well as the main
  scenario.
- A constant wrong propensity is flagged by the calibration check.
- The memo's outside-`P0` count is fixed and regression-tested.
- The "5% approved-label rate" is relabeled as a pre-resolution probability
  (**3.06%** realized).
- `e_approve` no longer omits the audit resolution factor. IPW under estimated
  `e` is **2.92%**, not 11.19%; the old claim was a bug.
- The report's audit-only estimate is post-stratified by follow-up.
- The gate refuses a declared outcome-dependent mechanism.

## 4. What is not in it

- No production deployment, API, database, or dashboard.
- No bank log or PII.
- No legal or compliance certification.
- No claim that the reject margin is point-identified.
- No claim that the method generalizes beyond the BAF simulation without a
  partner pilot.

## 5. Verify it

```bash
pip install -e ".[dev,baf]"
pytest -q                     # 92 passed
python scripts/check_claims.py  # 43/43
python scripts/check_links.py   # 0 missing
onboarding-audit demo --out reports/demo
python -m onboarding_audit.cli report \
  --log examples/case_log.csv \
  --candidate examples/case_candidate.csv \
  --config configs/case_study.yaml \
  --capacity 0.05 \
  --observation-assumption action \
  --out reports/case_study
```

The benchmark rebuild (`scripts/prepare_baf.py --verify`) requires the public
`Base.csv`; it reproduced the recorded SHA-256 on 2026-11-21.

## 6. Verdict

**PASS (conditional) for the Level 2, simulation-scoped claim. INCONCLUSIVE for
production generalization. FAIL for point-identifying the reject margin from logs
alone.**

The release is useful because it is explicit about which of those three it is.
