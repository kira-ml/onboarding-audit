# Red-Flag and Weakness Audit Log

**Status:** Pre-review audit, 2026-11-27.
**Scope:** `onboarding-audit` v1.0.1 and the post-release working tree.
**Stance:** Skeptical fintech data scientist. The purpose is to protect
credibility, not to encourage.
**Related:** [`EXTERNAL_CREDIBILITY_REVIEW.md`](EXTERNAL_CREDIBILITY_REVIEW.md)
for the full narrative and sources.

**Severity:** **Critical** = can invalidate the project or immediately
discredit it; **High** = materially weakens technical credibility or business
relevance; **Medium** = noticeable methodological/analytical weakness;
**Low** = minor improvement.

**Type:** **Verified** = observed in the artifact or a primary source;
**Potential** = plausible but not demonstrated; **Unverified** = evidence is
insufficient or search-based.

**Status:** **Fixed** = corrected and verified; **Partial** = main risk
addressed, residual remains; **Disclosed** = explicitly stated, not resolved;
**Open** = not addressed.

---

## 1. Summary

| ID | Severity | Issue | Type | Status |
|---|---|---|---|---|
| C1 | Critical | False “no peer-reviewed work” claim and missing closest 2026 citations | Verified | **Fixed** |
| C2 | Critical | Headline bias is a property of the simulated observation mechanism | Verified | **Disclosed** |
| C3 | Critical | Product promise includes the reject margin; `P0` excludes it | Verified | **Partial** |
| C4 | Critical | No native onboarding action log; severe adoption prerequisite | Verified | **Partial** |
| C5 | Critical | Paper novelty/positioning vs OSCAR, Beyond Holdout Error, DOiT | Verified | **Partial** |
| C6 | Critical | Live `v1.0.1` tag/release still contains the false claim and uncited paper | Verified | **Fixed** |
| H1 | High | Case-study candidate is an oracle, not a trained model | Verified | **Disclosed** |
| H2 | High | Audit-only targets logging-approved, not candidate-approved | Verified | **Fixed** |
| H3 | High | Identification gate is a heuristic, not a test of identification | Verified | **Partial** |
| H4 | High | Reject-margin bounds are uninformative in key scenarios | Verified | **Disclosed** |
| H5 | High | Cost matrix and business case are assumptions; value is marginal | Derived | **Partial** |
| H6 | High | Vendor-gap claim is search-based; 18-vendor matrix not committed | Unverified | **Partial** |
| H7 | High | Fairness is descriptive, not an audit | Verified | **Partial** |
| H8 | High | No external validation; release gate waived by owner | Verified | **Open** |
| H9 | High | “Better model” not ablated; model-class confound | Potential | **Partial** |
| M1 | Medium | BSP 1213 date 25 vs 30 June 2026 | Unverified | **Fixed** (language) |
| M2 | Medium | Related-work metadata errors | Verified | **Fixed** |
| M3 | Medium | Search-based “25 sources / 18 vendors” not reproducible | Verified | **Partial** |
| M4 | Medium | Point estimates without intervals in prose | Verified | **Partial** |
| M5 | Medium | BSP 1213 is FMS, not MRM; regulatory relevance can overstate | Verified | **Fixed** |
| M6 | Medium | Audit design legal/operational feasibility unverified | Unverified | **Open** |
| M7 | Medium | Candidate model not tuned; no feature ablation | Potential | **Open** |
| M8 | Medium | Documentation/status drift | Verified | **Partial** |
| L1 | Low | “Audit-ready” can be read as an audit opinion | Potential | **Fixed** |
| L2 | Low | Paper is 7 pages total (6 body + references); venue rule unconfirmed | Verified | **Fixed** (disclosed) |
| L3 | Low | Release is a pre-release with a waived gate | Verified | **Fixed** |

---

## 2. Critical findings

### C1 — False “no peer-reviewed work” claim and missing closest 2026 citations

- **What:** `CLAIMS.md` and `PROBLEM.md` claimed no peer-reviewed
  fraud-specific policy evaluation with a counterfactual design; the manuscript
  did not cite the three closest ICAIF 2026 papers.
- **Why it matters:** the claim is false. OSCAR, Beyond Holdout Error, and DOiT
  are peer-reviewed ICAIF 2026 papers on selective labels, estimator-ranking
  reversal, and account-selection trade-offs. A reviewer will treat the claim as
  either ignorance or overclaim.
- **Why an experienced DS notices:** they know the 2026 financial selective-label
  literature; the repository’s own `RELATED_WORK.md` lists the papers the
  manuscript omits.
- **Evidence:** `docs/CLAIMS.md` (pre-fix), `docs/PROBLEM.md` §3.5,
  `paper/main.tex` §Related Work, `docs/RELATED_WORK.md`; ICAIF 2026 accepted
  papers, ACM DOI 10.1145/3858063.3858757 and 10.1145/3858063.3858808,
  arXiv:2611.27809.
- **Credibility impact:** critical. This is the first thing a reviewer checks.
- **Resolution:** corrected the claim to “no reviewed work jointly provides the
  full account-opening `P0` + reject-margin + audit + open-tool combination”;
  added OSCAR, Beyond Holdout Error, DOiT, JUBILEE, and the selection-aware
  certification paper to `RELATED_WORK.md` and `REFERENCES.md`; added the three
  closest citations and a 2026 related-work paragraph to the manuscript;
  repositioned the contribution as the applied account-opening layer, not a new
  ranking phenomenon.
- **Status:** **Fixed.**
- **Verification:** `paper/main.pdf` contains OSCAR/Beyond Holdout/DOiT/Kuroki/
  Bhola/Hong; no “No peer-reviewed” claim remains in `CLAIMS.md`/`PROBLEM.md`;
  `pytest` and link check pass.

### C2 — The headline bias is a property of the simulated observation mechanism

- **What:** the pilot simulates actions, propensities, delay, audit, and review
  capacity. The naive bias is a property of that mechanism; the main headline
  (112–278%) is not a bank estimate.
- **Why it matters:** a skeptical DS will say “you simulated a biased mechanism
  and measured the bias.” The project discloses this, but the headline still
  reads like a market fact.
- **Why an experienced DS notices:** BAF has no action log; the README says the
  actions are simulated; the observation model is authored.
- **Evidence:** `src/onboarding_audit/observation.py`,
  `src/onboarding_audit/pilot.py`, `README.md` headline, `paper/main.tex`
  abstract, `docs/THREATS.md` F1.
- **Credibility impact:** critical for any market-magnitude claim; lower for the
  method/gate claim.
- **Resolution:** added an explicit “all numbers are simulation results; none is
  a bank estimate” block above the headline table; the paper abstract states the
  results are conditional on a simulated mechanism; the action-weighted baseline
  shows the point-estimate gap survives one more realistic baseline.
- **Status:** **Disclosed.** Residual: no real log; the only closure is a
  real-log pilot or a holdout baseline.
- **Verification:** `README.md` headline caveat; `paper/main.tex` abstract;
  `reports/baseline_sensitivity/` for the action-weighted baseline.

### C3 — The product promise includes the reject margin; `P0` excludes it

- **What:** the headline question is “catch more fraud without rejecting more
  good customers”; the identified estimand is `P0`, which excludes the rejected
  population where that trade-off lives.
- **Why it matters:** a reader can act on a `P0` recommendation and miss the
  reject margin. The memo now prints a warning and a full-policy break-even, but
  the headline promise is still broader than the identified quantity.
- **Why an experienced DS notices:** the estimand is stated; the promise is not.
- **Evidence:** `README.md` line 14, `METHODS.md` §2, `report.py` §2.1/§4.1,
  `CASE_STUDY.md` (one reject).
- **Credibility impact:** critical product-claim risk; partially mitigated by the
  full-policy check.
- **Resolution:** memo labels the recommendation `P0`-conditional, adds §4.1,
  and warns when the recommendation does not survive the reject margin. The
  README still needs a narrower first-paragraph promise.
- **Status:** **Partial.**
- **Verification:** `pytest` full-policy tests; constructed material-reject log
  shows the warning. Residual: break-even is a sensitivity, not identification.

### C4 — No native onboarding action log; severe adoption prerequisite

- **What:** BAF has no actions, propensities, label timestamps, or audit flags;
  a real bank may not log them. BSP 1213’s 11 fields are transaction fields.
- **Why it matters:** the tool may not run on a bank’s existing data without a
  reconstruction project. “Who has this log?” is the first buyer question.
- **Why an experienced DS notices:** the schema is explicit; the pilot protocol
  says “stop” if fields are missing.
- **Evidence:** `docs/SCHEMA.md`, `docs/PILOT_PROTOCOL.md` §4,
  `docs/DATA.md`, `src/onboarding_audit/data.py`.
- **Credibility impact:** critical practical blocker, not a mathematical flaw.
- **Resolution:** added [`DATA_READINESS.md`](DATA_READINESS.md) with the minimum
  fields, BSP 1213 gap, reconstruction paths, and stop rules; linked from the
  README, docs index, and pilot protocol.
- **Status:** **Partial.** Residual: no partner log; this is guidance, not data.
- **Verification:** link check; the readiness table covers the missing-field
  cases.

### C6 — The live `v1.0.1` tag/release still contains the false claim and uncited paper

- **What:** the `v1.0.1` tag was created before the external-credibility audit.
  It still contains the false “no peer-reviewed work” claim and the paper
  without the three closest 2026 citations. The `main` branch is fixed, but a
  reviewer who checks the release tag sees the old artifact.
- **Why it matters:** the release page is the public artifact; a corrected `main`
  does not protect a reviewer who cites the tag.
- **Why an experienced DS notices:** they check the tag/release, not just
  `main`.
- **Evidence:** `git show v1.0.1:docs/CLAIMS.md` contains the old claim;
  `paper/main.pdf` at the tag lacks the 2026 citations.
- **Credibility impact:** critical; this is the artifact that would be cited.
- **Resolution:** issue a corrective `v1.0.2` pre-release with the fixed claims,
  citations, paper, and audit log; add a correction notice to the `v1.0.1`
  release body; do not move or delete the public tag.
- **Status:** **Fixed** by `v1.0.2`; the `v1.0.1` release body is corrected with
  a supersession notice.
- **Verification:** `git show v1.0.2:docs/CLAIMS.md`; GitHub release body.

### C5 — Paper novelty/positioning vs the closest 2026 work

- **What:** the manuscript positioned credit-scoring sampling bias as the
  closest work and presented the ranking gap as a finding; OSCAR, Beyond Holdout
  Error, and DOiT already establish selective-label/ranking/selection issues.
- **Why it matters:** at ICAIF, omitting the closest accepted papers is a
  desk-reject/major-revision risk; claiming the phenomenon as new is overclaim.
- **Why an experienced DS notices:** the 2026 papers are in the repository’s own
  related-work doc.
- **Evidence:** `paper/main.tex` §Related Work/Positioning;
  `docs/RELATED_WORK.md`; ICAIF 2026.
- **Credibility impact:** critical for the paper; the applied tool survives.
- **Resolution:** added a 2026 related-work subsection and citations; repositioned
  the contribution as the applied account-opening combination; updated the
  gap statement. The paper is 7 pages total: 6 pages of body plus a references
  page.
- **Status:** **Partial.** Residual: confirm the venue's reference policy; no
  peer review.
- **Verification:** PDF text contains the three citations; paper README notes
  the 6-body + references layout.

---

## 3. High findings

### H1 — Case-study candidate is an oracle

- **What:** `make_case_study.py` builds the candidate as `p_true + N(0,0.003)`,
  not a model trained on pre-decision features.
- **Why it matters:** the case is a best-case demonstration, not evidence that a
  real challenger model wins.
- **Why an experienced DS notices:** the script is readable; “true probability +
  noise” is an oracle.
- **Evidence:** `scripts/make_case_study.py`, `CASE_STUDY.md` §2/§7.
- **Credibility impact:** high if presented as a model comparison; lower as a
  known-truth pipeline test.
- **Resolution:** labeled as a synthetic oracle in the case study, README,
  one-pager, and paper.
- **Status:** **Disclosed.** Residual: no trained-model case.
- **Verification:** docs/paper text.

### H2 — Audit-only targets the logging-approved population, not the candidate’s

- **What:** audit labels are drawn from the incumbent’s approved rows; the
  estimator is unbiased for the logging-approved population, not the candidate’s
  approved population.
- **Why it matters:** a candidate that changes who is approved is outside the
  audit target.
- **Why an experienced DS notices:** the estimand is defined on
  `a_incumbent = approve`.
- **Evidence:** `observation.py`, `pilot.py`, `AUDIT_DESIGN.md`,
  `REPORT_USAGE.md`, `paper/main.tex`.
- **Credibility impact:** high; previously overbroad language.
- **Resolution:** qualified the target in the memo, model card, methods, audit
  design, report usage, one-pager, V1 docs, and paper.
- **Status:** **Fixed.**
- **Verification:** grep “logging-approved”; memo target note; paper abstract.

### H3 — The identification gate is a heuristic, not a test of identification

- **What:** thresholds (100 labels, ESS 100, max weight 100) are conventions; the
  gate cannot test unmeasured confounding; the analyst’s declaration cannot be
  verified.
- **Why it matters:** “Measured” can still be wrong if the declaration is false.
- **Why an experienced DS notices:** the gate is a checklist; identification is
  an assumption, not a threshold.
- **Evidence:** `gates.py`, `MODEL_CARD.md` §4, `AUDIT_REPORT.md` F3.
- **Credibility impact:** high if the gate is sold as proof; lower if labeled a
  screen.
- **Resolution:** added “readiness screen, not a proof of identification” to the
  paper, model card, and report usage; the memo still uses “Measured” with the
  assumption-unverified flag.
- **Status:** **Partial.** Residual: naming (`IdentificationReport`) and the
  “Measured” label can still overstate.
- **Verification:** docs/paper text; gate tests.

### H4 — Reject-margin bounds are uninformative in key scenarios

- **What:** F5 narrow fails (15/88); widened passes 77/88 but is ~4× wider; in
  `frej_002` the width is 0.203 vs policy values ~0.01.
- **Why it matters:** the bounds are honest but not decision-grade for the
  margin that matters.
- **Why an experienced DS notices:** width vs value; F5 is recorded.
- **Evidence:** `reports/pilot.json`, `RESULTS.md` §6, `VALIDATION_REPORT.md` §6.
- **Credibility impact:** high; the project discloses it.
- **Resolution:** reported as partial identification, not CI; added full-policy
  break-even as a decision aid.
- **Status:** **Disclosed.** Residual: needs a controlled design or an explicit
  assumption; no cheap fix.

### H5 — Cost matrix and business case are assumptions; value is marginal

- **What:** normalized costs; ranking flips at `frej_050`; benchmark-consistent
  net is 20–47 units per 1M at `p_wrong=1.0`, negative at 0.5; 1% audit ~193.
- **Why it matters:** the pilot may cost more than it saves; the value depends on
  the institution’s costs and audit price.
- **Why an experienced DS notices:** cost units are not pesos; the audit cost is
  a real share of the policy gap.
- **Evidence:** `BUSINESS_CASE.md` §4, `reports/pilot.json`.
- **Credibility impact:** high for commercial claims; disclosed.
- **Resolution:** replaced the factor-of-ten template with benchmark-consistent
  arithmetic; added the `p_wrong` range and audit-cost share.
- **Status:** **Partial.** Residual: no bank costs; no measured ROI.

### H6 — Vendor-gap claim is search-based; 18-vendor matrix not committed

- **What:** the claim that vendors do not document selection/delay-aware
  evaluation is based on an 18-vendor review that is not in the repository.
  Taktile/Effectiv/ThreatMetrix/Sphinx sell backtesting/champion-challenger.
- **Why it matters:** a reviewer cannot verify the claim; the category is
  commoditized; the differentiation is narrower.
- **Why an experienced DS notices:** they know the vendor landscape.
- **Evidence:** `PROBLEM.md` §3.4, `CLAIMS.md`, vendor pages.
- **Credibility impact:** high if stated absolutely; lower if search-based.
- **Resolution:** downgraded to “No vendor publicly documents, in the reviewed
  sources” and “search-based absence; matrix not committed”; added vendor
  examples.
- **Status:** **Partial.** Residual: publish the matrix or remove the claim.

### H7 — Fairness is descriptive, not an audit

- **What:** the segment table shows counts/rates, not outcomes for rejected
  applicants; it is not a fairness certification.
- **Why it matters:** the inclusion promise cannot be answered for the rejected
  margin.
- **Why an experienced DS notices:** rejected rows have no labels; selection
  bias remains.
- **Evidence:** `report.py` segment diagnostics, `REPORT_USAGE.md`,
  `MODEL_CARD.md`.
- **Credibility impact:** high for a PH fintech flagship; disclosed.
- **Resolution:** added the segment diagnostic with small-cell suppression and a
  “not a fairness certification” caveat.
- **Status:** **Partial.** Residual: full fairness audit with rejected outcomes
  is V1.1.

### H8 — No external validation; release gate waived by owner

- **What:** no external readers, partner log, or independent replication; the
  v1.0.1 release is a pre-release published by owner decision.
- **Why it matters:** the project is not externally validated; the release page
  says so.
- **Why an experienced DS notices:** the status page and pre-release label.
- **Evidence:** `RELEASE_STATUS.md`, `EXTERNAL_REVIEW.md`,
  `RELEASE_NOTES_v1.0.1.md`.
- **Credibility impact:** high; this is the binding constraint.
- **Resolution:** recorded the waiver explicitly; added the reviewer packet.
- **Status:** **Open.** Residual: two external readers.

### H9 — “Better model” is not ablated; model-class confound

- **What:** the main benchmark compares logistic vs LightGBM on the same
  features; no feature/model-class ablation.
- **Why it matters:** the ranking flip may be about model capacity, not
  observation selection.
- **Why an experienced DS notices:** the candidate is a different model class;
  the case study is an oracle.
- **Evidence:** `configs/pilot.yaml`, `scripts/prepare_baf.py`,
  `CASE_STUDY.md`.
- **Credibility impact:** high for the “better model” premise.
- **Resolution:** added a post-hoc model/score ablation (`scripts/model_ablation.py`).
  Candidate AUC 0.8829 vs incumbent 0.8733 (AP 0.1545 vs 0.1442); retrained
  HistGB 0.8773 vs logistic 0.8754; reduced logistic 0.8711. The candidate is a
  modestly better ranker; model class alone is not a large driver.
- **Status:** **Partial.** Residual: the ablation does not isolate observation
  selection from model capacity; a trained-model case is still open.

---

## 4. Medium findings

### M1 — BSP 1213 date 25 vs 30 June 2026

- **What:** the project stated 25 June 2026; secondary sources report both 25 and
  30 June.
- **Why it matters:** a wrong regulatory date is an avoidable embarrassment.
- **Why an experienced DS notices:** compliance dates are checkable.
- **Evidence:** `BSP_MAPPING.md`, `references.bib`; secondary sources conflict.
- **Credibility impact:** medium.
- **Resolution:** changed to “one-year transition ended June 2026” with a note
  that secondary sources differ; the bib note says the same.
- **Status:** **Fixed (language).** Residual: verify the primary circular.

### M2 — Related-work metadata errors

- **What:** OSCAR title omitted “Financial”; Beyond Holdout Error title
  paraphrased; DOiT title shortened.
- **Why it matters:** a reviewer who knows the papers will see sloppy metadata.
- **Why an experienced DS notices:** the exact titles are searchable.
- **Evidence:** `RELATED_WORK.md`, `REFERENCES.md`, `paper/references.bib`.
- **Credibility impact:** medium.
- **Resolution:** corrected titles/authors/DOIs; added bib entries.
- **Status:** **Fixed.**
- **Verification:** PDF text; REFERENCES entries.

### M3 — Search-based “25 sources / 18 vendors” not reproducible

- **What:** the search protocol and vendor matrix are not committed.
- **Why it matters:** “absence of evidence” is presented as a gap; a reviewer
  cannot reproduce it.
- **Why an experienced DS notices:** the claims are absolute.
- **Evidence:** `PROBLEM.md` §3.4/§3.5, `CLAIMS.md`.
- **Credibility impact:** medium.
- **Resolution:** labeled as search-based; downgraded the claims.
- **Status:** **Partial.** Residual: publish the matrix/protocol.

### M4 — Point estimates without intervals in prose

- **What:** 0%/100% P(best) claims are sample proportions; the abstract/prose
  sometimes omit Wilson intervals.
- **Why it matters:** “100%” from 50 reps is not certainty.
- **Why an experienced DS notices:** small-sample proportions.
- **Evidence:** `README.md` headline, `paper/main.tex` abstract,
  `reports/pilot.json`.
- **Credibility impact:** medium.
- **Resolution:** added a headline caveat that 50–100 rep estimates are sample
  proportions; the paper has Wilson intervals in the sweep.
- **Status:** **Partial.** Residual: add intervals to every 0%/100% claim.

### M5 — BSP 1213 is FMS, not MRM

- **What:** the regulatory hook could be read as MRM compliance; BSP 1213 is an
  FMS circular and the draft MRM is not binding.
- **Why it matters:** a compliance reviewer may see overclaim.
- **Why an experienced DS notices:** the circular’s title/scope.
- **Evidence:** `BSP_MAPPING.md` §6, `CLAIMS.md`.
- **Credibility impact:** medium.
- **Resolution:** added the FMS/MRM qualifier to the claim ledger; mapping
  already had it.
- **Status:** **Fixed.**
- **Verification:** grep FMS/MRM.

### M6 — Audit design legal/operational feasibility unverified

- **What:** post-hoc verification of approved applications is legally/operationally
  plausible but not reviewed.
- **Why it matters:** the audit is the identification device for the approved
  margin.
- **Why an experienced DS notices:** customer consent, DPA, ops cost.
- **Evidence:** `AUDIT_DESIGN.md`, `DECISIONS.md` D3.
- **Credibility impact:** medium-high.
- **Resolution:** stated as requiring legal/risk review; no legal opinion.
- **Status:** **Open.**

### M7 — Candidate model not tuned; no feature ablation

- **What:** fixed hyperparameters; no tuning; no feature ablation.
- **Why it matters:** the “better model” advantage may be model class.
- **Why an experienced DS notices:** fixed parameters in `prepare_baf.py`.
- **Evidence:** `scripts/prepare_baf.py`, `paper/main.tex` §Experimental Design.
- **Credibility impact:** medium.
- **Resolution:** corrected the “validated on 3–4” wording; no ablation.
- **Status:** **Open.**

### M8 — Documentation/status drift

- **What:** the release docs contradicted themselves (65 vs 92 tests, wrong
  sweep grid, CI pending, 32/32 vs 43/43, v0.2.1 statuses).
- **Why it matters:** a credibility-first project cannot have stale numbers.
- **Why an experienced DS notices:** they check the validation report.
- **Evidence:** `VALIDATION_REPORT.md`, `ONE_PAGER.md`, `ROADMAP.md`,
  `README.md` (pre-fix).
- **Credibility impact:** high before the fix; now lower.
- **Resolution:** corrected the validation report, test counts, statuses, claim
  counts, and links; added a release status page; 101 tests/43 checks/0 links.
- **Status:** **Partial.** Residual: a consistency check in CI would prevent
  recurrence.

---

## 5. Low findings

### L1 — “Audit-ready” can be read as an audit opinion

- **What:** the name implies assurance.
- **Why it matters:** a reader may think internal audit approved it.
- **Why an experienced DS notices:** “audit-ready” is not a standard.
- **Evidence:** README, model card.
- **Credibility impact:** low.
- **Resolution:** added a definition in the README: the memo exposes evidence and
  assumptions; it is not an audit opinion or compliance certification.
- **Status:** **Fixed.**

### L2 — Paper is 7 pages total; 6 pages of body plus a references page

- **What:** the PDF has 6 pages of body plus a references page.
- **Why it matters:** a strict 6-page venue may or may not exclude references.
- **Why an experienced DS notices:** page count and the venue’s rule.
- **Evidence:** `paper/main.pdf`, `paper/README.md`.
- **Credibility impact:** low-medium.
- **Resolution:** paper README now says “7 pages total: 6 pages of body plus a
  references page; confirm the venue rule.”
- **Status:** **Fixed (disclosed).** Residual: confirm the target venue’s
  reference policy; trim only if required.

### L3 — Release is a pre-release with a waived gate

- **What:** v1.0.1 is published as a pre-release; the external-review gate is
  waived, not met.
- **Why it matters:** the release page must not imply external validation.
- **Why an experienced DS notices:** the release notes/status.
- **Evidence:** `RELEASE_STATUS.md`, GitHub release.
- **Credibility impact:** low if labeled; high if hidden.
- **Resolution:** release notes/status say “published by owner decision; gate
  waived, not met.”
- **Status:** **Fixed.**

---

## 6. What is still open

| ID | Residual | What would close it |
|---|---|---|
| C2 | No real log | A partner historical log; holdout baseline |
| C3 | Full-policy break-even is a sensitivity | Controlled approval/review design |
| C4 | No native action log | A reconstructed real log or a partner pilot |
| C5 | Paper 6 body + references; no peer review | Confirm venue rule; submit after citations |
| C6 | v1.0.1 tag has old claim/paper | **Fixed:** v1.0.2 pushed; v1.0.1 body corrected |
| H4 | Bounds wide | Controlled design or explicit assumption |
| H5 | No bank costs/ROI | Institution cost matrix and volume |
| H6 | 18-vendor matrix absent | Publish the matrix or remove the claim |
| H7 | No rejected outcomes | Full fairness audit |
| H8 | No external readers | Two reader calls, recorded |
| H9 | Ablation run; candidate advantage modest; no isolation | Trained-model case or a stronger challenger |
| M3 | Search protocol absent | Publish the search/matrix |
| M4 | Some intervals missing | Add Wilson/MC intervals to every proportion |
| M6 | Legal/ops review | Legal/risk sign-off on the audit design |
| M7 | No tuning/ablation | Tune and ablate the candidate |

---

## 7. Verification record

| Check | Command | Result |
|---|---|---|
| Unit tests | `pytest -q` | **101 passed** |
| Claim checks | `python scripts/check_claims.py` | **43/43** |
| Link check | `python scripts/check_links.py` | **0 missing** |
| Paper build | `tectonic paper/main.tex` | PDF written; 6 body + references; citations present |
| Label holdout | `onboarding-audit pilot --config configs/holdout_baseline.yaml` | Naive >100%; action-weighted/DR ≤6%; ranking unstable |
| Model ablation | `python scripts/model_ablation.py` | Candidate AUC 0.8829 vs 0.8733; HistGB 0.8773 vs logistic 0.8754 |
| False claim removed | `grep "No peer-reviewed"` on current docs | Only the audit log/review quote it |
| 2026 citations | PDF text search | OSCAR/Beyond Holdout/DOiT/Kuroki/Bhola/Hong present |
| Release | GitHub | `main` + `v1.0.1` pre-release |

**Not verified:** primary BSP 1213 PDF (403 to fetcher); exact 25 vs 30 June date;
AFASA/NPC primary texts; vendor implementation details; real-log audit/legal
feasibility; peer review; independent replication.

---

## 8. Verdict

**The project is not fundamentally flawed. It is overclaimed and simulation-bound.**

- **Problem:** real and documented. **Verified.**
- **Core method:** sound; the `P0`/reject-margin split, DR/IPW, bounds, gate, and
  audit design are coherent.
- **Evidence:** simulation-only; the action-weighted baseline helps but does not
  create external validity.
- **Novelty:** applied combination/open artifact, not a new estimator or ranking
  finding. The closest 2026 work is now cited; the paper is repositioned.
- **Commercial:** plausible for model risk/validation; unproven as a standalone
  product. The vendor category is commoditized; the wedge is narrow.
- **Decision:** **pursue as a research/portfolio artifact and open benchmark;
  do not present it as a validated production system or a novel paper without
  the open issues above.**
