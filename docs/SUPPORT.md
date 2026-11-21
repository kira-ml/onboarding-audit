# Support

**Status:** V1 support guide, 2026-11-21.

---

## 1. Where to ask

Open an issue in the repository:

`https://github.com/kira-ml/onboarding-audit/issues`

For a usage question, include:

- the version (`python -c "import onboarding_audit; print(onboarding_audit.__version__)"`);
- the command you ran;
- the config and scenario id, if relevant;
- the expected and actual result;
- the smallest non-sensitive excerpt of the log or error.

## 2. What not to post

Do not post:

- PII, names, account numbers, raw documents, or unhashed contact data;
- a bank's proprietary log;
- credentials, tokens, or connection strings.

If the issue requires sensitive data, describe the shape of the problem instead.

## 3. Scope

This is a **research pilot**, not a production support service. Support is best
effort. The project does not provide:

- a production SLA;
- legal, compliance, or model-risk advice;
- a guarantee that a point estimate is identified;
- a replacement for the institution's validator or risk committee.

## 4. Before asking

1. Run `pytest -q`.
2. Run `onboarding-audit demo --out reports/demo`.
3. Read [`REPORT_USAGE.md`](REPORT_USAGE.md), especially the identification
   gate.
4. Check [`FAQ.md`](FAQ.md).

## 5. Security and privacy

Do not open a public issue for a suspected data leak or a security problem.
Follow [`PRIVACY.md`](PRIVACY.md) and notify the data owner and the
institution's privacy office.

## 6. Related documents

- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
- Privacy: [`PRIVACY.md`](PRIVACY.md)
- Testing: [`TESTING.md`](TESTING.md)
- Contributing: [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
- Maintainers: [`MAINTAINERS.md`](MAINTAINERS.md)
