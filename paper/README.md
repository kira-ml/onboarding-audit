# Paper Workspace

**Status:** Initial IEEEtran draft, v1.0.0 (2026-11-22). The manuscript is
`main.tex`; `main.pdf` is the compiled two-column rendering. The canonical
content remains the research documentation; the paper is a derived artifact.

> **Build status (2026-11-26):** `main.tex` has a post-tag methods addition (the
> full-policy difference bound and break-even). The committed `main.pdf` has
> **not** been rebuilt in the current environment; rebuild it before circulating
> or submitting. The LaTeX toolchain is not available here.

**Purpose:** Keep the paper-specific material separate from the canonical
research documentation, without duplicating the claims, methods, or results.

---

## 1. What is here

| File | What it is | What it is not |
|---|---|---|
| [`main.tex`](main.tex) | The IEEEtran conference manuscript | The claim ledger |
| [`references.bib`](references.bib) | The verified bibliography | A literature review |
| [`main.pdf`](main.pdf) | The compiled two-column draft (6 pages) | A submission-ready camera copy |
| [`make_figures.py`](make_figures.py) | Regenerates the three figures from committed JSON | A result |
| [`figures/`](figures/) | The vector figures used by the paper | Source data |
| [`brief.md`](brief.md) | A 2-page research brief for a reviewer | The paper |
| [`outline.md`](outline.md) | An IMRaD skeleton with measured numbers | A draft |

The manuscript is **derived** from the canonical documents. If it disagrees with
[`../docs/CLAIMS.md`](../docs/CLAIMS.md) or
[`../docs/RESULTS.md`](../docs/RESULTS.md), the canonical document wins.

## 2. Build

The draft uses `IEEEtran` in conference mode, two columns, 10pt. It compiles
with Tectonic, `latexmk`, or Overleaf:

```bash
# Tectonic (no local TeX install; fetches the bundle on first run)
tectonic main.tex

# latexmk with a TeX distribution
latexmk -pdf main.tex
```

Overleaf: upload `main.tex`, `references.bib`, and `figures/`; the compiler is
pdfLaTeX or XeLaTeX.

To regenerate the figures:

```bash
python paper/make_figures.py
```

The draft is 6 pages. IEEE conference limits vary by venue; the current length
fits a 6-page paper and leaves room for one page of revisions.

## 3. What the paper is built from

Do not start from a blank page. Start from these documents, in this order:

1. **Problem and positioning:** [`../docs/PROBLEM.md`](../docs/PROBLEM.md),
   [`../docs/RELATED_WORK.md`](../docs/RELATED_WORK.md),
   [`../docs/REFERENCES.md`](../docs/REFERENCES.md).
2. **Methods:** [`../docs/METHODS.md`](../docs/METHODS.md), with the
   pre-registration in [`../docs/PILOT_SPEC.md`](../docs/PILOT_SPEC.md).
3. **Results:** [`../docs/RESULTS.md`](../docs/RESULTS.md), with the generated
   reports in [`../reports/pilot.md`](../reports/pilot.md) and
   [`../reports/propensity_sensitivity.md`](../reports/propensity_sensitivity.md).
4. **Claims:** [`../docs/CLAIMS.md`](../docs/CLAIMS.md). Every number in the
   paper must appear here.
5. **Limitations:** [`../docs/THREATS.md`](../docs/THREATS.md).
6. **Data:** [`../docs/DATA.md`](../docs/DATA.md),
   [`../docs/DATA_DICTIONARY.md`](../docs/DATA_DICTIONARY.md).
7. **Practice/policy:** [`../docs/SCHEMA.md`](../docs/SCHEMA.md),
   [`../docs/AUDIT_DESIGN.md`](../docs/AUDIT_DESIGN.md),
   [`../docs/BSP_MAPPING.md`](../docs/BSP_MAPPING.md).
8. **Reproduction:** [`../docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md).
9. **Decisions and open questions:** [`../docs/DECISIONS.md`](../docs/DECISIONS.md),
   [`../docs/OPEN_QUESTIONS.md`](../docs/OPEN_QUESTIONS.md).

## 4. What the draft covers

- The `P0` estimand and the seven identification assumptions.
- Naive, IPW-HT, IPW-Hájek, DR, audit-only, and partial-identification bounds.
- The identification gate, the observation-mechanism declaration, and propensity
  calibration.
- The paired decision layer: difference, interval, P(candidate cheaper), regret,
  and labels needed for 80% power.
- The BAF benchmark, the 12-cell sweep, the propensity and covariate
  sensitivity, the double-robustness test, the month-by-month stability check,
  and the case study.
- The negative results: outcome-dependent labels, the F5 bounds failure, and the
  ranking gap.

## 5. Before submission

- [ ] Choose the venue and confirm its page limit and template version.
- [ ] Replace the affiliation/email if needed.
- [ ] Re-check every number against `docs/CLAIMS.md`.
- [ ] Re-run `python scripts/check_claims.py`.
- [ ] Confirm the bibliography entries marked **verify** in
      [`../docs/REFERENCES.md`](../docs/REFERENCES.md) are not cited; the current
      draft cites only verified entries.
- [ ] Add the venue's required acknowledgments, data statement, and artifact
      appendix.
- [ ] Have an independent reader check the identification section.

## 6. Writing rules

- Every number in the abstract must appear in `docs/RESULTS.md`.
- Every claim must appear in `docs/CLAIMS.md`.
- Every limitation must appear in `docs/THREATS.md`.
- Do not introduce a new scenario or a new estimator in the paper without
  adding it to the pre-registration and the claim ledger.
- Do not describe the narrow bounds as confidence intervals.
- Do not describe the audit as random approvals/rejections.
- Do not claim production, a specific bank, or a causal deployment effect.
- Cite the closest work; do not claim a new estimator.

## 7. Related documents

- Documentation index: [`../docs/README.md`](../docs/README.md)
- Methods: [`../docs/METHODS.md`](../docs/METHODS.md)
- Technical note: [`../docs/TECHNICAL_NOTE.md`](../docs/TECHNICAL_NOTE.md)
- Results: [`../docs/RESULTS.md`](../docs/RESULTS.md)
- Claims: [`../docs/CLAIMS.md`](../docs/CLAIMS.md)
- Publication checklist: [`../docs/PUBLICATION_CHECKLIST.md`](../docs/PUBLICATION_CHECKLIST.md)
