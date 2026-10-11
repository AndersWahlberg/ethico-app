# Scanner verification

## Automated verification

Verified on 2026-10-11 with Flutter 3.29.2 / Dart 3.7.2 and the unchanged
`mobile_scanner: 6.0.2` pin. The containing PR/commit identifies this implementation.

- `flutter pub get`: passed; dependency pins/lockfile unchanged.
- Dart formatting and `flutter analyze`: passed.
- Flutter suite: 49 tests passed (scanner session, real route with fake camera
  platform, scan-to-lookup with mocked HTTP, and existing UI/API tests).
- `python -m app.validate_curated`: passed.
- `python -m app.apply_curated_corrections --validate-only`: passed.
- Full pytest suite: 204 passed; one existing Starlette HTTPX deprecation warning.
  Windows temporary-folder access required an explicit isolated `--basetemp`
  under the ignored backend virtual environment.
- Repository hygiene and `git diff --check`: passed.

Changed files were reviewed against AGENTS.md: no personal contacts, local home
paths, account/device identifiers, secrets, environment files, databases, signing
material, telemetry, scan history, frame/image transmission, scan logging, or
developer-specific runtime URLs were added. Scanner changes introduce no network
requests; existing EAN-only lookup and local-first provider behavior are preserved.

Coverage includes ASCII EAN shape, single-result acceptance, duplicate frames,
initial readiness, permission-dialog transitions, pending start/stop races,
all non-resumed lifecycle states, cancellation, reopening, disposal, safe errors,
one lookup after scanning, clearing stale facts, and retry without rescanning.
The scanner route tests use the package's public platform interface as a fake;
they test Ethico navigation and cleanup, not native camera implementation.
All automated HTTP/provider behavior is mocked. No live Open Food Facts requests.

## Android build and emulator verification

- Android debug APK build: passed on 2026-10-11 using the installed toolchain.
- CAMERA and INTERNET permissions present; camera hardware remains optional.
- Application ID and signing configuration unchanged.
- Emulator runtime verification: **Not yet verified** in this task.

The debug build checks compilation only. CI does not prove camera hardware
behavior, permissions, real-device connectivity, or camera release. No iOS
camera verification was performed or claimed.

## Physical Android device verification

**Not yet verified.** No physical-device acceptance testing was performed in
this task. P2 remains partially complete until these results are recorded.

Fill in this record only after performing the tests. Do not put device serials,
personal contact details, or machine-specific paths in the repository.

| Field | Value |
| --- | --- |
| Date | Not yet verified |
| Device model | Not yet verified |
| Android version | Not yet verified |
| App commit/build SHA | Not yet verified |
| Backend configuration | Not yet verified |
| Tester (non-personal role label) | Not yet verified |
| Overall pass/fail/notes | Not yet verified |

Use USB forwarding (`adb reverse tcp:8000 tcp:8000`) and
`--dart-define=API_BASE_URL=http://127.0.0.1:8000`. Bind the backend to loopback:
`python -m uvicorn app.main:app --host 127.0.0.1 --no-access-log`.
Start with local/demo data. A local miss discloses the requested EAN and ordinary
HTTP metadata to Open Food Facts. The provider check below is a deliberate live
manual test, separate from automated tests. Do not persist scan traces or frames;
use temporary observation of request counts without logging raw EAN activity.

| Check | Pass/fail | Notes |
| --- | --- | --- |
| Launch app | Not yet verified | |
| Open scanner | Not yet verified | |
| Grant camera permission | Not yet verified | Include permission-dialog lifecycle transitions |
| Scan known valid EAN | Not yet verified | Start with local/demo data |
| Verify exactly one lookup | Not yet verified | Observe request count without retained EAN logs |
| Verify EAN populates input | Not yet verified | Preserve leading zeroes |
| Scan same product in a new scanner session | Not yet verified | |
| Cancel scanner with Android Back and app-bar Back | Not yet verified | No lookup, input change, or cancellation error; reopen |
| Deny camera permission | Not yet verified | Safe settings/manual-entry message |
| Confirm manual entry remains usable | Not yet verified | Return with Back after permission/camera error |
| Background app while scanner is open | Not yet verified | Include background during startup if practical |
| Resume app | Not yet verified | No overlapping starts |
| Scan after resume | Not yet verified | |
| Lookup failure and retry without rescanning | Not yet verified | EAN retained, old facts cleared; restore backend and retry |
| Scan curated Leader product | Not yet verified | EAN 6430051512933; verify reviewed facts/sources |
| Scan product resolving through Open Food Facts | Not yet verified | Live disclosure boundary; verify attribution and unknown company |
| Scan unknown valid product if practical | Not yet verified | Confirm actual absence; safe not-found message |
| Hold barcode in frame | Not yet verified | One navigation/result/lookup |
| Verify camera releases after leaving scanner | Not yet verified | Check cancellation, result, and background paths |

Granting permission through Android settings is not claimed to recover the same
scanner session automatically. Go back and reopen the scanner after changing
settings; verify that behavior on the device. Record failures and limitations
rather than inferring a pass from the automated suite or APK.
