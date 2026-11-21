# Business Case

**Status:** V1 business case, 2026-11-21.
**Nature:** Decision framework, not a forecast. No revenue, loss, or ROI figure
in this document is a measured result for any institution.

---

## 1. The decision

A bank has a candidate onboarding policy (a new model, a new cutoff, or a new
review capacity). It can:

- **A. Adopt on a vendor or backtest claim.** Cheap, fast, and exposed to the
  selection and delay bias this repository measures.
- **B. Run a controlled pilot first.** Slower and costlier, but the decision is
  based on an identified estimate.
- **C. Do nothing.** Keeps the incumbent's cost and forgoes the candidate's gain.

This repository supports **B**. The business case is the value of avoiding a
wrong A, net of the cost of B.

## 2. Why A is risky

The measured failure is not "the estimate is a bit off." It is that the naive
estimate can **reverse the ranking** of policies:

| Evidence | Value | Artifact |
|---|---|---|
| Naive P(select the true best policy) | **0%** in 11 of 12 observation-rate cells | `reports/obs_sweep/pilot.json` |
| Naive relative bias | **7.8% to 538.5%** (max across policies); above 5% in **12/12** cells for at least one policy; incumbent **1.5–218%** | `reports/obs_sweep/pilot.json` |
| DR P(select the true best policy) | **64%** at the lowest approve-label rate; **96–100%** at the highest | `reports/obs_sweep/pilot.json` |

A bank that adopts on the naive number can reject the better model and adopt the
worse one. That is a decision error, not a rounding error.

## 3. What the pilot costs

The pilot is a retrospective, read-only exercise. Its cost is:

| Cost driver | Driver |
|---|---|
| Analyst time | Extract preparation, run, memo |
| Validator time | Independent reproduction and review |
| Data engineering | Pseudonymized extract and field mapping |
| Governance | DPA, sponsor, and review meeting |
| Delay | The decision waits for the pilot |

There is no production change, no live traffic, and no customer contact, so
there is no operational risk from the pilot itself.

## 4. What the pilot is worth

Let:

- `V` = the annual value of moving from the incumbent to the better policy, if
  the candidate really is better;
- `p_wrong` = the probability that the naive evaluation picks the wrong policy
  when the two are close;
- `L` = the annual loss from adopting the worse policy;
- `C` = the cost of the pilot.

The pilot is worth running when:

```
p_wrong * L  >  C
```

The measured evidence says `p_wrong` is not small when the policies are close:
the naive rule picked the true best policy in **0%** of replications in 11 of 12
cells. The pilot reduces `p_wrong` by replacing the naive comparison with an
identified one.

### Illustrative arithmetic (not a claim)

The following is a template, not a result. Substitute the institution's own
numbers.

| Input | Illustrative value | Source |
|---|---|---|
| Annual applications in scope | 1,000,000 | Institution |
| Cost difference between the better and worse policy, per application | 0.001 cost units | Institution's cost matrix |
| Annual loss from adopting the worse policy `L` | 1,000 cost units | Derived |
| `p_wrong` under the naive rule | 0.5 (illustrative) | Conservative midpoint |
| Expected loss avoided | 500 cost units | `p_wrong * L` |
| Pilot cost `C` | 50 cost units | Institution estimate |

In this template the pilot is worth running by a factor of ten. The factor is
driven by `L` and `p_wrong`; both must be supplied by the institution. Do not
quote the illustrative row as evidence.

## 5. What the pilot does not buy

- It does not prove the candidate is better in production.
- It does not replace a controlled live test for a high-stakes change.
- It does not validate the cost matrix.
- It does not remove the need for monitoring after adoption.

The pilot buys a **defensible decision**, not a guarantee.

## 6. When not to run it

Do not run the pilot when:

- the extract cannot be pseudonymized to the agreed standard;
- the cost matrix cannot be agreed before the run;
- the candidate and incumbent are so far apart that any method ranks them the
  same way (the audit adds little);
- the institution cannot provide an independent validator;
- the decision is already committed and the pilot would be a formality.

## 7. The regulatory angle

BSP Circular 1213 requires calibration, stress testing, and independent review
of AI models used in financial services. A shadow evaluation with a recorded
gate, a frozen cost matrix, and an independent validator is closer to that
standard than a vendor backtest. The mapping is in
[`BSP_MAPPING.md`](BSP_MAPPING.md); this document is not legal advice.

## 8. Related documents

- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Pilot protocol: [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md)
- One-pager: [`ONE_PAGER.md`](ONE_PAGER.md)
- BSP mapping: [`BSP_MAPPING.md`](BSP_MAPPING.md)
