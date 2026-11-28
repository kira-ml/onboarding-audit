# Decision Reliability Audit

**Status:** Post-hoc, 2026-11-28. **Not a pre-registered headline.**

20 replications per scenario; 100 bootstrap replicates per replication.
A **false certification** is a wrong directional decision graded A/B.
**Abstention** means the decision was withheld from release (not
necessarily that the point estimate was inconclusive).

## Overall

- n = **60**
- grades: **A 1 / B 1 / C 38 / D 20**
- released A/B directional decisions: **2** (3%)
- released accuracy: **100%**
- false certifications (released A/B and wrong): **0**
- withheld from release (abstention): **97%**
- all directional decisions, including C/D not released: **11**, accuracy **45%**

## By scenario

| Scenario | n | Grades | Released | Released acc. | False cert. | Abstention |
|---|---:|---|---:|---:|---:|---:|
| `e001` | 20 | D 20 | 0 | n/a | 0 | 100% |
| `frej_050` | 20 | A 1 / C 19 | 1 | 100% | 0 | 95% |
| `main` | 20 | B 1 / C 19 | 1 | 100% | 0 | 95% |

**Read:** the profile is conservative. In this audit it made no false
certifications, but it withheld many close calls. That is the
reliability trade-off: the cost of caution is decision volume, not a
confident wrong decision. The sample is 20 replications per scenario; do
not over-read the percentages.
