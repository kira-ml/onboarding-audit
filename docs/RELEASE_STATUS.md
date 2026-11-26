# Release Status

**Current tag:** `v1.0.2`, 2026-11-27.
**Previous tags:** `v1.0.1` (2026-11-26) and `v1.0.0` (2026-11-22).
**Public-release gate:** **NOT MET.**
**Publication decision:** published to GitHub as `v1.0.2` by owner decision on
2026-11-27. The gate is **waived, not met**; this is not an externally validated
release.

**Supersession:** `v1.0.1` contained the false “no peer-reviewed” claim and the
uncited paper. `v1.0.2` corrects those artifacts; cite `v1.0.2`, not `v1.0.1`,
for the literature claim and the paper.

---

## 1. What is released

`v1.0.2` is a **corrective pre-release**: a reproducible research artifact and a
review-ready package. It is not an externally validated release, a production
system, or an audit opinion.

The release notes are in [`RELEASE_NOTES_v1.0.2.md`](RELEASE_NOTES_v1.0.2.md).
The previous releases are in
[`RELEASE_NOTES_v1.0.1.md`](RELEASE_NOTES_v1.0.1.md) and
[`RELEASE_NOTES_v1.0.0.md`](RELEASE_NOTES_v1.0.0.md).
The V1 plan and its definition of done are in [`V1/README.md`](V1/README.md).

## 2. Gate status

| Gate | Status | Evidence |
|---|---|---|
| Tests pass | **pass** (101 at `v1.0.2`; 92 at `v1.0.0`) | `pytest -q` |
| Claim checks | **pass** (43/43) | `python scripts/check_claims.py` |
| Link check | **pass** (0 missing) | `python scripts/check_links.py` |
| Benchmark hash reproduced | **pass** | [`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md) |
| Observation sweep | **pass** | [`V1/EXPERIMENTS.md`](V1/EXPERIMENTS.md) |
| F5 recorded | **pass** (narrow fail, widened pass) | [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) §6 |
| Identification gate | **pass** | `tests/test_gates.py` |
| Reviewer packet | **ready** | [`REVIEWER_PACKET.md`](REVIEWER_PACKET.md); no reader recorded yet |
| Two external readers | **open** | none recorded |
| Public release | **published as review update** | owner decision; external validation gate remains open |

## 3. Why the tag exists before external review

The project's own definition of done requires two external readers. The tag was
created to freeze the reproducible artifact so reviewers can inspect a stable
commit. It is not a claim that the external review happened.

A hostile reviewer is right to ask why a `1.0.x` tag exists before the gate is
met. The honest answer is: **the tags are review candidates, and the public
release has not happened.** Do not describe `v1.0.1` as externally validated.

## 4. What v1.0.2 adds over v1.0.1

`v1.0.2` corrects the 2026 research-gap claim, adds the closest-work citations,
rebuilds the paper, and adds the data-readiness and red-flag audit. It retains
the `v1.0.1` full-policy decision check:

- a sharp partial-identification bound on the candidate-vs-incumbent difference
  over the unobserved reject margin;
- a break-even rejected-fraud rate under a stated common-rate assumption;
- a memo warning when the `P0` recommendation does not survive the reject margin.

It also adds the action-weighted baseline (`reports/baseline_sensitivity/`), the
observational segment diagnostic, and the reviewer packet. These are review
update changes; the public-release gate is unchanged.

**Post-release evidence on `main` (not in the `v1.0.2` tag):** the
label-holdout baseline (`reports/holdout_baseline/`) and the model/score
ablation (`reports/model_ablation.*`). See `RESULTS.md` §5.2–5.3. Issue a
`v1.1.0`/`v1.0.3` if these need to be in a tagged release.

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
- Release notes: [`RELEASE_NOTES_v1.0.2.md`](RELEASE_NOTES_v1.0.2.md)
