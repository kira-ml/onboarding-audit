# Decision-Log Schema

**Version:** 0.1.0.
**Purpose:** Define the minimum fields a team must log to evaluate an
account-opening fraud policy. The schema extends BSP Circular 1213's mandated
11-field transaction log with the fields the regulation does not require but an
evaluation needs.

---

## 1. The gap in the mandated schema

BSP Circular 1213 (2025) requires at least five years of tamper-protected logs
with these 11 minimum fields:

1. sender name and account number;
2. date and time;
3. amount and currency;
4. receiving financial institution;
5. recipient name and account number;
6. unique transaction reference;
7. payment-instruction mode (PESONet, InstaPay, etc.);
8. authentication mode;
9. non-financial information (password changes, challenge questions);
10. transaction channel;
11. network, hardware, and software information (device fingerprint, IP,
    browser).

A team can satisfy this rule and still be unable to evaluate its onboarding
policy, because the schema contains **no decision, score, propensity, or
outcome field**.

## 2. Extension for account-opening evaluation

### 2.1 Application and eKYC context (BSP Circular 1170)

| Field | Type | Required | Used by | Description |
|---|---|---|---|---|
| `application_id` | string | yes | all | Stable, non-PII application key |
| `application_time` | timestamp | yes | all | When the application was submitted |
| `decision_time` | timestamp | yes | all | When the action was taken |
| `channel` | string | yes | diagnostics | Mobile, web, branch, partner |
| `document_type` | string | no | outcome model | e.g., PhilSys, passport, driver's license |
| `identity_verification_result` | string | no | outcome model | pass / fail / manual |
| `liveness_result` | string | no | outcome model | pass / fail / not_run |
| `face_match_result` | string | no | outcome model | pass / fail / not_run |
| `device_id_hash` | string | no | outcome model | Hashed device identifier |
| `phone_hash` | string | no | outcome model | Hashed phone identifier |
| `email_hash` | string | no | outcome model | Hashed email identifier |
| `philsys_flag` | 0/1 | no | outcome model | PhilSys/eKYC used |

### 2.2 Decision

| Field | Type | Required | Used by | Description |
|---|---|---|---|---|
| `action` | enum | yes | all | `approve`, `review`, `reject` |
| `score` | float | yes | all | Logging-policy fraud score |
| `model_version` | string | yes | audit | Model/version identifier |
| `threshold_version` | string | no | audit | Policy/threshold identifier |
| `review_capacity` | float | no | diagnostics | Fraction of applications the policy could review |
| `reviewed` | 0/1 | yes | IPW/DR | Whether the application was reviewed |
| `review_outcome` | enum | no | IPW/DR | `fraud`, `legit`, `unknown` |
| `review_time` | timestamp | no | delay | When the review concluded |

### 2.3 Observation and audit

| Field | Type | Required | Used by | Description |
|---|---|---|---|---|
| `propensity` | float | no | IPW | P(observed \| action, x), if known |
| `audit_flag` | 0/1 | no | audit-only | Random post-hoc verification sample |
| `audit_time` | timestamp | no | delay | When the audit concluded |
| `censoring_reason` | enum | no | diagnostics | `not_resolved`, `not_reviewed`, `not_approved`, `other` |

### 2.4 Label

| Field | Type | Required | Used by | Description |
|---|---|---|---|---|
| `label` | 0/1 | no | all | Observed account-opening fraud outcome |
| `label_time` | timestamp | no | delay | When the label arrived |
| `label_source` | enum | no | diagnostics | `review`, `post_approval_report`, `chargeback`, `mule_investigation`, `audit` |
| `label_confidence` | enum | no | sensitivity | `confirmed`, `probable`, `unconfirmed` |

### 2.5 Context

| Field | Type | Required | Used by | Description |
|---|---|---|---|---|
| `amount` | float | yes | cost | Credit-line/exposure proxy |
| `segment` | string | no | fairness | Customer/segment grouping |
| `product` | string | no | diagnostics | Account product |
| `region` | string | no | fairness | Coarse region |

## 3. Validation rules

- `action in {approve, review, reject}`.
- `score in [0, 1]`.
- `reviewed == 1` implies `action == "review"`.
- `reviewed == 1` implies `review_outcome in {fraud, legit, unknown}`.
- `audit_flag == 1` implies `action == "approve"`.
- `label` is null or 0/1.
- `label` observed implies `label_time` and `label_source` are present.
- `propensity` is null or in `(0, 1]`.
- `amount >= 0`.
- `decision_time >= application_time`.

## 4. Which fields each estimator needs

| Estimator | Minimum fields |
|---|---|
| Naive | `action`, `label` |
| IPW | + `propensity` (or a known audit design) |
| DR | + pre-decision features for the outcome model |
| Audit-only | + `audit_flag`, `label_time` |
| Bounds | + `amount`, `action`, logging action |
| Ranking | + candidate scores/actions |

## 5. Example row

```csv
application_id,application_time,decision_time,channel,action,score,model_version,reviewed,review_outcome,audit_flag,propensity,label,label_time,label_source,amount
app_0001,2026-06-01T09:12:00Z,2026-06-01T09:12:02Z,mobile,approve,0.0042,lr_v2,0,,1,0.051,0,2026-07-10T14:00:00Z,audit,200
app_0002,2026-06-01T10:02:00Z,2026-06-01T10:02:03Z,mobile,review,0.0810,lr_v2,1,legit,0,0.900,0,2026-06-03T11:00:00Z,review,500
app_0003,2026-06-02T18:44:00Z,2026-06-02T18:44:01Z,web,approve,0.0210,lr_v2,0,,0,0.050,1,2026-07-20T08:00:00Z,post_approval_report,800
```

## 6. Privacy and data protection

- The open-source project uses public or synthetic data only.
- In a production deployment, identifiers must be hashed/pseudonymized; the
  schema uses `*_hash` fields for device/phone/email.
- Collect the minimum data needed for the evaluation (Data Privacy Act
  minimization principle; NPC Advisory 2024-04).
- Do not log raw documents, names, account numbers, or unhashed contact data in
  the evaluation extract.
- Access to the evaluation extract should be role-controlled and audited.

## 7. Relationship to the regulation

This schema is an **extension**, not a replacement. A team should keep the BSP
1213 11-field log as the regulatory floor and add the decision/observation/
label fields in a separate evaluation table keyed by `application_id` or a
hashed transaction reference. The evaluation table can inherit the 5-year
retention and tamper-protection requirements of the primary log.
