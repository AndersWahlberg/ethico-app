# First real product: Leader creatine

This reviewed record is separate from the [external fallback](#open-food-facts-read-only-fallback) below.
The broader [source registry](data-sources.md) describes future candidates and
evidence rules; it does not extend the claims supported by this reviewed record.

Reviewed on **2026-09-05**. The user supplied EAN **6430051512933**, the product
description "kreatiinimonohydraatti", and manufacturer "Leader Foods". The EAN
passes the check-digit validation. The pack size and full display name were
resolved using the references below.

## Evidence

1. [Kespro product listing](https://www.kespro.com/tuotteet/leader-sport-nutrition-kreatiini-300g-ravintolisa-6430051512933)
   identifies GTIN 6430051512933, brand LEADER, a 300 g creatine product, and
   Leader Foods Oy under "Valmistaja". This is a trade product listing, not an
   independent audit. Its product content may require JavaScript; the indexed
   product text was available during review.
2. [Leader's product page](https://leader.fi/product/leader-creatine-monohydrate-300-g/)
   gives the display name "Leader Performance Creatine Monohydrate 300 g".
   This is the company's own product description. The EAN match relies on Kespro;
   the Leader page is not presented as independent proof of the EAN assignment.

The stored brand is Leader, company is Leader Foods Oy, and company role is
manufacturer. We do not infer brand ownership, parent company, ethical quality,
health benefits, or manufacturing location from this record. Source information
can change, and the check date does not update automatically.

## Storage and updates

The reviewed record is in `backend/app/curated_products.json`, versioned with
the code so another checkout can import it. New records and their sources are
inserted together at startup. Existing database rows are not overwritten by
subsequent imports. If correcting an existing row, review and update its product
facts and sources together using the explicit [correction workflow](curated-corrections.md); do not merely change
the JSON and assume the existing row has changed.

The three original demo records remain explicitly fictional and have no sources.
The app distinguishes missing source information from fictional data. Source URLs
open only after a user taps them; no web research occurs during a product lookup.

## Manual acceptance check

1. Restart the backend, rebuild the Flutter app (new native URL plugin), and keep
   the USB forwarding/API_BASE_URL used for the working Pixel setup.
2. Scan or enter 6430051512933 and verify the product, company, and manufacturer role.
3. Scroll through both sources; verify their scope and date. Open both in the browser.
4. Return to Ethico and look up a demo code; it must be labelled fictional and
   must not inherit the previous product's sources.
5. Try an unknown valid EAN; the old product and sources must disappear.

## Open Food Facts read-only fallback

Added 2026-10-09 as Ethico's first external product provider. Local SQLite products
take priority. A local miss makes one GET to
`https://world.openfoodfacts.org/api/v3/product/{ean}?fields=code,product_name,brands`.
The integration preserves reported name/brand text, not company identity or
ethical claims. Missing brand is null; missing name or mismatched code makes the
record unusable (503, not a claim that the product does not exist).

Open Food Facts is a community-maintained external dataset. Ethico does not
guarantee that supplied facts are complete or correct. API retrieval is not an
Ethico human evidence review: external sources carry `retrieved_on` (UTC), whereas
curated sources retain `checked_on`. External results include the provider,
product-page URL, precise scope, and visible `ODbL 1.0` attribution. No curated
sources are attached to external results. No external products or images are
stored, imported, or cached, and no writes are made to Open Food Facts.

Official references inspected for this integration:

- [API introduction and usage rules](https://openfoodfacts.github.io/openfoodfacts-server/api/)
- [API v3 schema](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/ref/api-v3.yaml)
  and [response status schema](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/ref/responses/response-status/response_status.yaml)
- [Barcode normalization](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-barcode-normalization/)
- [Licensing guidance](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/tutorials/license-be-on-the-legal-side/),
  [terms of use](https://world.openfoodfacts.org/terms-of-use), and
  [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1.0/)

The database is licensed under ODbL 1.0, and individual contents under the
Database Contents License. Keep Open Food Facts attribution and the source link
with its results. Future storage, combination or redistribution needs a separate
review of the attribution/share-alike requirements; this integration does not
merge third-party records into Ethico's curated database. The terms/wiki pages
returned bot protection during inspection; the official API and licensing guide
were accessible. The API introduction also asks reusers to register their use;
no registration, account creation or external correspondence was performed here.

Requests identify the app as
`Ethico/0.3.0 (https://github.com/AndersWahlberg/my-new-project)`;
the version is shared with the FastAPI application. The documented product-read
limit is **15 requests/minute/IP**, shared across this backend's users. There is
no rate limiter in this MVP: no automatic retries or redirects, and one request
per local miss. HTTPX has a three-second timeout per network operation (not a
total wall-clock deadline). A 429 or other upstream failure becomes a temporary
503. Capacity/rate-limit handling needs review before broader public use.

An external lookup reveals the requested barcode and normal HTTP metadata,
including the backend's network address and custom User-Agent, to Open Food Facts.
Ethico sends no device identity, account data, camera frames or analytics. Opening
a source link is a separate user-initiated browser request.
