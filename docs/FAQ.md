# FAQ

**Status:** Canonical question bank for v0.2.1 (2026-11-20).
**Purpose:** Answer the questions a practitioner, a researcher, or an interviewer
will actually ask, with links to the canonical document instead of a new claim.

---

## For a practitioner

### What problem does this solve?

Your onboarding policy decides who is approved, reviewed, or rejected. Those
decisions determine which fraud outcomes you ever observe. A naive backtest on
the labeled subset answers "how did the old policy's labels look?", not "what
would the new policy do?" This project gives you the estimand, the estimators,
the diagnostics, the audit design, and the memo to answer the second question.

Start with [`PROBLEM.md`](PROBLEM.md) and [`REPORT_USAGE.md`](REPORT_USAGE.md).

### What do I need to run it?

A decision log with one row per application: `application_id`, `action`, `score`,
`amount`, `label`, `label_time`, and preferably `reviewed`, `audit_flag`,
`propensity`, `label_source`, and numeric features. A candidate score file with
one row per application. See [`SCHEMA.md`](SCHEMA.md).

### I don't have per-row propensities. Can I still use it?

Yes. The report estimates an action-level propensity from the log's review and
audit rates. If observation depends on application features, use
`--propensity-model covariate` with numeric features. The memo labels the source
as `estimated` or `estimated_covariate`; it never hides that the propensities
are estimated. See [`REPORT_USAGE.md`](REPORT_USAGE.md) §3.

### I don't have an audit. What happens?

The report still runs, but `audit_only` is `n/a`, and the approved-population
validation is weaker. The action-level or covariate propensity is estimated from
the review/approve channels. If the label-source mix suggests outcome-dependent
observation, a point estimate is not defensible without an audit. See
[`AUDIT_DESIGN.md`](AUDIT_DESIGN.md).

### What does the memo tell me?

The target population, the estimate or bounds, the propensity source, overlap and
ESS, the weight distribution, the label-source mix, the label delay, the
reject-margin bounds, an audit recommendation, a measured/assumed/unverifiable
ledger, and what would change the estimate. See [`MEMO_TEMPLATE.md`](MEMO_TEMPLATE.md).

### How many audit labels do I need?

It depends on the decision's effect size. At a 1.26% fraud rate, a 20% relative
standard error on the fraud rate needs about 1,959 labels; 10% needs about 7,835;
5% needs about 31,340. For a 10% relative difference between two policies at 80%
power, you need roughly 117,000 labels per group. A generic 1% audit is not sized
to detect small differences. See [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md) §4.

### Can I randomize approvals or rejections?

No, not as a default. Random approval of would-be-rejected applicants
deliberately onboards fraud; random rejection of would-be-approved applicants
deliberately excludes legitimate customers. Use random post-hoc verification of
approved applications and shadow scoring. Any other design needs legal/risk
approval. See [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md) §2 and
[`BSP_MAPPING.md`](BSP_MAPPING.md) §4.

### Can I use it for transaction fraud?

The estimator layer is general, but the schema, the audit design, and the
benchmark are account-opening specific. A transaction-fraud application needs a
different unit of analysis, different label delays, and a different action set.
The project does not claim transaction-fraud validity. See
[`THREATS.md`](THREATS.md) §3.

### Is this legal/compliant?

It is a measurement and documentation layer, not legal advice. The schema
extends BSP 1213's 11-field floor; the audit design respects the constraint
against random holds/approvals; the memo supports NPC explainability and
human-intervention documentation. Your compliance and legal teams must review
the actual design. See [`BSP_MAPPING.md`](BSP_MAPPING.md).

### What if my candidate policy reviews applications the incumbent never reviewed?

The log cannot identify that region without an audit or a model assumption. The
memo reports the count of candidate review/approve actions outside `P0`, the
overlap, and the bounds. If the count is material, do not report a point
estimate; run shadow scoring or an audit. See [`REPORT_USAGE.md`](REPORT_USAGE.md) §4.

### What if my labels are delayed?

A label that has not arrived by the cutoff is unresolved, not negative. The
report shows the label-delay distribution and the resolution diagnostics. The
pilot tests delays from 0.5 to 90 days; the correction holds, but precision
falls. See [`PILOT_SPEC.md`](PILOT_SPEC.md) and [`RESULTS.md`](RESULTS.md).

### What if my log has no outcome for rejected applications?

That is the normal case. The primary estimand is `P0`, the logging non-rejected
population. The rejected rows enter only the full-population bounds. Do not
report a point estimate for the full population when the reject margin is
material. See [`METHODS.md`](METHODS.md) §2–3.

### How do I interpret the bounds?

They are **partial-identification intervals conditional on the `P0` estimate**,
not confidence intervals. The width is the cost of not observing the reject
margin. The incumbent's narrow interval covers the true full value only 34% of
the time in the pilot; that is a diagnostic, not a guarantee. See
[`THREATS.md`](THREATS.md) §4.

### What is the biggest practical risk?

Using the tool as a point-estimate machine. The tool is useful only if the
observation model, the overlap, the weight diagnostics, and the reject margin are
read together. A confident-looking memo with a failed positivity check or a
34% bounds coverage is not a decision. See [`THREATS.md`](THREATS.md).

---

## For a researcher

### What is the estimand?

The primary estimand is the policy value on the logging non-rejected population:
`V_P0(pi) = E[C(pi(X), Y) | i in P0]`. The approved population and the full
population are secondary. See [`METHODS.md`](METHODS.md) §2.

### Why `P0`, not the full population?

`P0` is the part the log identifies under positivity and no unmeasured
confounding of observation. The reject margin has no outcome; a point estimate
would require an assumption or a controlled approval design. Reporting `P0` plus
bounds is more honest than pretending the full population is identified.

### What are the identification assumptions?

Consistency, positivity, no unmeasured confounding of observation, a correct
observation model, a stable cost model, and no interference/anticipation. See
[`METHODS.md`](METHODS.md) §3.

### Why DR? Why does IPW fail?

DR is consistent if either the outcome model or the propensity model is correct.
IPW relies entirely on the propensity. In the pilot, action-level IPW is fragile
when `e` is estimated (2.92% bias, 92% coverage) and fails under
covariate-dependent observation (67.52% bias, 1.5% coverage). Action-level DR is
better but still fails under covariate dependence (21.25% bias, 72.5% coverage);
the fitted covariate model recovers the oracle (1.97–3.68%). See
[`RESULTS.md`](RESULTS.md) and [`CLAIMS.md`](CLAIMS.md).

### Why did DR fail under covariate-dependent observation?

DR is consistent if either the outcome model or the propensity model is correct,
but that is a theoretical property, not a finite-sample guarantee. In the
covariate stress test, the outcome model included log amount, yet action-level DR
was still **21.25%** biased (20.27% with the delay). The observation gradient was
strong enough that the residual correction did not absorb it. The fitted
covariate propensity model directly targets the observation mechanism and
recovers the oracle (**1.97–3.68%**). The lesson: check the observation-rate
gradient and use the covariate model when it is present; do not treat DR as
universal immunity.

### What is new here?

The applied measurement layer: an account-opening estimand under policy-induced
selection, delayed/censored labels, capacity-constrained review, a compliant
audit design, a logging schema that extends BSP 1213, and an open-source
benchmark/tool. The estimators are standard; the contribution is the assembly,
the identification discipline, and the audit-ready artifact. See
[`RELATED_WORK.md`](RELATED_WORK.md).

### What is the closest work?

Pombal et al. (2022) on selective labels/performative prediction in
account-opening fraud; the reject-inference literature; the OPE literature; and
the 2026 ICAIF work on selective/delayed labels in finance (OSCAR, Beyond Holdout
Error, DOiT, Top-K Review, Alert-Feedback Trap). See
[`RELATED_WORK.md`](RELATED_WORK.md).

### What would falsify the claim?

A realistic observation mechanism where the naive bias is negligible and no
ranking flips; estimated or covariate propensities that remove the correction's
advantage; bounds so wide that no decision is supported; or an audit design that
is legally/operationally infeasible. See [`THREATS.md`](THREATS.md) §6.

### Why is the naive bias positive?

The labeled subset is dominated by reviewed/rejected applications with non-zero
costs, and approved fraud is more likely to be labeled than approved legitimate
accounts. The naive mean therefore overstates cost. The direction is not
universal: it depends on the action mix and the cost matrix. The practical harm
is that it reverses the better-model/incumbent ranking. See
[`CLAIMS.md`](CLAIMS.md) §Interpretation.

### Why is the audit not a universal fix?

At a 5% approved-label base rate, a 1% audit mainly validates the approved
margin and improves ESS; the marginal RMSE gain is modest. It becomes the only
approximately unbiased option when approved fraud is more likely to be labeled
than approved legitimate accounts, though its interval is still undercovered
(80–86%). See [`RESULTS.md`](RESULTS.md) §4.

### What about fairness?

The schema has `segment` and `region` fields, but the pilot does not evaluate
fairness. A false-reject cost is an inclusion parameter; the memo reports the
false-reject rate, but a full fairness audit is future work. See
[`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md).

### What about performativity?

A deployed policy changes fraudster and customer behavior. The project estimates
policy value under a stated observation model; it does not claim a causal
deployment effect. Pombal et al. is the closest work on performativity. See
[`THREATS.md`](THREATS.md) §3 and [`RELATED_WORK.md`](RELATED_WORK.md).

### What about the cost matrix?

It is a normalized assumption, sensitivity-tested across false-reject costs
0.02–0.50 and audit/capacity/delay sweeps. It is not a production estimate. See
[`DECISIONS.md`](DECISIONS.md) D4 and [`RESULTS.md`](RESULTS.md) §5.

### Why does the bounds coverage say 34%?

Because the bounds are conditional on the noisy `P0` estimate and the unobserved
cost can fall outside the assumed min/max range. The 34% is a diagnostic that
the narrow interval is not a 95% confidence interval. Report the bounds as
bounds. See [`THREATS.md`](THREATS.md) §4.

---

## For an interviewer

### 60-second pitch

A fintech onboarding team wants to know whether a new approve/review/reject
policy will catch more fraud without rejecting more good customers. The only
labels they have were selected by the current policy. I formalize the problem,
separate the identifiable `P0` margin from the unobserved reject margin, and test
naive, IPW, DR, audit-only, and bounds on the public BAF account-opening
benchmark. The naive evaluation overstates cost by 112–278% and would reject the
better model; DR recovers the identified value within 0.94% with 96% coverage.
The artifact is an open-source logging schema, audit design, and audit-ready
memo mapped to BSP 1170/1213 and AFASA.

### What did you build?

A Python package and CLI (`pilot`, `report`, `sensitivity`, `validate`), a
decision-log schema, a schema validator, a simulation benchmark with known ground
truth, an audit designer, and a memo generator. See [`ARCHITECTURE.md`](ARCHITECTURE.md).

### What did you find?

The premise is real; the correction works on `P0`; the reject margin needs
bounds; the audit is the only approximately unbiased option under outcome-dependent labels but not a universal
fix; both DR and IPW survive estimated action-level propensities, and DR is
better under noise; under
covariate-dependent observation, action-level IPW and DR both fail, and the
fitted covariate propensity model recovers the oracle. See
[`RESULTS.md`](RESULTS.md).

### What is the hardest part?

The identification discipline: deciding what is measured, what is assumed, and
what is unverifiable, and refusing to report a point estimate for the reject
margin. The code is not the hard part; the honesty is. See
[`THREATS.md`](THREATS.md).

### What would you do next?

Finalize the documentation, get two external readers, add the FiFAR capacity
layer, add a bootstrap/randomization-inference interval, and seek a bank partner
for a real log. See [`ROADMAP.md`](ROADMAP.md) and
[`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md).

---

## Related documents

- Problem: [`PROBLEM.md`](PROBLEM.md)
- Methods: [`METHODS.md`](METHODS.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Claims: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
- Audit design: [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md)
- Schema: [`SCHEMA.md`](SCHEMA.md)
- Related work: [`RELATED_WORK.md`](RELATED_WORK.md)
- Open questions: [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)
