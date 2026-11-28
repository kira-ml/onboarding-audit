# Strategic Review — V1

**Status:** Author-led strategic review, 2026-11-26. Includes an independent
red-team pass (Appendix A).
**Subject:** `onboarding-audit`, `v1.0.0` review tag and the post-tag working
tree.
**Method:** Mental Models OS — Model 5 (Inversion & Falsification), Model 2 /
Theory of Constraints, and the Goodhart & Counter-Metrics discipline. One
artifact per model: a constraint table, a pre-mortem, a falsification ledger, and
a counter-metric audit.
**Verdict:** **FAIL for a public flagship release; PASS for external review as a
Level 2 research artifact.** The binding constraint is external evidence and
buyer clarity, not code. The product promise is broader than the identified
estimand, the release gate is open, the headline ranking is a selected scenario,
and the scientific framing leads with the weakest claim.

---

## 1. Classification and framing

**Task class:** high-stakes strategic review. The release decision is
hard-to-reverse in reputation, though the code is reversible. The cost of a
false "ready" is a hostile reviewer or a risk team acting on a `P0`-only
recommendation.

**Decision:** Should `v1.0.0` be presented as the flagship fintech release, and
what must change before it is?

**User:** the author, pursuing a Summer 2027 fintech internship and a durable
research project. Secondary users: a fintech model-risk reviewer, a fraud/KYC
practitioner, and a research reviewer.

**Binding constraint:** access to external evidence — a real historical log, a
risk-team reviewer, or at minimum two external readers. The project has enough
methods, tests, and documentation for a pilot; it does not have external
validation.

**Smallest acceptable outcome:** a review package that (a) states the
`P0`-conditional claim and the full-policy limitation without contradiction,
(b) refuses to overclaim, (c) is internally consistent, and (d) has a concrete
path to two external readers. A completed pilot is upside, not the minimum.

---

## 2. What V1 does well — preserve this

The review should not destroy what is working. The following are genuine assets
and should survive any redesign:

1. **The estimand split.** `P0` versus the reject margin is the correct
   conceptual move. It separates what the log identifies from what it does not.
   Most applied fraud papers blur this; this project does not.
2. **The identification gate.** The report refuses a point estimate on
   positivity, sample, ESS, weight, cost, and observation-mechanism failures.
   This is the product's most defensible feature.
3. **Recorded negative results.** F5 is recorded as a failure for the narrow
   interval; the outcome-dependent label failure is disclosed; the ranking gap
   is reported. This is rarer than it should be.
4. **Reproducibility infrastructure.** The benchmark hash, `check_claims.py`,
   CI, and the claim ledger are real. They are the reason a reviewer can engage
   at all.
5. **The audit design's legal discipline.** Rejecting random
   approvals/rejections and using post-hoc verification plus shadow scoring is
   the right constraint for a regulated institution.
6. **The regulatory mapping.** `BSP_MAPPING.md` is careful about BSP 1213 being
   an FMS circular, not the draft MRM. That precision is an asset; protect it.
7. **The independent-pass corrections.** The audit found real defects (the
   `e_approve` resolution bug, the zero-propensity crash, the memo key bug) and
   changed the claims. That is the behavior of a credible project.

The problem is not quality. The problem is **strategic fit and evidence tier**.

---

## 3. Artifact 1 — Constraint table (Model 2)

| Constraint | Evidence | Binding? | What it blocks | Next action |
|---|---|---|---|---|
| **External validation** | No partner log; no external readers; `EXTERNAL_REVIEW.md` has no entries; `V1/README.md` definition of done still open | **Yes** | Level 3; the public-release gate; the strongest internship story | Reviewer packet, 10 targeted asks, two calls, a real-log pilot |
| **Buyer clarity** | `V1/VISION.md` lists five audiences; README speaks to onboarding teams; model card speaks to model risk; paper speaks to researchers | **Yes** | Adoption; the business case; the one-pager's "who is this for?" | Choose model risk / independent validation as the beachhead |
| **Product-decision fit** | The headline promise is "catch more fraud without rejecting more good customers"; the identified estimand excludes rejects; the memo's recommendation is `P0`-conditional | **Yes** | The core value proposition; trust with a risk committee | Full-policy difference bounds + break-even (implemented); make it the default reading |
| **Scientific novelty** | Standard DR/IPW/bounds; the paper admits "not a new estimator"; evidence is a simulation on one synthetic dataset | **Yes for publication** | A main-conference paper; peer-reviewed credibility | Re-center on decision reliability, not bias magnitude; target a workshop/technical report first |
| **Fairness / inclusion evidence** | Schema has `segment`/`region`; the pilot does not evaluate fairness; the promise is inclusion-sensitive | **Yes for a PH fintech flagship** | A regulator/risk-committee question the tool cannot answer | Minimal segment diagnostic or an explicit narrowing of the claim |
| **Engineering quality** | 119 tests in the current tree, CI, hash, claim checks | No | Nothing material | Do not add more tests for their own sake |
| **Documentation volume** | 40+ docs, canonical map, claim ledger | No (but consistency is binding) | Reviewer trust when docs contradict | Fix drift; do not add more docs without a reader |
| **Time / attention** | 10–12 h/week cap; GPA, applications, health | **Yes** (personal) | Scope | Stop adding methods; spend the next block on external review |

**Reading:** the project is optimizing the two non-binding constraints
(engineering and documentation volume) while the three binding constraints
(external validation, buyer clarity, product-decision fit) are open. This is the
classic Theory of Constraints failure: local improvements that do not move the
system.

---

## 4. Artifact 2 — Inversion pre-mortem (Model 5)

Assume it is December 2027 and the project failed as a flagship. The most
plausible failure narratives:

| # | Failure narrative | Early warning | Kill test | Severity |
|---|---|---|---|---|
| P1 | A risk team reads "prefer candidate," adopts, and the candidate is worse once rejected applicants are counted. The project is blamed for a bad decision. | The memo's recommendation is `P0`-only; the full-policy row says "not identified" but is easy to miss. | Construct a log where the `P0` ranking and the full-policy ranking disagree; run the report. Before the fix, the memo recommended the `P0` winner. | **Critical** |
| P2 | A hostile reviewer checks the `v1.0.0` tag, finds the validation report says 65 tests in one section and 92 in another, the sweep design is wrong, and CI is "pending" in one place and "pass" in another. The package is dismissed. | A reviewer asks for the exact command and the exact test count. | Read `VALIDATION_REPORT.md` against the code and `reports/`. It failed before the fix. | **Critical** |
| P3 | The paper is rejected as "an applied simulation with standard estimators." The flagship has no peer-reviewed artifact, and the internship story is "a student project with good docs." | Reviewer 2 says "the contribution is incremental" or "the magnitude is a simulation artifact." | Ask: what would a reviewer cite this paper for? If the answer is the bias magnitude, it is weak. | **High** |
| P4 | No external reader engages. The project stays at Level 2. The author spends the next six weeks adding another scenario, which no one reads. | The reviewer list is still empty; commits are code/docs, not outreach. | Count external contacts and reviewer calls over the last two weeks. If zero, the constraint is not being worked. | **Critical** |
| P5 | A bank's log lacks `action`, `score`, `label_time`, or `audit_flag`; the pilot stops at the schema gate. The team concludes the tool is unusable. | The first partner call reveals a fields gap; the pilot protocol says "stop." | Run `validate` on a realistic BSP 1213-only log. It will not support the estimators. | **High** |
| P6 | A compliance reviewer says the project overstates BSP 1213 or the audit design. The regulatory hook becomes a liability. | The claim ledger says "BSP 1213 mandates calibration..." without "FMS, not MRM." | Read `CLAIMS.md` without `BSP_MAPPING.md`; ask whether it overclaims. | **Medium–high** |
| P7 | The tool recommends a policy that improves aggregate cost but rejects more applicants from a vulnerable segment. There is no fairness diagnostic. | A risk committee asks for segment-level false-reject rates; the memo has none. | Add a segment question to the reviewer packet; see whether the report can answer it. It cannot. | **High** |
| P8 | The candidate score was fit on the evaluation window, or the benchmark hash differs on another stack. The "reproducible" claim fails. | A reviewer on another machine reports a hash mismatch; the score pipeline is external. | Rebuild from a clean checkout on a different library version; compare the hash. | **Medium** |
| P9 | The business case is challenged: the audit costs ~58% of the value of the policy switch, `p_wrong=0.5` is unsupported, and the units are not pesos. The pilot is not worth it. | A risk team asks "what does it save?" and the answer is a template. | Fill the template with the committed numbers and compute the net. | **High** |
| P10 | The full-policy break-even is misread as an estimate. A risk committee treats `p*` as a prior and approves a fragile policy. | The memo says "break-even" but a reader quotes it as "the rejected fraud rate." | Ask a non-author to read §4.1 and explain what `p*` is. If they call it an estimate, the label is not strong enough. | **Medium** |

The pre-mortem's common thread: **the project is credible about what it cannot
identify, but it has not made the decision layer safe for a reader who does not
read the limitations.** The fix is not more caveats; it is a decision surface
that makes the limitation impossible to miss.

---

## 5. Artifact 3 — Falsification ledger

Each row states the claim, the test that could disprove it, the result, and the
verdict. The tests were run on the repository at `4527a4f` plus the working-tree
changes described in §7.

| # | Claim under test | Falsification test | Result | Verdict |
|---|---|---|---|---|
| F1 | The report's recommendation answers the buyer's full-policy question. | Build a log where the candidate is `P0`-cheaper but worse on rejected rows; run the report. | Before the fix, the memo printed a directional `P0` recommendation and left the full-policy "not identified" in a later section. A constructed log showed the `P0` recommendation can reverse on the full population. | **False as stated; fixed** by full-policy difference bounds and a memo warning (§7). |
| F2 | `v1.0.0` is release-ready under the project's own gate. | Check `V1/README.md` definition of done, `EXTERNAL_REVIEW.md`, and the validation report. | Two external readers are open; no external review log; `VALIDATION_REPORT.md` contradicted itself (65 vs 92 tests, wrong sweep design, CI pending vs pass, 32/32 vs 43/43). | **False; gate open.** The tag is a review tag. |
| F3 | Every "Measured" claim traces to a committed artifact. | Search `CLAIMS.md` for "Measured" claims with artifact references; check the vendor-review claim. | The 18-vendor capability matrix is not in the repository; the red-team Finding 4 already flagged it. | **False; downgraded** to a search-based limitation. |
| F4 | The validation report accurately describes the sweep. | Compare §5 to `configs/obs_sweep.yaml`, `reports/obs_sweep/pilot.json`, and the paper table. | It listed `e_approve ∈ {0.01, 0.05, 0.10, 0.50}` and `kappa_review ∈ {0.10, 0.50, 0.90}`; the actual grid is `{0.01, 0.05, 0.20, 0.50} × {0.50, 0.90, 1.00}`. | **False; corrected.** |
| F5 | The paper's contribution is novel enough for a main conference. | Compare to `RELATED_WORK.md` and the paper's own "not a new estimator" statement. | The methods are standard; the evidence is a simulation on one synthetic dataset; the strongest novel finding (point accuracy ≠ ranking) is a subsection. | **Weak; reposition** around decision reliability. |
| F6 | The business case is decision-grade. | Fill `p_wrong * L > C` with the committed numbers; compute the audit cost share. | `p_wrong=0.5` is illustrative, not derived; the 1% audit costs ~58% of the benchmark policy gap; the units are not pesos. | **False as a forecast; fixed** with a `p_wrong` range and the audit-cost arithmetic. |
| F7 | The case study demonstrates the product's central decision. | Inspect `configs/case_study.yaml` and `examples/case_log.csv`. | The case has one logging-rejected row; it isolates selection, not the reject margin. | **False for the central claim; disclosed** in `CASE_STUDY.md`. |
| F8 | The reject margin is the only unidentified quantity. | Check whether the full-policy decision can be bounded without identifying the reject margin. | The full-policy difference can be bounded per rejected row; the break-even is a sensitivity, not an estimate. | **Partially true; the decision direction can be bounded, the magnitude cannot.** |
| F9 | The benchmark is reproducible. | `scripts/prepare_baf.py --verify` against the recorded hash. | Exact SHA-256 match on the reference machine. | **True on the reference stack; not verified on another stack.** |
| F10 | The evidence is external. | Check the data source. | BAF is public synthetic; no partner log. | **False for external validity; already disclosed.** |

**What survives:** the identification discipline, the gate, the reproducible
benchmark, the recorded negative results, and the core finding that naive
evaluation can reverse a ranking. **What does not survive:** the claim that the
product answers the full-policy question, the claim that the release gate is met,
and the claim that every "Measured" claim has an artifact.

---

## 5.1 Artifact 4 — Counter-metric audit (Goodhart)

The project's credibility metrics can become proxies that are optimized while the
outcome they stand for stagnates. Pair each proxy with an orthogonal
counter-metric and a gate:

| Proxy the project optimizes | Counter-metric | Current evidence | Verdict |
|---|---|---|---|
| Test count and documentation volume | External reader engagement; real-log use | 0 external readers; no partner log | **Fails:** internal proxy improves, external outcome flat |
| "Every claim has an artifact" | Every **Measured** claim has a committed artifact | Vendor claim had none; fixed | **Partial:** one violation found |
| "Credibility" via recorded failures | A reviewer treats the failure as a strength, not a dismissal | No external reader has responded | **Unverified** |
| DR point accuracy | Ranking reliability and cost of misranking | 72% main; 58% `frej_050` | **Partial:** point accuracy ≠ ranking |
| Audit recommendation | Audit cost as a share of the policy value; operational feasibility | ~58% of the benchmark gap; no ops review | **Fails:** the audit may not be worth it |
| Bias-magnitude headline | Robustness to the baseline and the cost matrix | `frej_050` counterexample; unweighted baseline | **Fails:** the headline is a selected scenario |

**Gate:** do not report a proxy improvement without its counter-metric. A release
that improves tests and docs but has no external reader is not more credible; it
is more documented. A ranking claim without the cost curve is not robust; it is a
selected cell.

## 6. Findings, ranked

### C0 — Critical (independent pass): the headline ranking is a selected scenario

**Evidence:** `reports/pilot.json` `frej_050` (false-reject cost 0.50, 50
replications): naive P(select true best) **100%**, DR **58%**. `frej_002`:
naive **64%**, DR **68%**. Main: naive **0%**, DR **72%**. The naive point
estimate is still badly biased at `frej_050` (**+162.7% to +291.2%**, coverage
**0%**), so this is not a case where naive is accurate. `AUDIT_REPORT.md` line 40
already says "Naive is a weak baseline by construction; the relevant comparison
is DR vs IPW vs audit-only." `RESULTS.md` §5 previously said only "the
correction holds; the ranking is cost-sensitive" without the counterexample, and
the README and paper led with the main-scenario 0% ranking.

**Why it matters:** the headline "the naive evaluation would reject the better
policy" is **scenario-specific**. A hostile reviewer will find the committed JSON
and say the baseline is a straw man. The project's stronger and more honest
finding is the **decoupling**: a biased point estimate can preserve the ranking
(`frej_050`), and an accurate point estimate can lose it (DR 58%). That is a more
credible scientific contribution than the bias magnitude, and it is the result
the paper should lead with.

**Falsification test:** compare against an action-weighted or holdout incumbent
baseline; report the cost curve and both metrics. The `frej_050` counterexample
is the disconfirming test that already exists in the committed JSON.

**Action taken:** reported the counterexample in `RESULTS.md` §5, `CLAIMS.md`,
`README.md`, `ONE_PAGER.md`, `paper/main.tex`, `MODEL_CARD.md`, `THREATS.md`,
`BUSINESS_CASE.md`, and `AUDIT_REPORT.md`. The paper now states that the ranking
is cost-dependent; the business case no longer claims a factor of ten.

**Action-weighted baseline (tested).** The post-hoc action-weighted Hájek
baseline (`reports/baseline_sensitivity/`, 50 reps) has a maximum relative bias
of **2.9%** in the main scenario and **2.4%** at `frej_050`, but selects the true
best policy only **62%** and **58%** of the time. The naive baseline is
**278.5% / 0%** and **291.2% / 100%**. The point-estimate gap is not merely an
unweighted-mean artifact; the ranking effect survives a realistic baseline.

**Residual:** the baseline sensitivity is post-hoc and 50 replications, not
pre-registered, and a **holdout** baseline (rather than action weighting) is
still untested. Do not claim the naive gap is a market fact until a holdout
baseline is run.

### C1 — Critical: the product promises more than the estimand identifies

**Evidence:** the README's headline question is "if we change the policy, will it
catch more fraud without rejecting more good customers?" (`README.md` line 15).
The primary estimand is `P0`, the logging non-rejected population (`METHODS.md`
§2). The memo's recommendation is `P0`-conditional (`report.py` §2.1), and the
full-policy value is "not identified" in a later section. The case study has one
logging-rejected row, so it does not test the hard case.

**Why it matters:** the reject margin is exactly where "rejecting more good
customers" lives. A reader can act on the recommendation and never reach the
caveat. This is the highest-severity product defect: not a statistical error, a
decision-surface error.

**Falsification test:** construct a log where the `P0` ranking and the
full-policy ranking disagree; run the report. Before the fix, the memo
recommended the `P0` winner without a full-policy warning.

**Action taken:** `full_policy_difference` in `estimators.py`; memo §4.1 with the
full-policy difference bound, break-even rejected-fraud rate, reference rates,
and a warning when the `P0` recommendation does not survive. Tests in
`tests/test_estimators.py`. See §7.

**Independent-pass correction:** the first implementation of the new check
attributed a zero-crossing to the reject margin even when the reject margin could
not change the difference. A buyer would have collected the wrong data. The
independent pass caught it; the fix adds `reject_can_change` and returns
**"P0 inconclusive"** when the zero-crossing is `P0` uncertainty. There is a
regression test for the exact case.

**Residual:** the break-even assumes a common fraud rate among rejected rows. It
is a sensitivity, not an estimate. The memo says so; a reader can still misread
it.

### C2 — Critical: the release gate is open and the validation report contradicts itself

**Evidence:** `V1/README.md` definition of done requires two external readers;
`EXTERNAL_REVIEW.md` has no entries; `v1.0.0` is tagged. `VALIDATION_REPORT.md`
said 65 tests in §9 and 92 in §2; the sweep design was wrong; §2 said CI was
pending while §9 said pass; §3 said 32/32 claim checks while the current check is
43/43. `ONE_PAGER.md` said v0.2.1. `ROADMAP.md` said v1.0 was a December release
with unchecked items. The independent pass added: `CHANGELOG.md` said 35
headline numbers (43 now); `VALIDATION_REPORT.md` said `test_gates.py` had 7
tests (15); the README roadmap said public v1.0 was "Later"; `prepare_baf.py`
created a validation split but never used it while the paper said "validated on
3-4"; and the paper's "test labels never used for fitting" was true for the
policy scores but not for the cross-fitted nuisance outcome model.

**Why it matters:** the project's differentiator is that every claim is traceable
and the documentation is canonical. A validation report that contradicts itself
is a hostile reviewer's first dismissal. The tag also creates a credibility
question: why `1.0.0` before the gate?

**Falsification test:** read the validation report against the code and the
committed reports. It fails.

**Action taken:** corrected the validation report (test count, sweep design, CI
status, claim count, gate-test count); added `RELEASE_STATUS.md` and
`EXTERNAL_REVIEW.md`; updated README, ONE_PAGER, ROADMAP, V1/README,
V1/PROGRESS; corrected the CHANGELOG count and the README roadmap; made the
`prepare_baf.py` validation split's non-use explicit; and corrected the paper's
data-split and nuisance-model language. The tag is labeled a **review release**,
not an externally validated release. See §7.

**Residual:** the tag itself is immutable. If the author wants a clean public
release, create `v1.0.1` after external review; do not rewrite `v1.0.0`.

### C3 — Critical: the project is optimizing the non-binding constraint

**Evidence:** `DECISIONS.md` D13 says the binding constraint is a real log and a
risk-team sponsor, not code; D14 says the next move is the Level 2 package plus
outreach. Yet the post-D13 commits add a power calculator, temporal stability, a
case study, a post-stratified audit estimator, a decision layer, and a paper.
Those are real improvements, but the external-review log is still empty. The
`V1/PROGRESS.md` next actions were still "record F5 / update CLAIMS / run the
red team" after the tag.

**Why it matters:** more internal evidence has diminishing returns. The marginal
hour is better spent on a reviewer packet and a real-log conversation than on a
ninth scenario. This is the Theory of Constraints failure in the project's own
decision journal.

**Falsification test:** count external contacts and reviewer calls over the last
two weeks. If zero, the constraint is not being worked.

**Action taken:** added `EXTERNAL_REVIEW.md` with the packet, ten questions, and
the gate; updated V1/PROGRESS next actions to put the reviewer packet first;
added a stop rule against new estimators/scenarios before external review.

**Residual:** the author still owns the outreach. No document can substitute for
sending the packet.

### C4 — High: the scientific framing leads with the weakest claim

**Evidence:** `paper/main.tex` abstract leads with the 111.6–278.5% bias and the
7.8–538.5% sweep. The paper admits the contribution is "the applied measurement
layer, not a new estimator" (`RELATED_WORK.md` §3). The strongest finding — an
accurate point estimate can still choose the wrong policy (64% P(best) at low
`e`) — is a subsection. The new full-policy fragility result is not in the
paper's results. The independent pass also found: the abstract omits the 95%
Monte Carlo upper bound (**4.3–9.6%**) and keeps the weaker "mean at most 1.89%"
form; "validated on 3–4" is not supported by `prepare_baf.py` (the `val` split
is created but unused); and "test labels never used for fitting" is true for the
policy scores but not for the cross-fitted nuisance outcome model.

**Why it matters:** a main-conference reviewer will ask "what is new?" A
simulation on one synthetic dataset with standard estimators is a weak answer.
The decision-reliability finding is a stronger, more citable answer. The bias
magnitude is the most simulation-dependent number and the easiest to attack.

**Falsification test:** ask what a reviewer would cite the paper for. If the
answer is "the 111–278% bias on BAF," the paper is vulnerable. If the answer is
"the point-accuracy/ranking gap and the full-policy break-even," it is stronger.

**Action taken:** added the full-policy difference bound and break-even to the
paper's methods and practical rules; added the `frej_050` ranking counterexample
to the abstract and results; corrected the data-split and nuisance-model
language. This is a start, not a full rewrite.

**Recommendation:** re-center the paper on **decision reliability**: (a) ranking
reliability (P(best), cost of misranking, labels needed for correct selection);
(b) structural decision fragility (full-policy break-even); (c) audit value
conditional on the label mechanism. Target a workshop or a technical report
first; do not chase a main conference with the bias-magnitude framing.

### C5 — High: the buyer is ambiguous across three audiences

**Evidence:** `V1/VISION.md` §2 lists fintech fraud/KYC analytics, model risk,
risk committee/internal audit, regulatory/compliance, and research reviewers.
The README speaks to onboarding teams; the model card lists model risk, internal
audit, data science, and a policy owner; the paper speaks to researchers. The
business case is a bank decision, but the product surface is a CLI for an
analyst.

**Why it matters:** a flagship needs a beachhead. The strongest buyer is **model
risk / independent validation**: the process is mandated and recurring, the
buyer is independent of the model owner, the deliverable is a validation memo,
and the buyer can authorize a read-only historical extract. Fraud analytics is a
user and champion, not the budget holder. Researchers are a distribution channel,
not a buyer.

**Falsification test:** ask a fraud analytics lead and a model-risk lead who owns
the budget and the decision. The model-risk lead has the mandate and the
independence.

**Recommendation:** rewrite the one-pager and business case around "independent
validation of onboarding policy changes under selective and delayed labels."
Keep fraud analytics as the user. Add a buyer/decision-rights section. Align the
paper's regulatory relevance with the model-risk buyer.

### C6 — High: the business case is not decision-grade

**Evidence:** `BUSINESS_CASE.md` used `p_wrong=0.5` as an "illustrative
midpoint" while the project's naive P(best) is 0% in 11/12 cells; the 1% audit
costs ~58% of the benchmark policy gap; the cost units are not pesos. The
red-team Finding 6 remains open in `RED_TEAM_CREDIBILITY_PLAN.md`. The
independent pass recomputed the benchmark arithmetic: the true `P0` gap is
**0.000333** per application, so a 1M-application annual loss is **333**; a 1%
audit at `review_cost=0.02` is **~193**; with `p_wrong_naive=1.0` and
`p_wrong_pilot=0.28–0.36`, the net is **20–47** (13–40 if the audit is 1% of
all applications), not a factor of ten. The old
table used a 0.001 gap and a 50-unit cost, which are not benchmark-consistent;
the document contained both the factor-of-ten table and the 58% audit-cost
paragraph, which cannot both be right.

**Why it matters:** a risk committee will ask "what does it save?" The current
answer is a template. The audit cost can consume most of the value, which is a
reason to size the audit, not to skip it.

**Falsification test:** fill the template with the committed numbers. The net
value is ~10.7 units, not "10×." The `p_wrong=0.5` assumption is not conservative
relative to the benchmark's 0%.

**Action taken:** added a `p_wrong` range and break-even table, replaced the
illustrative factor-of-ten table with benchmark-consistent arithmetic, added the
cost-sensitivity counterexample, and added a "what the pilot must answer"
section. See §7.

**Residual:** the institution must supply `L`, `C`, and `p_wrong`. The document
is still a framework, but it is now honest about the arithmetic.

### C7 — High: the audit design does not identify the reject margin, and no compliant alternative is specified

**Evidence:** `AUDIT_DESIGN.md` §3.3 says the audit does not buy the reject
margin; §6 says a controlled approval design is required. D3 rejects random
approvals/rejections. The docs do not specify a compliant alternative.

**Why it matters:** the reject margin is the product's central unanswered
question. "Bounds or an assumption" is honest but not a design. A risk team will
ask what to do next.

**Falsification test:** ask a risk team "what do we do about the reject margin?"
If the answer is "bounds," the product is a measurement layer, not a decision
layer; if the answer is "run this design," the product has a path.

**Recommendation:** add a design note for **randomized review escalation** (not
random approval): a random subset of marginal applications gets enhanced
verification; those that clear are approved, yielding outcomes for a defined
marginal population. State exactly what it identifies (the fraud rate among
marginal applicants who clear enhanced review, not the full reject margin), the
legal/ethical caveats, and the cost. Test it in simulation before claiming it.
If it is not legally feasible, state that the reject margin is out of scope for
V1 and remove it from the promise.

### C7A — High: audit-only targets the logging-approved population, not the candidate's approved population

**Evidence:** `observation.py` draws audit labels from the logging-approved mask;
`pilot.py` computes `true_approved` on `logging.actions == "approve"`; the docs
said "approved population" without the qualifier. A candidate that changes who
is approved is outside the audit's target. The project's own earlier red-team
note already said this (`RED_TEAM_CREDIBILITY_PLAN.md` line 200), but the public
docs did not carry the qualifier.

**Why it matters:** a risk team may believe the audit validates the candidate's
approved set. It does not. The audit is a validation of the logging-approved
margin under the candidate policy's costs.

**Action taken:** qualified the target in `REPORT_USAGE.md`, `AUDIT_DESIGN.md`,
`METHODS.md`, `CLAIMS.md`, `RESULTS.md`, `ONE_PAGER.md`, `V1/README.md`,
`V1/VISION.md`, and `paper/main.tex`; added a target note to the memo.

**Residual:** a candidate-specific audit is a V1.1 design; do not claim it.

### C8 — High: a "Measured" claim has no artifact

**Evidence:** `CLAIMS.md` listed "Vendors sell replay/champion-challenger but not
selection/delay-aware policy evaluation" as **Measured (vendor review)** with an
"18-vendor capability matrix, 2026." The matrix is not in the repository; the
red-team Finding 4 flagged it.

**Why it matters:** this is a direct violation of the project's own rule. A
hostile reviewer only needs one "Measured" claim without an artifact to discount
the ledger.

**Falsification test:** search the repository for the matrix. It is absent.

**Action taken:** downgraded to a **Limitation** (search-based absence; the
review is not committed). See §7.

**Residual:** if the matrix exists in the archived origin repository, publish it
as an appendix; otherwise do not call the claim measured.

### C9 — Medium–high: regulatory precision can drift into overclaim

**Evidence:** `CLAIMS.md` said "BSP Circular 1213 mandates calibration, stress
testing, independent review/audit" without the FMS/MRM qualifier.
`BSP_MAPPING.md` §6 correctly says BSP 1213 is an FMS circular, not an MRM
circular, and the draft MRM is not binding. `OPEN_QUESTIONS.md` already asks
whether BSP 1213 is a model-risk circular and answers no.

**Why it matters:** a compliance reviewer who reads the claim ledger without the
mapping may think the project claims MRM compliance. The regulatory hook is a
strength only if it is precise.

**Falsification test:** read `CLAIMS.md` without `BSP_MAPPING.md`; ask whether it
overclaims. It can.

**Action taken:** added the FMS/MRM qualifier to the claim ledger. See §7.

### C10 — High: no fairness or inclusion diagnostic

**Evidence:** `SCHEMA.md` has `segment` and `region`; `OPEN_QUESTIONS.md` Q7 said
the pilot did not evaluate fairness; the README's promise includes "without
rejecting more good customers." The false-reject cost is the inclusion
parameter, and there was no segment-level result.

**Why it matters:** for a Philippine fintech flagship, inclusion is not a
side-issue. A policy can improve aggregate cost while rejecting more low-income
or thin-file applicants. A risk committee or regulator will ask for the segment
view.

**Falsification test:** ask the report for the false-reject rate by segment. It
now returns a descriptive table; the test is whether that table is enough for a
fairness claim. It is not, because rejected outcomes are unobserved.

**Action taken:** added a minimal observational segment table to the memo:
incumbent approve/review/reject counts, candidate reject and change shares,
observed fraud rate, and candidate false-reject share among observed legitimate
rows, with small-cell suppression. It is tested in `tests/test_report.py` and
labeled “not a fairness certification.” See §7.

**Residual:** a full fairness audit needs outcomes for the rejected margin; that
is a V1.1 experiment, not a reporting change.

**Recommendation:** add a minimal segment diagnostic to the report: approval and
review rates, observed fraud rates, and false-reject cost by segment, with
small-cell suppression and a clear "observational, not a fairness certification"
caveat. If that is too much for V1, narrow the public claim and add it to V1.1.
Do not claim the tool protects inclusion without evidence.

### C11 — Medium: the case study isolates the easy case

**Evidence:** `configs/case_study.yaml` uses `false_reject_cost=1000`, producing
one logging-rejected row in `examples/case_log.csv`. The case demonstrates
selection bias (the naive ranking flips), not the reject margin. The candidate
is an **oracle** (`scripts/make_case_study.py`: `p_true + N(0, 0.003)`), not a
model trained on pre-decision features; the docs said "true fraud probability +
noise" but the README and paper used the case as a headline.

**Why it matters:** the case is the "decision the tool changes" story. A reviewer
will notice it avoids the hard problem. The case is still useful, but it must be
labeled as the selection-only case.

**Falsification test:** count `action == "reject"` in the case log. It is one.

**Action taken:** disclosed the one-reject selection-only design and the oracle
candidate in `CASE_STUDY.md`, `README.md`, `ONE_PAGER.md`, and `paper/main.tex`.
See §7. A trained-model case is a V1.1 experiment; do not treat the oracle case
as evidence that a real challenger model wins.

**Recommendation:** add a second case with a material reject margin and a
fragile full-policy decision, or use the BAF pilot's reject share to illustrate
§4.1. The new full-policy check needs a flagship example.

### C12 — Medium: documentation drift and stale status

**Evidence:** `ONE_PAGER.md` said v0.2.1; many canonical docs said "v0.2.1
(2026-11-20)" while the tag is v1.0.0; `AUDIT_REPORT.md` says 27 headline
numbers while the current claim check has 43; `VALIDATION_REPORT.md` had the
wrong sweep design and test counts; `README.md` said 92 tests after the tree had
already grown beyond the tagged count; `MODEL_CARD.md` carried the older
1,627.90% outcome-dependent DR figure without distinguishing oracle from
estimated `e`.

**Why it matters:** the project's brand is traceability. Drift is not cosmetic;
it is the failure mode the project claims to prevent.

**Falsification test:** run a status/version/claim-count check across the docs.
It fails in multiple places.

**Action taken:** corrected the visible release docs and test counts; added
`RELEASE_STATUS.md` as the single source of release truth; updated the canonical
status headers; distinguished oracle `e` (DR 1,301.5%) from estimated `e` (DR
1,737.0%) in the model card. See §7.

**Recommendation:** add a lightweight `scripts/check_docs_consistency.py` to CI:
version strings agree; README status matches the tag; no "v0.2.1" in current
docs; no stale test/claim counts. Do not add more docs without a reader.

### C13 — Medium: paper artifacts are stale or unportable

**Evidence:** `paper/main.pdf` was not rebuilt after the `main.tex` changes;
`REFERENCES.md` pointed the annotated bibliography at
`D:\delayed-label-fraud-decisioning\...` (removed in this pass); several 2026
citations are marked **verify** but appear in `RELATED_WORK.md`.
`paper/README.md` says the draft cites only verified entries; that needs a check.

**Why it matters:** a reviewer who cannot compile or verify the paper will
discount the research contribution. A private path in a public doc is a
reproducibility defect.

**Falsification test:** open `paper/main.pdf` and compare to `main.tex`; search
for `D:\` in public docs. It fails.

**Action taken:** removed the private path; added a build-status note to
`paper/README.md`. **Residual:** rebuild the PDF with the venue's toolchain;
verify or remove the 2026 citations before submission.

### C14 — Low for V1: no monitoring/change-control artifact

**Evidence:** `MODEL_CARD.md` §10 lists monitoring; there is no `monitor`
command or time-series report. This is a Level 4 adoption requirement, not a V1
requirement.

**Recommendation:** keep it in the V1.1 roadmap; do not build it before the
external review.

### C15 — Low: "audit-ready" can be read as an audit opinion

**Evidence:** the README says "audit-ready evaluation"; the model card says the
tool is not a legal/compliance certification. The phrase is doing more work than
the artifact supports.

**Recommendation:** add one line to the README: "audit-ready means the memo
exposes its evidence and assumptions; it is not an audit opinion or a compliance
certification." Do not rename the project.

---

## 7. What changed in this pass

The review is not only a document. The following changes are in the working tree
and are verified by tests.

### 7.1 Product: full-policy decision check

- `src/onboarding_audit/estimators.py`: new `full_policy_difference`.
  For each logging-rejected row, it evaluates the candidate and incumbent costs
  at `Y=0` and `Y=1`, bounds the mean difference by the per-row minima/maxima,
  and solves the break-even rejected-fraud rate under a common-rate assumption.
- `compare_policies` now returns `full_policy` in its output, including the
  `P0` difference, reject share, full difference bounds, break-even, and a
  decision label.
- `report.py`:
  - the comparison table now labels the recommendation **`P0`-conditional** and
    adds a **full-policy decision** row;
  - a warning is printed when a directional `P0` recommendation does not survive
    the reject margin, or when the full-policy bound favors the opposite policy;
  - new memo §4.1 with the full-policy difference, interpretation, break-even,
    reference fraud rates, and method caveat;
  - the claim ledger adds "Full-policy difference (candidate − incumbent)" with
    a derived status;
  - diagnostics now report observed review and approved fraud rates.
- The independent pass found that the first implementation attributed a
  zero-crossing to the reject margin even when the reject margin could not change
  the difference. The fix adds `reject_can_change` and returns **"P0
  inconclusive"** when the zero-crossing is `P0` uncertainty.
- `tests/test_estimators.py`: seven new tests (break-even arithmetic, no-rejected
  rows, candidate-rejects-all, P0-only uncertainty, small nonzero reject range,
  all-rejected population, integration through `compare_policies`).
- The independent code review found and we fixed further issues: §4.1 now
  respects the identification gate; the attribution test now requires the reject
  margin to flip the sign at the `P0` point estimate, not merely move the
  magnitude; the no-reject decision uses the same one-sided 95% rule as the
  `P0` recommendation; an all-rejected log returns its valid bound instead of
  withholding it; the out-of-range break-even memo text no longer claims the
  sharp bounds decide the direction; the claim-ledger vocabulary covers the
  no-reject decisions; and a missing `P0` standard error is withheld rather than
  treated as zero.

**Verification:** `pytest -q` → **106 passed**. The demo memo was regenerated and
inspected; the material-reject example shows the `P0` recommendation and the
full-policy decision diverging, with the warning printed.

### 7.3 Independent-pass corrections (scientific claims)

- **Ranking counterexample.** `RESULTS.md` §5 now reports `frej_050` naive
  P(best) **100%** vs DR **58%** and the `frej_002`/main values. `CLAIMS.md`
  adds a negative-result row and an interpretation point. `README.md`,
  `ONE_PAGER.md`, `paper/main.tex`, `MODEL_CARD.md`, `THREATS.md`,
  `BUSINESS_CASE.md`, and `AUDIT_REPORT.md` now state that the ranking is
  cost-dependent.
- **Audit target.** The audit-only target is qualified as the
  **logging-approved** population in `REPORT_USAGE.md`, `AUDIT_DESIGN.md`,
  `METHODS.md`, `CLAIMS.md`, `RESULTS.md`, `ONE_PAGER.md`, `V1/README.md`,
  `V1/VISION.md`, and `paper/main.tex`; the memo target note says the same.
- **Case study.** `CASE_STUDY.md`, `README.md`, `ONE_PAGER.md`, and
  `paper/main.tex` now label the candidate as a synthetic oracle, not a trained
  model.
- **Business case.** Replaced the factor-of-ten template with
  benchmark-consistent arithmetic (net **20–47** at `p_wrong_naive=1.0`,
  negative at 0.5) and added the cost-sensitivity counterexample.
- **Action-weighted baseline.** Added `action_weighted` to the pilot and
  `configs/baseline_sensitivity.yaml`; ran main + `frej_050` (50 reps). Main:
  naive 278.5% / 0% vs action-weighted 2.9% / 62%; `frej_050`: naive 291.2% /
  100% vs action-weighted 2.4% / 58%. The point-estimate gap survives action
  weighting; the ranking effect survives a realistic baseline.
- **Fairness.** Added an observational segment table to the memo with
  small-cell suppression, and labeled it “not a fairness certification.”
- **Paper precision.** Corrected "validated on 3–4" to "held out but not used
  for selection in this reproduction"; corrected "test labels never used for
  fitting" to distinguish the policy scores from the cross-fitted nuisance
  outcome model; added the `frej_050` counterexample to the abstract and
  results.
- **Documentation.** Corrected `CHANGELOG.md` (35 at the tag, 43 now),
  `VALIDATION_REPORT.md` (`test_gates.py` 15 tests), the README roadmap, the
  canonical doc status headers, and the `prepare_baf.py` validation-split
  comment; removed the private `D:\...` bibliography path.

### 7.2 Claims and release integrity

- `CLAIMS.md`: the vendor-review claim is downgraded from **Measured** to
  **Limitation**; BSP 1213 is qualified as an FMS circular; the full-policy
  check is added as a mechanism claim.
- `VALIDATION_REPORT.md`: corrected the sweep grid, test counts, claim-check
  count, CI status, and the external-review status.
- `RELEASE_STATUS.md`: new; states what is tagged, what is not, and the open
  public-release gate.
- `EXTERNAL_REVIEW.md`: new; the reviewer packet, ten questions, log, and gate.
- `README.md`, `ONE_PAGER.md`, `ROADMAP.md`, `V1/README.md`, `V1/PROGRESS.md`,
  `V1/VISION.md`: updated to the review-release status, test count, and the
  full-policy check.
- `BUSINESS_CASE.md`: added the `p_wrong` range, audit-cost arithmetic, and the
  pilot decision questions.
- `METHODS.md`, `TECHNICAL_NOTE.md`, `REPORT_USAGE.md`, `ARCHITECTURE.md`,
  `CASE_STUDY.md`: documented the full-policy check and the case-study scope.
- `paper/main.tex`: added the full-policy bound to the decision layer and the
  practical rules; updated the abstract.

**Not changed:** no new estimator, no new simulation scenario, no tag move. The
full-policy check is a post-tag change and should be released as `v1.0.1` or
folded into `v1.1`.

---

## 8. Strategic repositioning

### 8.1 Beachhead buyer: model risk / independent validation

The buyer is not the fraud analytics team. The buyer is the **model-risk or
internal-audit function** that must independently validate a policy change before
a risk committee approves it. Why:

- the process is mandated and recurring (BSP 1213 calibration/independent review;
  the draft MRM; NPC explainability);
- the buyer is independent of the model owner, so the tool's refusal to overclaim
  is a feature, not a nuisance;
- the deliverable is a validation memo, which the project already produces;
- the buyer can authorize a read-only historical extract without a production
  change;
- the buyer's alternative is a vendor backtest or an internal spreadsheet, both
  of which have the selection problem the project measures.

Fraud analytics is the **user** and **champion**. The research reviewer is a
**distribution channel**. Do not try to sell to all three at once.

### 8.2 Promise

Replace the full-population promise with a decision-reliability promise:

> **On the population the log can identify, the tool estimates the policy value,
> bounds the full-policy difference over the reject margin, and tells you whether
> the decision survives the unobserved reject margin. It refuses to print a point
> estimate when the log cannot support one.**

This is narrower, true, and still valuable. It does not claim to answer the full
question; it tells the buyer what would have to be true for the decision to hold.

### 8.3 Evidence ladder

| Tier | Evidence | Current | Next |
|---|---|---|---|
| E0 | Assertion | — | — |
| E1 | Code/demo inspection | Pass | — |
| E2 | Simulation with known truth | Pass (V1) | — |
| E3 | External real-world data or review | **Open** | Two readers; a real-log pilot |
| E4 | Independent replication | Not claimed | A second team reproduces the result |

The next unit of effort should buy **E3**, not another E2 scenario. A single
external reader is worth more than a tenth scenario.

### 8.4 Paper strategy

Re-center on **decision reliability**, not bias magnitude:

1. **Ranking reliability.** An accurate point estimate can still choose the wrong
   policy: 64% P(best) at low `e`, 0% naive. This is the most novel and
   practitioner-relevant result.
2. **Structural decision fragility.** The reject margin can reverse the `P0`
   recommendation. The full-policy difference bound and break-even make that
   explicit. This is a new decision-theoretic contribution.
3. **Audit value is conditional.** The audit is modest in the main scenario and
   the only approximately unbiased option under outcome-dependent labels. This is
   a practical rule, not a universal fix.

Target a workshop or a technical report first. A main-conference paper needs
either a sharper theoretical result or a real dataset; the current simulation is
a strong workshop/technical-report contribution, not a main-conference one.

### 8.5 Release strategy

| Version | Content | Gate |
|---|---|---|
| `v1.0.0` (tagged) | Review release: estimators, gate, bounds, sweep, case study, docs | Passed for review; external gate open |
| `v1.0.1` | Full-policy decision check; doc consistency fixes | Tests, claim checks, link check |
| `v1.1` | External review responses; real-log pilot or a documented fallback; fairness diagnostic | Two external readers or a documented fallback |
| Public `1.0` | After `v1.1`; no external gate exceptions | The public-release gate in `RELEASE_STATUS.md` |

Do not call the tag a public release. Do not add features to `v1.0.0` silently.

---

## 9. Release gate

### Must fix before a public release

1. **Baseline and ranking claim.** The action-weighted baseline is run and
   reported (`RESULTS.md` §5.1); narrow the ranking claim to "cost-dependent."
   Run a **holdout** incumbent baseline before the public release; if it collapses
   the gap, rewrite the headline.
2. **External review.** Two readers (or a documented fallback) recorded in
   `EXTERNAL_REVIEW.md`.
3. **Release integrity.** The validation report, claim ledger, README, one-pager,
   and version files agree; the tag is labeled a review tag.
4. **Product-decision surface.** The full-policy check is the default reading;
   the memo warns when the `P0` recommendation does not survive.
5. **Claim integrity.** No "Measured" claim without a committed artifact; the
   vendor claim is a limitation.
6. **Fairness.** The minimal segment diagnostic is implemented; a full fairness
   audit with rejected outcomes remains a V1.1 requirement.
7. **Paper artifacts.** Rebuild the PDF; verify the 2026 citations; add the
   MC upper bound to the abstract.

### Should fix before the next review

7. Reposition the one-pager and business case around the model-risk buyer.
8. Add the reviewer packet and a 10-person shortlist.
9. Add a monitoring/change-control section for V1.1.
10. Add a second case with a material reject margin.

### Defer

- FiFAR capacity/analyst layer.
- A second dataset or transaction-fraud extension.
- Bootstrap/randomization-inference intervals.
- A dashboard, API, or production integration.
- A main-conference submission with the current framing.

### Kill criteria

- **No external reader by 2026-12-15:** the public release slips; do not tag a
  public `1.0`.
- **A reviewer finds a false "Measured" claim:** fix it before any release.
- **The full-policy check reverses the `P0` recommendation in the flagship case:**
  rewrite the headline and the case study, do not explain it away.
- **The paper is rejected at the workshop:** narrow to a technical report; do not
  chase a main conference with the same framing.
- **The fairness diagnostic shows a material disparate false-reject rate:** the
  tool must report it and the policy recommendation must be reconsidered; do not
  ship an aggregate-only claim.

---

## 10. Reasoning check

**Claim and tier.** The review's central claim — "V1 is a strong Level 2 artifact
but not ready for a public flagship release; the binding constraint is external
evidence and buyer clarity" — is **derived** from the repository's own decision
journal, release gate, validation report, and the constructed full-policy test.
The product defect is **observed** in a constructed log. The `frej_050` ranking
counterexample is **derived** from the committed JSON. The "straw-man baseline"
critique is **partly tested**: an action-weighted baseline has been run
(post-hoc, 50 reps) and the point-estimate gap survives (naive 278.5% vs 2.9%),
so the bias is not merely an unweighted-mean artifact. A **holdout** baseline
has not been run. The paper's novelty judgment is **inferred** from
the related-work map and the paper's own framing; it is not a peer-review
outcome. The fairness gap is **observed** (no segment output), but its severity
is **assumed** from the Philippine inclusion context.

**Strongest counter-case.** The project is already stronger than most student
fintech projects; the tag is a review tag, the limitations are documented, and
the external review is scheduled for December. A reviewer might say the review is
too harsh: the project explicitly does not claim production or causal effects, so
the `P0`/reject-margin gap is disclosed, not hidden. The counter-case is partly
right. The response is that disclosure is not enough when the decision surface
recommends a policy and the buyer's question includes rejects; the full-policy
check and the memo warning are the minimum fix. The release gate remains the
harder issue: a `1.0.0` tag before the gate is a credibility risk regardless of
the disclosures.

The stronger counter-case is C0: the headline ranking is a comparison to an
unweighted labeled mean, and at `frej_050` the naive rule ranks correctly while
DR does not. The action-weighted baseline did **not** collapse the main-scenario
gap (naive 278.5% vs 2.9%), so the point-estimate premise survives a realistic
action-weighted backtest. A **holdout** baseline could still collapse it; that
test has not been run. The review treats the gap as measured under the stated
baselines, not as a market fact.

**Not verified.** No external reader has been asked; no risk team has been
interviewed; no partner log exists; the paper has not been peer-reviewed; the
PDF was not rebuilt in this environment (no TeX toolchain); the benchmark hash
was not re-run on another stack; the fairness severity is inferred, not measured.
Any of these could change the priority order. A risk team saying "the reject
margin does not matter for our decision" would weaken C1; a reviewer saying "the
ranking result is enough for a workshop" would strengthen C4's path. The
action-weighted baseline **was** run and the gap survived; a **holdout** baseline
was not run. If a holdout baseline collapses the naive gap, C0 becomes the
headline correction and the product's premise must be narrowed. The `frej_050`
counterexample is from 50 replications; its Wilson interval is not reported here,
so the 100%-vs-58% contrast is directionally clear but not precision-estimated.

**Next action.** The action-weighted baseline is run (`RESULTS.md` §5.1); run a
**holdout** baseline as the next falsification test. If the naive gap collapses,
rewrite the headline before any release. Send the reviewer packet in
`EXTERNAL_REVIEW.md` to 10 targeted
practitioners and researchers; record every objection; fix or narrow the
critical/high findings; release the full-policy check as `v1.0.1`. Stop adding
methods or scenarios until the external log has entries. The stop condition is
the public-release gate in `RELEASE_STATUS.md`, not a feeling of completeness.

---

## Appendix A — Independent red-team pass

*The independent pass was run as a separate adversarial review of the repository.
Its findings are summarized here; where it disagreed with the author-led review,
the disagreement is recorded rather than smoothed.*

*(See the red-team findings below. The pass is independent in the sense that it
was run by a separate agent with a fresh context and an instruction to disprove
the release, not to confirm it. It is not a human external reviewer; the
`EXTERNAL_REVIEW.md` gate remains open.)*

### A.1 Verdict and scope

The independent pass returned **FAIL for public flagship release**. It was a
separate agent with a fresh context and an instruction to disprove the release,
not to confirm it. It is not a human external reviewer; the
[`EXTERNAL_REVIEW.md`](EXTERNAL_REVIEW.md) gate remains open.

### A.2 What it found that the author-led review missed

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 1 | The naive ranking is a selected scenario: `frej_050` naive P(best) **100%**, DR **58%**, while naive remains biased. The headline 0% is main-scenario only. | Critical | `reports/pilot.json`; `RESULTS.md` §5 | Added C0; corrected RESULTS, CLAIMS, README, paper, business case |
| 2 | The first full-policy check attributed `P0` uncertainty to the reject margin. | Critical (product correctness) | `estimators.py`; demo JSON | Fixed with `reject_can_change`; regression test |
| 3 | Audit-only targets the logging-approved population, not the candidate's approved population. | High | `observation.py`/`pilot.py`; docs | Qualified the target across docs and paper |
| 4 | The case-study candidate is an oracle, not a trained model. | High | `scripts/make_case_study.py` | Labeled as an oracle; trained-model case deferred |
| 5 | Release package contradictions: CHANGELOG 35 vs 43; `test_gates.py` 7 vs 15; README roadmap; `val` split unused; test-label nuisance model. | High | docs/scripts | Corrected |
| 6 | The business case's factor-of-ten table contradicts its own benchmark arithmetic. | High | `BUSINESS_CASE.md` | Replaced with benchmark-consistent arithmetic |
| 7 | The paper's abstract omits the MC upper bound and overstates "validated on 3–4" / "test labels never used for fitting." | High | `paper/main.tex`; `prepare_baf.py` | Corrected the data-split/nuisance language and added the MC bound |

### A.3 Where it was right, and where it overstated

**Right:** the `frej_050` counterexample; the full-policy bug; the audit target;
the case-study oracle; the release contradictions; the business-case arithmetic.

**Overstated:** "the naive baseline is a straw man." It is a weak baseline, but
the main-scenario bias is real and the project's own audit report already labels
it as weak. The correct reading is **selected scenario**, not fabricated. The
point-estimate bias is robust across the cost sweep; only the ranking claim is
cost-dependent.

**Overstated:** "the case study is rigged." It is an oracle by construction and
is now labeled. The main BAF benchmark uses trained models, so the paper's
primary evidence is not an oracle.

**Overstated:** "the tag's demo is stale." The demo is generated and untracked;
the release notes describe the code path. The review-status page now makes the
tag explicit.

**Not adjudicated:** the paper's venue fit. No peer review was run; the
recommendation (workshop/technical report first) is inferred, not observed.

### A.4 What it confirmed

- The release gate is open; the tag is a review tag.
- The binding constraint is external evidence, not code.
- The buyer is ambiguous; model risk is the strongest beachhead.
- The paper's framing is a rejection risk.
- The business case is not decision-grade.
- The identification discipline, gate, reproducibility, and recorded negative
  results are genuine assets.

### A.5 Residual disagreement

The independent pass says the headline bias is "a comparison to a deliberately
wrong estimator." The author-led review says the bias is real but the ranking
claim is scenario-specific. The difference matters: if the naive baseline is a
straw man, the product's premise is weaker; if it is a weak-but-real baseline,
the point-estimate correction is still valuable.

The falsification test was an **action-weighted or holdout incumbent baseline**.
The action-weighted version has been run: the point-estimate gap survives
(naive 278.5% vs 2.9%), and the ranking effect survives (`frej_050`: naive 100%
vs action-weighted 58%). A **holdout** baseline remains untested. The review
therefore treats the point-estimate bias as measured under the unweighted and
action-weighted baselines, not as a market fact. The holdout test is the single
most important open question for V1.1.

## Appendix B — Evidence map

| Finding | Primary evidence |
|---|---|
| C1 product promise | `README.md` line 15; `METHODS.md` §2; `report.py` §2.1; `CASE_STUDY.md` |
| C2 release gate | `V1/README.md` §7; `VALIDATION_REPORT.md`; `git tag`; `ONE_PAGER.md` |
| C3 binding constraint | `DECISIONS.md` D13/D14; `V1/PROGRESS.md`; commit history |
| C4 paper framing | `paper/main.tex` abstract/introduction; `RELATED_WORK.md` §3 |
| C5 buyer ambiguity | `V1/VISION.md` §2; `MODEL_CARD.md` §2; `README.md` |
| C6 business case | `BUSINESS_CASE.md` §4; `RED_TEAM_CREDIBILITY_PLAN.md` Finding 6 |
| C7 audit design | `AUDIT_DESIGN.md` §3.3, §6; `DECISIONS.md` D3 |
| C8 vendor claim | `CLAIMS.md` vendor row; `RED_TEAM_CREDIBILITY_PLAN.md` Finding 4 |
| C9 regulatory precision | `CLAIMS.md`; `BSP_MAPPING.md` §6; `OPEN_QUESTIONS.md` |
| C10 fairness | `SCHEMA.md`; `OPEN_QUESTIONS.md` Q7; `MODEL_CARD.md` |
| C11 case study | `configs/case_study.yaml`; `examples/case_log.csv` |
| C12 documentation drift | `ONE_PAGER.md`; `VALIDATION_REPORT.md`; `AUDIT_REPORT.md`; `README.md` |
| C13 paper artifacts | `paper/README.md`; `REFERENCES.md` §10 |
