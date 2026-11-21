# Results

**Status:** Canonical results summary for v0.2.1 (2026-11-20).
**Source of truth:** `reports/pilot.json` and
`reports/propensity_sensitivity.json`. The prose here interprets those files; it
does not replace them.

**Scope:** simulation on the public BAF account-opening test window. Not a
production estimate, not a Philippine bank, not a causal deployment effect.

---

## 1. Headline

1. **Naive evaluation is materially biased, but the magnitude is conditional.**
   Relative bias **+111.6% to +278.5%** in the main pilot; across the 12-cell
   observation-rate sweep, **+7.8% to +538.5%** (12/12 cells above 5%). The
   direction is robust; the magnitude depends on the approve-label and review
   rates. It overstates cost and reverses the better-model/incumbent ranking.
2. **DR recovers the identified `P0` value.** Max |relative bias| **0.94%**,
   mean 95% coverage **96.0%**; IPW **1.18% / 95.0%**. The corrected ranking is
   better but not perfect (DR mean inversions **0.29**, P(select true best)
   **72%**).
3. **The audit is not a universal fix.** At a 5% approved-label base rate, the
   marginal RMSE gain is modest; the audit is decisive under outcome-dependent
   labels.
4. **The reject margin is not point-identified.** The widest bounds interval is
   **0.009942**; the incumbent's narrow interval covers the true full value in
   **35%** of replications. Bounds are not confidence intervals.
5. **DR survives estimated action-level propensities; IPW does not.** DR
   **2.67% / 91.0%**; IPW **11.19% / 73.0%**.
6. **Under covariate-dependent observation, action-level weighting fails.**
   Action-level IPW is **67.52%** biased; action-level DR is **21.25%** biased.
   A fitted per-action covariate propensity model recovers the oracle
   (**1.97% / 91.5%** IPW, **2.48% / 89.5%** DR). This is the newest result and
   the reason the report supports `--propensity-model covariate`.

## 2. Pilot: naive bias and rank flips

Main scenario: 1% audit, 45-day median approve-label delay, default cost matrix,
100 replications.

| Policy | True `P0` | Naive estimate | Naive relative bias |
|---|---:|---:|---:|
| `incumbent` | 0.008785 | 0.018584 | +111.6% |
| `better_model` | 0.008452 | 0.025835 | +205.7% |
| `lenient_cost` | 0.009540 | 0.036109 | +278.5% |
| `strict_cost` | 0.012757 | 0.038502 | +201.8% |

True ranking: `better_model < incumbent < lenient_cost < strict_cost`.
Naive ranking: `incumbent < better_model < lenient_cost < strict_cost`.

The naive estimate has mean **1.00** pairwise inversion and selects the true best
policy **0%** of the time. The practical consequence: the naive evaluation would
reject the better model.

**Direction caveat:** the bias is positive (overstates cost) in this scenario
because the labeled subset is dominated by reviewed/rejected applications with
non-zero costs, and approved fraud is more likely to be labeled than approved
legitimate accounts. The direction is not universal; it depends on the action mix
and the cost matrix. The harm is the ranking, not the sign.

## 3. Pilot: estimator comparison

| Estimator | Target | Max \|relative bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `naive` | `P0` | 278.49% | 0.0% | 12,171 |
| `ipw_ht` | `P0` | 1.18% | 95.0% | 7,864 |
| `ipw_hajek` | `P0` | 1.18% | 95.0% | 7,864 |
| `dr` | `P0` | **0.94%** | **96.0%** | 7,864 |
| `audit_only` | approved | 2.98% | 84.5% | 1,271 |

The corrected ranking is much better than naive but not perfect:

| Estimator | Mean inversions | P(select true best) | Mean cost of misranking |
|---|---:|---:|---:|
| `naive` | 1.00 | 0% | 0.000333 |
| `dr` | 0.29 | 72% | 0.000093 |
| `ipw_ht` | 0.26 | 75% | 0.000083 |

The residual instability is concentrated in the close
better-model/incumbent gap. A launch decision should treat the corrected ranking
as evidence, not a guarantee.

### 3.1 Observation-rate robustness sweep

The main pilot fixes `e_approve=0.05` and `kappa_review=0.90`. The V1 sweep
varies them: `e_approve ∈ {0.01, 0.05, 0.20, 0.50}` ×
`kappa_review ∈ {0.50, 0.90, 1.00}`, 50 replications per cell, everything else
fixed.

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

**Read:** naive bias exceeds 5% in **12/12** cells, but the range is **7.8% to
538.5%**. DR with known propensities stays within **1.89%** and coverage is
**84.5–96.0%**. At the lowest approve-label rate, DR's P(select true best) is
**64%**, so the correction is accurate but the ranking is not guaranteed. The
sweep supports the premise and rejects a universal magnitude. See
[`../reports/obs_sweep/obs_sweep.md`](../reports/obs_sweep/obs_sweep.md).

## 4. Pilot: audit value

At a 5% approved-label base rate, the audit's marginal value is modest in the
main scenario:

| Audit | DR RMSE | DR ESS | Audit-only max bias | Audit-only coverage |
|---:|---:|---:|---:|---:|
| 0% | 0.001159 | 6,610 | — | — |
| 0.5% | — | — | 3.33% | 75.0% |
| 1% | — | — | 2.98% | 84.5% |
| 2% | 0.001068 | 9,126 | 1.82% | 86.5% |

The audit is decisive when approved fraud is more likely to be labeled than
approved legitimate accounts. In the outcome-dependent scenario, audit-only bias
is **-2.37% to -1.98%** (coverage 80–86%), while action-only IPW is **+43.9% to
+368.3%** and DR **+596.4% to +1301.5%**. This is the strongest practical
argument for the audit.

## 5. Pilot: capacity, delay, and cost

| Sweep | Result |
|---|---|
| Review capacity 1–10% | Max \|relative bias\| **1.71%**; coverage **94–98%** |
| Approve-label delay 0–90 days | At 90 days, mean ESS **3,308**; max \|relative bias\| **1.28%**; coverage **84–96%** |
| False-reject cost 0.02–0.50 | The correction holds; the ranking is cost-sensitive, so report the cost curve |

Precision falls with delay; the correction still holds. Capacity 1–10% does not
break the correction.

## 6. Pilot: reject-margin bounds

| Quantity | Value |
|---|---:|
| Widest bounds interval | **0.009942** |
| Incumbent bounds width | **0.001581** |
| Incumbent bounds coverage of true full value | **35%** |
| Bounds type | Partial-identification interval conditional on the `P0` estimate |

The bounds are **not** confidence intervals. The 35% coverage is a diagnostic
that the narrow interval is not a 95% interval; it does not mean the bounds are
"wrong." It means the full-population value is not point-identified from logs
alone.

## 7. Propensity sensitivity: estimated and noisy `e`

50 replications per scenario, common random numbers.

| Scenario | Estimator | Max \|relative bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `main` (oracle) | `ipw_ht` | 1.30% | 94.5% | 7,863 |
| `main` (oracle) | `dr` | 0.96% | 95.5% | 7,863 |
| `propensity_estimated` | `ipw_ht` | **11.19%** | **73.0%** | 8,438 |
| `propensity_estimated` | `dr` | **2.67%** | **91.0%** | 8,438 |
| `propensity_noisy_10` | `ipw_ht` | 1.09% | 95.5% | 7,787 |
| `propensity_noisy_10` | `dr` | 1.11% | 94.5% | 7,787 |
| `propensity_noisy_25` | `ipw_ht` | 7.01% | 93.5% | 7,397 |
| `propensity_noisy_25` | `dr` | 1.58% | 96.5% | 7,397 |

**Read:** the oracle-IPW result was partly an artifact of knowing `e`. With an
estimated action-level propensity, IPW fails the 5%/80% gate; DR passes. Use DR,
not IPW, when `e` is estimated.

## 8. Propensity sensitivity: outcome-dependent labels

| Scenario | Estimator | Max \|relative bias\| | Mean coverage |
|---|---|---:|---:|
| `outcome_dependent` | `audit_only` | **2.58%** | **82.5%** |
| `outcome_dependent` | `ipw_ht` | 368.25% | 1.0% |
| `outcome_dependent` | `dr` | 1301.53% | 0.0% |
| `outcome_dependent_estimated` | `audit_only` | **2.58%** | **82.5%** |
| `outcome_dependent_estimated` | `ipw_ht` | 1350.76% | 0.0% |
| `outcome_dependent_estimated` | `dr` | 1627.90% | 0.0% |

**Read:** when approved fraud is more likely to be labeled than approved
legitimate accounts, action-only weighting cannot separate the two rates.
Audit-only is the honest estimator. The audit is the identification device, not
a generic variance reduction.

## 9. Covariate-dependent observation

The post-approval report probability depends on standardized `log1p(amount)`:

```
logit(e_report) = logit(e_approve) + 0.75 * z
```

The review channel has the same gradient. The audit remains random. The outcome
model includes `log1p(amount)`, so DR has a second chance to adjust; IPW does
not. The `delay` variants add the 45-day approve-label delay.

| Scenario | Estimator | Max \|relative bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `covariate_oracle` | `ipw_ht` | 3.01% | 90.0% | 11,668 |
| `covariate_oracle` | `dr` | 2.63% | 89.0% | 11,668 |
| `covariate_action` | `ipw_ht` | **67.52%** | **1.5%** | 16,031 |
| `covariate_action` | `dr` | **21.25%** | **72.5%** | 16,031 |
| `covariate_model` | `ipw_ht` | **1.97%** | **91.5%** | 11,582 |
| `covariate_model` | `dr` | **2.48%** | **89.5%** | 11,582 |
| `covariate_action_delay` | `ipw_ht` | **51.72%** | **21.5%** | 9,938 |
| `covariate_action_delay` | `dr` | **17.59%** | **80.0%** | 9,938 |
| `covariate_model_delay` | `ipw_ht` | **3.35%** | **90.5%** | 6,798 |
| `covariate_model_delay` | `dr` | **3.68%** | **89.5%** | 6,798 |

Naive bias in the same scenarios is **226.03%** (delay 0.5) and **301.68%**
(delay 45).

**Read:**

1. **Action-level IPW fails catastrophically** when observation depends on the
   application: 67.52% bias without delay, 51.72% with delay. The action-level
   propensity is a weighted average that ignores the within-action gradient.
2. **Action-level DR is better than IPW but still fails.** 21.25% without delay,
   17.59% with delay. The outcome model includes the covariate, but it does not
   fully absorb the observation gradient. DR is not a universal immunity.
3. **The fitted covariate model recovers the oracle.** 1.97% / 2.48% without
   delay; 3.35% / 3.68% with delay. The cross-fitted per-action logistic model
   is the right correction for this mechanism.
4. **Coverage is ~89–91.5%, below nominal 95%.** The oracle itself has 89–90%
   coverage, so the shortfall is the heavy-tailed weight distribution, not the
   covariate model. A point estimate within 5% is not evidence that the interval
   is calibrated. The report must show ESS, max weight, and the weight tail.
5. **The practical rule:** if the observation rate varies across amount (or
   another pre-decision feature) within an action, use the covariate propensity
   model and report the weight diagnostics. If the rate is action-level, DR with
   an estimated action-level `e` is adequate.

## 10. Verdicts

| Hypothesis | Verdict | Key number |
|---|---|---|
| H1: naive bias > 5% | **Supported** | **+111.55% to +278.49%** |
| H2: naive rank inversion | **Supported** | Mean **1.00** inversion; P(select true best) **0%** |
| H3: correction <= 5% / coverage >= 80% | **Supported** | DR **0.94% / 96.0%**; IPW **1.18% / 95.0%** |
| H4: audit value | **Supported (modest in main; decisive under outcome-dependent labels)** | DR RMSE **0.001159 → 0.001068**; ESS **6,610 → 9,126**; audit-only **-2.37% to -1.98%** under outcome dependence |
| H5: reject margin not point-identified | **Supported** | Widest bounds **0.009942**; incumbent coverage **35%** (not a CI) |
| H6: outcome-dependent labels break action-only IPW | **Supported** | Audit-only **2.58% / 82.5%**; IPW **1350.8%**; DR **1627.9%** |
| S1 (post-hoc): covariate-dependent observation breaks action-level weighting | **Supported** | Action IPW **67.52%**, DR **21.25%**; covariate model **1.97% / 2.48%** |

S1 is post-hoc, not pre-registered. It is a sensitivity result, not a new
headline. The pre-registered H1–H6 remain the primary verdicts.

## 11. Negative controls

`pytest -q`: **57 passed**, including:

- full-observation identity (IPW/DR equal the full mean when `e=1`);
- full-audit identity (audit-only equals the approved mean);
- propensity recovery;
- bounds validity;
- capacity enforcement;
- no label leakage (permutation);
- schema validation;
- the arbitrary-log report's known-ground-truth check;
- the propensity and covariate helpers.

The tests protect the implementation, not the external validity of the
simulation.

## 12. What the results do not show

- No production or Philippine bank estimate.
- No causal deployment effect.
- No point-identified full-population value.
- No claim that the 1% audit detects small fraud-rate differences.
- No claim that the covariate model is correctly specified on a real log.
- No claim that the corrected ranking is always right; DR selects the true best
  72% of the time in the main pilot.
- No claim that the intervals are calibrated under heavy weights; coverage is
  89–91.5% in the covariate scenarios.

## 13. Related documents

- Methods: [`METHODS.md`](METHODS.md)
- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Pilot specification: [`PILOT_SPEC.md`](PILOT_SPEC.md)
- Generated pilot report: [`../reports/pilot.md`](../reports/pilot.md)
- Generated sensitivity report:
  [`../reports/propensity_sensitivity.md`](../reports/propensity_sensitivity.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
