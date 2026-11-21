# Paper Outline — Who Gets Onboarded?

**Working title:** *Who Gets Onboarded? Audit-Ready Evaluation of Account-Opening Fraud Policies under Selective and Delayed Labels.*

**Status:** Outline; results from the v0.2.1 pilot, propensity sensitivity, and
covariate sensitivity.
**Author:** Ken Ira Lacson Talingting.
**Target:** Public technical report / arXiv first. ICAIF 2027 or a fintech research workshop if the results hold. Do not overpromise a venue.

---

## Abstract (draft skeleton)

A bank or e-wallet must decide whether to approve, review, or reject each new
account application. The incumbent onboarding policy determines which
applications are reviewed and therefore which fraud outcomes are ever observed;
approved accounts are labeled late, if at all, and rejected applicants have no
outcome. We formalize the resulting policy-evaluation problem, distinguish the
identifiable approve/review margin from the non-identified reject margin, and
compare naive evaluation with inverse-probability weighting, doubly robust
estimation, audit-only estimation, and partial-identification bounds on the
public Bank Account Fraud (BAF) account-opening benchmark. We quantify the bias,
the rank flips, the value of a random post-hoc verification audit, and the
failure of action-only weighting when approved fraud is more likely to be
labeled than approved legitimate accounts. A covariate-dependent observation
stress test shows that action-level weighting also fails when the observation
rate depends on application features, and that a fitted covariate propensity
model is needed. We release an open-source logging
schema, audit design, and evaluation tool mapped to BSP Circular 1170 (eKYC),
BSP Circular 1213 (FMS calibration and independent audit), and AFASA. The
result is a measurement layer, not another fraud detector.

---

## 1. Introduction

### 1.1 The decision

- Account opening is the entry point to the financial system and to mule
  accounts and scams.
- The policy chooses approve / review / reject.
- The cost of error is two-sided: fraud losses and inclusion harm from false
  rejections.
- Regulators require calibration, stress testing, and independent review
  (BSP 1213), but the mandated log schema has no decision/score/outcome field.

### 1.2 Why the evaluation is hard

- Selection: the incumbent policy chooses which applications are reviewed.
- Delay: post-approval fraud labels arrive late; some are censored.
- Capacity: review is scarce; the review policy is part of the decision.
- The reject margin is structurally unobserved; a point estimate requires an
  assumption or a controlled approval design.

### 1.3 Contributions

1. Formalize audit-ready account-opening policy evaluation with policy-induced
   selection, delayed/censored labels, capacity constraints, and a legal log
   schema.
2. Distinguish the identified population (`P0`, logging non-rejected) from the
   full-population bounds; show why the reject margin is not point-identified
   from logs alone.
3. Compare naive, IPW, DR, audit-only, and bounds on BAF with known ground
   truth, including an outcome-dependent label stress test.
4. Quantify the value of a random post-hoc verification audit and show when it
   does and does not help.
5. Release a decision-log schema, an audit design, a benchmark, and an
   open-source tool; map the protocol to BSP 1170/1213 and AFASA.

### 1.4 What this paper does not claim

- No production or Philippine bank data.
- No causal deployment effect.
- No point estimate for the full population when the reject margin is material.
- No new fraud detector.

---

## 2. Related work

| Theme | Key work | What it establishes | What remains open here |
|---|---|---|---|
| Selective labels | Lakkaraju et al. 2017; Kleinberg et al. 2018 | Labeled outcomes are chosen by decision-makers; naive comparisons are biased | Account-opening policy value with delayed labels and a practical audit design |
| Reject inference | Boyes et al. 1989; Crook & Banasik 2004; Ehrhardt et al. 2021; Kozodoi et al. 2025; Scarone & Baeza-Yates 2026 | Selection bias is real; correction gains are small/method-dependent; evaluation-side correction and exploration can help | Delayed labels, fraud actions, capacity, and an audit protocol |
| PU learning | Elkan & Noto 2008; Bekker & Davis 2020; Bourazas et al. 2026 | Unlabeled data can be used under SCAR; calibration is fragile | Fraud labels violate SCAR; account-opening policy value, not just classification |
| Delayed feedback | Chapelle 2014; Dal Pozzolo et al. 2015; Vernade et al. 2017; Dhama 2026 | Delays/censoring must be modeled; investigator feedback differs from delayed customer labels | Joint selection + delay + capacity for account opening |
| Off-policy evaluation | Dudík et al. 2011; Swaminathan & Joachims 2015; Thomas & Brunskill 2016; Namkoong et al. 2020 | IPW/DR/SNIPS; positivity and unconfoundedness are binding | Fraud's observation mechanism and the reject margin; a usable memo |
| Account-opening benchmark | Jesus et al. 2022 (BAF); Pombal et al. 2022 | BAF is account-opening data; selective labels and performative prediction matter | No policy-evaluation toolkit, delay-aware comparison, capacity layer, audit design, or benchmark |
| Capacity / L2D | Alves et al. 2023 (FiFAR) | Public synthetic analysts and review capacity | Account-opening policy value under selective/delayed labels |
| Recent finance work | OSCAR (ICAIF 2026); Beyond Holdout Error (ICAIF 2026); DOiT (ICAIF 2026); Top-K Review (2026); Alert-Feedback Trap (ICAIF 2026); Standardized Protocol (ICAIF 2026) | Selective/delayed labels, ranking vs selection, queue construction, feedback, protocols | The applied account-opening measurement layer, open tool, and regulatory logging/audit protocol |

**Gap statement:** no peer-reviewed fraud-specific paper jointly handles
policy-induced selection, delayed/censored labels, capacity-constrained review,
and an audit-ready logging protocol for account-opening decisions. The closest
work studies pieces; this paper assembles and tests the applied layer.

---

## 3. Problem formulation

### 3.1 Actions and costs

- `a in {approve, review, reject}`.
- `C(a, y)` with fraud loss, review cost, residual fraud loss, and false-reject
  cost.
- Review capacity `K`.

### 3.2 Observation model

- Review labels with `kappa_review`.
- Approved labels with `e_approve`; audit with `rho_audit`.
- Rejected: unobserved.
- Delay and censoring at cutoff.
- Propensities and positivity.

### 3.3 Estimands

- Primary: `V_P0(pi) = E[C(pi(X), Y) | X in P0]`.
- Secondary: full-population bounds `[L, U]`.
- Not claimed: point-identified full-population value; causal deployment effect.

### 3.4 Identification

- `P0` identified under positivity and no unmeasured confounding of
  observation.
- Reject margin not identified; bounds require the cost model.
- Outcome-dependent labels break action-only weighting; audit-only survives.

---

## 4. Estimators

- Naive.
- IPW-HT / IPW-Hajek.
- DR with cross-fitted outcome model.
- Audit-only.
- Bounds.
- Capacity-constrained policy value.
- Standard errors and coverage.
- What each estimator assumes and when it fails.

---

## 5. Benchmark

- BAF account-opening test window.
- Logging policies, candidate policies, review capacity.
- Observation/delay mixture.
- Audit design.
- Scenarios and metrics.
- Negative controls (full observation, full audit, permutation, capacity,
  no leakage).

---

## 6. Results

### 6.1 Naive bias and rank flips

Naive relative bias ranges from **+111.6% to +278.5%** across the four policies.
The true P0 ranking is `better_model < incumbent < lenient_cost < strict_cost`;
the naive ranking is `incumbent < better_model < lenient_cost < strict_cost`.
The naive estimate has a mean **1.00** pairwise inversion and selects the true
best policy **0%** of the time. Practical consequence: the naive evaluation
would reject the better model.

A 12-cell observation-rate sweep shows the magnitude is conditional: naive bias
ranges **7.8–538.5%**, but exceeds 5% in **12/12** cells. DR with known
propensities stays within **1.89%**, but its P(select true best) falls to **64%**
at the lowest approve-label rate.

### 6.2 Estimator comparison

DR: max |relative bias| **0.94%**, mean coverage **96.0%**, mean ESS **7,864**.
IPW: max **1.18%**, mean coverage **95.0%**. Audit-only at 1%: max **2.98%**,
coverage **84.5%**, ESS **1,271**. The corrected ranking is much better than
naive but not perfect: DR mean inversions **0.29**, P(select true best) **72%**,
cost of misranking **0.000093** (naive: **1.00 / 0% / 0.000333**).

### 6.3 Audit value

At a 5% approved-label base rate, the audit's marginal RMSE gain is modest:
DR **0.001159 → 0.001068** and ESS **6,610 → 9,126** from 0% to 2% audit.
Audit-only improves from max bias **3.33% / coverage 75% / ESS 634** at 0.5% to
**1.82% / 86.5% / 2,546** at 2%. The audit is a validation and
outcome-dependent-label tool, not a universal bias fix.

### 6.4 Capacity and delay

Capacity 1–10%: max |relative bias| **1.71%**, coverage **94–98%**. A 90-day
approve-label delay reduces mean ESS to **3,308** and coverage to **84–96%**,
with max |relative bias| **1.28%**. Precision falls; the correction still holds.

### 6.5 Outcome-dependent labels

When approved fraud is labeled at 30% and approved legitimate applications only
by the audit: audit-only bias **-2.37% to -1.98%** (coverage **80–86%**);
action-only IPW **+43.9% to +368.3%**; DR **+596.4% to +1301.5%**; naive
**+597.1% to +1147.4%**. This is the strongest practical argument for the audit.

### 6.6 Reject-margin bounds

Widest bounds interval **0.009942**; the incumbent's width is **0.001581** with
**35%** coverage of the true full-population value. The bounds are
partial-identification intervals conditional on the P0 estimate, not confidence
intervals. The reject margin is not point-identified from logs alone.

### 6.7 Negative controls

`pytest -q`: 49 tests pass, including full-observation identity, full-audit
identity, propensity recovery, bounds validity, capacity, no leakage, schema
validation, the arbitrary-log report's known-ground-truth check, and the
propensity/covariate helpers.

### 6.8 Propensity sensitivity

When `e` is estimated from the log: DR max |relative bias| **2.67%**, mean
coverage **91.0%**; IPW max **11.19%**, coverage **73.0%**. At lognormal noise
sigma 0.25: DR **1.58% / 96.5%**, IPW **7.01% / 93.5%**. Under outcome-dependent
labels with estimated `e`: audit-only **2.58% / 82.5%**; IPW **1350.8%**; DR
**1627.9%**. The paper should recommend DR, not IPW, when `e` is estimated, and
audit-only when the label-source mix suggests outcome-dependent observation.

### 6.9 Covariate-dependent observation

When the post-approval report probability depends on standardized log amount,
action-level `e` is misspecified. The 50-replication study compares oracle,
action-level, and cross-fitted covariate propensities, with and without the
45-day delay. Action-level IPW is **67.52%** biased (coverage **1.5%**) and
action-level DR **21.25%** (coverage **72.5%**); with the delay, **51.72%** and
**17.59%**. The fitted covariate model recovers the oracle: IPW **1.97%** / DR
**2.48%** (coverage **91.5% / 89.5%**), and **3.35% / 3.68%** with the delay.
The oracle itself covers **89–90%**, so the shortfall from 95% is the heavy-tail
variance, not the model. The paper should claim covariate-model robustness, not
action-level DR robustness, under covariate-dependent observation.

---

## 7. A logging and audit protocol for practice

- BSP 1170 eKYC context.
- BSP 1213 11-field floor + decision/observation/label extension.
- Audit design: post-hoc verification and shadow scoring; no random
  approvals/rejections.
- Sample-size and cost guidance.
- The memo: measured / assumed / unverifiable.
- What a risk committee, internal auditor, and BSP reviewer can use.

---

## 8. Limitations and threats to validity

- Simulated observation and capacity; no PH production data.
- BAF is synthetic; one dataset.
- Cost matrix is a normalized assumption.
- Oracle propensities in the main pilot; the sensitivity tests estimated,
  noisy, and covariate propensities. The covariate model is a logistic
  approximation, and heavy weights can undercover the interval.
- Reject margin not identified.
- The audit design is a recommendation; legal/risk review required.
- No causal deployment claim.
- The project is an applied measurement layer, not a new estimator theory.

---

## 9. Conclusion

The value of the paper is not a new fraud model. It is a defensible answer to a
question every onboarding team faces: *can we trust the expected-impact number
when our own policy chose the labels?* The answer is: only if the estimand,
the observation model, the overlap, and the audit design are stated — and the
reject margin is reported as bounds, not a point estimate.

---

## Appendix A — Claim ledger

See `docs/CLAIMS.md`.

## Appendix B — Reproducibility

- Seed, config, versions, `reports/pilot.json`, `reports/pilot_rows.parquet`.
- `pytest -q`.
- Data card.

## Appendix C — Cost model

- Base values, semantic mapping, sensitivity.
- Why the false-reject cost is the key inclusion parameter.
