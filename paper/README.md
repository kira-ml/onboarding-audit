# Paper Workspace

**Status:** Research notes only. No paper draft and no PDF are produced in
v0.2.1. This folder exists so the paper is easier to write when the project
decides to start it.

**Purpose:** Keep the paper-specific planning separate from the canonical
research documentation, without duplicating the claims, methods, or results.

---

## 1. What is here

| File | What it is | What it is not |
|---|---|---|
| [`brief.md`](brief.md) | A 2-page research brief for a reviewer | The paper |
| [`outline.md`](outline.md) | An IMRaD skeleton with measured numbers | A draft |

Both files are **derived** from the canonical documents. If they disagree with
[`../docs/CLAIMS.md`](../docs/CLAIMS.md) or
[`../docs/RESULTS.md`](../docs/RESULTS.md), the canonical document wins.

## 2. What the paper should be built from

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

## 3. What is already finalized

- The problem brief and the evidence-backed Philippine context.
- The estimand, identification assumptions, estimators, and metrics.
- The pre-registered pilot and the sensitivity designs.
- The measured pilot, action-level sensitivity, and covariate sensitivity.
- The claim ledger, threats register, decision journal, and open questions.
- The schema, audit design, regulatory mapping, and report usage guide.
- The reproducibility, architecture, testing, and publication checklists.

The remaining paper work is **writing and interpretation**, not new measurement.

## 4. What is not finalized

- The full covariate 50-replication results are in
  [`../docs/RESULTS.md`](../docs/RESULTS.md) §9.
- Two external readers.
- A bootstrap/randomization-inference interval.
- The FiFAR capacity layer.
- A bank partner or a Philippine log.

These are limitations or future work, not blockers to a paper draft.

## 5. Before drafting

- [ ] Read `docs/RESULTS.md` and `docs/CLAIMS.md` end to end.
- [ ] Confirm every headline number traces to a committed JSON.
- [ ] Decide the venue and the length.
- [ ] Decide whether the paper is a methods/measurement paper or an applied
      case study. The current evidence supports a measurement paper with an
      applied benchmark.
- [ ] Freeze the claim set. Do not add a new headline during drafting.
- [ ] Re-run `pytest -q` and the pilot/sensitivity if the code changed.
- [ ] Run the link and stale-number check in
      [`../docs/PUBLICATION_CHECKLIST.md`](../docs/PUBLICATION_CHECKLIST.md).

## 6. Suggested paper shape

The outline is already in [`outline.md`](outline.md). The short version:

1. **Introduction:** the decision, the selection/delay/capacity problem, the
   regulatory gap, the contributions.
2. **Related work:** selective labels, reject inference, PU learning, delayed
   feedback, OPE, BAF, FiFAR, 2026 finance work.
3. **Problem formulation:** actions, costs, observation model, estimands,
   identification.
4. **Estimators:** naive, IPW, DR, audit-only, bounds, propensity estimation.
5. **Benchmark:** BAF, policies, scenarios, metrics, negative controls.
6. **Results:** naive bias/rank flips, estimator comparison, audit value,
   capacity/delay, outcome-dependent labels, bounds, propensity and covariate
   sensitivity.
7. **Practice:** schema, audit design, memo, regulatory mapping.
8. **Limitations:** simulation, BAF, costs, oracle/estimated propensities,
   reject margin, no PH data, no causal deployment claim.
9. **Conclusion:** the measurement layer, not a new detector.

## 7. Writing rules

- Every number in the abstract must appear in `docs/RESULTS.md`.
- Every claim must appear in `docs/CLAIMS.md`.
- Every limitation must appear in `docs/THREATS.md`.
- Do not introduce a new scenario or a new estimator in the paper without
  adding it to the pre-registration and the claim ledger.
- Do not describe the bounds as confidence intervals.
- Do not describe the audit as random approvals/rejections.
- Do not claim production, a specific bank, or a causal deployment effect.
- Cite the closest work; do not claim a new estimator.

## 8. When the paper starts

The first draft should be a **Markdown or LaTeX manuscript**, not a PDF-first
artifact. The PDF is a rendering step. The canonical content lives in the docs
and the paper folder; the PDF should not become the source of truth.

## 9. Related documents

- Documentation index: [`../docs/README.md`](../docs/README.md)
- Methods: [`../docs/METHODS.md`](../docs/METHODS.md)
- Results: [`../docs/RESULTS.md`](../docs/RESULTS.md)
- Claims: [`../docs/CLAIMS.md`](../docs/CLAIMS.md)
- Publication checklist: [`../docs/PUBLICATION_CHECKLIST.md`](../docs/PUBLICATION_CHECKLIST.md)
