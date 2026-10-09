# Project status

Last updated: **2026-10-09**.

This document describes the current repository state. Historical verification
commands are intentionally kept free of personal usernames, home-directory paths,
email addresses, and other machine-specific identifiers.

## Current milestone

Ethico is an Android-focused product lookup MVP with source attribution.

Implemented:

- EAN-8 and EAN-13 camera scanning, with manual entry fallback.
- Flutter shape validation and authoritative FastAPI EAN/check-digit validation.
- Product name, brand, company, company role, demo labeling, and source metadata.
- Loading, invalid-input, not-found, temporary-provider, timeout, and source-link handling.
- Local SQLite product lookup with three fictional demo fixtures and one reviewed real product.
- Read-only Open Food Facts fallback for local misses.
- Explicit curated-data validation before database access.
- Explicit, atomic curated-data correction workflow.
- GitHub Actions CI for backend and Flutter checks.

Not implemented:

- ethical scores or AI summaries
- automatic company identity/ownership resolution
- broader ethical evidence integrations
- accounts, payments, analytics, telemetry, or production deployment
- production Android signing/release configuration
- verified iOS build/device behavior

## Privacy and security posture

The application has no user accounts, analytics SDK, telemetry, persistent scan
history, or on-device product cache. Camera frames are decoded on-device and are
not sent to the backend; lookup requests contain only the detected/entered EAN.

Open Food Facts receives the requested barcode and ordinary HTTP metadata on a
local miss. The application identifies itself only by product name/version in its
User-Agent; developer identity, personal repository URLs, email addresses, and
device identifiers are not intentionally sent.

Local databases, `.env` files, signing material, Android `local.properties`, build
artifacts, logs, and common editor/OS files are ignored by Git. Repository hygiene
rules prohibit committing personal contact information, absolute home-directory
paths, secrets, credentials, private keys, device identifiers, or unnecessary
user-activity logs.

For local phone testing, prefer USB forwarding (`adb reverse`) with the backend
bound to loopback. Disable normal access logging when a test specifically requires
that lookup EANs not be written to terminal logs.

A public deployment requires a separate operational security review, including
HTTPS, authentication/abuse controls where appropriate, rate limiting, log
minimization/retention, deployment secrets, backups, and production signing.

## Product data and evidence

The seeded dataset contains three fictional demo fixtures and one reviewed real
product:

- Leader Performance Creatine Monohydrate 300 g
- EAN `6430051512933`
- brand `Leader`
- company `Leader Foods Oy`
- role `manufacturer`

Two reviewed product-fact sources support the recorded identity. They are not an
ethical rating or an independent manufacturer audit. See
[product source notes](product-sources.md).

Missing evidence remains unknown. Product/company identity, ownership, ethical
claims, and provider status must not be inferred beyond what sources support.

## Open Food Facts fallback

Local SQLite lookup has priority. A local miss makes one read-only Open Food Facts
API request for `code`, `product_name`, and `brands`.

Behavior:

- no external product persistence or cache
- no company inference
- no retries or redirects
- three-second HTTPX timeout per network operation
- upstream 404 maps to product-not-found
- unusable responses, rate limiting, and provider/network failures map to a safe temporary failure
- retrieved external results carry provider attribution, source URL, retrieval date, scope, and ODbL 1.0 license metadata

The provider request User-Agent is `Ethico/<version>` and intentionally contains no
personal developer metadata.

Automated provider tests use HTTPX MockTransport and make no live Open Food Facts
requests.

## Curated-data validation

Startup validates the complete curated JSON dataset before opening SQLite or
performing schema/import writes.

Validation includes:

- JSON/list/object structure
- required text fields
- EAN shape/checksum and uniqueness
- HTTP(S) source URL shape
- duplicate source URLs per product
- exact calendar dates

Run from `backend`:

```text
python -m app.validate_curated
```

Validation checks data structure and identifiers, not factual truth or live URL
availability.

## Explicit curated corrections

Editing `curated_products.json` does not silently overwrite an existing imported
SQLite row. Reviewed corrections use the separate explicit maintenance workflow:

```text
python -m app.apply_curated_corrections --validate-only
python -m app.apply_curated_corrections --database <database-path>
python -m app.apply_curated_corrections --database <database-path> --apply
```

Properties:

- preview is read-only by default
- expected and replacement states are validated before database access
- replacement must match the current reviewed curated entry
- product facts and sources are compared together
- conflicts, demo rows, or missing targets block the entire pending batch
- apply runs in one transaction with foreign keys enabled
- failures roll back the batch
- already-applied corrections are safe no-ops
- review dates are never refreshed automatically
- normal application startup never runs corrections

See [curated correction workflow](curated-corrections.md) and decision D009.

## CI and verification

`.github/workflows/ci.yml` runs on pull requests into `main` and pushes to `main`.

Backend job:

- Python 3.12
- install development requirements
- validate curated data
- run the complete pytest suite

Flutter job:

- Flutter 3.29.2 / Dart 3.7.2
- resolve dependencies
- `flutter analyze`
- `flutter test`

CI does not prove physical camera behavior, Android permissions, real-device
connectivity, native release signing, or iOS behavior.

Most recent merged correction-workflow verification recorded **204 passing backend
tests**. The Open Food Facts milestone recorded **148 passing backend tests** and
**15 passing Flutter tests**. These counts are historical results for their
containing revisions; current CI is authoritative for new changes.

## Scanner verification status

Scanner/end-to-end hardening and a complete physical-device acceptance run remain
unfinished P2 work.

A real-device verification must explicitly cover at least:

- permission grant and denial
- scan success
- cancellation/back navigation
- duplicate-frame/result protection
- background/resume behavior
- retry after lookup failure
- a reviewed local product
- an Open Food Facts fallback product
- camera release after leaving the scanner

Automated tests and emulator builds must not be described as physical-camera proof.

## Platform/deployment limitations

Android development is currently the primary target.

- Debug builds permit local cleartext HTTP for development.
- Release builds are not production-ready.
- Android still uses the placeholder application ID `com.example.ethico`.
- Release configuration still uses debug signing.
- iOS scaffolding exists but native iOS build/device behavior is unverified.

Before public distribution, assign a project-owned application ID and configure a
private release signing key outside Git.

## Immediate focus

1. Complete privacy/security cleanup and repository hygiene checks.
2. Complete scanner/end-to-end hardening.
3. Run and record privacy-first physical Android verification.
4. Run the small 3–5 reviewed-product learning pilot.
5. Continue with company identity resolution only after the pilot confirms the data model needs.

See [roadmap](roadmap.md), [architecture](architecture.md), and
[decisions](decisions.md) for the longer-term plan.
