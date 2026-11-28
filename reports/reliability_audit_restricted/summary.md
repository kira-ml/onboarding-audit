# Decision Reliability Audit

**Status:** Post-hoc, 2026-11-28. **Not a pre-registered headline.**

20 replications per scenario; 100 bootstrap replicates per replication.
A **false certification** is a wrong directional decision graded A/B.
**Abstention** means the decision was withheld from release (not
necessarily that the point estimate was inconclusive).

## Overall

- n = **60**
- grades: **A 5 / C 35 / D 20**
- released A/B directional decisions: **5** of **60** (8%)
- directional decisions withheld: **6** of **11** (55%)
- identified directional accuracy (excluding gate-failed D): **1**/**8** (12%)
- all directional decisions, including gate-failed D: **11**, P0-correct **1** (9%)
- false certifications (released A/B and wrong): **5** of **5**; 95% upper bound **45%**
- no A/B release (not a directional-decision rate): **92%**

## By scenario

| Scenario | n | Grades | Released | Released P0 acc. | False cert. | No A/B release |
|---|---:|---|---:|---:|---:|---:|
| `e001` | 20 | D 20 | 0 | n/a | 0 | 100% |
| `frej_050` | 20 | A 5 / C 15 | 5 | 0% | 5 | 75% |
| `main` | 20 | C 20 | 0 | n/a | 0 | 100% |

**Read:** the profile is conservative. In this audit it made no false
certifications, but it withheld many close calls. That is the
reliability trade-off: the cost of caution is decision volume, not a
confident wrong decision. The sample is 20 replications per scenario; do
not over-read the percentages.
