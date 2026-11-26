# Data Readiness — Can This Log Support the Audit?

**Status:** Pre-pilot readiness note, 2026-11-27.
**Purpose:** State the minimum historical log the tool needs, what BSP 1213 does
and does not provide, and when to stop rather than produce a misleading memo.

---

## 1. The uncomfortable prerequisite

The tool does **not** run on a typical transaction-fraud log. It needs an
**account-opening decision log** with the incumbent's action, the score, the
label, and the observation process. BSP Circular 1213's 11 mandated fields are
transaction-log fields; they contain no onboarding decision, score, propensity,
or outcome. A bank can be fully compliant with the logging rule and still be
unable to run this evaluation.

That is the project's motivation, but it is also its adoption cost: the first
pilot is a **data reconstruction project**, not a one-command analysis.

## 2. Minimum fields

| Field | Why it is needed | If missing |
|---|---|---|
| `application_id` | Join the log to the candidate score and labels | Stop; no row-level evaluation |
| `decision_time` | Temporal split, delay, censoring | Reconstruct from the decision system; otherwise delay diagnostics are unavailable |
| `action` (`approve`/`review`/`reject`) | The incumbent policy and `P0` | Stop; the estimand is undefined |
| `score` | Reproduce the incumbent decision and fit the outcome model | Reconstruct from the model archive; otherwise the candidate comparison is weaker |
| `amount` | Cost model and exposure | Use a documented proxy; state it |
| `label` (0/1, observed only) | The outcome | Stop; no evaluation |
| `label_time` | Delay and resolution | Required for audit-only; otherwise the report falls back to a complete-case mean |
| `label_source` | Review vs audit vs post-approval report | Strongly recommended; without it the outcome-dependent risk cannot be diagnosed |
| `reviewed`, `audit_flag` | Observation channels | Required for IPW/DR/audit-only |
| `propensity` (optional) | Known observation probability | If absent, the tool estimates action-level or covariate propensities and labels the source |
| Pre-decision features | Outcome/propensity models | If absent, DR is unavailable; IPW/audit-only may still run |

## 3. BSP 1213 versus the evaluation log

| BSP 1213's 11 fields | Onboarding evaluation needs |
|---|---|
| sender/recipient, amount, time, channel, authentication, device/network | `application_id`, `decision_time`, `action`, `score`, `label`, `label_time`, `label_source`, `reviewed`, `audit_flag`, pre-decision features |

A team should keep the BSP log as the regulatory floor and build a separate
evaluation table keyed by a hashed application/transaction reference. Do not
retrofit the evaluation fields into the transaction log without legal/privacy
review.

## 4. Readiness paths

| Situation | What can be done | What cannot be claimed |
|---|---|---|
| Full action log with labels, delay, audit flags | Run the report, gate, and memo | Production or causal effects |
| Action log without audit flags | Estimate action-level/covariate propensities; report the source and weight diagnostics | A random-audit validation of the approved margin |
| Score archive but no action log | Reconstruct actions from the archived cutoffs and review queue; document the reconstruction | That the reconstructed actions are exact |
| Only approved/rejected outcomes, no review action | No `P0`/review-band evaluation; stop | A policy comparison |
| Only BSP 1213 transaction fields | No onboarding policy evaluation | Any version of this audit |
| Labels but no `label_time` | Naive/IPW/DR may run; audit-only falls back | Delay-aware audit-only or maturity claims |

## 5. Stop rules

Stop and report a data-readiness failure if:

- the action field cannot be reconstructed or trusted;
- the label is a review outcome that is defined only for reviewed rows, and the
  observation mechanism cannot be stated;
- the audit flag is absent and the approved-label mechanism is outcome-dependent;
- the candidate score is not frozen before the evaluation window;
- the extract cannot be pseudonymized to the agreed standard;
- the cost matrix cannot be agreed before the run.

The report's identification gate is a **readiness screen**, not a substitute for
these checks. Passing the gate does not prove the log is complete; it only means
the obvious failures were not found.

## 6. What to show a reviewer

1. The field inventory and the reconstruction steps.
2. The observation mechanism and the label-source mix.
3. The audit design and its resolution probability.
4. The cost matrix and who agreed it.
5. The gate result and the reasons.
6. What the log cannot identify (the reject margin, the candidate-approved
   population, unmeasured confounding).

## 7. Related documents

- Schema: [`SCHEMA.md`](SCHEMA.md)
- Pilot protocol: [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md)
- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
- Audit design: [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md)
- BSP mapping: [`BSP_MAPPING.md`](BSP_MAPPING.md)
