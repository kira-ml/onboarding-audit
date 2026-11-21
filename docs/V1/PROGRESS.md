# V1 Progress Tracker

**Status date:** 2026-11-21.
**Current phase:** Phase 0 — credibility triage.
**Release target:** v1.0.0, 2026-12-31.

---

## 1. Workstreams

| Workstream | Status | Next action | Blocker |
|---|---|---|---|
| V1 documentation | **Done** | Keep current as decisions change | None |
| Scenario overrides | **Done** | — | None |
| Sweep config + analyzer | **Done** | — | None |
| Observation sweep (E1) | **Done** | Claim updated; start E2 F5 | None |
| Bounds F5 (E2) | **Not started** | Record F5; compute unconditional interval | None |
| Report gate (E3) | **Done** | Demo log + CI next | None |
| Reproducibility (E4) | **Not started** | Add `scripts/prepare_baf.py`; hash scores | Public BAF data |
| Adapter/demo (E5) | **Done** | Demo log + `demo` command; no-propensity path | None |
| Review package | **Not started** | Model card, validation report, pilot protocol, business case | None |
| CI/tests | **Local done** | 60 tests pass; workflow added; first GitHub run pending | None |
| External review | **Not started** | Reviewer packet; 10-person shortlist | Calendar |
| Release | **Not started** | v1.0.0 tag | Prior phases |

## 2. Milestones

| Milestone | Date | Status |
|---|---|---|
| M0 — V1 plan | 2026-11-21 | **Done** |
| M1 — Credibility triage | 2026-11-24 | Partial: sweep done; F5 and full triage pending |
| M2 — Core fixes | 2026-12-01 | Open |
| M3 — Package freeze | 2026-12-05 | Open |
| M4 — Review | 2026-12-15 | Open |
| M5 — v1.0.0 | 2026-12-31 | Open |

## 3. Next actions (top five)

1. Record F5 in `pilot.json`/`pilot.md`; compute the unconditional interval.
2. Create `docs/VALIDATION_REPORT.md`, `docs/MODEL_CARD.md`,
   `docs/PILOT_PROTOCOL.md`, `docs/BUSINESS_CASE.md`.
3. Write the V1 validation report's observation-sweep and gate sections.
4. Add the F5 and gate results to `docs/CLAIMS.md`.
5. Add `prepare_baf.py` and the score provenance, or narrow the Level 1 claim.

## 4. Blockers

| Blocker | Impact | Mitigation |
|---|---|---|
| No bank partner | Level 3 pilot impossible | Level 2 target; V1.1/V2 pilot |
| No external readers yet | Review package incomplete | Shortlist by Nov 30; send Dec 8 |
| Public BAF data not local | E4 pipeline blocked | Download from the public source |
| Six-week time cap | Scope pressure | Finish-first; cut to core package if needed |

## 5. Decision log

| ID | Decision | Status |
|---|---|---|
| D15 | Credibility release, not features | Accepted |
| D16 | Conditional bias claim | Accepted |
| D17 | Mandatory report gate | Accepted |
| D18 | Record F5; bounds are partial ID | Accepted |
| D19 | Reproducible pipeline or narrow claim | Accepted |
| D20 | Level 2, not Level 3 | Accepted |

## 6. Open questions

- Does the naive bias survive at `e_approve=0.20` and `0.50`?
- Does the ranking flip survive the sweep?
- Is F5 fixable with an unconditional interval, or is the bounds claim dead?
- Can the scores be reproduced without the original V2 pipeline?
- Which reviewers can we reach in December?
- Is the report gate too strict for a 2,500-row log?

## 7. Weekly review template

| Question | Answer |
|---|---|
| What did we finish this week? | |
| What did we learn? | |
| What changed in the claim? | |
| What is the next bottleneck? | |
| What did we cut? | |
| Are health/GPA/applications safe? | |

## 8. Status history

| Date | Phase | Note |
|---|---|---|
| 2026-11-21 | Phase 0 | V1 docs created; red-team findings accepted for triage |
| 2026-11-21 | Phase 0 | Scenario overrides, 12-cell sweep config, and analyzer added; 49 tests pass; full sweep running |
| 2026-11-21 | Phase 0 | E1 complete: naive bias 7.8–538.5%, >5% in 12/12; DR max 1.89%; DR P(best) 64% at low `e`; V1 claim updated |
| 2026-11-21 | Phase 1 | Identification gate implemented: positivity, sample, ESS, cost support; 20-row demo withholds estimates; 57 tests pass |
| | | |

## 9. Related documents

- V1 index: [`README.md`](README.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Experiments: [`EXPERIMENTS.md`](EXPERIMENTS.md)
- Evaluation: [`EVALUATION.md`](EVALUATION.md)
- Worklog: [`../WORKLOG.md`](../WORKLOG.md)
