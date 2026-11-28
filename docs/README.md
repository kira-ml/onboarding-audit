# Documentation Index

**Status:** Canonical documentation map for v1.0.2 (2026-11-27).
**Rule:** Every public number traces to a committed JSON or a cited primary
source. Every public claim appears in [`CLAIMS.md`](CLAIMS.md). If two documents
disagree, the precedence in §5 applies.

---

## 1. Start here

| If you are… | Read, in order |
|---|---|
| **A reviewer with 20 minutes** | [`../README.md`](../README.md) → [`PROBLEM.md`](PROBLEM.md) → [`RESULTS.md`](RESULTS.md) → [`CLAIMS.md`](CLAIMS.md) → [`THREATS.md`](THREATS.md) → [`MODEL_CARD.md`](MODEL_CARD.md) |
| **A fintech practitioner** | [`PROBLEM.md`](PROBLEM.md) → [`SCHEMA.md`](SCHEMA.md) → [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md) → [`REPORT_USAGE.md`](REPORT_USAGE.md) → [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md) → [`BSP_MAPPING.md`](BSP_MAPPING.md) |
| **A model-risk reviewer** | [`MODEL_CARD.md`](MODEL_CARD.md) → [`RELIABILITY.md`](RELIABILITY.md) → [`CLAIMS.md`](CLAIMS.md) → [`THREATS.md`](THREATS.md) → [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md) → [`REPORT_USAGE.md`](REPORT_USAGE.md) |
| **A researcher / paper writer** | [`PROBLEM.md`](PROBLEM.md) → [`METHODS.md`](METHODS.md) → [`PILOT_SPEC.md`](PILOT_SPEC.md) → [`RESULTS.md`](RESULTS.md) → [`CLAIMS.md`](CLAIMS.md) → [`THREATS.md`](THREATS.md) → [`RELATED_WORK.md`](RELATED_WORK.md) → [`REFERENCES.md`](REFERENCES.md) → [`../paper/README.md`](../paper/README.md) |
| **An engineer / contributor** | [`ARCHITECTURE.md`](ARCHITECTURE.md) → [`TESTING.md`](TESTING.md) → [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) → [`../CONTRIBUTING.md`](../CONTRIBUTING.md) |
| **Preparing an interview** | [`ONE_PAGER.md`](ONE_PAGER.md) → [`COMMUNICATION.md`](COMMUNICATION.md) → [`FAQ.md`](FAQ.md) → [`GLOSSARY.md`](GLOSSARY.md) |
| **Releasing the project** | [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md) → [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) → [`CLAIMS.md`](CLAIMS.md) |

## 2. Document map

### 2.1 Orientation

| Document | Purpose |
|---|---|
| [`../README.md`](../README.md) | The public entry point: problem, status, headline, quickstart, scope |
| [`PROBLEM.md`](PROBLEM.md) | The evidence-backed problem brief and the Philippine context |
| [`CASE_STUDY.md`](CASE_STUDY.md) | A reproducible case where the naive ranking flips |
| [`ONE_PAGER.md`](ONE_PAGER.md) | A one-page reviewer brief |
| [`FAQ.md`](FAQ.md) | Practitioner, researcher, and interviewer questions |
| [`LEARNING_GUIDE.md`](LEARNING_GUIDE.md) | Plain-English concept map, practice set, feedback loop, and self-test |
| [`GLOSSARY.md`](GLOSSARY.md) | Terms and acronyms |

### 2.2 Research

| Document | Purpose |
|---|---|
| [`METHODS.md`](METHODS.md) | Estimand, identification, estimators, simulation, metrics |
| [`RELIABILITY.md`](RELIABILITY.md) | Decision Reliability Profile: dimensions, grading, evidence, limits |
| [`TECHNICAL_NOTE.md`](TECHNICAL_NOTE.md) | The identification argument, influence functions, bounds proof, and evidence tiers |
| [`PILOT_SPEC.md`](PILOT_SPEC.md) | The pre-registered protocol, scenarios, negative controls, and addenda |
| [`RESULTS.md`](RESULTS.md) | The consolidated measured findings and verdicts |
| [`MODEL_CARD.md`](MODEL_CARD.md) | Intended use, estimand, assumptions, performance, limitations |
| [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) | The V1 validation record: commands, results, gates, open items |
| [`EXTERNAL_REVIEW.md`](EXTERNAL_REVIEW.md) | The external-review log and the gate that the tag does not replace |
| [`REVIEWER_PACKET.md`](REVIEWER_PACKET.md) | Cover note, shortlist template, agenda, and outreach tracker |
| [`AUDIT_REPORT.md`](AUDIT_REPORT.md) | The adversarial red-team audit: gates, findings, verdict |
| [`STRATEGIC_REVIEW_v1.md`](STRATEGIC_REVIEW_v1.md) | The V1 strategic review: constraint table, pre-mortem, falsification ledger, findings |
| [`EXTERNAL_CREDIBILITY_REVIEW.md`](EXTERNAL_CREDIBILITY_REVIEW.md) | The pre-review fintech data-scientist critique and external evidence |
| [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md) | The tracked red-flag/weakness log with severity and resolution status |
| [`DECISION_MEMO_PROJECT_FUTURE.md`](DECISION_MEMO_PROJECT_FUTURE.md) | The 12-week project-future decision: options, payoffs, ruin test, kill criteria |
| [`PILOT_PROTOCOL.md`](PILOT_PROTOCOL.md) | The partner-institution shadow-evaluation protocol |
| [`BUSINESS_CASE.md`](BUSINESS_CASE.md) | The decision framework and break-even condition |
| [`CLAIMS.md`](CLAIMS.md) | The claim ledger: what may be said, with evidence and status |
| [`THREATS.md`](THREATS.md) | The strongest counter-case and mitigations |
| [`RED_TEAM_CREDIBILITY_PLAN.md`](RED_TEAM_CREDIBILITY_PLAN.md) | Adversarial review of the credibility plan; six findings to triage |
| [`DECISIONS.md`](DECISIONS.md) | The decision journal (D1–D14) |
| [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) | What is not answered, and how to resolve it |
| [`RELATED_WORK.md`](RELATED_WORK.md) | The gap map and the closest work |
| [`REFERENCES.md`](REFERENCES.md) | The curated, checked bibliography for the paper |
| [`WORKLOG.md`](WORKLOG.md) | The current state for a resuming agent or collaborator |

### 2.3 Data and measurement

| Document | Purpose |
|---|---|
| [`DATA.md`](DATA.md) | The data card: provenance, split, limitations |
| [`DATA_SOURCES.md`](DATA_SOURCES.md) | Dataset licensing, privacy, permitted use, and go/no-go |
| [`DATA_USE_PLAN.md`](DATA_USE_PLAN.md) | The operational compliance, security, ethics, and publication rules for BAF |
| [`RESTRICTED_FEATURE_AUDIT.md`](RESTRICTED_FEATURE_AUDIT.md) | The negative result after removing protected attributes: 5/5 wrong A/B releases |
| [`BENCHMARK_PROVENANCE.md`](BENCHMARK_PROVENANCE.md) | The verified benchmark rebuild: hashes, split, parameters, leakage controls |
| [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) | Every column in the processed test frame |
| [`SCHEMA.md`](SCHEMA.md) | The decision-log schema and validation rules |
| [`DATA_READINESS.md`](DATA_READINESS.md) | Minimum fields, BSP 1213 gap, reconstruction paths, stop rules |
| [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md) | The compliant audit design and sample-size guidance |
| [`REPORT_USAGE.md`](REPORT_USAGE.md) | How to run and read the arbitrary-log report |
| [`PRIVACY.md`](PRIVACY.md) | Data handling, PII, sandbox, and incident rules |
| [`MEMO_TEMPLATE.md`](MEMO_TEMPLATE.md) | The audit-ready policy-change memo template |

### 2.4 Engineering

| Document | Purpose |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Module map, data flow, invariants, extension points |
| [`TESTING.md`](TESTING.md) | Test strategy, coverage, gaps |
| [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | Environment, data, commands, seeds, outputs, runtime |
| [`EVALS.md`](EVALS.md) | After-action reviews and process rule changes |
| [`MAINTAINERS.md`](MAINTAINERS.md) | Owner, responsibilities, release process, bus factor |
| [`SUPPORT.md`](SUPPORT.md) | How to ask for help and what not to post |
| [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | Research and code contribution rules |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Version history |
| [`../pyproject.toml`](../pyproject.toml) | Package metadata and dependencies |

### 2.5 Communication and release

| Document | Purpose |
|---|---|
| [`COMMUNICATION.md`](COMMUNICATION.md) | 60-second pitch, 10-minute walkthrough, hard questions |
| [`CREDIBILITY_PLAN.md`](CREDIBILITY_PLAN.md) | Adoption and hostile-review plan: credibility ladder, pilot protocol, 90-day roadmap |
| [`DECISION_MEMO_2026-11.md`](DECISION_MEMO_2026-11.md) | The Nov–Dec 2026 strategic decision: options, expected value, tail risk, recommendation |
| [`ONE_PAGER.md`](ONE_PAGER.md) | The one-page reviewer brief |
| [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md) | The pre-release claim, data, code, and docs checklist |
| [`RELEASE_NOTES_v1.1.0.md`](RELEASE_NOTES_v1.1.0.md) | The current Decision Reliability pre-release: profile, audit, refocused paper |
| [`RELEASE_NOTES_v1.0.2.md`](RELEASE_NOTES_v1.0.2.md) | The v1.0.2 corrective pre-release: what changed, how to verify |
| [`RELEASE_NOTES_v1.0.1.md`](RELEASE_NOTES_v1.0.1.md) | The v1.0.1 review update (superseded for the 2026 claim/paper) |
| [`RELEASE_NOTES_v1.0.0.md`](RELEASE_NOTES_v1.0.0.md) | The historical v1.0.0 review release |
| [`RELEASE_STATUS.md`](RELEASE_STATUS.md) | What is tagged, what is not, and the open public-release gate |
| [`ROADMAP.md`](ROADMAP.md) | The milestones and review dates |
| [`../paper/README.md`](../paper/README.md) | The paper workspace: IEEEtran draft and build instructions |
| [`../paper/main.tex`](../paper/main.tex) | The IEEEtran conference manuscript |
| [`../paper/main.pdf`](../paper/main.pdf) | The compiled two-column draft |
| [`../paper/brief.md`](../paper/brief.md) | The 2-page research brief |
| [`../paper/outline.md`](../paper/outline.md) | The IMRaD outline |

### 2.6 V1 planning

| Document | Purpose |
|---|---|
| [`V1/README.md`](V1/README.md) | V1 credibility-first release: index, scope, definition of done |
| [`V1/VISION.md`](V1/VISION.md) | Strategy, positioning, and the V1 claim |
| [`V1/REQUIREMENTS.md`](V1/REQUIREMENTS.md) | Functional/non-functional requirements and acceptance criteria |
| [`V1/ARCHITECTURE.md`](V1/ARCHITECTURE.md) | Target architecture, interfaces, invariants, trade-offs |
| [`V1/DECISIONS.md`](V1/DECISIONS.md) | The six V1 technical decisions |
| [`V1/ROADMAP.md`](V1/ROADMAP.md) | Phases, dates, milestones, kill criteria |
| [`V1/EXPERIMENTS.md`](V1/EXPERIMENTS.md) | Observation sweep, bounds F5, report gate, reproducibility |
| [`V1/EVALUATION.md`](V1/EVALUATION.md) | Evidence tiers, claim matrix, release gates |
| [`V1/PROGRESS.md`](V1/PROGRESS.md) | Live status and next actions |

### 2.7 Regulatory

| Document | Purpose |
|---|---|
| [`BSP_MAPPING.md`](BSP_MAPPING.md) | BSP 1170/1213/1214/1215, AFASA, NPC, draft MRM, AI principles |

## 3. Generated and local-only artifacts

These are outputs, not editable sources:

| Artifact | Committed? | Source |
|---|---|---|
| [`../reports/pilot.json`](../reports/pilot.json) | yes | `onboarding-audit pilot` |
| [`../reports/pilot.md`](../reports/pilot.md) | yes | `onboarding-audit pilot` |
| [`../reports/obs_sweep/pilot.json`](../reports/obs_sweep/pilot.json) | yes | `onboarding-audit pilot --config configs/obs_sweep.yaml` |
| [`../reports/obs_sweep/obs_sweep.md`](../reports/obs_sweep/obs_sweep.md) | yes | `scripts/analyze_sweep.py` |
| [`../reports/obs_sweep/obs_sweep_summary.csv`](../reports/obs_sweep/obs_sweep_summary.csv) | yes | `scripts/analyze_sweep.py` |
| `reports/obs_sweep/pilot.md` | no | Generated sweep report; the compact `obs_sweep.md` is the committed summary |
| `reports/obs_sweep/pilot_rows.parquet` | no | Generated row-level sweep output |
| [`../reports/propensity_sensitivity.json`](../reports/propensity_sensitivity.json) | yes | `onboarding-audit sensitivity` |
| [`../reports/double_robustness.json`](../reports/double_robustness.json) | yes | `scripts/double_robustness.py` |
| [`../reports/temporal_stability.json`](../reports/temporal_stability.json) | yes | `scripts/temporal_stability.py` |
| [`../reports/temporal_stability.md`](../reports/temporal_stability.md) | yes | `scripts/temporal_stability.py` |
| [`../reports/baseline_sensitivity/pilot.json`](../reports/baseline_sensitivity/pilot.json) | yes | `onboarding-audit pilot --config configs/baseline_sensitivity.yaml` |
| [`../reports/baseline_sensitivity/pilot.md`](../reports/baseline_sensitivity/pilot.md) | yes | Same run; compact report |
| `reports/baseline_sensitivity/pilot_rows.parquet` | no | Same run; row-level output |
| [`../reports/holdout_baseline/pilot.json`](../reports/holdout_baseline/pilot.json) | yes | `onboarding-audit pilot --config configs/holdout_baseline.yaml` |
| [`../reports/holdout_baseline/pilot.md`](../reports/holdout_baseline/pilot.md) | yes | Same run; compact report |
| [`../reports/model_ablation.json`](../reports/model_ablation.json) | yes | `python scripts/model_ablation.py` |
| [`../reports/model_ablation.md`](../reports/model_ablation.md) | yes | Same run; readable table |
| [`../reports/reliability_audit/pilot.json`](../reports/reliability_audit/pilot.json) | yes | `onboarding-audit pilot --config configs/reliability_audit.yaml --reliability-boot 100` |
| [`../reports/reliability_audit/pilot.md`](../reports/reliability_audit/pilot.md) | yes | Same run; compact report |
| [`../reports/reliability_audit/summary.json`](../reports/reliability_audit/summary.json) | yes | `python scripts/summarize_reliability_audit.py` |
| [`../reports/reliability_audit/summary.md`](../reports/reliability_audit/summary.md) | yes | Same run; audit table |
| [`../reports/restricted_main100/pilot.json`](../reports/restricted_main100/pilot.json) | yes | `onboarding-audit pilot --config configs/pilot_restricted.yaml --scenarios main` |
| [`../reports/reliability_audit_restricted/summary.md`](../reports/reliability_audit_restricted/summary.md) | yes | `onboarding-audit pilot --config configs/reliability_audit_restricted.yaml --reliability-boot 100` |
| [`../reports/case_reliability/report.json`](../reports/case_reliability/report.json) | yes | `onboarding-audit report` on `examples/case_log.csv`, `--out reports/case_reliability` |
| [`../reports/case_reliability/report.md`](../reports/case_reliability/report.md) | yes | Same run; grade A memo |
| [`../reports/demo_reliability/report.json`](../reports/demo_reliability/report.json) | yes | `onboarding-audit demo --out reports/demo_reliability` |
| [`../reports/demo_reliability/report.md`](../reports/demo_reliability/report.md) | yes | Same run; grade C memo |
| [`../reports/propensity_sensitivity.md`](../reports/propensity_sensitivity.md) | yes | `onboarding-audit sensitivity` |
| `reports/pilot_rows.parquet` | no | `onboarding-audit pilot` |
| `reports/sample_report/` | no | `onboarding-audit report` |
| `reports/demo/` | no | `onboarding-audit demo` |
| `data/scored_test.parquet` | no | `scripts/prepare_baf.py`; see [`DATA.md`](DATA.md) |
| `data/scored_test.provenance.json` | no | `scripts/prepare_baf.py`; input/output hashes and library versions |

Do not hand-edit a generated report. Change the code, rerun the command, and
update the claim ledger if the number changes.

## 4. Document status

| Status | Meaning | Examples |
|---|---|---|
| **Canonical** | The source of truth for its topic; update deliberately | `METHODS.md`, `RESULTS.md`, `CLAIMS.md`, `THREATS.md`, `DECISIONS.md`, `SCHEMA.md`, `AUDIT_DESIGN.md`, `ARCHITECTURE.md`, `TESTING.md`, `REPRODUCIBILITY.md`, `REFERENCES.md` |
| **Derived** | Summarizes canonical docs; must not introduce a new claim | `README.md`, `ONE_PAGER.md`, `COMMUNICATION.md`, `paper/brief.md`, `paper/outline.md` |
| **Generated** | Produced by a command; do not edit by hand | `reports/pilot.md`, `reports/propensity_sensitivity.md`, `reports/*.json` |
| **Historical** | Records a past state; do not update the numbers | `WORKLOG.md` (past entries) |
| **Template** | A fill-in form, not a measured result | `MEMO_TEMPLATE.md` |

## 5. Precedence when documents disagree

1. **Numbers:** `reports/pilot.json` and
   `reports/propensity_sensitivity.json` win over prose.
2. **Claims:** [`CLAIMS.md`](CLAIMS.md) wins over the README, one-pager, brief,
   or outline.
3. **Methods:** [`METHODS.md`](METHODS.md) wins over a summary of the method.
4. **Threats:** [`THREATS.md`](THREATS.md) wins over an optimistic limitation
   paragraph.
5. **Decisions:** [`DECISIONS.md`](DECISIONS.md) wins over an undocumented
   convention.
6. **Generated reports:** the committed JSON wins over the generated Markdown if
   they disagree; regenerate the Markdown.

If a derived document contradicts a canonical one, fix the derived document, not
the canonical one.

## 6. Update rules

| Change | Update |
|---|---|
| A new measured number | `reports/*.json` (rerun), `CLAIMS.md`, `RESULTS.md`, then derived docs |
| A new public claim | `CLAIMS.md` first; then `RESULTS.md` and the derived docs |
| A new method or estimator | `METHODS.md`, `PILOT_SPEC.md` (if pre-registered), `ARCHITECTURE.md`, `TESTING.md`, `DECISIONS.md` |
| A new scenario | `configs/pilot.yaml`, `PILOT_SPEC.md` §8, `CLAIMS.md`, `RESULTS.md` |
| A new data field or schema change | `SCHEMA.md`, `schema.py`, `REPORT_USAGE.md`, tests |
| A new regulatory source | `BSP_MAPPING.md`, `PROBLEM.md` if it changes the motivation |
| A new citation | `REFERENCES.md` first; then `RELATED_WORK.md` and the paper |
| A new open question | `OPEN_QUESTIONS.md`; `DECISIONS.md` if it changes a choice |
| A release | `CHANGELOG.md`, version files, `CITATION.cff`, `PUBLICATION_CHECKLIST.md` |
| A documentation-only change | This index if a new document is added |

## 7. What is not here

- No submission-ready camera copy; the initial IEEEtran draft is
  [`../paper/main.pdf`](../paper/main.pdf).
- No production system, API, database, or dashboard.
- No Philippine bank data or proprietary log.
- No legal opinion. [`BSP_MAPPING.md`](BSP_MAPPING.md) is a mapping, not advice.

## 8. Maintenance

- Review the claim ledger and the results after every full run.
- Review the threats register before every public release.
- Review the open questions at each roadmap gate.
- Keep the generated reports reproducible from
  [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).
- Do not let the documentation drift from the code: if a public function or CLI
  flag changes, update `ARCHITECTURE.md`, `REPORT_USAGE.md`, and the tests in the
  same change.
