# Ethico technical audit

Audit date: **2026-10-09**.

This is a sanitized historical summary of the October technical audit. Raw local
home-directory paths and other machine-specific identifiers were deliberately
removed from the repository record because they are not needed to reproduce the
findings.

## Scope

The audit reviewed:

- repository structure and Git-tracked files
- backend source, tests, requirements, SQLite behavior, and API contract
- Flutter source, tests, scanner integration, and source-link handling
- Android/iOS configuration relevant to the MVP
- documentation consistency and implementation claims
- privacy/security characteristics visible from source

No application behavior was changed by the original audit.

## Architecture observed

```text
Manual entry / on-device barcode scan
                |
                v
             Flutter
                |
                v
       GET /products/{ean}
                |
                v
             FastAPI
                |
        validate EAN/checksum
                |
        +-------+-------+
        |               |
        v               v
     SQLite       Open Food Facts
   local facts      local miss only
```

Camera frames remain on-device. Product lookup sends the detected/entered EAN to
the backend. The local SQLite database contains product facts and source metadata.
Open Food Facts is queried only after a local miss and is not persisted.

## Important findings from the audit

### R1 — UTF-8 client decoding

The Flutter HTTP client previously relied on response text decoding that could
mis-handle UTF-8 JSON without an explicit charset. This was subsequently fixed by
explicitly decoding response bytes as UTF-8 and covered with a regression test.

### R2 — curated-data validation

The original curated import accepted dictionaries without a dedicated complete
pre-import validation boundary. This was subsequently fixed with explicit dataset
validation before database access.

### R3 — curated corrections

Existing imported rows were intentionally preserved, but the original baseline had
no explicit correction workflow. This was subsequently addressed with an atomic,
expected-state correction CLI that updates facts and sources together and blocks on
conflicts.

### R4 — scanner verification

Scanner lifecycle, permission restoration, cancellation, duplicate detections, and
end-to-end retry behavior were under-tested. This remains active MVP hardening work.
Automated tests must not be described as physical-camera verification.

### R5 — client/API contract clarity

Some historical Flutter error paths were broad and some fixtures did not fully
exercise every metadata field. Continue strengthening focused contract tests as the
client evolves.

### R6 — dependency/reproducibility debt

Direct dependencies are pinned, but the project does not maintain a fully locked
Python transitive environment. Dependency upgrades should be deliberate rather than
mixed into unrelated feature work.

### R7 — release configuration

Android development builds are suitable for local MVP work, but public distribution
is not ready. The application still requires a project-owned application ID,
private release signing configuration, and a production deployment/security review.

## Privacy and security observations

Positive properties observed:

- no accounts or user-profile database
- no analytics or telemetry implementation
- no persistent scan history in application code
- camera frames are not uploaded by application code
- SQL uses parameterized statements
- source links are limited to HTTP(S) and opened only after user action
- no current server-side arbitrary source fetching/SSRF path
- local databases, environment files, and common build artifacts are ignored

Deployment boundaries:

- the development API has no authentication or rate limiting
- local cleartext HTTP is a debug/development concern, not a production design
- ordinary HTTP server access logs can expose requested EANs and client network metadata
- public deployment requires log minimization/retention, HTTPS, abuse controls, secret management, backups, and release signing

## Verification record

The original backend audit run completed successfully with **14 passing tests** and
two upstream dependency deprecation warnings. Flutter execution was unavailable in
that specific audit environment, so no Flutter pass was claimed by that audit.
Later repository milestones added CI and recorded successful Flutter analysis/tests.

Exact local temporary-directory paths are intentionally omitted. Reproduction
should use repository-relative commands and isolated temporary directories rather
than a developer-specific home path.

## Historical status

Several important findings from this audit have since been fixed:

- UTF-8 response decoding
- curated-data validation
- GitHub Actions CI
- Open Food Facts read-only fallback behavior/tests
- explicit curated-data correction workflow

Remaining relevant audit themes include scanner/device verification, production
release hardening, operational security, dependency review, and continued privacy
hygiene.

For the current implementation state, see [status](../status.md),
[architecture](../architecture.md), and [roadmap](../roadmap.md).
