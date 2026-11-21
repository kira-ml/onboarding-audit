# Maintainers

**Status:** V1 maintainer guide, 2026-11-21.

---

## 1. Current maintainer

**Ken Ira Lacson Talingting** — owner, maintainer, and release manager.

## 2. Responsibilities

- Keep `main` green: tests, demo, link check.
- Triage issues and pull requests.
- Keep the claim ledger and results consistent with the code.
- Cut releases and update `CHANGELOG.md`, `CITATION.cff`, and the README.
- Protect the privacy rule: no PII or proprietary data in the repository.
- Keep the V1 progress tracker current.

## 3. Review cadence

| Period | Cadence |
|---|---|
| V1 development | Weekly |
| After v1.0.0 | Monthly, or before a release |
| Security/privacy issue | Immediately |

## 4. Release process

1. Run `pytest -q`; all tests pass.
2. Run `python -m onboarding_audit.cli demo --out reports/demo_ci`; the gate
   passes and the memo is generated.
3. Run `python scripts/check_links.py`; zero missing links.
4. Update `CHANGELOG.md`, `CITATION.cff`, and the README status.
5. Tag the release.
6. Push the tag and publish the release notes.

## 5. Bus factor

The project currently has a single maintainer. The documentation, tests, and
reproducibility guide are the mitigation. A second maintainer or an external
reviewer is a V1 goal.

## 6. Becoming a maintainer

A contributor can become a maintainer after:

- several merged changes that follow the research and code rules;
- a demonstrated ability to run the release process;
- agreement to the privacy and claim-ledger rules.

## 7. Related documents

- Contributing: [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
- Testing: [`TESTING.md`](TESTING.md)
- Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Publication checklist: [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md)
- Privacy: [`PRIVACY.md`](PRIVACY.md)
