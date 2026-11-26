# Release Status

**Current tag:** `v1.0.1`, 2026-11-26.
**Previous tag:** `v1.0.0`, 2026-11-22 (commit `c7b5fe1`).
**Public-release gate:** **NOT MET.**

---

## 1. What is released

`v1.0.1` is a **review update**: a reproducible research artifact and a
review-ready package. It is not an externally validated release, a production
system, or an audit opinion.

The release notes are in [`RELEASE_NOTES_v1.0.1.md`](RELEASE_NOTES_v1.0.1.md).
The previous release is in [`RELEASE_NOTES_v1.0.0.md`](RELEASE_NOTES_v1.0.0.md).
The V1 plan and its definition of done are in [`V1/README.md`](V1/README.md).

## 2. Gate status

| Gate | Status | Evidence |
|---|---|---|
| Tests pass | **pass** (101 at `v1.0.1`; 92 at `v1.0.0`) | `pytest -q` |
| Claim checks | **pass** (43/43) | `python scripts/check_claims.py` |
| Link check | **pass** (0 missing) | `python scripts/check_links.py` |
| Benchmark hash reproduced | **pass** | [`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md) |
| Observation sweep | **pass** | [`V1/EXPERIMENTS.md`](V1/EXPERIMENTS.md) |
| F5 recorded | **pass** (narrow fail, widened pass) | [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) §6 |
| Identification gate | **pass** | `tests/test_gates.py` |
| Reviewer packet | **ready** | [`REVIEWER_PACKET.md`](REVIEWER_PACKET.md); no reader recorded yet |
| Two external readers | **open** | none recorded |
| Public release | **not ready** | the gate above is open |

## 3. Why the tag exists before external review

The project's own definition of done requires two external readers. The tag was
created to freeze the reproducible artifact so reviewers can inspect a stable
commit. It is not a claim that the external review happened.

A hostile reviewer is right to ask why a `1.0.x` tag exists before the gate is
met. The honest answer is: **the tags are review candidates, and the public
release has not happened.** Do not describe `v1.0.1` as externally validated.

## 4. What v1.0.1 adds over v1.0.0

The `v1.0.1` review update adds the **full-policy decision check**:

- a sharp partial-identification bound on the candidate-vs-incumbent difference
  over the unobserved reject margin;
- a break-even rejected-fraud rate under a stated common-rate assumption;
- a memo warning when the `P0` recommendation does not survive the reject margin.

It also adds the action-weighted baseline (`reports/baseline_sensitivity/`), the
observational segment diagnostic, and the reviewer packet. These are review
update changes; the public-release gate is unchanged.

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
- Release notes: [`RELEASE_NOTES_v1.0.1.md`](RELEASE_NOTES_v1.0.1.md)
