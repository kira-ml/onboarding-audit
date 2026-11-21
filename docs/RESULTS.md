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
   observation-rate sweep, the maximum across policies is **+7.8% to +538.5%**
   (12/12 cells above 5%). The incumbent's own bias is **1.5–218%**, above 5% in
   11/12 cells. The direction is robust; the magnitude depends on the
   pre-resolution report probability and the review rate. It overstates cost and
   reverses the better-model/incumbent ranking.
2. **DR recovers the identified `P0` value.** Mean |relative bias| **0.94%**,
   mean 95% coverage **96.0%**; IPW **1.18% / 94.5%**. The 95% Monte Carlo upper
   bound on the mean |bias| is **3.8%** in the main scenario, not 0.94%. The
   corrected ranking is better but not perfect (DR mean inversions **0.29**,
   P(select true best) **72%**).
3. **The audit is not a universal fix.** At a 5% pre-resolution report
   probability (3.06% realized), the marginal RMSE gain is modest; the audit is
   the only approximately unbiased option under outcome-dependent labels.
4. **The reject margin is not point-identified.** The main-scenario interval is
   **0.009942**; with a low false-reject cost (`frej_002`) it is **0.203**, 20×
   wider. The incumbent's narrow interval covers the true full value in **34%**
   of replications. The narrow interval is not a confidence interval; the
   widened interval is, but it is ~4× wider. The pre-registered F5 gate
   **failed** for the narrow interval (15/88 cells at ≥90%) and **passes** for
   the widened interval (99–100% in the main scenario).
5. **Both DR and IPW survive estimated action-level propensities; DR is
   better under noise.** DR **1.43% / 93.5%**; IPW **2.92% / 92.0%**. The earlier
   "IPW 11.19%" was an `e_approve` bug, corrected on 2026-11-21.
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
| `ipw_ht` | `P0` | 1.18% | 94.5% | 7,864 |
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

**`e_approve` is the pre-resolution post-approval report probability, not the
realized label rate.** With the 45-day median delay and 90-day cutoff, the
realized post-approval label rates are **0.61%, 3.06%, 12.24%, and 30.59%**; the
main scenario's 5% is **3.06%** realized (3.68% including the 1% audit). The
sweep axis is labelled by the parameter, but every interpretation uses the
realized rate.

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

**Read:** the maximum naive bias across policies exceeds 5% in **12/12** cells,
but the range is **7.8% to 538.5%**; the incumbent's own bias is **1.5–218%**,
above 5% in 11/12. DR with known propensities has a mean bias of at most
**1.89%**, a 95% Monte Carlo upper bound of **4.3%** for `e>=0.05` (**9.6%** at
`e=0.01`), and coverage of **84.5-96.0%**. At the lowest report probability,
DR's P(select true best) is **64%**, so the correction is accurate but the
ranking is not guaranteed. The sweep supports the premise and rejects a
universal magnitude. See
[`../reports/obs_sweep/obs_sweep.md`](../reports/obs_sweep/obs_sweep.md).

**Monte Carlo precision.** Each cell has 50 replications. The Wilson 95%
intervals are wide: DR P(best) at `e_approve=0.01` is **64% [50%, 76%]**, and at
`e_approve=0.50` it is **96–100% [86.5%, 100%]**. DR coverage at low `e` is
**84.5–85.5% [78.8%, 89.7%]**. The direction of the contrast is solid; the
decimal places are not. Do not quote a one-point difference between cells as a
finding. The intervals are in
[`../reports/obs_sweep/obs_sweep.md`](../reports/obs_sweep/obs_sweep.md); the
coverage interval treats policy–replications as independent, so it is an
optimistic lower bound on the uncertainty.

## 4. Pilot: audit value

At a 5% approved-label base rate, the audit's marginal value is modest in the
main scenario:

| Audit | DR RMSE | DR ESS | Audit-only max bias | Audit-only coverage |
|---:|---:|---:|---:|---:|
| 0% | 0.001159 | 6,610 | — | — |
| 0.5% | — | — | 3.33% | 75.0% |
| 1% | — | — | 2.98% | 84.5% |
| 2% | 0.001068 | 9,126 | 1.82% | 86.5% |

The audit is the only approximately unbiased option when approved fraud is more
likely to be labeled than approved legitimate accounts. In the outcome-dependent
scenario, audit-only bias is **-2.37% to -1.98%** (coverage 80–86%, below
nominal), while action-only IPW is **+43.9% to +368.3%** and DR **+596.4% to
+1301.5%**. This is the strongest practical
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
| Bounds interval, main scenario | **0.009942** |
| Bounds interval, `frej_002` (12.3% reject share) | **0.203** |
| Incumbent bounds width | **0.001581** |
| Incumbent bounds coverage of true full value | **34%** |
| Bounds type | Partial-identification interval conditional on the `P0` estimate |

**F5 failed for the narrow interval; it passes for the widened one.** The
pre-registered F5 criterion was `coverage_full >= 90%`.

| Interval | F5 pass | Coverage | Width (incumbent) |
|---|---:|---:|---:|
| Narrow (conditional on `P0`) | **15/88** | main **34–87%** | **0.001581** |
| Widened by the `P0` standard error | **77/88** | main **99–100%** | **0.006780** |

The 11 widened-interval failures are exactly the cells where the `P0` estimate
itself is biased: the eight outcome-dependent cells, the two action-level
covariate cells, and `delay_90`. That is the correct behavior: widening cannot
repair a biased center.

The correct reading is:

- The **narrow** interval is not a confidence interval and fails F5.
- The **widened** interval is a valid (conservative) 95% confidence interval for
  the full-population value *under the identification assumptions*
  (action-dependent observation, correct cost range). It passes F5 except where
  those assumptions fail. The width is the price of the `P0` uncertainty.
- Neither interval is valid when the observation mechanism is outcome-dependent.

Per the E2 decision rule, the coverage claim for the narrow interval is removed.
The bounds are reported as a partial-identification range with the reject share,
the widened width, and the assumption they require.

## 7. Propensity sensitivity: estimated and noisy `e`

50 replications per scenario, common random numbers.

| Scenario | Estimator | Max \|relative bias\| | Mean coverage | Mean ESS |
|---|---|---:|---:|---:|
| `main` (oracle) | `ipw_ht` | 1.30% | 94.5% | 7,863 |
| `main` (oracle) | `dr` | 0.96% | 95.5% | 7,863 |
| `propensity_estimated` | `ipw_ht` | **2.92%** | **92.0%** | 8,404 |
| `propensity_estimated` | `dr` | **1.43%** | **93.5%** | 8,404 |
| `propensity_noisy_10` | `ipw_ht` | 1.09% | 95.0% | 7,787 |
| `propensity_noisy_10` | `dr` | 1.11% | 94.5% | 7,787 |
| `propensity_noisy_25` | `ipw_ht` | 7.01% | 93.0% | 7,397 |
| `propensity_noisy_25` | `dr` | 1.58% | 96.5% | 7,397 |

**Read:** with the corrected marginal propensity, both estimators survive
action-level estimation (DR **1.43%**, IPW **2.92%**); the earlier "IPW 11.19%"
was an artifact of an `e_approve` formula that omitted the resolution factor on
the audit channel. DR remains better under noisy propensities (sigma 0.25:
**1.58%** vs **7.01%**). Use DR, not IPW, when `e` is noisy or
covariate-dependent.

## 8. Propensity sensitivity: outcome-dependent labels

| Scenario | Estimator | Max \|relative bias\| | Mean coverage |
|---|---|---:|---:|
| `outcome_dependent` | `audit_only` | **2.58%** | **82.5%** |
| `outcome_dependent` | `ipw_ht` | 368.25% | 1.0% |
| `outcome_dependent` | `dr` | 1301.53% | 0.0% |
| `outcome_dependent_estimated` | `audit_only` | **2.58%** | **82.5%** |
| `outcome_dependent_estimated` | `ipw_ht` | 2064.90% | 0.0% |
| `outcome_dependent_estimated` | `dr` | 1737.02% | 0.0% |

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
| `covariate_action_delay` | `ipw_ht` | **64.27%** | **10.0%** | 9,904 |
| `covariate_action_delay` | `dr` | **20.27%** | **79.0%** | 9,904 |
| `covariate_model_delay` | `ipw_ht` | **3.35%** | **90.5%** | 6,798 |
| `covariate_model_delay` | `dr` | **3.68%** | **89.5%** | 6,798 |

Naive bias in the same scenarios is **226.03%** (delay 0.5) and **301.68%**
(delay 45).

**Read:**

1. **Action-level IPW fails catastrophically** when observation depends on the
   application: 67.52% bias without delay, 64.27% with delay. The action-level
   propensity is a weighted average that ignores the within-action gradient.
2. **Action-level DR is better than IPW but still fails.** 21.25% without delay,
   20.27% with delay. The outcome model includes the covariate, but it does not
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

## 10. Double robustness (semi-synthetic)

The pilot uses BAF's real labels, so the outcome model's misspecification is
unknown. A separate 200-replication experiment makes it known: the outcome is
generated from a logistic model with an interaction (`x1*x2`); the analyst fits
either a main-effects model (misspecified) or the interaction model (correct).
The propensity is either the true one or a biased copy (`1.6x`).

| Arm | Plug-in | IPW | DR |
|---|---:|---:|---:|
| Correct `e`, wrong outcome model | **+5.09%** | +0.69% | **+0.14%** |
| Wrong `e`, correct outcome model | +0.34% | **−36.72%** | **+0.36%** |
| Both wrong | +5.33% | −36.87% | +2.09% |

**Read:** DR is approximately unbiased when *either* nuisance is correct
(**0.14%** and **0.36%**). IPW fails when `e` is wrong (−36.7%); the plug-in
fails when the outcome model is wrong (+5.1%). When both are wrong, DR degrades
gracefully (+2.1%) but is no longer guaranteed. This is the double-robustness
property the method relies on, tested directly rather than asserted.

**Caveat:** one data-generating process, one misspecification, 200 replications.
It demonstrates the mechanism; it does not prove robustness in every setting.
Artifact: `reports/double_robustness.json`; script:
`scripts/double_robustness.py`.

## 11. Verdicts

| Hypothesis | Verdict | Key number |
|---|---|---|
| H1: naive bias > 5% | **Supported** | **+111.55% to +278.49%** |
| H2: naive rank inversion | **Supported** | Mean **1.00** inversion; P(select true best) **0%** |
| H3: correction <= 5% / coverage >= 80% | **Supported** | DR **0.94% / 96.0%**; IPW **1.18% / 94.5%** |
| H4: audit value | **Supported (modest in main; the only approximately unbiased option under outcome-dependent labels)** | DR RMSE **0.001159 → 0.001068**; ESS **6,610 → 9,126**; audit-only **-2.37% to -1.98%** under outcome dependence |
| H5: reject margin not point-identified | **Supported** | Main interval **0.009942**, `frej_002` **0.203**; incumbent coverage **34%** (narrow interval not a CI); F5 **failed** for the narrow interval (15/88), **passes** for the widened one |
| H6: outcome-dependent labels break action-only IPW | **Supported** | Audit-only **2.58% / 82.5%**; IPW **2064.9%**; DR **1737.0%** |
| S1 (post-hoc): covariate-dependent observation breaks action-level weighting | **Supported** | Action IPW **67.52%**, DR **21.25%**; covariate model **1.97% / 2.48%** |

S1 is post-hoc, not pre-registered. It is a sensitivity result, not a new
headline. The pre-registered H1–H6 remain the primary verdicts.

## 12. Negative controls

`pytest -q`: **87 passed**, including:

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

## 13. What the results do not show

- No production or Philippine bank estimate.
- No causal deployment effect.
- No point-identified full-population value.
- No claim that the 1% audit detects small fraud-rate differences.
- No claim that the covariate model is correctly specified on a real log.
- No claim that the corrected ranking is always right; DR selects the true best
  72% of the time in the main pilot.
- No claim that the intervals are calibrated under heavy weights; coverage is
  89–91.5% in the covariate scenarios.

## 14. Related documents

- Methods: [`METHODS.md`](METHODS.md)
- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Pilot specification: [`PILOT_SPEC.md`](PILOT_SPEC.md)
- Generated pilot report: [`../reports/pilot.md`](../reports/pilot.md)
- Generated sensitivity report:
  [`../reports/propensity_sensitivity.md`](../reports/propensity_sensitivity.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
