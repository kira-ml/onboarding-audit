# Release Notes — v1.0.1

**Date:** 2026-11-26.
**Tag:** `v1.0.1`.
**Nature:** a decision-reliability review update, not a public `1.0` release.

---

## 1. What this release is

`v1.0.1` makes the V1 product surface safe for a `P0`-conditional decision and
adds the baseline and fairness evidence the strategic review required. It is a
review update: the public-release gate (two external readers) is still open.

## 2. What changed

### Full-policy decision check

- `full_policy_difference` bounds the candidate-vs-incumbent difference over the
  unobserved reject margin and reports the break-even rejected-fraud rate.
- The memo labels the recommendation **`P0`-conditional**, adds §4.1, and warns
  when the `P0` recommendation does not survive the reject margin.
- §4.1 is suppressed when the identification gate fails; an all-rejected log
  returns its valid bound; a missing `P0` standard error is withheld.

### Action-weighted baseline

The naive estimator is an unweighted labeled mean. `action_weighted` adds the
action-weighted Hájek baseline and a post-hoc sensitivity (`configs/baseline_sensitivity.yaml`,
50 reps per scenario):

| Scenario | Estimator | Max \|relative bias\| | P(select true best) |
|---|---|---:|---:|
| main | naive | **278.5%** | **0%** |
| main | action-weighted | **2.9%** | **62%** |
| main | DR | **0.96%** | **68%** |
| `frej_050` | naive | **291.2%** | **100%** |
| `frej_050` | action-weighted | **2.4%** | **58%** |
| `frej_050` | DR | **0.36%** | **58%** |

The point-estimate gap is not merely an unweighted-mean artifact; the ranking
effect is cost-dependent and survives a realistic action-weighted baseline.

### Segment diagnostic

The memo adds an observational segment table: incumbent approve/review/reject
counts, candidate reject and change shares, observed fraud rate, and candidate
false-reject share among observed legitimate rows. Segments with fewer than 50
rows are suppressed. It is **not** a fairness certification.

### Review package

- [`RELEASE_STATUS.md`](RELEASE_STATUS.md): what is tagged, what is not, and the
  open public-release gate.
- [`EXTERNAL_REVIEW.md`](EXTERNAL_REVIEW.md): the external-review log.
- [`REVIEWER_PACKET.md`](REVIEWER_PACKET.md): cover note, shortlist template,
  agenda, and outreach tracker.
- [`STRATEGIC_REVIEW_v1.md`](STRATEGIC_REVIEW_v1.md): the full strategic review.

## 3. What is not in it

- No external readers. The public-release gate is **not met**. This release is
  published to GitHub by owner decision as a review update; the gate is waived,
  not satisfied.
- No production deployment, API, database, or dashboard.
- No bank log or PII.
- No claim that the reject margin is point-identified.
- No claim that the paper is submission-ready; the PDF was not rebuilt in this
  environment.

## 4. Verify it

```bash
pip install -e ".[dev,baf]"
pytest -q                     # 101 passed
python scripts/check_claims.py  # 43/43
python scripts/check_links.py   # 0 missing
onboarding-audit demo --out reports/demo
onboarding-audit pilot --config configs/baseline_sensitivity.yaml --out reports/baseline_sensitivity
```

The benchmark rebuild (`scripts/prepare_baf.py --verify`) requires the public
`Base.csv`; it reproduced the recorded SHA-256 on 2026-11-21.

## 5. Verdict

**PASS (conditional) for the Level 2, simulation-scoped claim. INCONCLUSIVE for
production generalization. FAIL for point-identifying the reject margin from logs
alone. The public-release gate remains open.**

## 6. Related documents

- Release status: [`RELEASE_STATUS.md`](RELEASE_STATUS.md)
- Previous release: [`RELEASE_NOTES_v1.0.0.md`](RELEASE_NOTES_v1.0.0.md)
- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Validation report: [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md)
- Strategic review: [`STRATEGIC_REVIEW_v1.md`](STRATEGIC_REVIEW_v1.md)
