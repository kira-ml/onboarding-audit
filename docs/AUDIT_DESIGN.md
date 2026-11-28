# Audit Design

**Status:** Current-tree document (2026-11-28; v1.1.0 tag plus post-release negative result).

**Purpose:** Define what a defensible audit can and cannot buy when the
onboarding policy chooses its own labels.

---

## 1. The identification problem

A candidate policy's value on the full population is:

```
V_full(pi) = E[ C(pi(X), Y) ]
```

The log observes `Y` only through selected doors:

- reviewed applications (fast, reliable);
- approved applications later detected as fraud (late, incomplete);
- approved applications in a random post-hoc verification audit;
- **rejected applications: never.**

Therefore:

- the **approve/review margin** is identifiable with logs plus an audit;
- the **reject margin** is not point-identified from logs alone;
- a policy that changes the rejection rate requires bounds or an assumption.

This is a feature of the problem, not a bug in the estimator. The tool must say
so.

## 2. What is a defensible audit

### 2.1 Recommended: random post-hoc verification of approved applications

- Draw a random sample of approved applications.
- Verify identity, documents, device/behavior, or account activity after
  approval.
- Record the outcome (fraud / legitimate) and the time.
- Do not change the approval decision.
- This yields an unbiased label sample for the approved population and does not
  deliberately onboard fraud.

### 2.2 Recommended: shadow scoring

- Compute a challenger score on all applications.
- Do not change the decision.
- Use the scores for overlap/coverage diagnostics, not for labels.
- Shadow scoring is the lowest-risk way to test whether a candidate policy
  would explore regions the incumbent never labels.

### 2.3 Not recommended: random approval of would-be-rejected applicants

- Deliberately onboards fraud and mule accounts.
- May conflict with eKYC/AFASA duties and the institution's risk appetite.
- Not a defensible audit design for a regulated institution.

### 2.4 Not recommended: random rejection of would-be-approved applicants

- Deliberately excludes legitimate customers.
- Creates inclusion harm and complaints.
- Not a defensible audit design.

## 3. What the audit buys

### 3.1 Approved-population labels

The audit sample gives an unbiased estimate of the **logging-approved**
population's fraud rate and cost. It also validates the IPW/DR estimates and can
be used to fit the outcome model. It does not estimate the **candidate's**
approved population if the candidate changes who is approved: the audit labels
were drawn under the incumbent's approval decision.

### 3.2 Variance reduction for policy value

The audit increases the observation probability for approved applications,
which reduces the variance of IPW/DR and improves overlap for candidate
policies that review/approve differently from the incumbent.

### 3.3 What it does not buy

- **The reject margin.** Rejected applicants never become customers, so their
  fraud outcome is unobserved. Bounds or a controlled approval design are
  required.
- **Small fraud-rate differences.** A 1% audit of 227,491 applications is
  ~2,275 labels. At a 1.26% fraud rate, the standard error of the fraud rate is
  ~0.23 percentage points (about 19% relative). Detecting a 10% relative
  difference between two policies at 80% power would require ~100k+ labels per
  group. The audit is useful for policy-value variance, not for resolving small
  fraud-rate differences.
- **Causal deployment effects.** The audit measures outcomes under the current
  decision; it does not tell you how fraudsters or customers would respond to a
  different policy.

## 4. Sample-size guidance

### 4.1 Estimating a proportion

For a target standard error `s` on a fraud rate `p`:

```
n = p(1-p) / s^2
```

At `p = 0.0126`:

| Target relative SE | Target absolute SE | Approx. labels | Share of 227,491 |
|---|---:|---:|---:|
| 20% | 0.00252 | 1,959 | 0.9% |
| 15% | 0.00189 | 3,482 | 1.5% |
| 10% | 0.00126 | 7,835 | 3.4% |
| 5% | 0.00063 | 31,340 | 13.8% |

### 4.2 Comparing two policies

For a two-proportion comparison with power `1-beta` and significance `alpha`:

```
n_per_group = (z_{1-alpha/2} + z_{1-beta})^2 * [p1(1-p1) + p2(1-p2)] / (p1-p2)^2
```

At `p1=0.0126`, `p2=0.0113` (a 10% relative difference), 80% power, 5%
two-sided significance: approximately **117,000 labels per group**. This is
far beyond a 1–2% audit. The practical implication: **size the audit to the
decision's effect size, not to a generic 1% rule.**

### 4.3 Policy-value precision

For a cost outcome with variance `sigma_c^2`, the standard error of the mean is
`sigma_c / sqrt(n)`. The audit designer should use the observed cost variance
(dominated by fraud losses) to compute the sample needed for a target policy-
value precision. The pilot reports the realized RMSE and ESS so the team can
calibrate.

## 5. Combining the audit with logs

- Use the audit rows as a random sample of approved applications.
- Use the review rows as a selected sample of the review band.
- Use IPW/DR with the known observation probabilities.
- Report the audit share, the review share, and the approved-label share.
- Report the overlap/ESS for every candidate policy.
- If a candidate policy's review/approve set overlaps poorly with the logging
  policy, report bounds or recommend shadow scoring.

## 6. The reject margin

For a policy that changes the rejection rate, report:

- the share of applications rejected by the logging policy;
- the share the candidate would reject;
- the full-population bounds (min/max cost of the unobserved rejected rows);
- the assumption or controlled design that would narrow the bounds.

Do not report a point estimate for the full-population value if the reject
margin is material and unobserved.

## 7. Decision flow

```
Is the candidate policy's reject rate approximately the logging reject rate?
  yes -> the approve/review margin is the decision; logs + audit can identify it.
  no  -> the reject margin is material; report bounds, not a point estimate.
        -> Consider a controlled approval design only with legal/risk approval.
```

## 8. Regulatory mapping

| Requirement | How the audit/schema supports it |
|---|---|
| BSP 1213: continuous calibration, stress testing, independent review/audit | The audit produces an independent label sample and a reproducible evaluation memo |
| BSP 1213: 5-year tamper-protected logs | The schema extends the mandated log; the evaluation table inherits retention |
| BSP 1170: eKYC and identity verification | Post-hoc verification is a natural eKYC audit; the schema records identity-verification fields |
| AFASA s.6: liability for inadequate controls | The memo documents what was measured, assumed, and unverifiable |
| NPC Advisory 2024-04: explainability, human intervention, contestability | The memo records the decision logic and the human-review path; the audit uses hashed/minimal data |

## 9. What the audit cannot fix

- A target policy with no overlap and no audit data.
- A rejected population with no outcome.
- Unmeasured confounding in the review decision (analysts using unlogged
  information).
- A cost model that does not reflect the institution's actual costs.
- A fraudster population that changes in response to the policy.
