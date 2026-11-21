# Claim Ledger

**Status:** Canonical claim ledger for v1.0.0 (2026-11-22).

**V1 re-evaluation (2026-11-21):** the 12-cell observation-rate sweep is
complete. The maximum naive bias across the four policies is **7.8–538.5%** and
exceeds 5% in **12/12** cells. The incumbent's own naive bias is **1.5–218%** and
exceeds 5% in **11/12** cells (1.52% at `e050_k050`). The main-scenario
**112–278%** is one point in that range, not a universal magnitude. DR with known
propensities has a mean bias of at most **1.89%**, with a 95% Monte Carlo upper
bound on |bias| of **4.3%** for `e_approve >= 0.05` and **9.6%** at
`e_approve = 0.01`. See [`V1/EXPERIMENTS.md`](V1/EXPERIMENTS.md).

**Rule:** Every public claim carries one status: **Measured**, **Pre-registered**,
**Post-hoc**, **Non-finding**, or **Limitation**. A number that is not in the
pilot output or a cited primary source does not appear in the paper.

| Claim | Status | Evidence | What would change it |
|---|---|---|---|
| BAF is account-opening fraud data, not transaction authorization data | **Measured** (dataset paper) | Jesus et al., NeurIPS 2022, arXiv:2211.13358 | — |
| Pombal et al. used account-opening fraud for selective labels/performative prediction | **Measured** (paper) | arXiv:2206.13183 | — |
| BSP Circular 1213 mandates calibration, stress testing, independent review/audit | **Measured** (regulation) | BSP Circular 1213 (2025) | A superseding circular |
| The 11 mandated log fields contain no decision, score, or outcome | **Measured** (regulation) | BSP Circular 1213 logging provision | A new circular adding fields |
| BSP Circular 1170 governs eKYC/digital identity proofing | **Measured** (regulation) | BSP Circular 1170 (2023) | A superseding circular |
| AFASA s.6 ties inadequate controls to restitution without conviction | **Measured** (statute) | RA 12010, s.6 | A statutory amendment |
| BSP Project Sapiens names sampling/labelling bias | **Measured** (BSP document) | Project Sapiens 2024, bias taxonomy | — |
| Only 6/10 deep-dive institutions validate AI models during development and ongoing | **Measured** (BSP document) | Project Sapiens 2024 | A different sample or later review |
| Vendors sell replay/champion–challenger but not selection/delay-aware policy evaluation | **Measured** (vendor review) | 18-vendor capability matrix, 2026 | A vendor shipping the missing layer |
| No fraud-specific OPE library exists | **Limitation** (search-based absence) | Open-source review, 2026 | A new release |
| No peer-reviewed fraud-specific policy evaluation with a counterfactual design | **Limitation** (search-based absence) | Literature review, 25 sources | A paper not surfaced by the search |
| Naive onboarding evaluation is materially biased under the main scenario | **Measured** (H1 supported) | `reports/pilot.json`; relative bias **+111.55% to +278.49%** across the four policies | A different logging action mix, cost matrix, or observation mechanism |
| Naive bias exceeds 5% across plausible observation rates | **Measured** (V1 E1 sweep) | Maximum across policies **7.8-538.5%**, **12/12** cells; incumbent **1.5-218%**, **11/12** cells (`reports/obs_sweep/pilot.json`) | A different observation mechanism or policy mix |
| The bias magnitude is conditional on observation rates | **Measured** (V1 E1 sweep) | **386-538%** at `e_approve=0.01`; **7.8-34.7%** at `e_approve=0.50` (max across policies) | A different frame or cost matrix |
| DR with known propensities is robust to observation-rate changes | **Measured** (V1 E1 sweep) | Mean bias max **1.89%**; 95% MC upper bound on \|bias\| **4.3%** for `e>=0.05`, **9.6%** at `e=0.01`; coverage **84.5-96.0%** | Estimated propensities, not oracle `e` |
| The corrected ranking is weaker at low approve-label rates | **Measured** (V1 E1 sweep) | DR P(select true best) **64%** at `e_approve=0.01`; **96–100%** at `0.50` | A larger audit or a wider policy gap |
| The naive estimate reverses at least one policy ranking | **Measured** (H2 supported) | True ranking `better_model < incumbent < lenient_cost < strict_cost`; naive ranking `incumbent < better_model < lenient_cost < strict_cost`; mean inversions **1.00**, P(select true best) **0%** | A larger gap between the top policies, or a different review capacity |
| At least one corrected estimator recovers the identified policy value | **Measured** (H3 supported) | DR max \|relative bias\| **0.94%**, mean coverage **96.0%**; IPW max **1.18%**, mean coverage **94.5%** | Estimated propensities, a different observation mechanism, or a much smaller audit |
| The corrected ranking is better but not perfect | **Measured** | DR mean inversions **0.29**, P(select true best) **72%**, cost of misranking **0.000093**; IPW **0.26 / 75% / 0.000083** | A larger audit, a wider policy gap, or a better outcome model |
| The naive estimate would reject the better model | **Measured** | Naive: `better_model` **0.025835** vs `incumbent` **0.018584**; true: `better_model` **0.008452** vs `incumbent` **0.008785** | A different cost matrix or action mix; the direction of the bias is not universal |
| Audit-only is unbiased but high variance at a 1% audit | **Measured** | Max \|relative bias\| **2.98%**, mean coverage **84.5%**, mean ESS **1,271** | A larger audit; a different approved-label base rate |
| A larger audit improves the corrected estimator modestly in the main scenario | **Measured** (H4 supported, modest effect) | DR RMSE **0.001159 → 0.001068** (0% → 2%), ESS **6,610 → 9,126**; IPW **0.001162 → 0.001088** | A lower base approve-label rate, or outcome-dependent labels |
| Both DR and IPW survive estimated action-level propensities when observation is action-dependent | **Measured** | DR max \|relative bias\| **1.43%**, mean coverage **93.5%**; IPW max **2.92%**, coverage **92.0%** (`reports/propensity_sensitivity.json`) | Covariate-dependent observation (tested below); a much smaller audit |
| The earlier "IPW fails with estimated e" result was a propensity bug | **Measured** (correction) | The old action-level `e_approve` omitted the resolution factor on the audit channel; after the fix IPW is **2.92%**, not 11.19% | A different audit design or resolution model |
| Noisy propensities degrade IPW faster than DR | **Measured** | At sigma 0.25: DR **1.58%/96.5%**, IPW **7.01%/93.0%** | A different noise model |
| Outcome-dependent labels with estimated e break action-only estimators | **Measured** (H6 extended) | Audit-only **2.58%/82.5%**; IPW **2064.90%/0%**; DR **1737.02%/0%** | An action-dependent observation mechanism, or an audit-labeled approved sample |
| Covariate-dependent observation breaks action-level IPW | **Measured** (post-hoc S1) | Action-level IPW max **67.52%**, coverage **1.0%** (delay 0.5); **64.27% / 10.0%** (delay 45) | A different observation gradient, or an outcome model that fully absorbs it |
| Covariate-dependent observation also breaks action-level DR | **Measured** (post-hoc S1) | Action-level DR max **21.25%**, coverage **72.5%** (delay 0.5); **20.27% / 79.0%** (delay 45) | A covariate propensity model; DR alone is not enough |
| A fitted covariate propensity model recovers the oracle under covariate-dependent observation | **Measured** (post-hoc S1) | Covariate model: IPW **1.97%/91.5%**, DR **2.48%/89.5%** (delay 0.5); **3.35%/90.5%** and **3.68%/89.5%** (delay 45); oracle **3.01%/90.0%** and **2.63%/89.0%** | A misspecified covariate model, or a real log with unmeasured observation drivers |
| DR is approximately unbiased when either the propensity or the outcome model is correct | **Measured** (double-robustness test) | Correct `e`/wrong outcome **+0.14%**; wrong `e`/correct outcome **+0.36%**; 200 reps (`reports/double_robustness.json`) | A different outcome model, a much stronger misspecification, or a different observation mechanism |
| IPW fails when the propensity is wrong, and the plug-in fails when the outcome model is wrong | **Measured** (double-robustness test) | Wrong `e`: IPW **−36.72%**; wrong outcome: plug-in **+5.09%** | A different misspecification magnitude |
| DR degrades gracefully when both nuisances are wrong | **Measured** (one DGP) | Both wrong: DR **+2.09%**, IPW **−36.87%**, plug-in **+5.33%** | A different data-generating process; this is not a guarantee |
| The main result holds separately in both BAF test months | **Measured** (temporal stability) | Month 5: naive **230.37%**, DR **0.89%**, naive P(best) **0%**, DR **65%**; month 6: **254.99%**, **0.43%**, **0%**, **63%** (`reports/temporal_stability.json`) | A different split, or a real log |
| Heavy weights undercover even with oracle propensities | **Measured** (caveat) | Covariate-oracle coverage **89–90%**, covariate-model **89.5–91.5%**, below nominal 95% | A bootstrap/randomization-inference interval, or a different weight estimator |
| The audit stays approximately unbiased when approved labels are outcome-dependent | **Measured** (H6 supported) | Audit-only bias **-2.37% to -1.98%**, coverage **80-86%** (below nominal); IPW **+43.90% to +368.25%**; DR **+596.41% to +1301.53%** | An observation mechanism that is action-dependent after all |
| The reject margin is not point-identified from logs alone | **Measured** (H5 supported) | Widest **0.009942** in the main scenario; **0.203** in `frej_002` (12.3% reject share); incumbent width **0.001581** with **34%** coverage of the true full value | A controlled approval design or a defensible assumption |
| The bounds are not confidence intervals | **Measured** (caveat) | Incumbent bounds cover the true full value in **34%** of replications; bounds are conditional on the P0 estimate | A different P0 estimator or a wider interval construction |
| The pre-registered bounds coverage gate fails for the narrow interval | **Measured** (V1 E2, F5 failed) | Narrow `coverage_full >= 90%` in **15/88** cells; widened interval **77/88**; the 11 widened failures are the biased-`P0` cells | A valid narrow confidence-interval construction |
| Widening the bounds by the `P0` standard error gives a conservative interval | **Measured** (diagnostic) | Unconditional coverage **99–100%** in the main scenario; width ~4× the narrow interval; **0%** under outcome-dependent labels | A valid interval under outcome-dependent observation |
| Review capacity 1–10% does not break the correction | **Measured** | Max \|relative bias\| **1.71%**; coverage **94–98%** | A much smaller capacity or a policy with no overlap |
| A 90-day delay reduces precision but not correctness | **Measured** | Mean ESS **3,308**; max \|relative bias\| **1.28%**; coverage **84–96%** | A longer delay or informative censoring |
| The report refuses a declared outcome-dependent observation mechanism | **Measured** (mechanism) | `tests/test_gates.py`; the demo with `--observation-assumption outcome` refuses and withholds estimates | An analyst who declares the wrong mechanism |
| An undeclared observation mechanism is marked unverified, not measured | **Measured** (mechanism) | The memo says "Measured (observation assumption unverified)" by default | — |
| The report post-stratifies the audit-only estimate by follow-up time | **Measured** (mechanism) | Cohort test: complete-case 1.667, post-stratified 2.0, truth 2.0 (`tests/test_report.py`) | Within-stratum missing-at-random; a per-row resolution model would be sharper |
| The report outputs a paired candidate-vs-incumbent comparison | **Measured** (mechanism) | P(candidate cheaper), expected regret, and a recommendation; `tests/test_estimators.py`, `tests/test_demo.py` | Nuisance-estimation uncertainty is ignored; the comparison is `P0`-conditional |
| The naive ranking flips in the committed case study | **Measured** (known truth) | Naive candidate **+6.3% worse**; true candidate **−12.4% better**; report P(better) **0.984** (`examples/case_truth.json`, `tests/test_case_study.py`) | A different cost matrix or observation rate |
| The pilot generalizes to a Philippine production system | **Not claimed** | Public synthetic data; simulation | A bank partner and real logs |
| A random approval/rejection arm is acceptable | **Not claimed** | `AUDIT_DESIGN.md` | Legal/risk review |
| The audit is a universal bias fix | **Limitation / non-finding** | In the main scenario with a 5% approved-label base rate, the audit's marginal RMSE gain is modest; it is the only approximately unbiased estimator under outcome-dependent labels, but its coverage is 80-86%, below nominal | A lower base label rate or a different audit design |

## Interpretation

1. **The premise is real but the magnitude is conditional.** In the main
   scenario, naive evaluation overstates cost by 112–278%. Across the 12-cell
   observation-rate sweep, the maximum across policies exceeds 5% in **every**
   cell, but the range is **7.8–538.5%**. The incumbent's own bias is
   **1.5–218%**, above 5% in 11/12 cells. The direction is robust; the magnitude
   is not.
2. **The direction is not "flattering the incumbent."** The labeled subset is
   dominated by reviewed/rejected applications with non-zero costs, so the naive
   estimate overstates cost. The practical harm is that it would **reject the
   better model**: the naive ranking puts the incumbent ahead of the better
   model, while the true ranking reverses it.
3. **The correction works on the identified population.** DR has a mean bias of
   at most 0.94% in the main scenario (95% MC upper bound 3.8%) with 96%
   coverage; IPW is within 1.18% with 95% coverage. In the observation-rate
   sweep, DR's mean bias is at most **1.89%** (95% MC upper bound 4.3% for
   `e>=0.05`, 9.6% at `e=0.01`), but its P(select true best) falls to **64%**
   [50%, 76%] at the lowest approve-label rate. The residual rank instability is
   concentrated in the close better-model/incumbent gap.
4. **The audit is not a universal bias fix.** At a 5% pre-resolution
   post-approval report probability (3.06% realized), a 1% audit mainly
   validates the approved margin and improves ESS; it does not change the
   log-based estimate much. It becomes the only approximately unbiased
   estimator when approved fraud is more likely to be labeled than approved
   legitimate accounts — but its interval is still undercovered (80–86%).
5. **The reject margin needs bounds.** The main-scenario interval is 0.009942;
   with a low false-reject cost (`frej_002`) it is **0.203**, 20× wider. The
   narrower incumbent interval covers the true full value only 34% of the time.
   Do not report the narrow interval as a confidence interval or a point
   estimate.
6. **The correction depends on the observation model.** Action-level IPW fails
   under covariate-dependent observation (**67.52%** bias); action-level DR is
   better but still fails (**21.25%**). The fitted covariate propensity model
   recovers the oracle (**1.97–2.48%** without delay, **3.35–3.68%** with
   delay). The practical rule is: match the propensity model to the observation
   mechanism, and report the weight diagnostics. A point estimate within 5% is
   not evidence that the interval is calibrated; covariate-oracle coverage is
   **89–90%**, not 95%.
7. **DR has the double-robustness property it claims.** In a known-truth test,
   DR is approximately unbiased when either the propensity or the outcome model
   is correct (**0.14%** and **0.36%**), while IPW fails with a wrong propensity
   (−36.7%) and the plug-in fails with a wrong outcome model (+5.1%). When both
   are wrong, DR is no longer guaranteed (+2.1%). The practical rule: get one of
   the two models right, and report which one you trust.
