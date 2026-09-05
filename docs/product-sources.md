# First real product: Leader creatine

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
facts and sources together in a deliberate database change; do not merely change
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
