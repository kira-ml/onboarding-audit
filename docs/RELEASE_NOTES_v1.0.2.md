# Release Notes — v1.0.2

**Date:** 2026-11-27.
**Tag:** `v1.0.2`.
**Nature:** corrective pre-release, published by owner decision. The
external-review gate remains open.

---

## 1. Why this release exists

The external-credibility pre-review found that `v1.0.1` contained a **false
research-gap claim** in `CLAIMS.md` and `PROBLEM.md` (“no peer-reviewed
fraud-specific policy evaluation”) and that the manuscript did not cite the
closest 2026 work: OSCAR, Beyond Holdout Error, and DOiT (all ICAIF 2026). The
project’s own `RELATED_WORK.md` listed those papers. `v1.0.2` corrects that
before an external reader sees it.

The full audit is in [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md) and
[`EXTERNAL_CREDIBILITY_REVIEW.md`](EXTERNAL_CREDIBILITY_REVIEW.md).

## 2. What changed

### Literature and positioning

- Removed the false “no peer-reviewed” claim. Replaced it with the defensible
  combination claim: no reviewed work jointly provides the full account-opening
  `P0` + reject-margin + audit-design + open-tool combination.
- Added a 2026 financial selective-labels subsection and citations to OSCAR,
  Beyond Holdout Error, DOiT, JUBILEE, and the selection-aware certification
  paper in the manuscript and bibliography.
- Repositioned the paper’s contribution as the applied account-opening decision
  layer, not a new estimator or a new ranking phenomenon.
- Corrected the related-work metadata and the “verified” status of the closest
  papers.

### Credibility and readiness

- Added [`DATA_READINESS.md`](DATA_READINESS.md): minimum fields, the BSP 1213
  gap, reconstruction paths, and stop rules.
- Added [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md): severity-ranked issues,
  evidence, resolution status, and residual risks.
- Added [`EXTERNAL_CREDIBILITY_REVIEW.md`](EXTERNAL_CREDIBILITY_REVIEW.md): the
  fintech data-scientist pre-review with external sources.
- Added explicit caveats that all headline numbers are simulation results on
  synthetic BAF data, not bank estimates.
- Changed the BSP 1213 date language to “one-year transition ended June 2026”
  because secondary sources report 25 or 30 June; the primary text must be
  cited before a public compliance claim.
- Added the “audit-ready is not an audit opinion” definition.

### Paper

- Rebuilt `paper/main.pdf` with the 2026 citations.
- The paper is **7 pages**, over the stated 6-page target; trim or choose a
  7-page venue.
- Added a caveat that the identification gate is a readiness screen, not a proof
  of identification.

## 3. What this release does not fix

- No real bank log; the evidence remains a simulation on public synthetic BAF.
- No external readers; the public-release gate is **not met**.
- No candidate-model ablation; the “better model” premise is not isolated from
  model class/capacity.
- No legal/operational review of the audit design.
- The reject-margin bounds are still wide in `frej_002`; the full-policy
  break-even is a sensitivity, not an identification result.
- The paper is not peer-reviewed and is 7 pages.

## 4. Verify it

```bash
pip install -e ".[dev,baf]"
pytest -q                     # 101 passed
python scripts/check_claims.py  # 43/43
python scripts/check_links.py   # 0 missing
onboarding-audit demo --out reports/demo
```

The paper build requires Tectonic or a TeX distribution:

```bash
cd paper
tectonic main.tex
```

## 5. Verdict

**Corrective pre-release.** The false claim and missing citations are fixed.
The project remains a **Level 2 research artifact**, not a validated commercial
product. The external-review gate is open by owner decision.

## 6. Related documents

- Red-flag audit: [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md)
- External credibility review: [`EXTERNAL_CREDIBILITY_REVIEW.md`](EXTERNAL_CREDIBILITY_REVIEW.md)
- Release status: [`RELEASE_STATUS.md`](RELEASE_STATUS.md)
- Previous release: [`RELEASE_NOTES_v1.0.1.md`](RELEASE_NOTES_v1.0.1.md)
- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
