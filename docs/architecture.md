# Architecture

See [status](status.md) for current verification and [decisions](decisions.md) for
recorded rationale.

```text
Camera or manual EAN
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
   +----+------------------+
   |                       |
   v                       v
 SQLite local data     Open Food Facts
                         local miss only
```

## Responsibilities

- `frontend/lib/main.dart` owns manual input, loading, result, and error state.
- `frontend/lib/scanner_screen.dart` owns camera scanning and returns one EAN to the ordinary lookup flow.
- `frontend/lib/product_api.dart` owns HTTP lookup, timeout handling, and JSON parsing.
- `frontend/lib/product_details.dart` renders product facts and source metadata and opens HTTP(S) source links after user action.
- `backend/app/main.py` exposes the FastAPI routes and maps lookup outcomes to HTTP responses.
- `backend/app/ean.py` provides authoritative EAN shape/check-digit validation.
- `backend/app/database.py` owns SQLite initialization and lookup.
- `backend/app/validate_curated.py` validates the complete reviewed curated dataset before database access.
- `backend/app/apply_curated_corrections.py` performs explicit expected-state reviewed corrections.
- `backend/app/open_food_facts.py` performs one privacy-minimized, read-only external fallback request after a local miss.

The architecture deliberately remains small. There is no ORM, dependency injection
framework, account service, analytics stack, background sync, or microservice split.

## API contract

`GET /products/{ean}` accepts EAN-8 or EAN-13 values containing ASCII digits and a
valid check digit. EAN values remain strings so leading zeroes survive.

Successful local and external lookups use the same product envelope:

```json
{
  "ean": "2000000000015",
  "product_name": "Demo Oat Drink",
  "brand": "Demo Meadow",
  "company": "Fictional Meadow Foods",
  "company_role": null,
  "is_demo": true,
  "sources": []
}
```

Invalid input returns 422. A valid EAN absent from both local data and Open Food
Facts returns 404. Provider/network/unusable-response failures return a safe 503
without exposing upstream exception details.

`GET /health` is a process responsiveness check, not a database readiness probe.

## Local data

SQLite stores product facts and source metadata.

`products` contains:

- EAN
- product name
- brand
- company
- nullable company role
- demo flag

`product_sources` contains:

- EAN
- title
- URL
- review date
- statement describing what the source supports

Queries use SQLite placeholders rather than interpolating user input.

The local database is generated at runtime and is ignored by Git.

## Curated import

`backend/app/curated_products.json` is the reviewed desired dataset.

Startup:

1. validates the complete curated file
2. opens/creates SQLite only after validation succeeds
3. creates/upgrades the small schema
4. inserts missing demo and curated rows transactionally

Existing rows are deliberately not overwritten by ordinary startup. This avoids
silently attaching new evidence to locally edited or stale facts.

## Explicit corrections

Reviewed changes to an already imported curated row use the separate correction
workflow.

Each active correction records:

- EAN
- reason
- complete expected state
- complete replacement state

Replacement must match the current reviewed curated entry. Preview is read-only.
Explicit apply opens an existing database, enables foreign keys, reserves the write,
classifies all targets, and updates facts and sources in one transaction.

A conflict, missing target, or demo target blocks the entire pending batch.
Already-applied corrections are successful no-ops. Startup never automatically
executes correction definitions.

## Open Food Facts fallback

A local miss makes one HTTPS request to the Open Food Facts v3 product endpoint for:

- code
- product name
- brands

Properties:

- no retries
- no redirect following
- three-second timeout per network operation
- no cookies retained between lookups
- no external product persistence/cache
- no company inference
- requested EAN must match the returned valid identifier, allowing leading-zero normalization
- product name must be present and nonblank

The provider request User-Agent contains only the application name/version, for
example `Ethico/0.3.0`. It intentionally excludes developer identity, personal
repository URLs, email addresses, device identifiers, and other user-specific
metadata.

External results carry provider attribution, source URL, retrieval date, scope, and
license metadata. Retrieval is distinct from a human evidence review.

## Privacy and data flow

Camera barcode decoding happens on-device. Application code sends only the EAN to
the backend; it does not upload camera frames.

The application currently has:

- no accounts
- no analytics
- no telemetry
- no persistent scan history
- no on-device product cache

A backend operator can still observe ordinary HTTP request metadata. Because the
lookup EAN appears in the request path, default server access logs can record it.
Privacy-first local physical-device testing should therefore use loopback/USB
forwarding and may disable access logging when the test requires no scan trace.

A public deployment must explicitly design log minimization and retention rather
than inheriting development-server defaults.

## Source links

Source URLs are displayed to the user and only opened after a tap. Flutter accepts
only HTTP(S) URLs with a nonempty host before handing them to the platform browser.

There is no server-side arbitrary source fetching in the current application, so
this source-link flow does not create a current SSRF surface.

## Android development boundary

The default Flutter API address targets the Android emulator development bridge.
Debug Android configuration permits cleartext HTTP for local development only.

Release configuration is not production-ready:

- placeholder application ID remains
- debug signing remains configured for release builds
- production HTTPS/deployment controls are not implemented

Public distribution requires a project-owned application ID and private release
signing material kept outside Git.

## iOS

iOS scaffolding and a camera usage description exist, but native iOS build/device
behavior has not been verified. iOS should not be described as supported until a
native verification pass exists.

## Evidence model direction

Current company, brand, and role fields are still flat product-level values.
There is no implemented company entity graph or ethical evidence/event schema.

Future evidence records should preserve:

- stable entity identifiers and matching basis
- original source and source type
- dates and jurisdiction
- exact claim/status/scope
- self-reported vs independent role
- license/attribution
- uncertainty, supersession, and conflicts

An authoritative publisher does not automatically turn an allegation into a
finding. Ingestion, translation, and future AI summaries must not strengthen the
source's original evidentiary/legal status.

See [source registry](data-sources.md) and the D008 decision in
[decisions](decisions.md).

## Planned evolution

Near-term order remains conservative:

1. privacy/security cleanup
2. scanner/end-to-end hardening
3. real Android physical-device verification
4. small reviewed-product pilot
5. company identity resolution
6. stable company/relationship model
7. first official evidence integration
8. broader evidence/event schema and providers
9. conflict/uncertainty tooling
10. AI summaries
11. scoring only after separate methodology review
