# Contributing

This is a research repository. The contribution rules are designed to protect
the credibility of the claims, not just the code.

## Research rules

1. **No new headline without pre-registration.** Add the hypothesis to
   `docs/PILOT_SPEC.md` before running the analysis that tests it.
2. **Every public number traces to an artifact.** Add it to `docs/CLAIMS.md`
   with a status: Measured, Pre-registered, Post-hoc, Non-finding, or
   Limitation. The source is `reports/pilot.json` or a cited primary source.
3. **No silent leakage.** Pre-decision features only. The schema validator
   warns about post-decision fields; do not ignore it.
4. **No causal deployment claim.** The estimand is a counterfactual policy value
   under a stated observation model.
5. **No random approvals/rejections.** Use post-hoc verification and shadow
   scoring. Legal/risk review is required for anything else.
6. **No PII.** Use public or synthetic data; hash identifiers in examples.
7. **Report failures.** A non-finding or a failed estimator is a result. Do not
   hide it.

## Code rules

- Python 3.10+; type hints on public functions.
- Keep the estimator functions small and pure.
- Add a test for any behavior change.
- `pytest -q` must pass.
- Do not add a dependency without a reason in the PR.
- Do not change the cost matrix or the estimand without a dated decision in
  `docs/DECISIONS.md`.

## Adding a scenario

1. Add the scenario to `configs/pilot.yaml` with a unique `id`, `reps`,
   `audit_rate`, `approve_delay_median`, `false_reject_cost`, and optional
   `outcome_dependent`/`candidate_capacity`.
2. State the purpose in `docs/PILOT_SPEC.md` §8.
3. Run `onboarding-audit pilot --config configs/pilot.yaml --scenarios <id> --reps 5`
   as a smoke test.
4. Run the full scenario.
5. Add the result to `docs/CLAIMS.md` and, if it changes the headline, to the
   report.

## Reporting a bug

Include:
- the config and scenario id,
- the command,
- the expected vs actual behavior,
- the relevant part of `reports/pilot.json` or the stack trace.

## License

By contributing, you agree that your contribution is licensed under the MIT
License.
