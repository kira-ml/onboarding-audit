# Episode Reviews

**Purpose:** After-action reviews for material tasks. The point is to change a
rule, not to grade the work. A good result from a bad process is a warning; a
bad result from a good process is noise.

---

## 2026-11-20 — Credibility and adoption plan

**Task:** Answer how to make the project one a fintech risk team would actually
run, and one a hostile reviewer could not dismiss.

**Scores (0–2):**

| Dimension | Score | Evidence |
|---|---:|---|
| Goal | 2 | The plan is concrete and covers both audiences. |
| Verification | 1 | Repo and link checks were run, but the plan was not verified with a risk team or hostile reviewer. |
| Efficiency | 1 | One rework after the user asked whether the framework was followed. |
| Process | 1 | Used first principles, constraints, inversion, and decision logic, but skipped explicit model selection, the decision-journal entry, and the independent red team until challenged. |
| Learning | 2 | A specific rule change below. |

**Total: 7/10.**

**Expected vs actual:** Expected a strategic answer with an artifact. The plan
was strong, but the process was not fully protocol-compliant and the decision
record was missing until challenged.

**What worked:**

- Grounded in the repository; no invented features.
- Identified the binding constraint: access to a real log and a risk-team
  sponsor, not more code.
- Produced the hostile-reviewer attack table and the 90-day plan.
- Produced a concrete pilot protocol, business-case template, and model-risk
  package.

**What failed:**

- Did not explicitly classify the task or name 2–3 models and their artifacts
  before answering.
- Did not write the decision-journal entry until challenged.
- Did not run an independent red team before presenting the plan.
- Did not verify the plan with the target audience.

**Rule change:** Before presenting a material strategy, write the
decision-journal entry and launch an independent red team first. Do not present
the plan as verified without external review.

**Next:** Add the red-team findings to `docs/CREDIBILITY_PLAN.md`; keep D13 as
the decision record.
