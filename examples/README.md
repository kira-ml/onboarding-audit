# Examples

## Run the end-to-end demo

```bash
onboarding-audit demo --out reports/demo
```

This uses `examples/demo_log.csv` (2,500 rows, no `propensity` column) and
`examples/demo_candidate.csv`. It exercises the estimated-propensity path, the
identification gate, the report, and the memo. The known true `P0` value is in
`examples/demo_truth.json`; this is a usability fixture, not a research result.

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
are volatile at this size; the identification gate correctly reports **“Not
identified”** and withholds the point estimates. The generated memo is
`reports/sample_report/report.md`.

Because the sample log has a `propensity` column, the report uses it as the
`provided` source. To exercise the covariate model, drop the `propensity` column
or pass a log without it, then run:

```bash
onboarding-audit report \
  --log examples/sample_log.csv \
  --candidate examples/sample_candidate.csv \
  --config configs/pilot.yaml \
  --capacity 0.10 \
  --propensity-model covariate \
  --propensity-features customer_age,credit_risk_score \
  --out reports/sample_covariate
```

The 20-row sample is too small for a meaningful covariate fit; the model falls
back to the action mean. Use the synthetic 2,500-row test log in
`tests/test_report.py` or a real log to see the gradient.

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
