# Initial setup record

## Commands and results

- Inspected the working directory using `Get-ChildItem` and `rg --files`, and
  checked tool locations with `Get-Command`. No existing project files or
  applicable AGENTS.md files were found.
- Created `backend/.venv` with the bundled Python 3.12.14 using `-m venv`.
- Installed FastAPI, Uvicorn, pytest, and HTTPX with `-m pip install`; recorded
  the resolved direct versions in the two requirements files.
- Generated Flutter with `flutter create --empty --platforms=android,ios
  --project-name ethico`, then replaced Hello World with the Ethico welcome screen.
  The installed SDK is Flutter 3.29.2 / Dart 3.7.2.
- Ran `flutter pub get`, `dart format lib test`, `flutter analyze`, and
  `flutter test`. Analysis found no issues; one widget test passed.
- Ran `python -m pytest -q`: one endpoint test passed. Starlette emitted
  deprecation warnings about HTTPX TestClient support and its AnyIO portal alias.
  These are dependency warnings, not failed assertions; no warnings were hidden.
- Ran `python -m pip check`: no broken requirements.
- Started Uvicorn on loopback port 8765 temporarily; `Invoke-RestMethod` returned
  `{"status":"ok"}` from `/health`, and `/openapi.json` returned HTTP 200.
- Ran `flutter devices`: only Windows desktop detected. No Android/iOS launch
  or native build was verified. Generation reported Java 25.0.2 with Gradle
  8.10.2 as newer than its known configurations; native build compatibility
  remains unverified.

## Local tooling issues

The normal Flutter Windows launcher failed. Commands used the existing Dart
executable and `flutter_tools.snapshot` directly, as shown in the README.
The SDK's `bin/internal/engine.version` was empty when inspected after the failed
launcher calls. It was backed up in the workspace's `work/` directory and restored
from the SDK's own Git HEAD. A stale engine package was refreshed by invalidating
`bin/cache/flutter_sdk.stamp` (also backed up) and rerunning `pub get`.
No Flutter upgrade or launcher-script edit was performed.

Within the Codex sandbox, Git needed a process-only `safe.directory` entry for
this specific Flutter SDK. `APPDATA` and, for analysis, `LOCALAPPDATA` pointed at
workspace scratch settings; `PUB_CACHE` retained the installed package cache.
An initial temporary empty package configuration kept Flutter's project search
inside the workspace; `pub get` replaced it with the real generated config.
These sandbox workarounds are not application dependencies or global settings.

## Lookup milestone verification

- Camera scanning explicitly added to scope by the user; manual input retained.
- Backend: 11 tests passed, with the same two upstream deprecation warnings.
- Flutter: 5 tests passed; static analysis found no issues.
- Real loopback HTTP lookups returned the expected fictional products, preserved
  leading zeros, and returned 404/422 for unknown/invalid codes.
- Android debug APK compiled with the camera plugin. SDK Platform 34 was installed
  by Gradle; the app NDK was aligned to 27.0.12077973 for the plugin.
- Physical camera decoding, permission prompts, and device-to-backend UI behavior
  still require the hands-on checks in README.md. iOS was not built on Windows.
