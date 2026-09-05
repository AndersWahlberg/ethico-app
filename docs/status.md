# Project status

Last reviewed: **2026-09-05**.
Implementation baseline: [ab7bcf5](https://github.com/AndersWahlberg/my-new-project/commit/ab7bcf5e9b7fa2fa867f872915b344c94eaf211e),
"Add first real product with source-backed manufacturer information".

This is a snapshot of the committed repository, not uncommitted local work.
This documentation update changes no application behavior.

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
