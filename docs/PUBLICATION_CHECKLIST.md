# Publication Checklist

**Status:** Canonical pre-release checklist for v0.2.1 (2026-11-20).
**Purpose:** Prevent a public release from shipping an unsupported number, a
privacy mistake, a broken reproduction path, or an overclaim. This is the last
document to read before a tag, a blog post, or a paper submission.

---

## 1. Claims and numbers

- [ ] Every public number appears in [`CLAIMS.md`](CLAIMS.md) with a status.
- [ ] Every measured number traces to `reports/pilot.json`,
      `reports/propensity_sensitivity.json`, or a cited primary source.
- [ ] No stale number remains from a previous run (search the repo for the old
      value).
- [ ] The headline distinguishes:
  - the main pilot (oracle propensities, action-dependent observation);
  - the action-level propensity sensitivity;
  - the covariate-dependent sensitivity;
  - the outcome-dependent stress test.
- [ ] The paper does not claim a production estimate, a causal deployment
      effect, or a point-identified full-population value.
- [ ] The reject-margin language says **bounds**, not confidence interval.
- [ ] The audit language says **post-hoc verification and shadow scoring**, not
      random approvals/rejections.
- [ ] The regulatory language is precise: BSP 1213 is an FMS circular; the MRM
      guidelines are a draft; BSP AI principles are voluntary; NPC Advisory
      2024-04 is binding for explainability/fairness.
- [ ] The IPW caveat is present: IPW is less robust under noisy or
  covariate-dependent propensities;
      DR is the recommended corrected estimator.
- [ ] The covariate caveat is present: action-level IPW fails when observation
      depends on application features; the covariate model is the correction,
      and heavy weights can undercover.

## 2. Data and privacy

- [ ] No proprietary bank data, GCash data, or PII is in the repo.
- [ ] `data/scored_test.parquet` is gitignored.
- [ ] The examples use synthetic data only.
- [ ] The BAF license and citation are present in [`DATA.md`](DATA.md) and
      [`../CITATION.cff`](../CITATION.cff).
- [ ] The data hash in [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) matches the
      local file used for the committed results.
- [ ] No raw documents, names, account numbers, or unhashed contact data appear
      in examples or logs.
- [ ] The privacy section of [`REPORT_USAGE.md`](REPORT_USAGE.md) is current.

## 3. Code and tests

- [ ] `pytest -q` passes (82 tests on v0.2.1).
- [ ] The version in `pyproject.toml`, `src/onboarding_audit/__init__.py`, and
      `CITATION.cff` agree.
- [ ] `CHANGELOG.md` has an entry for the release.
- [ ] The CLI help lists `pilot`, `report`, `sensitivity`, `validate`.
- [ ] The `report` command runs on `examples/sample_log.csv` and writes a memo.
- [ ] The covariate report path runs with `--propensity-model covariate`.
- [ ] No debug prints, hard-coded paths, or local absolute paths remain in the
      package.
- [ ] The dependency bounds are current and installable from a clean venv.
- [ ] `LICENSE` is present and matches the package metadata.

## 4. Documentation

- [ ] [`README.md`](../README.md) opens with the problem, the status, and the
      headline, not a feature list.
- [ ] [`docs/README.md`](README.md) maps every document and states the update
      rules.
- [ ] [`METHODS.md`](METHODS.md), [`RESULTS.md`](RESULTS.md),
      [`CLAIMS.md`](CLAIMS.md), [`THREATS.md`](THREATS.md), and
      [`DECISIONS.md`](DECISIONS.md) are consistent.
- [ ] [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) reproduces the headline from a
      clean checkout.
- [ ] [`DATA.md`](DATA.md) and [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) match
      the processed file.
- [ ] [`SCHEMA.md`](SCHEMA.md) matches `schema.py` and the sample log.
- [ ] [`REPORT_USAGE.md`](REPORT_USAGE.md) matches the CLI flags.
- [ ] [`BSP_MAPPING.md`](BSP_MAPPING.md) does not overstate the regulatory
      requirement.
- [ ] [`RELATED_WORK.md`](RELATED_WORK.md) cites the closest work and states the
      gap without claiming novelty for a known estimator.
- [ ] [`REFERENCES.md`](REFERENCES.md) matches the citations in the paper; every
      **verify** entry has been checked or removed.
- [ ] [`GLOSSARY.md`](GLOSSARY.md) defines every acronym used in the README and
      the paper.
- [ ] [`../paper/README.md`](../paper/README.md) states that the paper is not
      drafted and points to the canonical docs.
- [ ] [`README.md`](README.md) lists every canonical document and the update
      rules.
- [ ] No broken relative links (run the link check in §9).
- [ ] No "to be added" or "TBD" placeholders remain in public docs.

## 5. Reproducibility

- [ ] A fresh venv installs the package.
- [ ] `pytest -q` passes.
- [ ] The pilot command runs on the local data and writes `pilot.json`/`pilot.md`.
- [ ] The sensitivity command runs and writes the JSON/Markdown.
- [ ] The report command runs on the sample log.
- [ ] The committed JSON matches the committed Markdown.
- [ ] The seed and replication counts are stated.
- [ ] The runtime is stated (or the run is marked long-running).
- [ ] The local-only files (`pilot_rows.parquet`, sample reports) are gitignored.
- [ ] A reader without the processed data understands what they cannot
      reproduce and why.

## 6. External review

- [ ] One fraud/KYC practitioner has read the problem brief and the audit design.
- [ ] One researcher has read the methods and the claim ledger.
- [ ] A red-team pass has tried to break the headline (see
      [`THREATS.md`](THREATS.md)).
- [ ] The reviewers' objections are recorded in [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)
      or [`DECISIONS.md`](DECISIONS.md).
- [ ] At least one reviewer has run the `report` command on a log.

## 7. Paper artifacts (when drafting starts)

- [ ] The abstract numbers match [`RESULTS.md`](RESULTS.md).
- [ ] The methods section follows [`METHODS.md`](METHODS.md).
- [ ] The related-work section follows [`RELATED_WORK.md`](RELATED_WORK.md).
- [ ] The limitations section follows [`THREATS.md`](THREATS.md).
- [ ] The appendix claim ledger matches [`CLAIMS.md`](CLAIMS.md).
- [ ] The reproducibility appendix follows [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).
- [ ] The paper does not introduce a new headline that is not in the claim
      ledger.
- [ ] The paper cites the BAF dataset and the closest work.
- [ ] The paper states the simulation and the lack of Philippine bank data.

## 8. Release mechanics

- [ ] `git status` is clean.
- [ ] The release commit is tagged (`v0.2.1` or later).
- [ ] The GitHub release notes summarize the change and the limitations.
- [ ] `CITATION.cff` has the correct version and date.
- [ ] The README badge/status matches the release.
- [ ] The docs index links the release.
- [ ] Optional: Zenodo DOI, arXiv, blog post, talk.

## 9. Link and consistency check

Run a relative-link check before release. The heredoc is Unix-style; on Windows
PowerShell, save the script to `check_links.py` and run `python check_links.py`.

```bash
python - <<'PY'
from pathlib import Path
import re

root = Path(".")
missing = []
for path in root.rglob("*.md"):
    if any(part in {".git", ".venv", "__pycache__", ".pytest_cache"} for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        candidate = (path.parent / target).resolve()
        if not candidate.exists():
            missing.append((str(path), target))
for path, target in missing:
    print(f"{path}: {target}")
print(f"{len(missing)} missing link(s)")
PY
```

Expected: `0 missing link(s)`.

Also search for stale status markers (use `Select-String` on Windows):

```bash
grep -rn "v0.1 pilot\|to be measured\|TBD\|to be added" --include="*.md" .
```

Expected: only intentional historical notes, no live placeholder.

## 10. Stop conditions

Do not release if any of these is true:

- A headline number has no committed JSON or cited source.
- The claim ledger and the README disagree.
- The reject margin is described as a confidence interval or a point estimate.
- The audit is described as random approvals/rejections.
- The paper claims production, a specific bank, or a causal deployment effect.
- A test fails or the reproduction path is broken.
- A reviewer has raised an unaddressed validity threat that would change the
  headline.
- The data or examples contain PII or proprietary material.

## 11. Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Author | Ken Ira Lacson Talingting | | |
| Research reviewer | | | |
| Fraud/KYC practitioner | | | |
| Legal/compliance (if applicable) | | | |

## 12. Related documents

- Claims: [`CLAIMS.md`](CLAIMS.md)
- Threats: [`THREATS.md`](THREATS.md)
- Results: [`RESULTS.md`](RESULTS.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Open questions: [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
