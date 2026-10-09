# Architecture

Implementation baseline reviewed on 2026-09-05: [ab7bcf5](https://github.com/AndersWahlberg/my-new-project/commit/ab7bcf5e9b7fa2fa867f872915b344c94eaf211e).
See [status](status.md) for verification and [decisions](decisions.md) for recorded rationale.

```text
Camera or manual EAN -> Flutter -> HTTP/JSON -> FastAPI -> validate EAN -> SQLite
                                                                         |
                                                           miss -> Open Food Facts
```

## Small, explicit responsibilities

- `main.dart` owns input, loading, result, and error state using setState.
- `scanner_screen.dart` owns the camera and returns one EAN through Navigator.
  A guard prevents multiple detections from closing multiple routes. The camera
  pauses on app inactivity, resumes on return, and is disposed when leaving.
- `product_api.dart` owns the HTTP request, a ten-second timeout, and JSON parsing.
  Tests inject an HTTP client; the screen closes only clients it creates.
- `main.py` maps lookup results to HTTP and uses `ean.py` for EAN shape/check-digit
  validation. The same helper is used by curated-data validation.
- `validate_curated.py` validates the complete JSON dataset before database access
  and provides the read-only `python -m app.validate_curated [path]` command.
- `open_food_facts.py` makes one HTTPS API v3 request only on a local miss.
  Its contract is a mapped product, None for upstream 404, or
  `ExternalLookupUnavailable` for failures/unusable responses. The app factory
  accepts a provider; its HTTPX transport is injectable for offline tests.
  HTTPX uses a three-second timeout per network operation, no retries, and no
  redirect following. A per-lookup client closes connections and does not retain
  cookies between users. There is no external cache, database write, or sync.
- `product_details.dart` displays product facts and per-source scope/date, and
  opens HTTP(S) source links in the browser using url_launcher.
- `database.py` initializes and queries products and their sources. Each operation
  closes its connection; queries use placeholders rather than SQL interpolation.

An application factory accepts a database path so tests can use temporary files.
No ORM, repository/service layers, or state-management framework is needed here.

## API contract

`GET /products/{ean}` accepts 8 or 13 ASCII digits with a valid check digit.
EAN remains text everywhere so leading zeros survive.

Success (200):

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

Unknown valid EAN after local and external lookup: 404 with
`{"detail":"Product not found."}`.

Local hits keep their existing response fields, facts, and reviewed sources and
make no external request. External results use the same product envelope, with
nullable `brand` and `company`, null `company_role`, and `is_demo: false`.
The provider requests `code,product_name,brands`. A nonblank product name and a
matching EAN are required. OFF's leading-zero normalization is accepted when the
valid EANs differ only in padding; Ethico returns the original requested EAN.
Missing/blank brand is null; reported brand text is retained without company inference.
Mismatched identifiers, invalid field types, incomplete identity, malformed JSON,
timeouts/network failures, rate limiting and unexpected HTTP statuses return 503:
`{"detail":"Product information could not be checked right now. Please try again."}`.
Flutter displays this distinct retryable message without upstream details.

Each external result has one source with `provider: "Open Food Facts"`, its
HTTPS product-page URL, scope, `license: "ODbL 1.0"`, a UTC `retrieved_on` date,
and null `checked_on`. Retrieval does not imply human review. Existing curated
sources retain their checked dates and serialized shape; additional optional
source fields are omitted when unset. SQLite and curated JSON remain unchanged.
Flutter explicitly renders `Company: Not yet resolved` and `Brand: Not supplied`
when those facts are missing. Attribution and retrieval dates appear in Sources.

Invalid length, characters, or check digit: 422 with a readable detail message.
The UI trims manual whitespace and checks length/characters; the backend is the
authority for the check digit. Errors clear the previous result.

`GET /health` returns `{"status":"ok"}`; it is a process check, not a database
integrity check.

## Database and evidence limits

The products table adds nullable `company_role` and boolean `is_demo` (stored as
an SQLite integer). A separate `product_sources` table has `ean`, `title`, `url`,
`checked_on`, and `supports`; `(ean, url)` is its primary key. One product can
have multiple references, each with a clear statement of what it supports.

Startup first reads and validates the complete curated file, before opening SQLite
or creating its parent directory. Invalid input raises a contextual `CuratedDataError`
without changing schema, demo rows, existing products, or sources. Validation covers
list/object shapes, required nonblank string fields, EAN checksums/uniqueness, source
HTTP(S) URLs with hosts, per-product duplicate URLs, and exact YYYY-MM-DD calendar
dates. It reuses the existing Pydantic HttpUrl validation for API-compatible URLs;
no dependency or schema framework was added. URL normalization is used only for
duplicate comparison (for example, host case and the default trailing slash);
original data is preserved for import. No live URL retrieval or fact verification occurs.

The nullable role must still be present. Empty source lists and an empty dataset
are allowed; additional fields are tolerated, but only the existing model's fields
are imported. Required text is checked without trimming or rewriting stored facts.
The command reports the first error; rerun it after correcting that error.

After validation, startup checks the old schema with PRAGMA table_info, adds missing columns, and
marks the existing three demo codes. It imports missing records from
`app/curated_products.json` with their sources in a transaction. Existing records
are preserved, and sources are attached only when a curated product is newly
inserted, to avoid attaching evidence to unrelated local edits. Repeated starts
do not duplicate data or refresh check dates. Changing an existing curated record
requires a deliberate database update alongside an evidence review; editing the
JSON alone does not overwrite that row.

The separate `app.apply_curated_corrections` maintenance CLI implements that
deliberate update. It validates all desired curated products and all correction
definitions before opening SQLite. One active definition per EAN records a reason
and complete expected/replacement facts and sources; replacement must match the
current curated entry. Source order alone is ignored during exact comparison.

Preview opens an existing database read-only. Explicit `--apply` uses an existing
read/write connection with foreign keys enabled and `BEGIN IMMEDIATE` before
classifying every target. A conflict, missing product or demo row blocks the whole
batch. Pending facts and sources are replaced in one transaction; any SQL/commit
failure rolls back all changes. Matching replacement is a successful no-op.
The command never initializes/upgrades the database or refreshes review dates.
Startup does not import or execute correction definitions. Git tracks definitions;
no schema, execution-history table or API change was added. See the
[correction guide](curated-corrections.md) for commands and multi-revision limits.

`checked_on` records the source review date, not the server startup date or a
guarantee of current accuracy. Unknown roles remain null and unsourced rows have
an empty sources list. The API validates source dates and HTTP(S) URLs.

The first real record is Leader's 300 g creatine product, EAN 6430051512933.
Kespro identifies the EAN and manufacturer; Leader's own page supports the
product name. Manufacturer, brand owner, and parent company are distinct roles.
This record asserts only the manufacturer role, with source attribution. No
ethical claims, scores, or independent manufacturer audit are implied.

## Dependencies and platform choices

Python: FastAPI, Uvicorn and HTTPX 0.28.1 at runtime, plus pytest for tests.
The previously used HTTPX pin is promoted from development requirements without
an upgrade. sqlite3 is built in.
Flutter: http 1.3.0, mobile_scanner 6.0.2, and url_launcher 6.3.1 for source links,
pinned for the installed Flutter
3.29.2 / Dart 3.7.2 and Android build tools. The scanner's bundled barcode model
works without a first-use model download, at the cost of extra app size.
The model decodes barcodes; no generative AI or ethical analysis is involved.

A newer scanner release inspected during implementation required newer native
build dependencies. We kept a compatible release instead of upgrading the
entire Android toolchain in this milestone.

Android debug HTTP is enabled for local development only. Release builds retain
HTTPS defaults. The API address is set with API_BASE_URL at build/run time;
the default targets the Android emulator. CORS is unnecessary for this native
mobile client. iOS native builds and camera behavior remain to be verified on macOS.

## Planned evolution

The current company field is a name stored on each product, not a separate company
entity or an ownership graph. Sources are associated with products; there is no
ethical-claim model. Proposed company relationships and
ethical evidence profiles are described in the [roadmap](roadmap.md).

### Evidence-source design direction (not implemented)

[D008](decisions.md#d008--evidence-provenance-and-legalstatus-fidelity) adopts
claim-level provenance and preservation of legal/evidentiary status. The
[source registry](data-sources.md) defines future metadata and integration gates.
Only Open Food Facts is currently an external API integration.

Future records should retain entity identifiers and matching basis, original
source and language, dates, jurisdiction, exact claim/scope/status, reporting role,
license/attribution and uncertainty. An authoritative publisher does not make an
allegation a finding. Ingestion, translation and summaries must not strengthen
status; contradictory claims remain separately attributable.

This is an architectural direction, not an implemented evidence/event schema or
API change. MVP hardening, traceable corrections and the small reviewed pilot
precede company resolution, stable entities and deeper evidence integrations.
