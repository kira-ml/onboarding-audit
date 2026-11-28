# BAF Data Use Plan

**Status:** Draft for owner approval, 2026-11-28. **Use is on hold.**
**Scope:** BAF Base and Variants I–V, plus every model, metric, figure, memo, and
paper claim derived from them.
**Not legal advice.** A commercial use, redistribution, or ambiguous case needs
counsel and the dataset owner's permission.

**Latest result:** the restricted-feature audit failed (13/13 wrong A/B releases in the 100-replication confirmation);
the BAF-suite audit remains on hold. See
[`RESTRICTED_FEATURE_AUDIT.md`](RESTRICTED_FEATURE_AUDIT.md).

---

## 1. Decision

**HOLD — no BAF-suite run, no new BAF-based claim, and no public release of new
BAF-derived artifacts until the gates below are closed and the protected-attribute
conflict is resolved.**
**NO-GO for commercial use, raw redistribution, real decisions, or an
“externally validated” claim.**

The purpose is to test the decision-reliability method on a public synthetic
benchmark. It is not to evaluate a real bank, produce a production score, or make
credit or fraud decisions about people.

## 2. Why this plan exists

The BAF dataset is public, but “public” is not “unrestricted.” The dataset is
**CC BY-NC-SA 4.0**; the repository code is Apache-2.0. The code license does not
relicense the data. The plan keeps the project inside the dataset license and
keeps synthetic evidence from being presented as real-bank evidence.

## 3. License map

| Item | Term | What it means here |
|---|---|---|
| BAF dataset | **CC BY-NC-SA 4.0** | Non-commercial use; attribution; share-alike; no extra restrictions |
| BAF code repository | **Apache-2.0** | Code only; commercial use has a separate contact note |
| Kaggle terms | Platform terms | Follow the download and use terms; no re-identification |
| Project code | MIT | Does not relicense the dataset or its adaptations |

**Attribution:** cite the BAF paper and Kaggle dataset, link the license, and
state that the project processed the data.

**Share-alike:** if we distribute an adapted row-level dataset, it must carry the
same license. The safest rule is: **do not distribute row-level BAF data or
derived row-level adaptations at all.**

## 4. Permitted and prohibited uses

| Use | Status | Rule |
|---|---|---|
| Download from official Kaggle release | **Allowed** | Keep raw files local; verify version and hash |
| Local cleaning, feature building, model training | **Allowed** | Non-commercial research only |
| Publish code, configs, aggregate metrics, figures | **Allowed** | Cite source and license; no raw rows |
| Publish a personal, non-commercial research write-up | **Allowed** | Label synthetic; no external-validation claim; not a paid service |
| Use the work in an employment-directed portfolio or to promote paid consulting | **Hold** | CC BY-NC-SA 4.0 non-commercial scope is ambiguous here; get counsel or permission first |
| Share raw data with external reviewers | **Not allowed** | Reviewers download from Kaggle; do not send raw files |
| Publish model weights trained on BAF | **Hold** | Treat as a possible adaptation; review license/counsel first |
| Publish row-level BAF or derived rows | **Prohibited** | Share-alike and privacy risk; do not redistribute |
| Commercial pilot, paid consulting, product | **Prohibited without permission** | Obtain a commercial license or use licensed data |
| Real underwriting or customer decisions | **Prohibited** | This is an evaluation method, not a production system |
| Re-identification or linkage to other data | **Prohibited** | No attempt, no external linkage |
| Claim “real bank data” or “external validation” | **Prohibited** | BAF is synthetic; external validation needs a partner log |
| Use protected attributes as decision features | **Prohibited** | Only aggregate fairness diagnostics, if at all |

## 5. Data handling and security

- Download only from the official Kaggle release or the Feedzai repository link.
- Record the Kaggle **version** and raw file **SHA-256** before use. The current
  provenance file records the hash but not the version; fix that first.
- Store raw files in `data/`, which is git-ignored. Do not force-add them.
  `tests/test_data_hygiene.py` fails if a raw or parquet data file is tracked.
- Do not put raw rows in notebooks, reports, issues, pull requests, chat, slides,
  or third-party services.
- Clear notebook outputs before committing.
- Do not send raw rows to an external LLM, API, or cloud service.
- Do not commit absolute local paths from provenance sidecars or debug output.
- Keep one controlled copy; if backed up, use the same access controls.
- Delete raw files when the project no longer needs them; aggregate results can
  remain.
- Use a locked environment and checksums so the benchmark is reproducible without
  redistributing the data.

## 6. Ethical standards

- BAF is synthetic, but it represents vulnerable applicants and sensitive
  financial behavior. Treat it as sensitive benchmark data, not as a toy.
- Do not attempt re-identification or linkage.
- Do not use protected attributes to target, rank, or exclude people.
- Do not claim the synthetic fraud rate is a real bank’s fraud rate.
- Do not claim fairness certification from a synthetic benchmark.
- Report group diagnostics only with sample-size suppression and clear caveats.
- Do not deploy the model or use it for real decisions.
- Do not use the dataset to make claims about a named bank, country, or
  population.

### 6.1 Known conflict: protected attributes

The BAF datasheet names **age group, employment status, and income** as protected
attributes. The current `scripts/prepare_baf.py` excludes neither
`customer_age`, `employment_status`, nor `income` from `FEATURE_EXCLUDE`, so all
three train the scores that the audit compares. The paper now discloses all three,
but disclosure is not remediation. This is a **critical blocker** for the
BAF-suite audit and for any new BAF-based claim.

Options:

1. **Remove `customer_age`, `employment_status`, and `income` from all decision
   features and rerun** the pilot, sweep, sensitivity, reliability audit, and
   paper. This is the recommended path for a clean ethics claim.
2. Keep them as research-only covariates, record an explicit exception, add
   group fairness diagnostics, and state that the model is not deployable. This
   is weaker and requires external review.

Do not run the BAF-suite audit until this is resolved and recorded in
`DECISIONS.md`. `credit_risk_score` is not a protected attribute by label, but it
may proxy income or employment; monitor it as a potential proxy.

### 6.2 Resolution path

1. Add `customer_age`, `employment_status`, and `income` to the default
   exclusion list in `scripts/prepare_baf.py`. **Done;**
   `--include-protected` is legacy-only.
2. Rebuild the processed frame and verify the new hash. **Done for the
   restricted frame; the canonical default is not yet switched.**
3. Rerun the main pilot, the sweep, the sensitivity study, and the reliability
   audit with the restricted feature set. **Partially done:** main 100-rep and
   the audit are committed; the sweep/sensitivity are not.
4. If the headline conclusions and reliability grades are materially unchanged,
   keep the restricted set and update the paper. If they change materially, report
   the protected-attribute dependence as a finding and narrow the claims.
5. Record the decision in `DECISIONS.md` before the BAF-suite audit.

## 7. Publication and claim rules

Allowed language:

- “synthetic BAF benchmark”
- “multi-distribution robustness across BAF variants”
- “simulation evidence”
- “decision-reliability method”

Not allowed:

- “externally validated”
- “real bank log”
- “production-ready”
- “causal effect of a live policy”
- “complies with” a regulation or audit standard
- “zero false certifications” without the release count and interval
- “the profile works” without the withheld-decision rate

Every publication must include:

1. the BAF citation and Kaggle link;
2. the CC BY-NC-SA 4.0 notice;
3. a data-availability statement pointing to Kaggle, not raw files;
4. the synthetic/limitations statement;
5. the no-commercial-use statement for the dataset.

Figures and tables must be aggregate. If a figure reproduces row-level BAF data,
treat it as a potential adaptation and review it before publication.

The current paper draft still needs a BAF data/license statement before
submission. Add it when the age-feature decision is resolved.

## 8. Roles and approvals

| Role | Responsibility |
|---|---|
| Owner | Approves the use, the release, and any exception |
| Technical maintainer | Version pin, hash, data handling, reproducibility |
| External reviewer | Challenges claims and synthetic-to-real overreach |
| Legal counsel | Required for commercial use, redistribution, model weights, or ambiguity |
| Dataset owner | Contact for permission or license clarification |

No one may approve their own commercial exception.

## 9. Gates

| Gate | Requirement | Stop rule |
|---|---|---|
| G0 — Purpose | Written non-commercial purpose | If commercial intent appears, stop |
| G1 — Source | Official release, version, hash, license recorded | If not pinnable, do not use |
| G2 — Handling | `data/` ignored, no raw outputs, access controlled | If raw data is exposed, stop and clean |
| G3 — Pre-registration | Audit config and metrics committed before results | If changed after seeing results, disclose or rerun |
| G4 — Claims | Claim ledger, synthetic language, and intervals for sparse counts checked | If a claim exceeds the evidence, remove it |
| G5 — Review | External reader or documented fallback | If not reviewed, do not call it validated |
| G6 — Release | License notice, citation, limitations present | If missing, do not publish |

## 10. Incident response

If raw BAF data is committed or shared:

1. Stop the run and remove the data from the working tree and history.
2. Check whether the exposure is public; if so, treat it as a license incident.
3. Notify the owner and, if needed, Feedzai/Kaggle.
4. Record what happened in `WORKLOG.md` without reproducing the data.
5. Re-run the handling checklist before continuing.

If the license changes or the source version cannot be verified: stop and
re-review before any further use.

If a commercial use is proposed: stop, obtain counsel and permission, and do not
use the current artifacts as a commercial deliverable.

## 11. Kill criteria

Stop the BAF work if any of these is true:

- the intended use is commercial or supports a commercial pilot;
- the license terms are unclear or change;
- the Kaggle version and raw hash cannot be pinned;
- raw data must be redistributed to reproduce the result;
- the work needs real applicant outcomes or real decisions;
- a reviewer finds the synthetic-to-real framing misleading;
- legal or ethics review says no.

## 12. Pre-use checklist

- [ ] Purpose is written and non-commercial.
- [ ] Kaggle version and raw SHA-256 recorded.
- [ ] License and citation captured in `DATA_SOURCES.md`.
- [ ] `data/` is git-ignored; no raw data staged.
- [ ] Audit config and metrics pre-registered.
- [ ] Claims use “synthetic” and “robustness,” not “validation.”
- [ ] No commercial pilot, paid engagement, or real decision is planned.
- [ ] Owner approval recorded in `DECISIONS.md`.

## 13. Related documents

- [`DATA_SOURCES.md`](DATA_SOURCES.md) — license and privacy verification
- [`../NOTICE`](../NOTICE) — code vs data licensing carve-out
- [`PRIVACY.md`](PRIVACY.md) — repository and real-log handling
- [`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md) — hashes and version gap
- [`DECISIONS.md`](DECISIONS.md) — D19
- [`CLAIMS.md`](CLAIMS.md) — claim ledger
