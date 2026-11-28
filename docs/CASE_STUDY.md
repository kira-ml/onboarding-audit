# Case Study — A Better Candidate That Looks Worse

**Status:** V1 worked case, 2026-11-21.
**Data:** synthetic, 20,000 applications, committed in `examples/case_log.csv`.
**Purpose:** show the decision the layer changes, end to end, with a known truth.

---

## 1. The question

A bank reviews 5% of account applications and approves the rest. A candidate
score ranks fraud better than the incumbent. The team runs the usual backtest on
the labeled data:

> The candidate looks **6.3% more expensive**. Should we keep the incumbent?

The correct answer is the opposite: the candidate is **12.4% cheaper**. This case
study shows why, and what the audit layer reports.

## 2. The setup

| Item | Value |
|---|---|
| Applications | 20,000 |
| Fraud rate | 4.93% |
| Review capacity | 5% (1,000 applications) |
| Review labels | 90% resolved |
| Approve labels | 8% post-approval reports + 1% random audit = **8.92%** |
| Observation model | known action-level `e` (provided in the log) |
| Incumbent score | true fraud probability + noise (sd 0.08) |
| Candidate score | true fraud probability + noise (sd 0.003) |
| Cost unit | normalized; fraud loss `amount * 0.02`, review cost 0.02, residual fraud 0.30, false reject 1000 |

The candidate is an **oracle score**: a less noisy estimate of the true
probability, not a model trained on pre-decision features. It is a best-case
benchmark for the evaluation layer, not a demonstration that a real challenger
model would produce the same gain. It does not observe the label `y`, but it does
observe the data-generating probability, which a real model cannot.

## 3. The naive answer

The labeled sample is not random. Reviewed applications are labeled at 90%;
approved applications at 8.9%. Reviews are 5% of the population but **36% of the
labeled sample**.

| Policy | Naive cost on labeled rows | True cost on `P0` |
|---|---:|---:|
| Incumbent | **0.5137** | 0.6865 |
| Candidate | **0.5460** | **0.6016** |
| Naive verdict | candidate **+6.3% worse** | candidate **−12.4% better** |

The candidate's review set is enriched in fraud (36.9% vs 29.5%), so its labeled
review rows carry more residual fraud cost. The naive mean is dominated by those
rows. The candidate's gain — catching more fraud before approval — is in the
approved population, which is barely labeled. The backtest sees the cost and
misses the benefit.

## 4. What the report says

```bash
onboarding-audit report \
  --log examples/case_log.csv \
  --candidate examples/case_candidate.csv \
  --config configs/case_study.yaml \
  --capacity 0.05 \
  --observation-assumption action \
  --out reports/case_study
```

| Quantity | Value |
|---|---:|
| Identification gate | **passed** |
| Naive estimate | 0.5460 |
| DR estimate | 0.6230 |
| Incumbent `P0` value | 0.7042 |
| Difference (candidate − incumbent) | **−0.0820** |
| 95% interval | **[−0.1558, −0.0081]** |
| P(candidate cheaper) | **0.985** |
| Expected regret if candidate | **0.0002** |
| Expected regret if incumbent | **0.0822** |
| Recommendation | **prefer candidate** |

The DR estimate is 3.6% above the true value (0.6230 vs 0.6016) and the incumbent
estimate 2.6% above (0.7042 vs 0.6865), but the **difference** is close
(−0.0820 vs −0.0850) and the decision is correct. The naive estimate would have
kept the worse policy.

## 5. Why the correction works here

- The candidate is an oracle score (true probability plus small noise); this
  isolates the evaluation bias from model-training quality.
- The observation mechanism is action-dependent and the action-level propensity
  is correct: review 90%, approve 8.9%.
- The outcome model uses the incumbent score, age, and credit risk; it is an
  approximation, but the propensity carries the identification.
- The comparison is paired: the candidate and incumbent differ on the review
  set, so the shared rows cancel in the difference.

## 6. What would change the answer

| Change | Effect |
|---|---|
| Approve labels at 1% instead of 8.9% | The interval widens; the decision may become inconclusive |
| Outcome-dependent approve labels | The action-only estimators break; use an audit-labeled sample |
| Observation depending on amount within action | Use `--propensity-model covariate`; action-level `e` is misspecified |
| A different cost matrix | The review/approve trade-off changes; report the cost curve |
| A smaller true gain | The decision becomes inconclusive; the tool says so rather than guessing |

## 7. What this case does not show

- It is synthetic. The truth is known by construction; a bank's log is not.
- It uses a normalized cost matrix, not pesos.
- It evaluates `P0`; a candidate that changes logging-rejected rows needs the
  bounds and a controlled design.
- It deliberately uses a high false-reject cost (one logging-rejected row), so it
  isolates the **selection** margin. It does not demonstrate the full-policy
  decision check; the unit tests and the BAF pilot exercise a material reject
  margin. Do not read this case as evidence that the reject margin is solved.
- The candidate is an **oracle** by construction. It does not show that a model
  trained on pre-decision features would produce the same gain. A trained-model
  case is a separate experiment.
- It is one draw. The report's interval is the relevant uncertainty; the point
  estimate alone is not a decision.

## 8. Reproduce

```bash
python scripts/make_case_study.py
onboarding-audit report \
  --log examples/case_log.csv \
  --candidate examples/case_candidate.csv \
  --config configs/case_study.yaml \
  --capacity 0.05 \
  --observation-assumption action \
  --out reports/case_study
pytest -q tests/test_case_study.py
```

The test asserts the naive ranking flip and the report's recommendation, so the
case cannot silently drift.

## 9. Related documents

- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Model card: [`MODEL_CARD.md`](MODEL_CARD.md)
- Pilot protocol: [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md)
