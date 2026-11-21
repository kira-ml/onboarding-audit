# Threats to Validity

**Status:** Canonical validity register for v0.2.1 (2026-11-20).

**Purpose:** The strongest reasons this project could be wrong, and the tests or
statements that bound the damage. This is the inversion artifact; it should be
read before the results.

---

## 1. Construct validity

| Threat | Why it matters | Mitigation | Residual risk |
|---|---|---|---|
| **The observation mechanism is simulated** | The bias result could be an artifact of the chosen propensities/delays | Pre-register the mechanism; sweep audit/capacity/delay; negative controls; state that the mechanism is assumed | Measured: the 12-cell observation-rate sweep shows a maximum naive bias of **7.8-538.5%**, >5% in **12/12** cells (incumbent 11/12); DR's mean bias is at most **1.89%** (95% MC upper bound 4.3% for `e>=0.05`, 9.6% at `e=0.01`), coverage **84.5-96%**. The magnitude is conditional; estimated `e` and the low-`e` ranking (DR P(best) **64%**) remain the residual risk. |
| **The cost matrix is assumed** | The policy ranking and the value depend on costs | Normalized, transparent, sensitivity-tested; report the false-reject sweep | A bank's true costs may reverse a close ranking |
| **BAF is synthetic** | External validity is limited | State it; use it as a task-matched benchmark, not a production estimate | Real account-opening data may have different fraud modes |
| **BAF is not Philippine data** | The local hook is motivational | Use BSP/industry evidence for the problem, not for calibration; state the gap | A reviewer may ask for PH data; the answer is a partner, not a scrape |
| **The review-capacity parameter is assumed** | The capacity conclusion depends on it | Sweep 1–10%; use FiFAR in a follow-on; elicit from practitioners | No public PH capacity data |
| **The audit is not a universal bias fix** | A team may expect a 1% audit to solve selection | The pilot measures the audit's marginal value; it is modest at a 5% approved-label base rate and the only approximately unbiased option under outcome-dependent labels | A team with a lower base rate may see a larger gain; a team with a high base rate may see little |

## 2. Internal validity

| Threat | Why it matters | Mitigation | Residual risk |
|---|---|---|---|
| **Label leakage** | Post-investigation fields can encode the outcome | The pilot uses only pre-decision features; the schema flags label/post-decision fields; no-leakage test | A real log may contain post-decision fields; the validator warns |
| **Policy leakage** | The candidate policy must not use evaluation labels | Actions are a deterministic function of scores/amounts; permutation test | A team could accidentally tune on the evaluation window; the protocol says hold out |
| **Cross-fitting errors** | The outcome model could overfit the observed rows | 5-fold cross-fitting; DR residual; full-observation identity test | Small samples may still overfit |
| **Oracle propensities** | The pilot isolates estimator behavior by using known e | State it; a follow-on estimates propensities and tests sensitivity | The sensitivity estimates action-level e, adds lognormal noise, and adds a covariate-dependent observation mechanism; covariate-dependent observation is tested with a fitted propensity model, with a heavy-tail caveat |
| **Action-level estimated propensities** | A real log may have covariate-dependent observation; an action-level e can be misspecified | The report labels the source and supports `--propensity-model covariate`; the sensitivity compares action-level, fitted covariate, and oracle e | Measured: both DR and IPW survive estimated action-level e when observation is action-dependent (DR max **1.43%**, coverage **93.5%**; IPW **2.92%**, **92.0%**). Under covariate-dependent observation, action-level IPW fails (**67.52%**) and action-level DR also fails (**21.25%**); the covariate model recovers the oracle (**1.97-3.68%**). |
| **Covariate-dependent observation** | `P(observed \| action, X)` can depend on the application, so action-level e is misspecified even with a large sample | A cross-fitted per-action logistic propensity model; report the feature list, ESS, max weight, and weight range; compare with oracle and action-level e | Measured: action-level IPW **67.52% / 1.5%** coverage, action-level DR **21.25% / 72.5%**; covariate model **1.97% / 91.5%** (IPW) and **2.48% / 89.5%** (DR). The oracle itself covers **89-90%**, so heavy weights can undercover even with a correct model. |
| **Outcome-dependent labels with estimated e** | The action-level e is a weighted average of the fraud and legitimate observation rates | The report exposes the label-source mix; audit-only is the fallback; the audit design is the identification device | Measured: audit-only **2.58% / 82.5%**; IPW **2064.9%**; DR **1737.0%**. The tool must warn before reporting a point estimate. |
| **Finite-sample bias** | IPW/DR can be biased/noisy at small audit sizes | Report MC SE, ESS, max weight; 100 reps main; 50 sweeps | The pilot may still be noisy for the audit-only estimator |
| **Multiple scenarios** | Searching many scenarios can produce false positives | Pre-register the main scenario and H1–H6; report all scenarios; no post-hoc headline switching | The reader should treat the sweep as sensitivity, not confirmation |

## 3. External validity

| Threat | Why it matters | Mitigation | Residual risk |
|---|---|---|---|
| **One dataset** | A single benchmark may not generalize | FiFAR capacity layer; IEEE-CIS/PaySim as future transactions extension; state the limitation | The paper cannot claim broad generalization |
| **Account opening vs transaction fraud** | The decision and labels differ | The project is explicitly account-opening; do not evaluate a transaction policy on BAF | A reader may want transaction fraud; that is a different project |
| **Scam/APP fraud** | The largest PH loss category; onboarding is the entry point, not the whole intervention | Frame onboarding as the entry point; plan a scam-intervention extension if a partner provides data | The project does not evaluate warn/delay/step-up directly |
| **Regulatory change** | BSP 1213/1170 and the draft MRM may evolve | Cite the current instruments; state the draft status; design the schema as an extension | A new circular could change the logging/audit requirements |

## 4. Statistical conclusion validity

| Threat | Why it matters | Mitigation | Residual risk |
|---|---|---|---|
| **Rank flips are noisy** | A single rep can flip by chance | 100 reps; Spearman/inversions/P(best)/cost of misranking; MC SE | The pilot's DR mean inversions is 0.29, concentrated in the close better-model/incumbent gap; P(select true best) is 72%, not 100% |
| **Coverage is not nominal** | Influence-function SEs may understate uncertainty | Report coverage; treat the outcome model as fixed (stated); use MC SE | Coverage may be <95% in some scenarios; report it |
| **Bounds are not CIs** | A reader may interpret the interval as a confidence interval | Label it a partial-identification interval; coverage of the true full value is a diagnostic, not a guarantee | The pilot's incumbent interval covers the true full value in only 34% of replications; the bounds can miss if the `P0` estimate is biased |
| **H3 is strong** | Requiring <=5% max bias across all policies may fail | Report the failure honestly; narrow to bounds/diagnostic if needed | A weaker per-policy criterion would overclaim |

## 5. The strongest counter-case

> The simulation is an assumption stack. The naive bias is real in the
> simulation, but the corrected estimators only work because the propensities
> are oracle-known and the observation mechanism is simple. In a real bank, the
> propensities are unknown, the labels are outcome-dependent, and the reject
> margin is unobserved. The tool may produce a confident-looking memo that is
> not identified.

**Response:**
- The project does not claim a point estimate for the reject margin; it reports
  bounds.
- The pilot includes an outcome-dependent stress test where action-only IPW
  fails and audit-only survives.
- The tool reports overlap/ESS and a measured/assumed/unverifiable ledger.
- The sensitivity estimates action-level and covariate propensities and tests
  both; the report supports `--propensity-model covariate`.
- The audit design is a recommendation, not a claim that every bank can run it.
- If the correction does not survive estimated or covariate propensities, the
  paper must say so and narrow the claim.
- The covariate result is exactly that: action-level DR fails (21.25%); the
  paper claims only the fitted covariate model (1.97–3.68%), with the
  heavy-tail coverage caveat.
- Covariate-dependent observation can produce heavy-tailed weights; a point
  estimate within 5% is not evidence that the interval is calibrated. The memo
  reports ESS, max weight, and the weight range.

## 6. What would change the conclusion

1. The naive bias is negligible and no ranking flips under all realistic
   scenarios.
2. Estimated or covariate propensities remove the corrected estimator's
   advantage.
3. The reject-margin bounds are so wide that no decision is supported.
4. The audit design is legally or operationally infeasible.
5. The binding problem is scam intervention UX, not onboarding policy
   evaluation.
6. A vendor ships the same measurement layer with documented mechanics.
