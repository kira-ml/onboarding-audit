# Model Card — Onboarding Policy Audit (V1)

**Status:** V1 model card, 2026-11-21.
**System version:** `0.2.1` (V1 review candidate).
**Document type:** Model card for the measurement layer, not for a fraud
classifier. The layer evaluates someone else's policy; it does not score
applicants.

---

## 1. What this system is

`onboarding-audit` is an offline policy-evaluation layer for account-opening
fraud decisions. Given a historical decision log (actions, sparse outcomes,
optional propensities) and a candidate policy's scores, it estimates what the
candidate policy would have cost on the logged population and writes an
audit-ready memo.

It is **not** a model that approves, rejects, or reviews applications. It has no
production endpoint, no real-time path, and no authority to change a decision.

## 2. Intended use

| Item | Description |
|---|---|
| Primary use | Post-hoc evaluation of a candidate onboarding policy before a controlled pilot |
| Users | Model risk, internal audit, data science, and a credit/fraud policy owner |
| Decision supported | Whether a candidate policy is worth a controlled pilot, and what the evidence does and does not support |
| Output | `report.md` (memo), `report.json` (machine-readable), gate status |
| Frequency | Per candidate policy and per log snapshot |
| Human role | A named analyst runs it; a named reviewer signs the memo |

### Out of scope

- Real-time or batch decisioning of applications.
- Individual adverse-action notices or customer-level explanations.
- Causal claims about what happens if the incumbent changes behavior
  (the log is observational and the incumbent's policy is held fixed).
- A production estimate for any specific bank.
- Legal, compliance, or model-risk certification.
- Any use with PII or a proprietary log without a data-sharing agreement.

## 3. Estimand

The primary estimand is the **mean realized cost per application on the logging
non-rejected population (`P0`)** — the applications the incumbent approved or
reviewed. Logging-rejected applications have no outcome and are outside the
primary estimate; they enter only the full-population partial-identification
bounds.

The cost model has four parameters: fraud loss rate, review cost, false-reject
cost, and residual fraud loss. They are **assumptions**, not measured values.
The report states the cost matrix it used.

## 4. Identification assumptions

The estimate is valid only when all of the following hold:

1. **Action-dependent observation.** The label mechanism is ignorable given the
   logged action and the observed covariates. If approval labels are
   outcome-dependent in a way the model does not capture, the corrected
   estimators break (measured: DR relative bias up to **1,627.90%**).
2. **Positivity.** Every `P0` row has a positive probability of observation.
   The report refuses on a zero-propensity row.
3. **Consistency.** The logged action and the candidate action are well defined
   for the same application.
4. **No interference.** One application's outcome does not depend on another's
   treatment.
5. **Correct cost model.** The cost matrix reflects the institution's economics.
6. **Covariate coverage.** If observation depends on covariates, the propensity
   model must include them. Action-level propensities are not enough (measured:
   action-level IPW relative bias up to **67.52%**, coverage **1.5%**).
7. **Action-invariant outcome.** The applicant's fraud status does not depend on
   the action; the label measures it rather than resulting from review. If
   "confirmed fraud" exists only for reviewed applications, the pooled outcome
   model is misspecified and DR relies on the propensity model.

The report's identification gate checks positivity, sample size, effective
sample size, max weight, cost support, and the declared observation mechanism. It
does **not** test assumptions 1, 4, or 5; those are the reviewer's responsibility
and are stated in the memo. Declaring `--observation-assumption outcome` makes
the report refuse; leaving it `unknown` marks the estimate as
assumption-unverified. The gate cannot verify the declaration is true.

## 5. Inputs

A decision log with the schema in [`SCHEMA.md`](SCHEMA.md):

- `application_id`, `application_time`, `decision_time`
- `action` (`approve`, `review`, `reject`)
- `score` (the incumbent score, optional)
- `amount` (credit-line exposure proxy)
- `reviewed`, `audit_flag`
- `label` (0/1, present only when observed)
- `label_time`, `label_source`
- optional `propensity` (the observation probability, if the institution knows it)
- optional outcome covariates

A candidate score file with `application_id` and `score`.

## 6. Outputs

| Output | Contents |
|---|---|
| `report.md` | Memo: gate status, estimates or refusal, candidate-vs-incumbent comparison, diagnostics, bounds, decision guidance |
| `report.json` | The same result, machine-readable, including the comparison and the diagnostic estimates when the gate fails |
| Gate | Pass/fail with reasons and warnings |

When the gate fails, the memo says **“Not identified”**, withholds the point
estimates, and lists the reasons. The JSON keeps the diagnostic numbers for
debugging; they are not a policy value.

## 7. Performance evidence

All numbers below trace to committed artifacts. They are **simulation results on
public synthetic data**, not a production estimate.

### 7.1 The problem the layer addresses

| Result | Value | Artifact |
|---|---|---|
| Naive relative bias, main scenario | **+111.55% to +278.49%** | `reports/pilot.json` |
| Naive relative bias across 12 observation-rate cells | **7.8% to 538.5%** (max across policies); above 5% in **12/12**; incumbent **1.5–218%**, 11/12 | `reports/obs_sweep/pilot.json` |
| Naive P(select the true best policy) | **0%** in 11/12 cells; **52%** at `e_approve=0.50`, `kappa_review=0.50` | `reports/obs_sweep/pilot.json` |

### 7.2 The correction

| Result | Value | Artifact |
|---|---|---|
| DR with known propensities, mean relative bias | **1.89%** across 12 cells; 95% MC upper bound **4.3%** (`e>=0.05`), **9.6%** (`e=0.01`) | `reports/obs_sweep/pilot.json` |
| DR coverage, known propensities | **84.5% to 96.0%** | `reports/obs_sweep/pilot.json` |
| DR P(select the true best policy) | **64%** at `e_approve=0.01`; **96–100%** at `e_approve=0.50` | `reports/obs_sweep/pilot.json` |
| DR with estimated action-level propensities | max **1.43%**, coverage **93.5%** | `reports/propensity_sensitivity.json` |
| DR with a wrong outcome model but correct `e` | **+0.14%** | `reports/double_robustness.json` |
| DR with a wrong `e` but correct outcome model | **+0.36%** | `reports/double_robustness.json` |
| Temporal stability, month 5 / month 6 | naive **230% / 255%**; DR **0.89% / 0.43%**; naive P(best) **0% / 0%** | `reports/temporal_stability.json` |
| Covariate propensity model under covariate-dependent observation | DR **2.48% / 89.5%**; IPW **1.97% / 91.5%** | `reports/propensity_sensitivity.json` |

### 7.3 Where it fails

| Failure | Value | Artifact |
|---|---|---|
| IPW with estimated action-level propensities | max **2.92%**, coverage **92.0%** | `reports/propensity_sensitivity.json` |
| Outcome-dependent approved labels | IPW **1,350.76%**, DR **1,627.90%**, coverage **0%** | `reports/propensity_sensitivity.json` |
| Action-level IPW under covariate-dependent observation | max **67.52%**, coverage **1.5%** | `reports/propensity_sensitivity.json` |
| Heavy weights | coverage **89–91.5%**, below nominal 95% | `reports/propensity_sensitivity.json` |
| Both nuisances wrong | DR **+2.09%**, IPW **−36.87%**; DR is no longer guaranteed | `reports/double_robustness.json` |
| Reject-margin bounds | incumbent covers the true full value in **34%** of replications (narrow interval); F5 **15/88** narrow, **77/88** widened | `reports/pilot.json` |

The last row is the reason the bounds are labeled **partial-identification
intervals**, not confidence intervals.

## 8. Limitations

1. **One public dataset.** BAF is synthetic, generated from a real anonymized
   account-opening dataset. There is no Philippine production evidence.
2. **No native action log.** BAF has no approve/review/reject actions,
   propensities, or label timestamps; the pilot simulates them.
3. **Cost matrix is assumed.** The four cost parameters are normalized
   assumptions, sensitivity-tested but not measured.
4. **Review capacity is a parameter.** Calibrated to 1–10%, not observed.
5. **The score pipeline is external.** `scripts/prepare_baf.py` rebuilds the
   benchmark frame from `Base.csv`; it must reproduce the recorded hash before
   the Level 1 claim holds.
6. **The gate is necessary, not sufficient.** It catches unidentified logs; it
   cannot detect an unmeasured confounder or a wrong cost model.
7. **Single maintainer.** Bus factor 1.

## 9. Ethical and privacy considerations

- No PII or proprietary data in the repository; see [`PRIVACY.md`](PRIVACY.md).
- The audit is **shadow scoring only**. It never approves, rejects, or contacts
  a customer, and it does not randomize real decisions.
- A rejected application is a real person's access to credit. The cost model
  must include a false-reject cost, and the memo reports it.
- The layer can make a policy look better or worse depending on the cost matrix.
  The matrix must be agreed before the evaluation, not tuned after it.

## 10. Monitoring after a pilot

- Re-run the gate on every new log snapshot.
- Track the observed label rate by action; a drop in approve labels degrades
  every estimator.
- Track the ESS and max weight; heavy weights undercover the interval.
- Re-fit the propensity model when the review policy changes.
- Re-check the cost matrix when pricing or review operations change.

## 11. Reproducibility

- Code: `src/onboarding_audit/`.
- Tests: `pytest -q`.
- Benchmark: `scripts/prepare_baf.py`, then `onboarding-audit pilot`.
- Sweep: `onboarding-audit pilot --config configs/obs_sweep.yaml`, then
  `scripts/analyze_sweep.py`.
- Every public number is listed in [`CLAIMS.md`](CLAIMS.md).

## 12. Related documents

- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Threats to validity: [`THREATS.md`](THREATS.md)
- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
- Audit design: [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md)
- Data card: [`DATA.md`](DATA.md)
