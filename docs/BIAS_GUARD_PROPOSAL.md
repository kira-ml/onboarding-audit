# Bias Guard Proposal (Not Yet Enabled)

**Status:** Post-hoc candidate, 2026-11-28. **Not a validated rule.**
**Purpose:** address the restricted-feature false-certification failure.
**Decision:** do not enable until pre-registered and tested on a fresh audit.

---

## 1. Failure to block

In the 100-replication restricted `frej_050` audit:

- 13 A releases, 0 correct.
- True candidate advantage: ~0.53% of cost.
- Estimated difference: 5.4–8.1% of incumbent cost.
- Bootstrap, cost stress, and full-policy checks all agreed with the wrong sign.

The profile had no dimension that could distinguish “small true effect” from
“large biased estimate.”

## 2. Candidate guard

Add a **materiality floor** before releasing A/B:

```text
relative_effect = abs(candidate_cost - incumbent_cost) / incumbent_cost
if relative_effect < min_effect_share:
    grade = C — collect more evidence
    reason = "estimated effect is below the materiality floor"
```

Proposed default for pre-registration: **`min_effect_share = 0.10`**.

## 3. Offline counterfactual

Using the committed 100-replication audit:

| Check | Result |
|---|---|
| 13 A releases, relative effect range | **5.4–8.1%** |
| Would a 10% floor block them? | **Yes, all 13** |
| Case study (clear case) relative effect | **11.6%** — would pass |
| Original main B relative effect | **~19%** — would pass |

This is a **post-hoc** calculation. It shows the guard is capable of blocking the
known failures; it does not prove the guard is safe or that 10% is the right
threshold.

## 4. Why 10%

The observed point-estimate bias in the restricted setting is about 1.3–1.6% of
cost, and the paired difference bias is larger. A 10% floor is a conservative
convention: below that, a small bias can flip the sign. It is a decision
threshold, not a statistical confidence bound.

## 5. What must be pre-registered

Before the next audit:

- the threshold and the denominator;
- the exact scenarios and replications;
- the treatment of near-ties and missing incumbent values;
- whether the floor applies to A only or A/B;
- the primary metric: false certifications, release count, and withheld rate;
- the stopping rule if the guard blocks all releases.

## 6. Test plan

1. Freeze the guard and config in a commit **before** running.
2. Run the 100-replication restricted `frej_050` audit with the guard.
3. Report all 13 previous failures; do not exclude them.
4. Run the main and low-label scenarios to check that the guard does not simply
   suppress every decision.
5. If the guard blocks all releases, report that as a cost, not a success.
6. Only then decide whether to make it the default.

## 7. Strongest counter-case

A 10% floor may be arbitrary and may block real 5–9% improvements that a bank
would care about. The correct response is not to lower the threshold after
seeing the result; it is to compare the floor against an independent audit or a
bias bound, and to report the trade-off.

## 8. Status

**Proposed.** Not implemented in `reliability.py`, not used by `report`, and not
claimed in the paper. The next run must pre-register it.
