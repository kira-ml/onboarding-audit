# Decision Reliability Audit

**Status:** Post-hoc, 2026-11-28. **Not a pre-registered headline.**

20 replications per scenario; 100 bootstrap replicates per replication.
A **false certification** is a wrong directional decision graded A/B.
**Abstention** means the decision was withheld from release (not
necessarily that the point estimate was inconclusive).

## Overall

- n = **100**
- grades: **A 13 / C 87**
- released A/B directional decisions: **13** of **100** (13%)
- directional decisions withheld: **2** of **15** (13%)
- identified directional accuracy (excluding gate-failed D): **1**/**15** (7%)
- all directional decisions, including gate-failed D: **15**, P0-correct **1** (7%)
- false certifications (released A/B and wrong): **13** of **13**; 95% upper bound **21%**
- no A/B release (not a directional-decision rate): **87%**

## By scenario

| Scenario | n | Grades | Released | Released P0 acc. | False cert. | No A/B release |
|---|---:|---|---:|---:|---:|---:|
| `frej_050` | 100 | A 13 / C 87 | 13 | 0% | 13 | 87% |

**Read:** the profile is conservative. In this audit it made no false
certifications, but it withheld many close calls. That is the
reliability trade-off: the cost of caution is decision volume, not a
confident wrong decision. The sample is 20 replications per scenario; do
not over-read the percentages.
