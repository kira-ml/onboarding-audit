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
observation-rate cells. But the ranking is cost-dependent: at `frej_050` the
naive rule is **100%** and DR **58%**. The pilot reduces `p_wrong` only if it
improves the ranking on the institution's cost matrix.

### Benchmark-consistent arithmetic (not a forecast)

The following uses the project's committed main-scenario numbers, scaled to
1,000,000 applications. It is a **lower bound** on the pilot cost: it counts the
audit labels, not analyst or governance time.

| Input | Benchmark value | Source |
|---|---|---|
| Annual applications | 1,000,000 | Illustrative scale |
| Cost difference per application | 0.000333 | `reports/pilot.json`, better model vs incumbent, main |
| Annual loss from the worse policy `L` | 333 | Derived |
| `p_wrong` under the naive rule | 1.0 (main) / 0.5 (illustrative) | `reports/pilot.json`; midpoint |
| `p_wrong` after the pilot (DR P(best) 64–72%) | 0.28–0.36 | `reports/pilot.json` |
| Audit cost `C` (1% of approved at `review_cost=0.02`) | 193 | 0.02 × 1% × 1,000,000 |
| Value of the pilot: `(p_wrong_naive − p_wrong_pilot) × L − C` | **20–47 / −120** | Derived |

At the benchmark's main-scenario gap, the pilot is worth running only if (a) the
naive rule is likely to pick the wrong policy and (b) the residual misranking
after the pilot is small. With `p_wrong_naive=0.5` and a 28–36% residual, the net
is **negative**. The "factor of ten" is not a benchmark result; it was a template
with a much larger `L` and a much smaller `C`. Do not quote it.

### 4.1 What the benchmark implies for `p_wrong`

The pilot's naive rule selected the true best policy in **0%** of replications in
11 of 12 observation-rate cells; at the easiest cell it was **52%**. That does
not mean a bank's `p_wrong` is 1.0: the benchmark's top two policies are
deliberately close. It does mean **0.5 is not a conservative default**. Use a
range and show the break-even:

`p_wrong * L > C` is equivalent to `L / C > 1 / p_wrong`.

| `p_wrong` | Break-even `L / C` | Reading |
|---:|---:|---|
| 0.25 | 4.0 | the pilot pays only if the annual loss from the wrong policy is more than 4× the pilot cost |
| 0.50 | 2.0 | the illustrative template |
| 0.75 | 1.33 | the pilot pays if the wrong-policy loss is at least 1.33× the pilot cost |
| 1.00 | 1.0 | the pilot pays if the wrong-policy loss exceeds the pilot cost |

The measured 0% naive selection rate is a warning about close policy comparisons,
not a claim that every bank is at 1.0. The ranking is cost-dependent: at
`frej_050` (false-reject cost 0.50), the naive rule selects the true best policy
**100%** of the time while DR selects it **58%**. The institution must estimate
`p_wrong` from its own champion–challenger history and cost matrix, or accept the
range.

### 4.2 The audit cost can consume most of the value

On the benchmark, the true `P0` gap between the better model and the incumbent is
**0.000333** cost units per application. Over 227,491 applications that is
**75.75** cost units. A 1% audit of 219,344 approved rows is 2,193 labels ×
0.02 = **43.87** cost units, about **58%** of the gap. The residual misranking
cost is **0.000093** per application (~21.16 units), leaving about **10.7** units
of net value, or **0.000047** per application.

This is benchmark arithmetic, not a bank forecast. The implication is real:
**do not treat a 1% audit as free, and do not default to 1%.** Size the audit to
the decision's effect size and compare its cost with the value of the policy
switch. If the audit costs more than the decision is worth, bounds and a smaller
validation sample may be the better buy.

### 4.3 What the pilot must answer

The pilot is not worth running if it cannot change the decision. Before the run,
write down:

1. the candidate-vs-incumbent decision and the cost matrix;
2. the smallest effect that would change the decision;
3. the audit size needed to distinguish that effect from zero;
4. the audit cost as a share of the expected value;
5. the stop rule if the gate fails or the interval is inconclusive.

## 5. What the pilot does not buy

- It does not prove the candidate is better in production.
- It does not identify the reject margin; the full-policy check bounds it and
  reports a break-even, but the decision still depends on an unobserved fraud
  rate among rejected applicants.
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
