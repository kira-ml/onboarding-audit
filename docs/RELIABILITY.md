# Decision Reliability for Financial ML

**Status:** Specialization thesis and method note, 2026-11-28.
**Scope:** the decision-reliability layer added to `onboarding-audit`.
**Related:** [`METHODS.md`](METHODS.md), [`REPORT_USAGE.md`](REPORT_USAGE.md),
[`TECHNICAL_NOTE.md`](TECHNICAL_NOTE.md), [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md).

---

## 1. The specialization

**Decision reliability** is the extent to which a financial decision remains
correct under the uncertainty the available evidence cannot eliminate:
sampling error, nuisance-model error, selective labels, delayed labels, cost
assumptions, and data readiness.

A reliable system does not stop at a point estimate. It reports:

1. whether the decision is **identified** from the log;
2. whether it is **stable** to sampling and model uncertainty;
3. whether the **outcome and propensity models are calibrated**;
4. whether it survives **cost and reject-margin stress**;
5. whether the **operational data** is ready;
6. what the **full-policy** decision does to the unobserved reject margin.

This project is a natural fit because account-opening fraud has all of these
problems at once: the incumbent chooses the labels, approved labels are delayed,
rejected applicants are never observed, review capacity is constrained, and the
cost matrix is an assumption. The existing `P0`/reject-margin split, the
identification gate, the full-policy break-even, and the decision layer are the
foundation; this note makes reliability the product spine.

### End-to-end pipeline

```text
decision log + candidate score
        │
        ▼
validate / DATA_READINESS ──► schema + operational readiness
        │
        ▼
identification gate ────────► D: refuse, no point estimate
        │ pass
        ▼
P0 estimate + reject-margin bounds + full-policy break-even
        │
        ▼
reliability profile: bootstrap · calibration · cost stress · readiness
        │
        ├── A/B + directional ──► release for review/pilot
        ├── C ──────────────────► defer; collect labels/audit/cost agreement
        └── D ──────────────────► refuse
```

The same pipeline is used by `report`; the pilot runs it per replication with
`--reliability-boot`.

---

## 2. The reliability profile

The report returns a `reliability` object in `report.json` and a
**Decision reliability profile** in the memo (§4.2).

| Dimension | What it measures | Evidence |
|---|---|---|
| **Identification** | Can the log support a `P0` point estimate? | Gate: positivity, labels, ESS, max weight, cost support, observation declaration, propensity calibration |
| **Statistical stability** | Would the decision survive a resample of the evaluation rows? | Paired row bootstrap of DR influence terms: `P(candidate cheaper)`, same-direction share, 95% interval, regret |
| **Full-policy / reject margin** | Does the direction survive the unlogged rejected rows? | Full-policy difference bound and break-even; `depends` is a caveat, `P0 inconclusive` is unavailable |
| **Model calibration** | Are the outcome and observation models trustworthy at the decision boundary? | Brier, log loss, ECE for the outcome model; observed/expected ratio and ECE for a **provided** propensity. An action-level propensity estimated from the same observed rows is an identity and is not counted as calibration evidence. |
| **Cost stress** | Does the decision survive plausible cost changes? | 3×3 grid of review-cost and false-reject-cost multipliers; share of cells with the same decision |
| **Operational readiness** | Is the log large and clean enough to act on? | Observed labels, ESS, gate warnings |

### Grade rules

The grade is a **rule-based decision aid**, not a certification. A/B also
require a **directional point decision**; an inconclusive point estimate is C,
even if the bootstrap looks strong.

| Dimension | Strong | Moderate | Weak / unavailable |
|---|---|---|---|
| Identification | gate passes | — | gate fails → D |
| Statistical stability | bootstrap $P\le0.05$ or $\ge0.95$ and same-direction $\ge0.90$ | $P\le0.20$ or $\ge0.80$ | otherwise, or bootstrap unavailable |
| Full-policy | direction survives any reject outcome | direction depends on the reject margin | P0 inconclusive / conflict; *not applicable* if there are no rejected rows |
| Model calibration | outcome ECE $\le0.05$ and propensity O/E $0.75$-$1.25$ | ECE $\le0.10$ or O/E $0.5$-$1.5$ | worse, or unavailable |
| Cost stress | $\ge80\%$ of 9 cost cells same decision | $\ge60\%$ | $<60\%$, or unavailable |
| Operational | $\ge500$ labels, ESS $\ge500$, $\le1$ gate warning | $\ge100$ labels, ESS $\ge100$, $\le3$ warnings | otherwise |

- **A - decision-grade (conditional on assumptions):** all measured dimensions
  strong (structural may be not applicable when there are no rejected rows).
- **B - decision-grade with caveats:** credible directional decision with one
  moderate dimension or a full-policy caveat.
- **C - collect more evidence:** any weak or unavailable dimension (including
  calibration and operational readiness), full-policy conflict, or an
  inconclusive point decision.
- **D - not identified:** the gate fails; no point estimate.

The grade never overrides the gate. A failed gate is D even if the point
estimate looks attractive.

### Reliability contract

The pipeline makes four enforceable commitments:

1. A failed gate returns **D** and withholds the point estimate.
2. A/B require a directional point decision and a pass on the measured
   dimensions; C/D are not released.
3. The profile reports every dimension, including the ones that failed; it does
   not collapse them into a single score.
4. The grade is reproducible from the log, candidate file, config, and bootstrap
   seed; the JSON records the method and `n_boot`.

It does **not** prove the observation model, the cost matrix, or the audit
design. Those remain reviewer responsibilities.

---

## 3. Why this is not a renamed metric

A generic OPE or model-risk report gives a point estimate, an interval, and a
list of limitations. This layer adds:

- **Decision-level resampling**: the unit is the policy decision, not the model
  score. The bootstrap answers “would I make the same decision on a different
  draw of applications?”
- **Calibration at the decision boundary**: a model can rank well and still be
  miscalibrated where the approve/review/reject thresholds sit.
- **Cost-stress stability**: the decision is re-evaluated over a cost grid
  before it is recommended.
- **Structural reliability**: the unobserved reject margin is a separate
  dimension, not a footnote.
- **Operational readiness**: the profile refuses to separate a statistical
  result from a log that cannot support it.

The contribution is the **integration and the refusal logic**, not a new
estimator. That is consistent with the project's claim: the applied measurement
layer is the contribution.

---

## 4. What the evidence shows

On the BAF simulation:

- The naive labeled mean is biased by 112–278% in the main scenario; the
  action-weighted baseline is within 2.9%; DR within 0.94%.
- A label-holdout split leaves the point-estimate gap intact (naive 275% vs
  action-weighted 4.2% / DR 2.8%) but the ranking remains unstable
  (DR-holdout 52% main, 70% at `frej_050`).
- The candidate is a modestly better ranker (AUC 0.8829 vs 0.8733); the
  better-model premise is real but small.
- The full-policy break-even can reverse the `P0` recommendation; the memo
  flags it.
- The bounds are wide in `frej_002`; the profile marks the structural dimension
  as a caveat, not a pass.

### 4.1 Two contrasting reports

| Case | Grade | Why |
|---|---|---|
| `examples/case_log.csv` (synthetic candidate clearly better, provided `e`; report in `reports/case_reliability/`) | **A** | bootstrap P(candidate cheaper)=0.998; full-policy robust; ECE 0.019; 9/9 cost cells; 2,496 labels |
| `reports/demo_reliability/` (near-tie, 267 labels) | **C** | bootstrap P=0.934; full-policy `P0 inconclusive`; outcome ECE 0.094; propensity calibration unavailable; 6/9 cost cells; operational readiness moderate |

The grade is not always A. It can separate a clear decision from a near-tie
with the same code path. That is the point of the profile.

### 4.2 Reliability audit

The per-replication audit (`reports/reliability_audit/`, 20 reps per scenario,
100 bootstrap replicates) released only **2 of 60** A/B directional decisions;
both were P0-correct, with **no false certification observed** (0/2; 95% upper bound 78%) and **9 of 11
directional decisions withheld (82%)**. Main: 1 B, 19 C. Lowest label rate: 20 D.
High false-reject cost: 1 A, 19 C. Identified directional accuracy was 4/7
(57%), or 5/11 (45%) if the gate-failed D diagnostics are included. The
profile is deliberately conservative; the cost of caution is decision volume,
not a confident wrong decision. The audit is small, post-hoc, and uses the
oracle action-level observation model, so it is a sampling/cost stability check,
not a propensity-misspecification stress test.

These are **simulation** results on public synthetic BAF data. They demonstrate
the reliability layer's behavior; they are not a bank estimate.

### 4.3 Restricted-feature failure

Removing `customer_age`, `employment_status`, and `income` preserved the main
point estimates but failed the release test: **5 A/B releases, 0 correct**, all
in `frej_050`, where the true candidate advantage is only about 0.53% of cost.
The bootstrap, cost stress, and full-policy check all agreed with the wrong sign.
The profile is not a certification and is under revision. See
[`RESTRICTED_FEATURE_AUDIT.md`](RESTRICTED_FEATURE_AUDIT.md).

---

## 5. How a risk team uses it

1. Run `onboarding-audit report` on a historical log.
2. Read the gate first. If it fails, stop; the profile is D.
3. Read the reliability profile. If C, collect labels/audit/cost agreement; do
   not act on the `P0` recommendation.
4. If A/B, use the memo as a **pre-pilot** decision aid; the observation model,
   cost matrix, and audit design still need review.
5. Re-run the profile on a new log snapshot; monitor the dimensions over time.
6. Do not treat the grade as a certification or a substitute for a controlled
   pilot.

---

## 6. Limitations

- The bootstrap fixes the nuisance models; it measures evaluation-sample
  uncertainty, not propensity/outcome-model uncertainty. A nuisance bootstrap
  is a future extension.
- The outcome calibration is measured on observed labels only; under
  outcome-dependent observation it is biased.
- Only a provided propensity is calibration-checked; an action-level estimate
  from the same observed rows is an identity and is not counted.
- The cost grid is a local stress test, not the institution's cost accounting.
- The operational dimension is a readiness screen, not a data-quality audit.
- The grade thresholds are conventions; they are documented and should be
  reviewed with a risk team.
- The evidence is simulation on BAF; no real bank log, no legal/ops review, no
  external reader.

---

## 7. Reproduce

```bash
pytest -q tests/test_reliability.py tests/test_report.py
onboarding-audit demo --out reports/demo_reliability
```

The memo §4.2 and `report.json` `diagnostics.reliability` contain the profile.

## 8. Related documents

- Methods: [`METHODS.md`](METHODS.md) §6.11
- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
- Technical note: [`TECHNICAL_NOTE.md`](TECHNICAL_NOTE.md)
- Model card: [`MODEL_CARD.md`](MODEL_CARD.md)
- Red-flag audit: [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md)
