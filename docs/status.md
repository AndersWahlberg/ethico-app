# Project status

## GitHub Actions CI — 2026-10-09

The containing CI commit/PR adds `.github/workflows/ci.yml` for pull requests into
`main` and pushes to `main`. Independent Ubuntu jobs run backend dependency
installation, curated-data validation and pytest on Python 3.12, and dependency
resolution, analysis and tests on Flutter 3.29.2 / Dart 3.7.2. There is no deployment,
secret configuration, or Android/iOS artifact build. Physical-device barcode
scanning, permissions, and device-to-API connectivity remain outside CI coverage.
GitHub run/job results are recorded in the PR; adding the workflow alone does not
establish a successful remote run. Earlier verification records below remain historical.

## Curated-data validation update — 2026-10-09

Startup now validates the complete curated JSON file before opening SQLite or
performing any schema/seed/import writes. The API and importer share the existing
EAN helper. Validation rejects malformed structures, missing/wrong-type/blank
required fields, invalid EAN shape/checksum, duplicate EANs, malformed/non-HTTP(S)
URLs, duplicate source URLs per product, and invalid YYYY-MM-DD calendar dates.
Nullable company roles and empty source lists remain supported; facts are not
normalized or overwritten. The curated product file and dependencies are unchanged.

From `backend`, run `.venv\Scripts\python.exe -m app.validate_curated` for a
database-free check; an optional file path checks a proposed dataset. Errors include
file/product/source/field context and return a non-zero exit code. The existing
database-preservation and idempotent-startup behavior remains in place.

Verification for the containing commit/PR on `feat/curated-data-validation`:

- `.venv\Scripts\python.exe -B -m app.validate_curated`: passed for the real dataset
  (one curated product).
- `.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
  --basetemp=C:\Users\anwah\Documents\Codex\2026-10-09\l-y\work\ethico-validation-final
  --tb=short`: **111 passed**, including 97 new parametrized validation/command/import
  cases; two existing Starlette HTTPX and AnyIO BlockingPortal deprecation warnings.
- From `frontend`, `flutter analyze`: no issues; `flutter test`: **12 passed**.
- Python syntax/indentation checks and `git diff --check` passed. No Python formatter
  or linter is configured/installed; no formatting dependency was added. These
  checks ran before the final test pass.

Tests prove that an invalid later product leaves a pre-existing legacy database
byte-for-byte unchanged, invalid input creates no new database, and the standalone
command returns success/failure without database access. Validation checks data
shape and identifiers, not source truth or live URL availability.

## UTF-8 decoding update — 2026-10-09

The Flutter API client now explicitly decodes successful response bytes as UTF-8
before JSON parsing. The API contract, status-code handling, backend, product data,
and dependency versions are unchanged. This update is recorded by the containing
commit/PR on `fix/flutter-utf8-json-decoding`.

A regression test in `frontend/test/product_details_test.dart` supplies raw UTF-8
bytes with `Content-Type: application/json` and no charset, then checks exact
product, brand, company, source-title, and source-scope text through `ProductApi.lookup`.
The focused test failed with the previous parser (`Crème München` became
`CrÃ¨me MÃ¼nchen`) and passed in the full suite after the fix.

Verification actually run with Flutter 3.29.2 / Dart 3.7.2:

- From `frontend`: `flutter pub get` passed with the lockfile unchanged;
  `flutter analyze` reported no issues; `flutter test` passed all **12 tests**.
- From `backend`: `.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
  --basetemp=C:\Users\anwah\Documents\Codex\2026-10-09\l-y\work\ethico-utf8-pytest
  --tb=short` passed all **14 tests**, with the existing Starlette HTTPX and AnyIO
  BlockingPortal deprecation warnings. Temporary databases were outside the repository.

The following baseline and its historical verification results are retained;
this update does not establish new physical-device or iOS verification.

## Historical baseline

Baseline reviewed: **2026-09-05**.
Implementation baseline: [ab7bcf5](https://github.com/AndersWahlberg/my-new-project/commit/ab7bcf5e9b7fa2fa867f872915b344c94eaf211e),
"Add first real product with source-backed manufacturer information".

This is a snapshot of the committed repository, not uncommitted local work.
The original September documentation update changed no application behavior.

## Current milestone

Ethico is an Android-focused product lookup MVP with source attribution.
A scan or manually entered EAN retrieves facts from a small local SQLite dataset.
The next development milestones remain proposals in the [roadmap](roadmap.md).

## Implemented

- EAN-8 and EAN-13 camera scanning, with manual entry as a fallback.
- Shape validation in Flutter and shape/check-digit validation in FastAPI.
  EAN values stay as text, preserving leading zeros.
- Product name, brand, company, company role, and fictional-demo labeling.
- Source title, HTTP(S) link, review date, and a statement of what the source supports.
  Source opening failures leave the product and copyable URL visible.
- Loading, invalid-input, not-found, network-failure, and timeout handling.
  Failed lookups clear the previous product.
- Camera lifecycle handling and protection against returning multiple detections.
  Camera images are decoded on the device; lookup requests contain only the EAN.
- SQLite initialization, an upgrade from the original schema, and transactional
  insertion of missing curated products and sources.
- GET /health and GET /products/{ean}.

## Data and evidence

The seeded dataset contains **three fictional demo fixtures and one real product**:
Leader Performance Creatine Monohydrate 300 g, EAN 6430051512933.
The recorded company is Leader Foods Oy with role manufacturer.

Two references are stored, checked on 2026-09-05. Kespro supports the EAN and
manufacturer mapping; Leader's page supports the product name and size.
These are product-fact sources, not an independent audit or an ethical rating.
See [the evidence notes](product-sources.md).

Existing local database rows can differ from the seed data. Editing
curated_products.json does not update an already imported record or its sources.

## Technology

- Python 3.12 in the documented development environment; FastAPI and Uvicorn.
- SQLite through Python's built-in sqlite3 module.
- Flutter 3.29.2 / Dart 3.7.2 in the documented development environment.
- Flutter packages: http 1.3.0, mobile_scanner 6.0.2, url_launcher 6.3.1.
- pytest and HTTPX for backend tests; flutter_test for client tests.

The requirements files and pubspec files are authoritative for dependencies.
See [architecture](architecture.md) for the API and platform details.

## Verification record

| Area | Evidence and limits |
| --- | --- |
| Backend at ab7bcf5 | On 2026-09-05, 14 tests passed in an isolated copy of the GitHub backend, using the existing project Python environment. Two upstream deprecation warnings concerned HTTPX TestClient and the AnyIO BlockingPortal alias. |
| Backend command | From the isolated backend directory: python -m pytest -q -p no:cacheprovider --basetemp=../test-temp-review --tb=short. A fresh review-specific temporary directory was used after the system temporary directory denied access. |
| Flutter at ab7bcf5 | 11 tests identified and reviewed across widget_test.dart and product_details_test.dart. They were not run in this repository review; current flutter analyze was not run either. |
| Earlier builds/tests | setup-notes.md records earlier backend/Flutter passes and an Android debug APK build. These are historical milestone results, not a full test run of ab7bcf5. |
| Physical phone | The project owner reported testing the app on a phone and successfully scanning one real product. This does not establish completion of every camera, source-link, or lifecycle acceptance check for ab7bcf5. |
| iOS | Project scaffolding and a camera usage description exist; a native iOS build and device behavior remain unverified. |
| CI | No GitHub Actions workflows or runs were found during the 2026-09-05 review. |

Backend tests cover lookup, leading zeros, invalid and unknown EANs, source
metadata, repeat initialization, preservation of existing rows, and schema upgrades.
Flutter tests cover lookup UI, loading/errors, response parsing, source display,
link-opening callbacks, demo labeling, missing evidence, and rejection of non-web
links. They do not exercise physical barcode decoding or a live mobile-to-API connection.

## Not implemented and known limitations

- No ethical evidence model, ethical scores, generative AI, automated web research,
  account system, payments, or production deployment.
- No separate company profiles, company identifiers, ownership graph, or automatic
  product-to-company resolution. A company name and role are stored per product.
- Other real products normally return not found because the dataset is small.
- No general workflow for correcting existing curated rows and sources.
- Local development requires a running backend and the appropriate API_BASE_URL.
  On-device decoding does not make the product lookup available offline.
- Android release still uses com.example.ethico and debug signing; these have
  explicit TODOs in the build configuration.
- Timeout UI and camera lifecycle/permission behavior need focused verification.
- No open GitHub issues or pull requests were found at review time.

## Immediate focus

Establish and maintain this documentation baseline before implementing another
feature. Choose the next milestone from the [roadmap](roadmap.md); ownership
research and ethical summaries should follow evidence and data-model decisions.
