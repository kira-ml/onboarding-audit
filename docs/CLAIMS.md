# Claim Ledger

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
| The naive estimate reverses at least one policy ranking | **Measured** (H2 supported) | True ranking `better_model < incumbent < lenient_cost < strict_cost`; naive ranking `incumbent < better_model < lenient_cost < strict_cost`; mean inversions **1.00**, P(select true best) **0%** | A larger gap between the top policies, or a different review capacity |
| At least one corrected estimator recovers the identified policy value | **Measured** (H3 supported) | DR max \|relative bias\| **0.94%**, mean coverage **96.0%**; IPW max **1.18%**, mean coverage **95.0%** | Estimated propensities, a different observation mechanism, or a much smaller audit |
| The corrected ranking is better but not perfect | **Measured** | DR mean inversions **0.29**, P(select true best) **72%**, cost of misranking **0.000093**; IPW **0.26 / 75% / 0.000083** | A larger audit, a wider policy gap, or a better outcome model |
| The naive estimate would reject the better model | **Measured** | Naive: `better_model` **0.025835** vs `incumbent` **0.018584**; true: `better_model` **0.008452** vs `incumbent` **0.008785** | A different cost matrix or action mix; the direction of the bias is not universal |
| Audit-only is unbiased but high variance at a 1% audit | **Measured** | Max \|relative bias\| **2.98%**, mean coverage **84.5%**, mean ESS **1,271** | A larger audit; a different approved-label base rate |
| A larger audit improves the corrected estimator modestly in the main scenario | **Measured** (H4 supported, modest effect) | DR RMSE **0.001159 → 0.001068** (0% → 2%), ESS **6,610 → 9,126**; IPW **0.001162 → 0.001088** | A lower base approve-label rate, or outcome-dependent labels |
| The audit is decisive when approved labels are outcome-dependent | **Measured** (H6 supported) | Audit-only bias **-2.37% to -1.98%**, coverage **80–86%**; IPW **+43.90% to +368.25%**; DR **+596.41% to +1301.53%** | An observation mechanism that is action-dependent after all |
| The reject margin is not point-identified from logs alone | **Measured** (H5 supported) | Widest bounds **0.009942**; incumbent width **0.001581** with **35%** coverage of the true full value | A controlled approval design or a defensible assumption |
| The bounds are not confidence intervals | **Measured** (caveat) | Incumbent bounds cover the true full value in **35%** of replications; bounds are conditional on the P0 estimate | A different P0 estimator or a wider interval construction |
| Review capacity 1–10% does not break the correction | **Measured** | Max \|relative bias\| **1.71%**; coverage **94–98%** | A much smaller capacity or a policy with no overlap |
| A 90-day delay reduces precision but not correctness | **Measured** | Mean ESS **3,308**; max \|relative bias\| **1.28%**; coverage **84–96%** | A longer delay or informative censoring |
| The pilot generalizes to a Philippine production system | **Not claimed** | Public synthetic data; simulation | A bank partner and real logs |
| A random approval/rejection arm is acceptable | **Not claimed** | `AUDIT_DESIGN.md` | Legal/risk review |
| The audit is a universal bias fix | **Limitation / non-finding** | In the main scenario with a 5% approved-label base rate, the audit's marginal RMSE gain is modest; it is decisive under outcome-dependent labels | A lower base label rate or a different audit design |

## Interpretation

1. **The premise is real.** Naive evaluation is not a small approximation: it
   overstates cost by 112–278% in the main scenario.
2. **The direction is not "flattering the incumbent."** The labeled subset is
   dominated by reviewed/rejected applications with non-zero costs, so the naive
   estimate overstates cost. The practical harm is that it would **reject the
   better model**: the naive ranking puts the incumbent ahead of the better
   model, while the true ranking reverses it.
3. **The correction works on the identified population.** DR is within 0.94%
   with 96% coverage; IPW is within 1.18% with 95% coverage. The residual rank
   instability is concentrated in the close better-model/incumbent gap.
4. **The audit is not a universal bias fix.** At a 5% approved-label base rate,
   a 1% audit mainly validates the approved margin and improves ESS; it does not
   change the log-based estimate much. It becomes decisive when approved fraud is
   more likely to be labeled than approved legitimate accounts.
5. **The reject margin needs bounds.** The widest interval is 0.009942, and the
   narrower incumbent interval covers the true full value only 35% of the time.
   Do not report the bounds as a confidence interval or a point estimate.
