# Architecture

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
- `database.py` initializes and queries a single products table. Each operation
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
  "company": "Fictional Meadow Foods"
}
```

Unknown valid EAN: 404 with
`{"detail":"Product not found in the demo dataset."}`.

Invalid length, characters, or check digit: 422 with a readable detail message.
The UI trims manual whitespace and checks length/characters; the backend is the
authority for the check digit. Errors clear the previous result.

`GET /health` returns `{"status":"ok"}`; it is a process check, not a database
integrity check.

## Database and evidence limits

One table: `products(ean TEXT PRIMARY KEY, product_name TEXT, brand TEXT,
company TEXT)`, with all name fields non-null. Startup inserts three fixtures
with INSERT OR IGNORE, preserving edits to existing rows.

This denormalized table deliberately keeps the first lookup readable. Brand,
manufacturer, and parent-company relationships will need separate modeling once
we introduce verified evidence. Current company values are fictional labels,
not researched ownership claims. No ethical claims or scores are generated.

## Dependencies and platform choices

Python: FastAPI and Uvicorn, plus pytest/HTTPX for tests. sqlite3 is built in.
Flutter: http 1.3.0 and mobile_scanner 6.0.2, pinned for the installed Flutter
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

## Next learning step

Walk through one lookup in the code and run the error cases. Then decide how
to replace fictional fixtures with a small, verified dataset and source records
before adding ownership research or ethical analysis.

