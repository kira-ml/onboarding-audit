# Release Notes — v1.1.0

**Date:** 2026-11-28.
**Tag:** `v1.1.0`.
**Nature:** Decision Reliability for Financial ML pre-release. The external-review
gate remains open.

---

## 1. What this release is

`v1.1.0` makes **decision reliability** the product spine, not a label. The
system now answers a different question: not only “what is the policy value?”
but “would this policy decision survive sampling, nuisance-model, calibration,
cost, reject-margin, and operational uncertainty — and should it be released,
deferred, or refused?”

## 2. What changed

### Decision Reliability Profile

- `src/onboarding_audit/reliability.py`: paired bootstrap of the DR influence
  terms, outcome/propensity calibration, 3×3 cost-stress stability, and an A–D
  grade over identification, statistical, structural, model, cost, and
  operational dimensions.
- `report` returns the profile in memo §4.2 and `diagnostics.reliability`;
  `report --reliability-boot` controls the bootstrap.
- `validate` reports reliability readiness alongside estimator readiness.
- `pilot --reliability-boot` records per-replication grades; the reliability
  audit is in `reports/reliability_audit/`.
- A/B require a directional point decision; C/D are not released. A failed gate
  is D.

### Reliability audit

60 replications (main, low-label, high false-reject-cost), 100 bootstrap
replicates each:

| Scenario | n | Grades | Released | Released accuracy | False cert. | Withheld |
|---|---:|---|---:|---:|---:|---:|
| main | 20 | 1 B, 19 C | 1 | 100% | 0 | 95% |
| `e001` | 20 | 20 D | 0 | n/a | 0 | 100% |
| `frej_050` | 20 | 1 A, 19 C | 1 | 100% | 0 | 95% |
| **Overall** | **60** | 1 A, 1 B, 38 C, 20 D | **2** | **100%** | **0** | **97%** |

The profile is deliberately conservative. The cost of caution is decision
volume, not a confident wrong decision. The audit is small and post-hoc.

### Research paper

The manuscript is refocused on Decision Reliability for Financial ML:

- New title and abstract centered on decision reliability.
- Formal reliability dimensions and metrics (bootstrap stability, calibration,
  cost stress, structural reject margin, operational readiness, false
  certification, withheld decisions).
- Reliability profile/gate and the accuracy–reliability gap as the primary
  results.
- 2026 closest-work citations retained (OSCAR, Beyond Holdout Error, DOiT).
- **6 body pages plus a references page** (7 pages total); the paper is not
  peer-reviewed.

### Evidence

- Label-holdout baseline: the correction survives a disjoint label half; the
  ranking remains unstable.
- Model/score ablation: candidate AUC 0.8829 vs 0.8733; retrained HistGB 0.8773
  vs logistic 0.8754; the better-model premise is modest.
- Reliability audit: 2/60 A/B decisions released, both correct; 0 false
  certifications; 97% of decisions withheld from release.

## 3. What this release does not fix

- No real bank log; the evidence remains a simulation on public synthetic BAF.
- No external readers; the public-release gate is **not met**.
- No peer review.
- The reliability bootstrap fixes the nuisance models; calibration is
  observed-label only; the cost grid is local.
- The audit is 20 replications per scenario; the percentages are not a
  production calibration.

## 4. Verify it

```bash
pip install -e ".[dev,baf]"
pytest -q                     # 115 passed
python scripts/check_claims.py  # 43/43
python scripts/check_links.py   # 0 missing
onboarding-audit demo --out reports/demo
onboarding-audit pilot --config configs/reliability_audit.yaml --out reports/reliability_audit --reliability-boot 100
python scripts/summarize_reliability_audit.py
```

The paper builds with Tectonic or a TeX distribution:

```bash
cd paper
tectonic main.tex
```

## 5. Verdict

**Decision-reliability pre-release.** The profile and audit are implemented and
tested; the paper is refocused. The project remains a Level 2 research artifact,
not a validated commercial product. The external-review gate is open by owner
decision.

## 6. Related documents

- Reliability method: [`RELIABILITY.md`](RELIABILITY.md)
- Reliability audit: [`../reports/reliability_audit/summary.md`](../reports/reliability_audit/summary.md)
- Release status: [`RELEASE_STATUS.md`](RELEASE_STATUS.md)
- Red-flag audit: [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md)
- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Previous release: [`RELEASE_NOTES_v1.0.2.md`](RELEASE_NOTES_v1.0.2.md)
