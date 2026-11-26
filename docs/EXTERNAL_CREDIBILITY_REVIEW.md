# External Credibility Review — V1

**Status:** Pre-mortem, 2026-11-27. **Post-review note:** the critical
research-gap claim and citation defects identified here were corrected in
`v1.0.2`; the tracked status is in [`RED_FLAG_AUDIT.md`](RED_FLAG_AUDIT.md).
**Stance:** Skeptical fintech data scientist. The objective is to find the
embarrassing mistake before an external reviewer does.
**Method:** Inversion & Falsification (pre-mortem + falsification ledger),
Causal Hierarchy (estimand/identification audit), and Goodhart & Counter-Metrics
(claim and business-value audit).
**Verdict:** **The problem is real. The project is worth pursuing as a
research/portfolio artifact and an open applied benchmark. It is not credible as
a commercial product, a production system, or a paper claiming a new estimator
or a new ranking finding.** The public materials contain one **false
research-gap claim**, and the manuscript omits the three closest 2026 papers.
Those two defects must be fixed before any external review.

---

## 1. What the project claims

| Claim | Where | Evidence tier |
|---|---|---|
| Naive onboarding evaluation is materially biased | README, paper, CLAIMS | Simulation (E2) |
| The naive estimate can reverse the policy ranking | README, paper, CLAIMS | Simulation (E2), main scenario only |
| DR recovers the `P0` value | Paper, CLAIMS | Simulation (E2), oracle/estimated `e` |
| The reject margin is not point-identified | Paper, CLAIMS | Derivation + simulation |
| Audit-only recovers the logging-approved population under outcome-dependent labels | Paper, CLAIMS | Simulation (E2) |
| The tool refuses unidentified logs | README, validation report | Code/test (E1) |
| Vendors do not document selection/delay-aware policy evaluation | PROBLEM, CLAIMS | Search-based absence |
| No peer-reviewed fraud-specific policy evaluation exists | PROBLEM, CLAIMS | **False as stated** |
| The project is a review-ready fintech measurement layer | README, release notes | Self-assessment |

The first six are defensible **within their stated scope**. The last three are
where the credibility risk sits.

---

## 2. External problem validation

### 2.1 The problem is real

The selective-label problem in account-opening fraud is documented, not
imagined:

- **Pombal et al. (2022)**, *Prisoners of Their Own Devices* (ICML 2022
  workshop, arXiv:2206.13183), uses a real-world account-opening fraud case
  study and explicitly discusses selective labels: blocking an account means
  never observing its true label.
- **Jesus et al. (2022)**, the BAF dataset (NeurIPS 2022 Datasets and
  Benchmarks), is generated from a real online bank account-opening fraud
  dataset and states that labels are only observed for applications the
  incumbent policy did not block.
- **“Understanding Unfairness in Fraud Detection through Model and Data Bias
  Interactions”** (arXiv:2207.06273) explicitly describes the selective-label
  problem in account-opening fraud.
- **BSP Circular 1213** requires automated fraud management, calibration, stress
  testing, independent review, and audits; **BSP Project Sapiens** names
  sampling bias and labelling bias and reports that six of ten deep-dive
  institutions validate AI models during development and ongoing.
- Industry vendors sell **backtesting, champion–challenger, shadow mode, and
  outcome feedback** (Taktile, Effectiv, ThreatMetrix, Sphinx AML). This is
  evidence that the *category* is real and budgeted.

**Conclusion:** the problem is legitimate. A fintech data scientist would not
call it imagined.

### 2.2 Existing solutions cover parts of the gap

| Existing solution | What it does | What it does not establish |
|---|---|---|
| **Taktile Iterations** | Historical backtesting, champion/challenger, outcome feedback, model-risk controls, audit trails | The public page does not document selective-label or delay-aware correction |
| **Effectiv / ThreatMetrix / Sphinx** | Champion–challenger, shadow mode, rule backtesting | Same: no documented selection/delay correction |
| **Open Bandit Pipeline / SCOPE-RL / banditml** | General off-policy evaluation | No account-opening actions, review capacity, reject margin, or audit memo |
| **rejectkit** | Credit-scoring reject inference, eight methods, honest benchmark | Not fraud-specific; no policy value, delay, audit, or review capacity |
| **JUBILEE (2026)** | OPE benchmark for debt collections with hidden assignment dependence | Adjacent, not account-opening fraud; shows intervals fail under hidden dependence |
| **OSCAR (ICAIF 2026)** | Certified online learning for auditable financial screening under selective and delayed labels | Online learning/certification focus; not the account-opening `P0` + reject-margin + audit-memo combination |
| **Beyond Holdout Error (ICAIF 2026)** | Layered evaluation of estimators under selective labels; shows rankings can reverse | Not an account-opening policy-value tool; no reject-margin bounds or audit design |
| **DOiT (ICAIF 2026)** | Shows better money-flow ranking can coexist with worse account selection in AML review | AML-specific; not account-opening fraud or a policy-evaluation toolkit |

**Conclusion:** the **combination** the project offers — account-opening `P0`,
capacity-constrained review, delay/selection-aware estimators, partial
identification of the reject margin, an audit design, an identification gate,
and a public reproducible artifact — is not obviously covered by one existing
product. That is the defensible gap.

The **absolute** claims are not defensible:

- “No vendor publicly documents selection/delay-aware policy evaluation” is a
  **search-based absence**, not a proof. The 18-vendor matrix is not committed;
  a reviewer cannot check it. Taktile’s public page already covers backtesting,
  champion–challenger, feedback, model-risk controls, and audit trails. The
  differentiation is the *correction and the gate*, not the category.
- “No peer-reviewed fraud-specific policy evaluation with a counterfactual
  design” is **false**: OSCAR, Beyond Holdout Error, and DOiT are peer-reviewed
  ICAIF 2026 papers in exactly this space. The project’s own `RELATED_WORK.md`
  lists them. The claim ledger and the problem brief contradict the related-work
  doc.

### 2.3 The gap is real but narrower than the pitch

The honest gap statement is:

> No reviewed work jointly provides an account-opening `P0` estimand, a
> capacity-constrained review layer, partial-identification bounds for the
> reject margin, a compliant audit design, an identification gate, and an open
> reproducible benchmark/tool.

That is a legitimate applied contribution. It is **not** “no one has studied
this” and it is **not** a new estimator or a new ranking phenomenon.

---

## 3. Technical credibility audit

### Critical red flags

#### C1 — The “no peer-reviewed work” claim is false and internally contradictory

`CLAIMS.md` says:

> “No peer-reviewed fraud-specific policy evaluation with a counterfactual
> design | Limitation (search-based absence) | Literature review, 25 sources.”

`PROBLEM.md` §3.5 repeats it. But OSCAR (ICAIF 2026), Beyond Holdout Error
(ICAIF 2026), and DOiT (ICAIF 2026) are peer-reviewed papers on selective
labels, estimator rankings, and account selection in financial screening. The
project’s own `RELATED_WORK.md` lists all three. The manuscript does **not**
cite them.

**Why this is critical:** an experienced reviewer will read “no peer-reviewed
work” and immediately know it is false. That single sentence can discredit the
entire package. At ICAIF, omitting the three closest accepted papers is a
desk-reject or major-revision risk.

**Verdict:** stop-the-line. Remove the claim; cite the three papers; reposition
the contribution as the applied combination/open artifact.

#### C2 — The headline is still a simulation of the bias it measures

The pilot simulates the action log, observation probabilities, label delay,
audit, and review capacity. The naive bias is a property of that simulation. The
project discloses this, but the README and paper still lead with
“112–278%” as the headline. A skeptical data scientist will say: *you simulated
a biased mechanism and then measured the bias.*

The action-weighted baseline improves the defense: the main-scenario point
estimate still differs by 278.5% vs 2.9%, so the gap is not merely an
unweighted-mean artifact. But it does **not** establish external validity; it
establishes that the simulation result survives one more realistic baseline.

**Verdict:** the conditional claim survives; the market-magnitude claim does
not. Lead with the method/gate, not the percentage.

#### C3 — The product promise includes the reject margin, but the estimand does not

The README asks: “will it catch more fraud without rejecting more good
customers?” The primary estimand is `P0`, which **excludes** the rejected
population — exactly where “rejecting more good customers” lives. The memo now
adds a full-policy difference bound and a break-even, and warns when the `P0`
recommendation does not survive. That is a real improvement, but the headline
promise is still broader than the identified quantity.

**Verdict:** the product is a `P0`-conditional measurement layer plus a
full-policy fragility check, not a full-policy evaluator. Say that in the first
paragraph.

#### C4 — There is no native onboarding action log, and the adoption prerequisite is severe

BAF has no approve/review/reject actions, no propensities, no label timestamps,
and no audit flags; the project simulates them. A real bank may not log
`action`, `score`, `decision_time`, `label_time`, `audit_flag`, or review
outcomes. BSP 1213’s 11 fields are transaction-log fields, not onboarding
decision fields. The pilot protocol says “stop” if the fields are missing.

**Verdict:** the tool is not runnable on a typical bank’s existing data without
a reconstruction/data-engineering project. This is a practical adoption blocker.
A fintech data scientist will ask “who has this log?” The project has no answer
beyond a partner pilot.

#### C5 — The paper’s novelty is narrower than the manuscript claims

The manuscript positions the closest work as credit-scoring sampling bias and
generic OPE. That is outdated. The closest 2026 work is:

- **OSCAR**: certified online learning for **auditable financial screening under
  selective and delayed labels**.
- **Beyond Holdout Error**: a layered evaluation framework under selective
  labels that shows estimator rankings can reverse.
- **DOiT**: better ranking can coexist with worse account selection in AML.

The project’s “accurate point estimate does not imply a correct decision”
finding is anticipated by Beyond Holdout Error and DOiT. The contribution is the
account-opening instantiation, the `P0`/reject-margin split, the full-policy
break-even, the gate, the audit design, and the open benchmark. The paper must
say that, cite the closest work, and stop implying a new phenomenon.

**Verdict:** the paper as written is not submission-ready. Either reposition it
or do not submit it.

### Significant weaknesses

#### S1 — The case study candidate is an oracle

`scripts/make_case_study.py` builds the candidate as `p_true + N(0, 0.003)`, a
less noisy estimate of the true probability, not a model trained on pre-decision
features. The case is now labeled as an oracle, which is honest, but it is still
a best-case demonstration. A reviewer will say it does not show that a real
challenger model wins.

#### S2 — Audit-only targets the logging-approved population, not the candidate’s approved population

The audit sample is drawn from the incumbent’s approved rows. The estimator is
unbiased for the **logging-approved** population under random audit and correct
resolution. A candidate that changes who is approved is outside the target. The
docs now qualify this, but the phrase “audit-only recovers the approved
population” is still easy to misread.

#### S3 — The identification gate is a governance heuristic, not an identification test

The gate checks positivity, 100 observed labels, 30 per action, ESS 100, max
weight 100, cost support, and a declared observation mechanism. Those thresholds
are conventions, not derived. The gate cannot test unmeasured confounding. An
analyst can declare `action` falsely and the memo will say “Measured.” This is
disclosed, but a data scientist will call it a screening heuristic, not
identification.

#### S4 — The bounds are uninformative in the scenarios where the decision is hard

The narrow F5 interval fails (15/88); the widened interval passes 77/88 but is
~4× wider; in `frej_002` the width is **0.203** against policy values around
0.01. The bounds are honest but not decision-grade for the reject margin. The
full-policy break-even is a sensitivity, not an identification result.

#### S5 — The cost matrix and business case are still assumptions

The cost matrix is normalized; the false-reject cost is the inclusion
parameter; the ranking flips at `frej_050`. The benchmark-consistent business
case is net **20–47** units per 1M applications at `p_wrong=1.0`, and
**negative** at `p_wrong=0.5`; a 1% audit costs ~193 units. The pilot is
marginal unless the naive rule is very likely wrong and the audit is cheap. A
bank’s costs may make it worse.

#### S6 — The vendor-gap claim is unproven

Taktile publicly sells backtesting, champion/challenger, outcome feedback,
model-risk controls, and audit trails. Effectiv, ThreatMetrix, and Sphinx sell
champion/challenger, shadow mode, and rule backtesting. The project’s
differentiation is selection/delay correction and the gate, not the category.
The 18-vendor matrix is not committed; the claim is search-based absence.

#### S7 — Fairness is descriptive, not audited

The new segment diagnostic shows approval/review/reject counts, observed fraud,
and observed false-reject shares, with small-cell suppression. It is explicitly
not a fairness certification. Rejected applicants have no outcome, so the
diagnostic cannot answer the inclusion question for the margin that matters.

#### S8 — No external validation, solo maintainer, waived release gate

The release is a pre-release published by owner decision; the external-review
gate is waived, not met. No partner log, no independent replication, no peer
review. A data scientist will treat this as a research prototype.

#### S9 — The “better model” premise is not ablated

The main benchmark compares a logistic incumbent with a LightGBM candidate on
the same features. The candidate is “better” by model class/capacity; the
project does not ablate features, tuning, or model class to show that the
ranking flip is about observation selection rather than model capacity. The case
study is an oracle. A reviewer may say the “better model” is constructed, not
discovered.

### Minor issues

- **BSP 1213 date:** the project says 25 June 2026; several secondary sources say
  30 June 2026. The primary circular should be cited; the date is contested in
  secondary sources.
- **Related-work metadata:** OSCAR’s title is “Auditable **Financial**
  Screening,” not “Auditable Screening”; Beyond Holdout Error’s title is “A
  Layered Framework for Evaluating Estimators under Selective Labels”; DOiT’s
  full title is longer. Fix the bibliography.
- **Search-based claims:** “25 sources” and “18 vendors” are not committed
  artifacts; the reader cannot reproduce the search.
- **Precision:** 50-rep scenarios and “100%”/“0%” point estimates need Wilson
  intervals in the prose; the JSON has them in places, the abstract does not.

---

## 4. Falsification ledger

| Claim | Test | Result | Verdict |
|---|---|---|---|
| The problem is real | Pombal 2022, BAF 2022, fairness 2022, BSP 1213/Sapiens | Documented | **Survives** |
| Naive bias is not just an unweighted-mean artifact | Action-weighted baseline (50 reps) | Main naive 278.5% vs action-weighted 2.9%; `frej_050` 291.2% vs 2.4% | **Survives** |
| The correction always ranks better | `frej_050` | Naive P(best) 100%, DR/action-weighted 58% | **Fails**; cost-dependent |
| No peer-reviewed fraud-specific evaluation exists | ICAIF 2026 search | OSCAR, Beyond Holdout Error, DOiT | **Fails**; claim false |
| Vendors do not do selection/delay-aware evaluation | Vendor pages | Taktile/Effectiv/ThreatMetrix/Sphinx sell backtesting/champion-challenger; selection/delay correction not documented | **Inconclusive**; search-based |
| Audit-only recovers the approved population | Code/docs | Logging-approved only | **Fails as stated**; qualified |
| The case study shows a real better model | `make_case_study.py` | Candidate is an oracle | **Fails as a model claim**; labeled |
| The reject margin is decision-grade | Bounds/F5 | Narrow fails; `frej_002` width 0.203 | **Fails**; partial identification only |
| The gate identifies a valid log | Gate code | Heuristic; declaration untestable | **Partially survives**; governance control |
| The paper is novel enough | Closest 2026 work | Ranking/selection phenomenon anticipated | **Fails as framed**; reposition |
| The business case is positive | Benchmark arithmetic | Net 20–47 at `p_wrong=1.0`; negative at 0.5 | **Conditional**; not proven |

---

## 5. Business value

**Who is the buyer?** The strongest buyer is model risk / independent validation,
not fraud analytics. The buyer has a recurring, mandated process, independence
from the model owner, and a deliverable (validation memo) that matches the
project. Fraud analytics is a user/champion; researchers are a distribution
channel.

**What is the value?** A defensible `P0` estimate, an explicit reject-margin
bound, a full-policy break-even, a gate that refuses unidentified logs, and a
memo that separates measured/assumed/unverifiable. That is a real model-risk
artifact.

**What is the commercial problem?** The buyer already has backtesting,
champion–challenger, model-risk platforms, and internal validation. The
project’s unique wedge is the selection/delay correction and the refusal gate,
not the category. The integration requires a historical decision log with fields
many banks do not have; the audit design requires legal/ops review; the business
case is marginal at the benchmark’s own numbers. A standalone CLI is unlikely to
be adopted; a paid retrospective validation engagement is more plausible.

**Verdict:** worth pursuing as a research/portfolio artifact and a possible
model-risk service; not worth pursuing as a standalone product or a “validated”
fintech solution without a real-log pilot.

---

## 6. Verdict

**Problem:** real and documented. **Not imagined.**

**Core method:** sound in principle. The `P0`/reject-margin split, DR/IPW,
partial identification, gate, and audit design are coherent. The action-weighted
baseline and the negative results are genuine strengths.

**Execution:** competent but simulation-bound. The headline is a property of the
simulated observation mechanism; the case study is an oracle; the audit design
and cost matrix are unvalidated; the candidate model is not ablated; the gate is
a heuristic; the bounds are uninformative in the hard scenarios.

**Novelty:** incremental. The ranking/selection phenomenon is anticipated by
2026 work; the paper omits the closest papers and contains a false “no
peer-reviewed work” claim. The applied combination/open artifact is the real
contribution.

**Business value:** plausible for model risk/validation, unproven commercially.
Existing vendors cover backtesting/champion–challenger; the project’s wedge is
narrow; the integration and audit costs are real.

**Fundamental flaw?** **No.** The project is overclaimed and simulation-bound,
not worthless. It is worth pursuing as a **research/portfolio artifact and open
applied benchmark**. It is **not** ready to be presented as a commercial
product, a production system, or a novel paper.

**Decision:**
- **Continue** as a narrow applied measurement layer/open benchmark.
- **Stop** claiming “no peer-reviewed work,” a new ranking finding, or
  production readiness.
- **Do not submit the paper** until the closest 2026 work is cited and the
  contribution is repositioned.
- **Do not pursue the standalone product** without a real-log pilot and a
  model-risk buyer.

---

## 7. If you continue: minimum corrections

These are ordered by credibility risk, not by effort.

1. **Remove the false research-gap claim.** Replace “No peer-reviewed
   fraud-specific policy evaluation” with “No reviewed work jointly provides the
   full account-opening `P0` + reject-margin + audit + open-tool combination.”
2. **Cite OSCAR, Beyond Holdout Error, and DOiT in the paper.** Add a 2026
   financial selective-labels subsection; state what each does and what the
   project adds. Fix the bibliography metadata.
3. **Reposition the paper.** Claims: applied account-opening instantiation,
   `P0`/reject-margin split, full-policy break-even, gate, audit design, open
   benchmark. Do not claim a new estimator or the ranking phenomenon.
4. **Lead with the conditional claim and the gate.** The 112–278% number is a
   simulation result; put it after the method and the scope.
5. **Keep the action-weighted baseline** and run a holdout baseline; report both.
6. **Get a real log or label the project as a simulation prototype.** Do not
   claim production or a specific bank.
7. **Publish the 18-vendor matrix** or downgrade the vendor-gap claim to
   search-based absence.
8. **Cite the BSP 1213 primary text and resolve the 25 vs 30 June date.**
9. **Narrow the fairness claim**; the segment diagnostic is descriptive, not an
   audit.
10. **Get two external readers** before calling it validated. The release is
    currently a pre-release with a waived gate.

---

## 8. Sources checked

| Source | URL | Status |
|---|---|---|
| Pombal et al. 2022, *Prisoners of Their Own Devices* | https://arxiv.org/abs/2206.13183 | Verified; ICML 2022 workshop |
| BAF, Jesus et al. 2022 | https://proceedings.neurips.cc/paper_files/paper/2022/file/d9696563856bd350e4e7ac5e5812f23c-Paper-Datasets_and_Benchmarks.pdf | Verified; NeurIPS 2022 |
| Fairness in account-opening fraud | https://arxiv.org/abs/2207.06273 | Verified |
| Taktile Iterations | https://taktile.com/product/iterations | Verified; vendor page (marketing) |
| Effectiv champion–challenger | https://effectiv.ai/resources/champion-challenger | Verified; vendor page |
| ThreatMetrix champion–challenger | https://threatmetrix.com/digital-identity-blog/fraud-prevention/champion-challenger-enabling-better-fraud-detection | Verified; vendor page |
| Sphinx AML backtesting/shadow mode | https://sphinxhq.com/blog-posts/aml-rule-backtesting-shadow-mode | Verified; vendor page |
| Open Bandit Pipeline | https://zr-obp.readthedocs.io/en/latest/ | Verified; general OPE |
| SCOPE-RL | https://github.com/hakuhodo-technologies/scope-rl | Verified; general OPE |
| rejectkit | https://pypi.org/project/rejectkit | Verified; credit reject inference |
| JUBILEE (2026) | https://arxiv.org/abs/2611.10972 | Verified; OPE in debt collections |
| Selection-Aware Certification (2026) | https://arxiv.org/abs/2611.18687 | Verified; fraud rule portfolios, BAF case |
| OSCAR (ICAIF 2026) | https://icaif2026.org/accepted-papers | Verified; ACM DOI 10.1145/3858063.3858757 |
| Beyond Holdout Error (ICAIF 2026) | https://dl.acm.org/doi/10.1145/3858063.3858808 | Verified; Bloomberg/ACM |
| DOiT (ICAIF 2026) | https://arxiv.org/abs/2611.27809 | Verified; ICAIF 2026 |
| BSP Circular 1213 | https://www.bsp.gov.ph/Regulations/Published%20Issuances/Images/Circular_1213.pdf | Verified official URL; PDF blocked to fetcher |
| BSP Project Sapiens | https://www.bsp.gov.ph/Media_And_Research/Special%20Publications/BSP_Thematic_Review_on_the_Use_of_AI_and_ML_in_Financial_Services.pdf | Verified via snippet; six of ten validate |
| BSP 1213 deadline | Secondary sources | **Contested:** 25 June vs 30 June 2026; cite primary |

**What this review did not verify:** the actual vendor implementations behind
their marketing pages; the audit design’s legal/operational feasibility; a real
bank log; the AFASA/NPC primary texts; the exact BSP 1213 deadline from the
primary PDF; the 2026 paper PDFs (abstracts/metadata only). These are stated as
unverified, not assumed.

---

## 9. Reasoning check

**Claim and tier.** The verdict — “the problem is real; the project is worth
pursuing as a research artifact, not as a commercial product or a novel paper
without corrections” — is **derived** from the repository and **verified**
external sources. The false research-gap claim is **observed** in `CLAIMS.md`
and `PROBLEM.md` and **contradicted** by verified ICAIF 2026 papers. The
simulation-bound critique is **observed** in the code. The commercial verdict is
**inferred** from vendor pages, integration prerequisites, and the benchmark
arithmetic; it is not a market study.

**Strongest counter-case.** The project is more honest and more reproducible than
most student fintech projects; it records failed controls, includes an
action-weighted baseline, and refuses unidentified logs. The vendor pages may
not document selection/delay correction because the feature is internal; the
project’s gap may be real even if Taktile sells “backtesting.” The paper could be
positioned as an applied account-opening study even if the ranking phenomenon is
known. The counter-case is partly right: the project is not worthless, and the
applied combination is a legitimate contribution. The response is that the
**absolute claims** and the **missing citations** are still disqualifying for an
external review, regardless of the project’s honesty.

**Not verified.** No real bank log; no audit/legal review; no vendor
implementation details; no primary BSP 1213 text/date; no peer review; no
holdout baseline; no independent replication. Any of these could change the
commercial verdict. A real log showing action-dependent observation and a
feasible audit would strengthen the case; a real log showing outcome-dependent
observation would weaken the point-estimate claim and make audit-only the only
fallback, with its 80–86% coverage.

**Next action.** Fix the false claim and citations first, then decide whether to
continue as a research artifact or stop. The stop rule: if the paper is not
repositioned or a real log cannot be obtained, do not present the project as a
validated solution.
