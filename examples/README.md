# Examples

## Validate a decision log

```bash
onboarding-audit validate --log examples/sample_log.csv
```

The sample log is synthetic and contains no real personal data. It includes:

- approved applications with a post-approval label;
- approved applications in the random post-hoc verification audit;
- reviewed applications with a review label;
- rejected applications with no outcome (the structural missingness the project
  is about).

The validator reports which estimators the log can support and what is missing.

## Run the arbitrary-log report

```bash
onboarding-audit report \
  --log examples/sample_log.csv \
  --candidate examples/sample_candidate.csv \
  --config configs/pilot.yaml \
  --capacity 0.10 \
  --out reports/sample_report
```

This is a 20-row schema/CLI smoke example, not a research result. The estimates
are volatile at this size; use the pilot benchmark or a real log for inference.
The generated memo is `reports/sample_report/report.md`.

## Run the pilot

```bash
onboarding-audit pilot --config configs/pilot.yaml --out reports
```

The pilot uses `data/scored_test.parquet` (the BAF account-opening test window).
See `docs/DATA.md` for provenance and limitations.

## Run the propensity sensitivity

```bash
onboarding-audit sensitivity --config configs/pilot.yaml --out reports --reps 50
```

See `reports/propensity_sensitivity.md` and `docs/REPORT_USAGE.md`.
