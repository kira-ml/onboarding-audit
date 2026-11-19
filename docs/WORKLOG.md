# Worklog

## 2026-11-19 — Direction set, repo scaffolded

**Done:**

- Archived the origin repository as `v2.1.0` with `ARCHIVE.md`.
- Committed the evidence memo and six research reviews to the origin repo.
- Created `D:\onboarding-audit` as the new flagship repo.
- Wrote the public surface: `README.md`, `LICENSE`, `pyproject.toml`,
  `CITATION.cff`, `.gitignore`.
- Wrote the research contract: `docs/PROBLEM.md`, `docs/PILOT_SPEC.md`,
  `docs/SCHEMA.md`, `docs/AUDIT_DESIGN.md`, `docs/DATA.md`, `docs/CLAIMS.md`,
  `docs/DECISIONS.md`.
- Copied the processed BAF test file to `data/scored_test.parquet` for the
  local pilot.

**Next:**

1. Implement `src/onboarding_audit/`: config, data, policies, observation,
   estimators, metrics, pilot.
2. Add `configs/pilot.yaml`.
3. Add tests: policy capacity, observation propensities, full-observation
   identity, bounds, no leakage, metrics.
4. Run the pilot; write `reports/pilot.json` and `reports/pilot.md`.
5. Fill the claim ledger with measured results.
6. Add the CLI and a minimal report template.
7. External readers: one fraud/KYC practitioner, one researcher.
8. FiFAR capacity layer (follow-on).
9. Paper draft and release.

**Open questions:**

- What are the actual PH onboarding review rates, label delays, and
  false-rejection costs? No public data; elicit via interviews.
- Is post-hoc verification operationally feasible at a PH bank/e-wallet?
- What is the base-rate difference between BAF and PH e-wallet onboarding?
- Does FiFAR's analyst model add enough to justify the complexity in v0.1?
- What is the right cost model for a fraudulent account: credit-line exposure,
  expected draw-down, or a fixed loss?

**Blockers:** None.

**Health:** The research contract is complete; the pilot is the next decisive
test.

---

## 2026-11-19 — Full pilot complete

**Result:** the premise is real and the correction holds on the identified
population.

- Naive relative bias: **+111.6% to +278.5%** across four policies.
- Naive rank flip: mean **1.00** inversion, P(select true best) **0%**; the
  naive estimate would reject the better model.
- DR: max |relative bias| **0.94%**, mean coverage **96.0%**; IPW **1.18% /
  95.0%**.
- Audit-only at 1%: max **2.98%**, coverage **84.5%**, ESS **1,271**.
- Audit value: DR RMSE **0.001159 → 0.001068** (0% → 2%), ESS **6,610 → 9,126**;
  modest in the main scenario, decisive under outcome-dependent labels
  (audit-only **-2.4% to -2.0%** vs IPW **+44% to +368%** and DR **+596% to
  +1302%**).
- Reject margin: widest bounds **0.009942**; incumbent bounds coverage **35%**;
  bounds are not confidence intervals.
- Runtime: 1,114 s; 700 replications; 13 scenarios.

**Claim ledger and public artifacts updated:** `docs/CLAIMS.md`,
`docs/ONE_PAGER.md`, `paper/brief.md`, `paper/outline.md`, `README.md`,
`reports/pilot.md`, `reports/pilot.json`.

**Next:**

1. Recompute the final verdict with the corrected H2 (naive-only) and H3
   (IPW/DR-only) logic, and regenerate `reports/pilot.md` (done).
2. Two external readers: a fraud/KYC practitioner and a researcher.
3. FiFAR capacity/analyst layer (v0.2).
4. Propensity estimation from logs/audit and sensitivity (v0.2).
5. Paper draft from the outline; fill the claim ledger references.
6. Public release and application package.

**Open questions:** unchanged, plus:
- The naive bias is positive (overestimates cost), not "flattering the
  incumbent." The direction depends on the action mix and costs; test a logging
  policy with a different action mix.
- The corrected ranking still has ~0.29 mean inversions, concentrated in the
  close better-model/incumbent gap. Is that acceptable for a launch decision?
- The audit's marginal value is modest at a 5% approved-label base rate. What is
  the realistic base rate in a PH e-wallet?

**Health:** The pilot supports the premise and the correction; the project is
ready for external review and the v0.2 tool layer.
