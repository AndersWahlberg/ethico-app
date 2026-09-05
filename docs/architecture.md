# Architecture

Implementation baseline reviewed on 2026-09-05: [ab7bcf5](https://github.com/AndersWahlberg/my-new-project/commit/ab7bcf5e9b7fa2fa867f872915b344c94eaf211e).
See [status](status.md) for verification and [decisions](decisions.md) for recorded rationale.

```text
Camera or manual EAN -> Flutter -> HTTP/JSON -> FastAPI -> SQLite
```

## Small, explicit responsibilities

- `main.dart` owns input, loading, result, and error state using setState.
- `scanner_screen.dart` owns the camera and returns one EAN through Navigator.
  A guard prevents multiple detections from closing multiple routes. The camera
  pauses on app inactivity, resumes on return, and is disposed when leaving.
- `product_api.dart` owns the HTTP request, a ten-second timeout, and JSON parsing.
  Tests inject an HTTP client; the screen closes only clients it creates.
- `main.py` validates EAN shape/check digit and maps lookup results to HTTP.
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

Unknown valid EAN: 404 with
`{"detail":"Product not found in the local dataset."}`.

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

Startup checks the old schema with PRAGMA table_info, adds missing columns, and
marks the existing three demo codes. It imports missing records from
`app/curated_products.json` with their sources in a transaction. Existing records
are preserved, and sources are attached only when a curated product is newly
inserted, to avoid attaching evidence to unrelated local edits. Repeated starts
do not duplicate data or refresh check dates. Changing an existing curated record
requires a deliberate database update alongside an evidence review; editing the
JSON alone does not overwrite that row.

`checked_on` records the source review date, not the server startup date or a
guarantee of current accuracy. Unknown roles remain null and unsourced rows have
an empty sources list. The API validates source dates and HTTP(S) URLs.

The first real record is Leader's 300 g creatine product, EAN 6430051512933.
Kespro identifies the EAN and manufacturer; Leader's own page supports the
product name. Manufacturer, brand owner, and parent company are distinct roles.
This record asserts only the manufacturer role, with source attribution. No
ethical claims, scores, or independent manufacturer audit are implied.

## Dependencies and platform choices

Python: FastAPI and Uvicorn, plus pytest/HTTPX for tests. sqlite3 is built in.
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
ethical-claim model. Proposed company relationships, correction workflows, and
ethical evidence profiles are described in the [roadmap](roadmap.md).
