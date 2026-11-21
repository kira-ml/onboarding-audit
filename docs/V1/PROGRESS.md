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
| Observation sweep (E1) | **Done** | Claim updated | None |
| Bounds F5 (E2) | **Done — split** | Narrow 15/88 (fail); widened 77/88 (pass) | None |
| Report gate (E3) | **Done** | Demo log + CI next | None |
| Reproducibility (E4) | **Done** | `prepare_baf.py --verify` reproduced the exact SHA-256 | None |
| Adapter/demo (E5) | **Done** | Demo log + `demo` command; no-propensity path | None |
| Review package | **Done** | Model card, validation report, pilot protocol, business case | None |
| Double robustness | **Done** | Known-truth test: DR +0.14% / +0.36% with one wrong nuisance | None |
| Audit-only resolution | **Done** | Post-stratified by follow-up; complete-case fallback | None |
| Decision layer | **Done** | P(candidate cheaper), expected regret, recommendation | None |
| Case study | **Done** | 20k-row reproducible case; naive flips the ranking; report prefers the candidate | None |
| Temporal stability | **Done** | Month 5 vs 6: naive 230%/255%, DR 0.89%/0.43%, naive P(best) 0%/0% | None |
| CI/tests | **Done** | 92 tests pass; GitHub Actions green | None |
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

1. Record F5 in `pilot.json`/`pilot.md` and in the claim ledger.
2. Update `CLAIMS.md` with the gate, the reproduced benchmark hash, and F5.
3. Run the adversarial red-team audit (inversion and falsification) on V1.
4. Fix or disclose every red-team finding; do not soften a gate to pass.
5. Freeze the reviewer packet.

## 4. Blockers

| Blocker | Impact | Mitigation |
|---|---|---|
| No bank partner | Level 3 pilot impossible | Level 2 target; partner pilot is external |
| No external readers yet | Review package unvalidated | The user owns reviewer outreach |
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
| 2026-11-21 | Phase 1 | F5 failed: 15/88 cells at ≥90%; coverage claim removed. Benchmark rebuild verified byte-for-byte (SHA-256 match). Demo, CI, model card, validation report, pilot protocol, business case added; 92 tests pass |
| 2026-11-21 | Phase 1 | Red-team corrections: zero-propensity crash, `e_approve` resolution bug, HT variance, memo outside-`P0` key, and gate silent-pass paths fixed; propensity calibration added. IPW under estimated `e` is 2.92%, not 11.19% — the old claim was a bug. MC bounds, per-policy naive bias, and the `frej_002` bounds width added. F5: narrow 15/88, widened 77/88. 92 tests pass |
| | | |

## 9. Related documents

- V1 index: [`README.md`](README.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Experiments: [`EXPERIMENTS.md`](EXPERIMENTS.md)
- Evaluation: [`EVALUATION.md`](EVALUATION.md)
- Worklog: [`../WORKLOG.md`](../WORKLOG.md)
