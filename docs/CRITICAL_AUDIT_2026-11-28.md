# Critical Audit — 2026-11-28

**Scope:** current `main` after the restricted-feature negative result.
**Purpose:** record the credibility-threatening findings that a senior fintech
data scientist or ML engineer would notice first.
**Status key:** **Fixed** = corrected and verified; **Open** = still a risk;
**Blocked** = requires a person, data, or counsel.

---

## 1. Critical

### C1 — The reliability profile can be confidently wrong

**Finding:** the restricted-feature audit released **13 A/B decisions and all 13
were wrong** in the 100-replication `frej_050` confirmation. The true candidate
advantage was ~0.53% of cost; the estimate put it ~7% worse. Bootstrap, cost
stress, and full-policy checks all agreed with the wrong sign.

**Why it matters:** this is the project's central safety claim, and it fails on
the protected-attribute-free feature set. A reviewer will ask why the profile is
called decision-grade.

**Status: Open.** Reported in `RESTRICTED_FEATURE_AUDIT.md`, paper, README, and
`CLAIMS.md`; D20 stops the BAF-suite audit. A guard is proposed but not enabled.

### C2 — Protected attributes remain in the default feature pipeline

**Finding:** the original scores and several legacy configs use `customer_age`,
`employment_status`, and `income`. `prepare_baf.py` now excludes them by default;
`--include-protected` is legacy-only. The legacy configs still reproduce the
unsafe scores for the v1.1.0 record.

**Why it matters:** a new user following a legacy config can still reproduce the
ethically weaker model. The default preparation path is now safe.

**Status: Partially fixed.** Default preparation is safe; legacy configs are
labeled; the full restricted rerun of every paper experiment is not done.

### C3 — The BAF source version is not pinned

**Finding:** `BENCHMARK_PROVENANCE.md` records a raw SHA but not the Kaggle
version. The restricted frame came from a different public copy; the raw hash
differs.

**Why it matters:** a reviewer cannot tell a version mismatch from a
reproduction failure, and the index–label fix in Kaggle v2 is relevant.

**Status: Open.** Recorded as a release gate; no BAF-suite run until fixed.

### C4 — `main` and the `v1.1.0` tag disagree

**Finding:** the title, restricted negative result, license/plan changes, and
paper updates are on `main`; `v1.1.0` points to an earlier commit.

**Why it matters:** a reader who cites the tag gets different claims from a
reader who cites `main`.

**Status: Open.** No new tag was created; release decision pending.

## 2. High

### H1 — “Zero false certifications” was under-powered

**Finding:** the original audit released 2 decisions; 0/2 has a 95% upper bound
of 78%. The original text treated it as a safety result.

**Status: Fixed.** Now reported as 0/2 with the interval, and the restricted
13/13 failure is reported separately.

### H2 — Data-use/portfolio ambiguity

**Finding:** CC BY-NC-SA 4.0 is non-commercial. Employment-directed portfolio use
is ambiguous; the project is on HOLD for that use.

**Status: Blocked.** Needs counsel or permission; recorded in D19 and
`DATA_USE_PLAN.md`.

### H3 — Publication license/availability statement is incomplete

**Finding:** the paper names the license and says data are not redistributed, but
does not give a full Kaggle data-availability statement.

**Status: Partially fixed.** A `NOTICE` and README carve-out exist; the paper
still needs the availability statement before submission.

### H4 — Default pipeline can still produce protected-feature scores

**Finding:** same root as C2. The default now excludes protected columns, but a
legacy config can still opt back in with `--include-protected`.

**Status: Partially fixed.** Safe default and explicit legacy flag exist; no
runtime refusal for a legacy config.

### H5 — Absolute local paths in provenance

**Finding:** `prepare_baf.py` writes `raw_path` and `output_path` into the
provenance sidecar; those can leak local paths.

**Status: Open.** Not committed in the restricted provenance (git-ignored), but
the script should sanitize or use basenames.

### H6 — CI did not run lint

**Finding:** `ruff` was not in the dev dependencies or CI, and the tree had 25
lint errors.

**Status: Fixed.** `ruff` added to dev/CI; `ruff check .` passes.

### H7 — Stale status lines and counts

**Finding:** several canonical docs still said “v1.0.0” while the tree was at
v1.1.0 plus a negative result; test counts varied.

**Status: Fixed for the current-tree status lines and test/claim counts.** Some
historical documents intentionally retain old numbers.

### H8 — Paper/README claim language overstates safety

**Finding:** “zero false certifications” and “reliability profile” language
survived after the restricted failure.

**Status: Partially fixed.** The paper abstract, limitations, README, RESULTS,
CLAIMS, and RELEASE_STATUS now report the 13/13 failure; the final paper rewrite
still needs to make the negative result the organizing result.

## 3. Medium

### M1 — 60-rep negative result vs 100-rep confirmation

**Finding:** the first negative result was 5/5 on 20 `frej_050` draws. The
100-draw confirmation is 13/13.

**Status: Fixed.** Canonical docs use the 100-rep confirmation.

### M2 — Case study and demo artifacts use different propensity paths

**Finding:** the case study now provides the known `e`; the demo uses estimated
`e`. This is intentional but easy to misread.

**Status: Fixed/documented.** Case A uses provided `e`; demo C uses estimated
`e` and is marked unavailable for propensity calibration.

### M3 — No test for the proposed materiality guard

**Finding:** the guard is a proposal only.

**Status: Open.** Must be pre-registered and tested before enabling.

### M4 — No independent reproduction of the false certifications

**Finding:** the 13/13 result is generated by this project; no independent
reviewer has reproduced it.

**Status: Blocked.** Needs an external reviewer or a second implementation.

### M5 — `paper/brief` and outreach packet can drift

**Finding:** brief status was stale; it now includes the negative result.

**Status: Partially fixed.** A full reviewer packet update is still pending.

## 4. Low

- Historical release notes intentionally retain old numbers.
- Some docs still use “v1.0.0” in body text; those are historical references.
- `CITATION.cff` version still names 1.1.0 while `main` is ahead; release
  decision pending.

## 5. What a hostile reviewer will ask first

1. “Why did 13/13 A/B releases fail?” — **C1**.
2. “Why are protected attributes still in the default pipeline?” — **C2/H4**.
3. “Which BAF version produced these numbers?” — **C3**.
4. “What exactly is in v1.1.0 versus `main`?” — **C4**.
5. “Show me the independent reproduction.” — **M4**.

Those five must be answered before any new release or submission.

## 6. Blocked tasks

These cannot be completed from the repository alone:

| Task | Owner | Why blocked |
|---|---|---|
| Two external readers | Owner | Requires reviewer names, consent, and time |
| One real-log/schema conversation | Owner | Requires a bank or fintech contact |
| Legal/counsel on portfolio/commercial use | Owner | Requires counsel or dataset-owner permission |
| Independent reproduction of 13/13 | External reviewer | Requires a second implementation/reviewer |
| Kaggle v2 raw-hash confirmation | Owner | Requires the exact Kaggle download/version |

No automated agent should fabricate these outcomes.
