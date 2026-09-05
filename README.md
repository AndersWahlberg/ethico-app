# Ethico

Ethico helps users understand the companies behind products. Future ethical
claims must be source-backed; future AI will analyze evidence, not invent opinions.

## Current MVP

Scan an EAN barcode with the camera or enter it manually. Flutter requests a
product from FastAPI, which reads a small SQLite database and returns the product
name, brand, and company. All current records are fictional demo fixtures.

No ethical scores, AI, web research, accounts, payments, or production services.

## Run on your Android emulator (Command Prompt)

Start the backend in one terminal:

```cmd
cd /d "C:\Users\anwah\Documents\Codex\2026-09-05\i-want-to-start-a-new\outputs\ethico\backend"
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Startup creates `backend/data/ethico.sqlite3` and inserts missing demo records.
Existing rows are preserved. SQLite uses Python's built-in library.

Start your emulator in Android Studio's Device Manager. In a second terminal:

```cmd
cd /d "C:\Users\anwah\Documents\Codex\2026-09-05\i-want-to-start-a-new\outputs\ethico\frontend"
flutter pub get
flutter run
```

Stop the old app run first with `q`. Camera support is a native plugin, so this
change needs a full rebuild, not just hot reload. Flutter should use the JDK 17
configured during setup.

Tap **Look up product** after entering one of these:

| EAN | Product | Brand | Company |
| --- | --- | --- | --- |
| 2000000000015 | Demo Oat Drink | Demo Meadow | Fictional Meadow Foods |
| 2000000000022 | Demo Hand Soap | Demo River | Fictional River Care |
| 0000000000017 | Demo Tea | Demo Leaf | Fictional Leaf Foods |

These are test codes, not verified assignments to real products.
Try `2000000000039` for a valid but unknown EAN, and `2000000000016` for an
invalid check digit.

## Camera test

Tap **Scan barcode**, allow camera permission, and point the camera at an EAN-8
or EAN-13 barcode. The scanner returns one code and automatically performs the
same lookup as manual entry. QR codes and other barcode types are excluded.
Camera frames are decoded on the device; only the detected EAN is sent to the API.

An emulator's virtual camera may not show real products. Use an emulator camera
configured for your webcam or a physical Android phone for a realistic scan.
Real products will normally return **Product not found in the demo dataset**.
Also test denying camera access, backing out without scanning, backgrounding and
resuming the scanner, and scanning again after a result. Manual entry remains
available when the camera cannot be used.

## Backend address

The default `http://10.0.2.2:8000` reaches the host computer from the Android
emulator. In your computer browser, use:
- [API docs](http://127.0.0.1:8000/docs)
- [Demo lookup](http://127.0.0.1:8000/products/2000000000015)

For a USB-connected Android phone with debugging enabled, use the Android SDK's
`adb` tool to forward the port, then override the address:

```cmd
adb reverse tcp:8000 tcp:8000
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

If adb is not on PATH, its executable is in
`C:\Users\anwah\AppData\Local\Android\sdk\platform-tools`.
Only Android debug builds permit plain HTTP. iOS has a camera usage description
but has not been built/tested here; local iOS networking configuration is not
part of this Windows/Android milestone.

## Tests

From `backend`:

```cmd
.venv\Scripts\python.exe -m pytest -q
```

From `frontend`:

```cmd
flutter analyze
flutter test
```

Backend tests use isolated temporary SQLite files. Flutter tests mock HTTP
responses and test input, loading, results, invalid input, not-found, and failures.
They do not prove physical camera decoding or emulator connectivity.

## Structure

```text
ethico/
  backend/
    app/main.py          # Routes, validation, response schema
    app/database.py      # Schema, seed, parameterized SQL
    data/ethico.sqlite3  # Generated locally; ignored by Git
    tests/
    requirements.txt
    requirements-dev.txt
  frontend/
    lib/main.dart        # Input and result screen
    lib/product_api.dart # HTTP request and response parsing
    lib/scanner_screen.dart
    test/widget_test.dart
    android/
    ios/
    pubspec.yaml
    pubspec.lock
  docs/
    architecture.md
    setup-notes.md       # Historical first-iteration setup
```

On a fresh checkout, create `backend/.venv` with Python 3.12:
`python -m venv .venv`, then install the requirements above.
See [architecture](docs/architecture.md) for design decisions and the API contract.

