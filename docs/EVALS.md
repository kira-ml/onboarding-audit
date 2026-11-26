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

---

## 2026-11-26 — V1 strategic review

**Task:** Decide whether `v1.0.0` is ready for a public flagship release, and
strengthen it using the Mental Models OS (Inversion & Falsification, Theory of
Constraints, Goodhart & Counter-Metrics).

**Scores (0–2):**

| Dimension | Score | Evidence |
|---|---:|---|
| Goal | 2 | The review names the decision, the binding constraint, and the smallest acceptable outcome; it produced a release verdict and a ranked finding set. |
| Verification | 2 | Tests, claim checks, link check, and a constructed full-policy reversal case were run. The paper PDF was not rebuilt (no TeX toolchain). |
| Efficiency | 1 | The review touched many documents; the test-count change required a second consistency pass. |
| Process | 2 | Models were selected by failure mode; a constraint table, pre-mortem, falsification ledger, decision entry, and independent red-team pass were produced. |
| Learning | 2 | A specific rule change below. |

**Total: 9/10.**

**Expected vs actual:** Expected a documentation review; found a product-decision
defect (the `P0` recommendation can reverse on the reject margin), a release-gate
bypass, and a false "Measured" claim. The code fix was smaller than the
documentation cleanup.

**What worked:**

- Started from the repository's own OS and decision journal, not generic
  red-teaming.
- Found the strongest failure mode: the product answers a narrower question than
  it promises.
- Implemented a small, testable extension instead of a new estimator.
- Preserved the identification discipline, gate, reproducibility, and recorded
  negative results.

**What failed:**

- The first pass did not anticipate that adding four tests would change every
  public test count; that is the same drift the review criticizes.
- The paper PDF remains stale because the environment has no TeX toolchain.
- The independent red-team pass was launched but not a human external reader;
  the release gate remains open.

**Rule change:** **Before a version tag or a public release, run the project's
own definition-of-done check and record the result in `RELEASE_STATUS.md`. A tag
must not outrun the gate.** A second rule: **a decision-surface change must be
tested with a constructed case where the recommendation reverses; a passing
happy-path test is not enough.**

**Next:** Send the reviewer packet; record objections in `EXTERNAL_REVIEW.md`;
release the full-policy check as `v1.0.1` or `v1.1`; do not tag a public `1.0`
until the gate is met.
