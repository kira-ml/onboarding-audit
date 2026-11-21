# Related Work Map

**Status:** Canonical related-work map for v1.0.0 (2026-11-22).

**Purpose:** Show what is established, what is adjacent, and what this project
adds. The curated public bibliography is [`REFERENCES.md`](REFERENCES.md). The
full annotated bibliography is in the archived origin repository:
`D:\delayed-label-fraud-decisioning\research_notes\Philippine fintech fraud problem evidence\literature_review.md`.

---

## 1. The closest work

| Work | Setting | What it does | What it does not do |
|---|---|---|---|
| **Pombal et al. (2022)**, *Prisoners of Their Own Devices* (ICML workshop) | Real-world account-opening fraud case study | Studies distribution shift and selective labels in performative prediction; taxonomy of bias | No policy-evaluation toolkit, delay-aware estimator comparison, capacity layer, audit design, or public benchmark |
| **OSCAR** (Kuroki et al., ICAIF 2026) | Financial screening under selective and delayed labels | Certified online learning for auditable screening | Online learning/certification focus; not account-opening approve/review/reject, no open logging/audit tool |
| **Beyond Holdout Error** (Bhola et al., Bloomberg, ICAIF 2026) | Financial estimators under selective labels | Layered evaluation framework; shows estimator rankings can reverse | Not a fraud/account-opening policy tool; no capacity/audit design |
| **DOiT** (Hong et al., KFTC/KAIST, ICAIF 2026) | AML review | Shows better money-flow ranking can coexist with worse account selection | AML-specific; not account-opening fraud or selective/delayed label estimation |
| **Cost-Sensitive Top-K Review** (Zhang et al., 2026) | Capacity-constrained fraud screening | Converts ranked scores to review queues under capacity and case costs | Evaluates on labeled data; does not correct policy-induced selection or delayed labels |
| **The Alert-Feedback Trap** (ICAIF 2026) | Drift-adaptive fraud detectors under label feedback | Shows feedback loops and the exploration needed to escape | Detection/adaptation focus; not account-opening policy value or audit memo |
| **A Standardized Training and Evaluation Protocol for Sequential Fraud Detection** (Mašková & Šmídl, ICAIF 2026) | Sequential fraud detection | Training/evaluation protocol and code | Model evaluation, not policy value under selective labels |
| **FiFAR** (Alves et al., 2023) | Learning to defer in fraud alert review | 50 synthetic analysts, work-capacity constraints, 300 scenarios | A benchmark for L2D; not an account-opening policy-evaluation or audit protocol |
| **BAF** (Jesus et al., NeurIPS 2022) | Public account-opening fraud dataset | 1M applications, temporal dynamics, bias variants | A dataset; no action log, propensities, label timestamps, or policy-evaluation method |

## 2. Method foundations

| Theme | Key references | Use in this project |
|---|---|---|
| Selective labels | Lakkaraju et al. 2017; Kleinberg et al. 2018; Ensign et al. 2018 | The label is chosen by the policy; naive evaluation is biased |
| Reject inference | Boyes et al. 1989; Crook & Banasik 2004; Ehrhardt et al. 2021; Kozodoi et al. 2025; Scarone & Baeza-Yates 2026 | Closest analogue: approved-only outcomes; correction can hurt; evaluation-side correction and exploration |
| PU learning | Elkan & Noto 2008; Bekker & Davis 2020; Bourazas et al. 2026 | Approved fraud is a positive label; approved legit is often unlabeled; calibration is fragile |
| Delayed feedback | Chapelle 2014; Dal Pozzolo et al. 2015; Vernade et al. 2017; Dhama 2026 | Delay/censoring; investigator feedback differs from customer labels |
| OPE | Dudík et al. 2011; Swaminathan & Joachims 2015; Thomas & Brunskill 2016; Namkoong et al. 2020 | IPW/DR/SNIPS; positivity and unconfoundedness; confounding can dominate |
| Capacity / L2D | FiFAR 2023; Cost-Sensitive Top-K Review 2026 | Review capacity and queue construction |
| Model risk / audit | BSP 1213; BSP Project Sapiens; NPC Advisory 2024-04 | Calibration, independent review, explainability, human intervention |

## 3. The gap this project fills

> No reviewed work jointly provides: (a) an account-opening policy-evaluation
> estimand under policy-induced selection and delayed/censored labels, (b) a
> capacity-constrained review layer, (c) a compliant audit design (post-hoc
> verification/shadow scoring, not random approvals/rejections), (d) an
> evidence-backed logging schema that extends BSP 1213's 11 fields, and (e) an
> open-source benchmark/tool that a fintech team can run on its own logs.

The contribution is the **applied measurement layer**, not a new estimator
theory. The paper should say this plainly and cite the closest work.

## 4. What would make this redundant

- A vendor shipping selection/delay-aware policy evaluation with propensity
  logging and audit-arm design as documented, usable features.
- A peer-reviewed account-opening policy-evaluation paper with the same
  logging/audit/tool contribution.
- Evidence that target institutions already run mature randomized audits and
  OPE, removing the practical gap.
