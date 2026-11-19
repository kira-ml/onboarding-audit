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

## Run the pilot

```bash
onboarding-audit pilot --config configs/pilot.yaml --out reports
```

The pilot uses `data/scored_test.parquet` (the BAF account-opening test window).
See `docs/DATA.md` for provenance and limitations.
