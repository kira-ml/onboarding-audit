# Release Status

**Current tag:** `v1.1.0`, 2026-11-28.
**`main` is ahead of the tag:** it includes the retitled paper, the data-use
plan, and the restricted-feature negative result. The `v1.1.0` tag does not
include those changes.
**Previous tags:** `v1.0.2` (2026-11-27), `v1.0.1` (2026-11-26), and `v1.0.0` (2026-11-22).
**Public-release gate:** **NOT MET.**
**Publication decision:** published to GitHub as `v1.1.0` by owner decision on
2026-11-28. The gate is **waived, not met**; this is not an externally validated
release.

**Supersession:** `v1.0.2` corrected the false “no peer-reviewed” claim and the
uncited paper. `v1.1.0` adds the Decision Reliability Profile and the refocused
paper. Cite `v1.1.0` for the reliability method; cite `v1.0.2` only for the
correction history.

---

## 1. What is released

`v1.1.0` is a **Decision Reliability pre-release**: a reproducible research
artifact and a review-ready package. It is not an externally validated release, a
production system, or an audit opinion.

The release notes are in [`RELEASE_NOTES_v1.1.0.md`](RELEASE_NOTES_v1.1.0.md).
The previous releases are in
[`RELEASE_NOTES_v1.0.2.md`](RELEASE_NOTES_v1.0.2.md),
[`RELEASE_NOTES_v1.0.1.md`](RELEASE_NOTES_v1.0.1.md), and
[`RELEASE_NOTES_v1.0.0.md`](RELEASE_NOTES_v1.0.0.md).
The V1 plan and its definition of done are in [`V1/README.md`](V1/README.md).

## 2. Gate status

| Gate | Status | Evidence |
|---|---|---|
| Tests pass | **pass** (119 at `v1.1.0`; 101 at `v1.0.2`; 92 at `v1.0.0`) | `pytest -q` |
| Claim checks | **pass** (73/73) | `python scripts/check_claims.py` |
| Link check | **pass** (0 missing) | `python scripts/check_links.py` |
| Benchmark hash reproduced | **pass** | [`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md) |
| Kaggle version pin | **open** | raw SHA recorded; exact Kaggle version not yet pinned |
| Observation sweep | **pass** | [`V1/EXPERIMENTS.md`](V1/EXPERIMENTS.md) |
| F5 recorded | **pass** (narrow fail, widened pass) | [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) §6 |
| Identification gate | **pass** | `tests/test_gates.py` |
| Reliability audit (original features) | **pass** (post-hoc) | 2/60 A/B released, both P0-correct, 0/2 false certifications (95% UB 78%), 9/11 directional decisions withheld (82%); [`../reports/reliability_audit/summary.md`](../reports/reliability_audit/summary.md) |
| Restricted-feature audit | **FAIL** | 13/13 A/B releases wrong; 13/13 false certifications; BAF suite stopped (D20); [`RESTRICTED_FEATURE_AUDIT.md`](RESTRICTED_FEATURE_AUDIT.md) |
| Reviewer packet | **ready** | [`REVIEWER_PACKET.md`](REVIEWER_PACKET.md); no reader recorded yet |
| Two external readers | **open** | none recorded |
| Public release | **published as pre-release** | owner decision; external validation gate remains open |

## 3. Why the tag exists before external review

The project's own definition of done requires two external readers. The tag was
created to freeze the reproducible artifact so reviewers can inspect a stable
commit. It is not a claim that the external review happened.

A hostile reviewer is right to ask why a `1.0.x`/`1.1.0` tag exists before the
gate is met. The honest answer is: **the tags are review candidates, and the
public release has not happened.** Do not describe `v1.1.0` as externally
validated.

## 4. What v1.1.0 adds over v1.0.2

`v1.1.0` makes decision reliability the product spine:

- a Decision Reliability Profile (`reliability.py`): paired bootstrap decision
  stability, outcome/propensity calibration, 3×3 cost stress, full-policy
  fragility, and operational readiness, summarized as an A–D grade;
- `validate` reports reliability readiness; `report` returns the grade in memo
  §4.2 and `diagnostics.reliability`; `pilot --reliability-boot` records
  per-replication grades;
- A/B require a directional point decision; C/D are not released; a failed gate
  is D;
- a 60-replication reliability audit (`reports/reliability_audit/`): 2/60 A/B
  directional decisions released, both P0-correct, 0/2 false certifications (95% UB 78%), 9/11
  directional decisions withheld (82%);
- the paper is refocused on Decision Reliability for Financial ML and remains
  6 body pages plus references.

It retains the `v1.0.2` correction, the `v1.0.1` full-policy decision check, the
sharp reject-margin bound, the break-even, the action-weighted baseline, the
segment diagnostic, and the reviewer packet. These are pre-release changes; the
public-release gate is unchanged.

## 5. Next release rule

Do not announce a public `1.0` release until:

1. two external readers (or a documented fallback) have reviewed the package;
2. the objections are recorded in [`EXTERNAL_REVIEW.md`](EXTERNAL_REVIEW.md);
3. any objection that changes a headline claim is resolved in
   [`CLAIMS.md`](CLAIMS.md) before the release;
4. the validation report and the claim ledger agree with the tagged tree.

## 6. Related documents

- Validation record: [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md)
- Claim ledger: [`CLAIMS.md`](CLAIMS.md)
- Publication checklist: [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md)
- V1 definition of done: [`V1/README.md`](V1/README.md)
- External review log: [`EXTERNAL_REVIEW.md`](EXTERNAL_REVIEW.md)
- Reviewer packet: [`REVIEWER_PACKET.md`](REVIEWER_PACKET.md)
- Red-flag audit: [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md)
- Release notes: [`RELEASE_NOTES_v1.1.0.md`](RELEASE_NOTES_v1.1.0.md)
