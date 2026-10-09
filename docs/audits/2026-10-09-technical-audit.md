# Ethico technical audit

- Audit date: **2026-10-09** (Europe/Helsinki).
- Inspected baseline branch: **main**, fetched and confirmed up to date before branching.
- Inspected commit: **867ca5c4b7a37b33018446f8abe4f55b28113607**.
- Audit branch: **docs/technical-audit-2026-10**.
- Initial working tree: clean.
- No application code, product data, dependencies, or configuration were changed.
  This document is the only repository content added by the audit.

## Scope and runtime evidence

Reviewed the tracked file inventory, Git history, [AGENTS.md](../../AGENTS.md),
[README](../../README.md), all project documents in the parent docs directory,
backend source/tests/requirements, Flutter source/tests/pubspec files, and relevant
Android/iOS manifests, build settings, entry points, and test scaffolding.
Application code is unchanged from `ab7bcf5`; subsequent commits add documentation
and development instructions. Findings concern this baseline, not future proposals.

| Tool/component | Evidence available during this audit |
| --- | --- |
| Git | `git --version`: 2.52.0.windows.1 |
| Python | Existing backend environment: 3.12.14 |
| SQLite | Python runtime reports 3.53.1 |
| Backend installed packages | FastAPI 0.141.1, Uvicorn 0.52.4, pytest 9.1.1, HTTPX 0.28.1, Pydantic 2.13.5, Starlette 1.6.0, AnyIO 4.15.1, pip 25.0.1 |
| Flutter/Dart | Documentation and existing generated package configuration record Flutter 3.29.2 / Dart 3.7.2. These are historical/configured versions, not successfully executed runtimes in this audit. |
| Flutter dependencies | pubspec and lockfile pin http 1.3.0, mobile_scanner 6.0.2, url_launcher 6.3.1; flutter_lints resolves to 5.0.0 |
| Android configuration | Gradle wrapper 8.10.2, Android Gradle plugin 8.7.0, Kotlin plugin 1.8.22, NDK 27.0.12077973; Java/Kotlin bytecode target 11. README specifies JDK 17 for the build toolchain. No native build was executed. |
| iOS configuration | Deployment target 12.0 and Swift language setting 5.0 in the Xcode project; no Xcode/iOS runtime verification |

No dependency upgrade or vulnerability-database scan was performed. Version age
alone is not treated as evidence of a vulnerability. External product pages were
not re-reviewed, and their recorded review dates were not advanced.

## 1. Actual architecture and data flow

```text
Manual text entry ------+
                       +--> LookupScreen --> ProductApi --> GET /products/{ean}
On-device EAN scanner --+                                      |
                                                              v
                                                     FastAPI EAN validation
                                                              |
                                                              v
                                                     SQLite product + sources
                                                              |
                                                              v
                                              JSON --> Product --> ProductDetails
                                                                      |
                                                            user taps source URL
                                                                      v
                                                              external browser

FastAPI startup --> schema initialization/upgrade --> demo seed + curated JSON import
```

| Responsibility | Actual implementation and reference |
| --- | --- |
| Manual entry and UI state | [main.dart](../../frontend/lib/main.dart): trims input, checks 8/13 ASCII digits, clears previous results, disables input while loading, handles success/errors with `setState`. Leading zeros survive because EAN is text. |
| Scanning | [scanner_screen.dart](../../frontend/lib/scanner_screen.dart): mobile_scanner restricted to EAN-8/EAN-13; accepts the first shape-valid detection, guards duplicate route returns, then returns the string through Navigator to the ordinary lookup flow. Decoding is on-device. |
| Lifecycle | Scanner observes inactive/resumed, stops/starts the camera when permission is reported, and disposes its controller. The lookup screen checks `mounted` after awaits and closes only the HTTP client it owns. |
| HTTP client | [product_api.dart](../../frontend/lib/product_api.dart): injectable HTTP client, build-time `API_BASE_URL`, emulator default `http://10.0.2.2:8000`, encoded EAN path, ten-second timeout, status mapping and JSON parsing. |
| API | [main.py](../../backend/app/main.py): application factory accepts a database path. `GET /health` checks process responsiveness only. `GET /products/{ean}` returns product JSON, 404 for unknown valid EANs, or 422 for invalid shape/checksum. |
| EAN validation | Backend `is_valid_ean` uses full-match ASCII digit validation and alternating checksum weights from the right. Flutter checks shape only. A valid checksum is not proof of a real product assignment. |
| Persistence | [database.py](../../backend/app/database.py): file-backed SQLite, parameterized SQL, connection per operation, explicit close. Products and sources are queried separately; sources are ordered by URL. There is no ORM or write API. |
| Initialization | Startup creates the original table if absent, inspects columns, adds role/demo columns, marks legacy demo codes, creates sources, and inserts seeds inside an explicit transaction. Foreign keys are enabled for that initialization connection. |
| Curated import | [curated_products.json](../../backend/app/curated_products.json) supplies one real product. `INSERT OR IGNORE` preserves existing products; sources are inserted only for a newly inserted product. Restarts do not refresh dates or correct existing rows. |
| Product and company facts | Backend Pydantic and Dart models carry EAN, product name, brand, company, nullable company role, demo flag, and a source list. Company and brand are strings on each product, not separate entities. |
| Evidence | Each source has title, HTTP(S) URL, checked date, and free-text `supports`. Backend response validation checks URL/date shape. It does not validate truth, relevance, independence, or import-time integrity. |
| Presentation and links | [product_details.dart](../../frontend/lib/product_details.dart): product facts, role, demo warning, missing-source message, scope/date, and selectable URL. HTTP(S) and nonempty host are checked before external launch. False/throwing launch results show a snackbar and retain the product. |

The current seed contains three explicitly fictional demo rows and one Leader
creatine product (EAN 6430051512933), with manufacturer role and two references.
[Product source notes](../product-sources.md) distinguish Kespro's product listing
from Leader's own product page. Neither is presented as an independent ethical
audit. There is no network research during lookup or source prefetching by the API.

## 2. Implementation status and evidence levels

### Implemented in code

Manual lookup, camera integration, API checksum validation, SQLite initialization
and legacy schema upgrade, curated import, demo labeling, scoped sources, source
links, loading/errors/timeouts, and scanner lifecycle hooks are present. The app
has no lookup history, account system, or on-device product cache.

### Covered by automated tests

The backend's 14 cases passed during this audit. They cover health, successful
demo/real lookup, leading zeros, malformed/unknown EANs, existing-row preservation,
idempotence, legacy migration, and source association. Eleven Flutter tests are
present and were inspected, but could not be executed here. They exercise manual
lookup/loading/errors, parsing, source presentation, demo/missing evidence, and
link callbacks. Coverage in source is distinguished from a current passing run.

### Manually verified only / historical verification

[Status](../status.md) records the owner's successful phone scan of one real
product. This is an owner report, not a repeated audit observation or a complete
acceptance run. [Setup history](../setup-notes.md) records earlier loopback HTTP
checks and an Android debug APK build, plus earlier test results. No physical
camera, permissions, external browser, lifecycle, emulator connection, or native
build was manually tested in this audit. The manual checklists in README and
product-sources are instructions, not proof that all their steps passed.

### Planned / not implemented

[Roadmap](../roadmap.md) proposes a 10-20-product pilot, repeatable corrections,
CI, company identity/relationships, and an ethical evidence profile. AI summaries,
automated discovery, ownership resolution, scores, alternatives, personalization,
accounts, payments, offline lookup, and production deployment are not implemented.
The [original vision](../project-idea.md) is explicitly marked as long-term scope.

### Documentation consistency

The current architecture, status, and decision records substantially agree with
the code. Earlier missing-document observations no longer apply: status, roadmap,
and decisions were added in `9769b87`. Their September dates and historical test
counts are clearly scoped; they should not be rewritten as October verification.
The status statement that no PR existed was true only at its recorded review time.
The architecture's statement that the API validates dates/URLs describes response
validation, not safe curated import. Its small scope should not be read as a claim
that every camera lifecycle path has been verified. Local ignored SDK paths are
stale in this environment; the portable README does not guarantee an installed SDK.

## 3. Technical risks and debt

No Critical finding was established. Important means a concrete correctness or
verification risk to address before expanding the pilot; it does not imply a
demonstrated production incident. Speculative failures are identified as such.

| ID / classification | Problem and repository evidence | Consequence and timing |
| --- | --- | --- |
| R1 **Important** | `product_api.dart` parses `jsonDecode(response.body)`. The pinned http 1.3.0 implementation defaults response text to Latin-1 when Content-Type lacks a charset. An in-memory probe of the installed backend JSONResponse emitted UTF-8 bytes with `application/json` and no charset. | Non-ASCII product/company/source text can become mojibake. Current seed and test strings largely hide this. Fix before adding Finnish/international records. This is a source-level finding plus backend encoding probe, not a successfully run Flutter reproduction. |
| R2 **Important** | `initialize_database` reads unvalidated dictionaries. No import-time EAN/checksum, nonempty text, date, URL, source-presence, or duplicate-EAN validation exists. `INSERT OR IGNORE` also suppresses product NOT NULL/duplicate conflicts. | Malformed metadata can persist until response validation fails; invalid EAN rows can be unreachable; duplicate/null-invalid products can be silently skipped. Other malformed input can abort startup. Validate before expanding curated data. Current seed is not alleged to contain these errors. |
| R3 **Important** | Existing curated rows and sources are never refreshed; sources are attached only when a product insert succeeds. No correction command or versioned update exists (`database.py`, decision D004). | Reviewed corrections can exist in Git while installations retain older facts. Preserve this deliberate protection until an explicit atomic, conflict-aware correction workflow exists; address before repeated data corrections. |
| R4 **Important** | No scanner or integration test exists; start/stop/dispose futures are unawaited, permission state gates resume handling, and only inactive/resumed are explicitly handled (`scanner_screen.dart`). | Permission restoration, rapid transitions, cancellation, repeated scans, and multiple visible codes are uncertain. The first shape-valid code wins; checksum failure happens after leaving the scanner. Verify before claiming the full scanning MVP reliable. No race or permission failure was reproduced. |
| R5 **Minor** | Broad catch in `main.dart` maps malformed response/type failures to a connection message. Missing `is_demo` defaults to false and missing sources to empty in `product_api.dart`. | API incompatibility looks like connectivity trouble; an incomplete demo response can lose its fictional label. Tighten contract/error tests with the next client reliability work. |
| R6 **Minor** | The non-web URL test supplies a callback that throws, but `_openSource` catches callback exceptions. The test asserts only the resulting snackbar. Several lookup fixtures omit role/demo/source metadata; 422 and 500 checks assert only the same exception class. | The URL test can pass even if the forbidden callback is invoked; fixtures can conceal API-contract drift; swapped error messages may pass. Fix assertions and fixtures in a focused test change. |
| R7 **Minor** | Python direct requirements are pinned but transitive versions are not locked; Pydantic is imported directly but supplied transitively by FastAPI. No CI workflow is tracked. Current backend tests emit two deprecations. Flutter SDK is unavailable locally. | Fresh environments may differ and regressions are not automatically checked. Record a reproducible supported environment and add CI; investigate warnings deliberately rather than upgrading during unrelated tasks. |
| R8 **Acceptable for current MVP** | Three independent shape regexes exist in backend, lookup UI, and scanner; only backend implements checksum. Validation is ASCII-only and preserves text EANs. | This is modest duplication across boundaries, not a proven checksum bug. A shared Dart helper could be useful when behavior changes; no cross-language framework is justified. Add a successful EAN-8 storage test. |
| R9 **Acceptable for current MVP** | Product/company/brand/role are flat strings. Source key is `(ean, url)`; checked date and scope are plain stored text. Schema evolution uses column inspection, not numbered migrations. | Aliases, multiple company roles, ownership periods, conflicting claims, and successive reviews of one URL are awkward. Revisit when real pilot cases require them; do not introduce a large graph/schema redesign now. |
| R10 **Acceptable for current MVP** | Build-time API URL defaults to an Android emulator HTTP endpoint; only debug manifest permits cleartext. Release uses debug signing and `com.example.ethico`; iOS remains scaffolding without verified plugin build/network setup. | Phone/other-platform use needs correct address/forwarding. Release configuration is not distribution-ready. Keep local scope explicit; HTTPS, signing, platform builds, and operational controls are required before public deployment. |
| R11 **Acceptable for current MVP** | `/health` does not query SQLite; local DB path is fixed by default. Reads use separate statements without an explicit read transaction, and foreign-key enabling occurs only on the initialization connection. | Adequate for startup-only writes and a tiny local service. Future writers must enable foreign keys and preserve a consistent fact/source snapshot; operations will need readiness checks, backups, and migrations. No current concurrent-write failure was observed. |

Privacy/security observations: camera frames are not sent by application code;
only EAN is requested, but a backend operator could still observe lookup traffic.
There are no accounts or stored user profiles. SQL is parameterized. Source URLs
are checked for web schemes and require a tap, avoiding arbitrary file/custom
scheme launches. Scheme checking does not certify the destination's safety or
independence, and a browser visit exposes ordinary request metadata to that site.
No server-side source fetching exists, so that flow creates no current SSRF path.
The API has no authentication or rate limits; this is a deployment boundary, not
an immediate requirement for the documented loopback development setup. Git ignore
rules exclude local databases, environments, and common build artifacts; this audit
is not a comprehensive secret-history or third-party security assessment.

## 4. Automated tests and exact execution results

### Commands executed

From `backend`, using the existing environment (PowerShell):

```powershell
& .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp='C:\Users\anwah\Documents\Codex\2026-10-09\l-y\work\ethico-audit-pytest' --tb=short
```

The sandboxed invocation stalled without output after creating the first health
test's temporary directory. It was interrupted with Ctrl-C and exited 1, without
a test summary. This is an incomplete run, not an assertion-failure result. Its
root cause was not established. The following retry ran outside the sandbox:

```powershell
& .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp='C:\Users\anwah\Documents\Codex\2026-10-09\l-y\work\ethico-audit-pytest-retry' --tb=short -o faulthandler_timeout=30
```

Result: **14 passed, 2 warnings in 0.49s; exit 0**. No test or application
configuration was changed. `-B` suppresses bytecode writes, pytest's cache was
disabled, and test SQLite files were directed outside the repository. The local
product database was not used by these tests.

Warnings, reported rather than suppressed:

- `StarletteDeprecationWarning`: using `httpx` with `starlette.testclient` is
  deprecated; the warning recommends `httpx2`.
- `DeprecationWarning`: `anyio.abc.BlockingPortal` alias is deprecated; the warning
  recommends `anyio.from_thread.BlockingPortal`.

From `frontend`:

```powershell
flutter analyze
flutter test
```

Both commands failed to launch: PowerShell reported that `flutter` was not
recognized. `Get-Command flutter,dart,git` found Git only. The SDK recorded in
ignored `android/local.properties` and `.dart_tool/package_config.json` points to
`C:\Users\anwah\Desktop\flutter`; its cached Dart executable and Flutter version
file were absent. A direct `dart.exe --version` attempt at that path also failed.
No SDK was installed, moved, repaired, or upgraded. **No Flutter analysis or test
pass is claimed.** Missing SDK is an environment limitation, not a failed Dart test.

Runtime inspection also executed `python --version`, `python -m pip list`,
`git --version`, and a `python -B -c` read of `sqlite3.sqlite_version`.

An additional in-memory Python probe (sent to the backend interpreter with `-B -`)
constructed `JSONResponse({'product_name': 'Maito \u00e4', 'company': 'Yhti\u00f6'})`,
printed its Content-Type/body hex, and compared JSON round trips after UTF-8 and
Latin-1 decoding. It returned `application/json`, UTF-8 round trip **True**, and
Latin-1 round trip **False**, exit 0. The cached http 1.3.0
`lib/src/response.dart` was read to confirm its missing-charset fallback. This
diagnostic is not part of the 14 tests and did not modify product data.

A second diagnostic confirmed the actual endpoint's response using a patched
in-memory lookup result, again via `python -B -` from `backend`, outside the
sandbox. The TestClient was not entered as a lifespan context, so database
initialization was not run:

```python
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import create_app
import json
record = dict(ean='6430051512933', product_name='Maito \u00e4', brand='Brand',
              company='Yhti\u00f6', company_role=None, is_demo=False, sources=[])
with patch('app.main.find_product', return_value=record):
    response = TestClient(create_app()).get('/products/6430051512933')
print(response.status_code, response.headers['content-type'])
print(json.loads(response.content.decode('utf-8'))['company'] == record['company'])
print(json.loads(response.content.decode('latin-1'))['company'] == record['company'])
```

Result: **200**, **application/json**, **True**, **False**, exit 0. The same
Starlette HTTPX deprecation warning appeared. This strengthens the backend-wire
evidence for R1 without claiming an executed Dart/client test.

### Coverage assessment

Backend coverage is useful for the present seed and lookup contract: invalid
length/ASCII/checksum, valid unknown EAN-8/13, leading zeros, real metadata, repeated
initialization, legacy upgrade, and preservation of edited local rows. The explicit
test preventing imported evidence from being attached to a pre-existing matching
EAN is particularly valuable for provenance.

Important backend omissions: malformed import rejection, rollback after a failed
source insert/schema change, duplicate/null-invalid seed handling, successful
stored EAN-8, and correction/conflict behavior once such a workflow exists.
Counts of exactly four/five products will need intentional revision when expanding
the seed; changing counts alone is not proof of data quality.

Flutter's eleven test definitions cover five lookup/API scenarios and six evidence
scenarios. Missing high-value cases are actual UTF-8 response bytes, the ten-second
timeout, real-with-sources to demo/404/422/network-failure transitions, retries after
failure, malformed field types, and scanner permissions/lifecycle/cancellation.
The test named "permits retry" stops after the 404 and does not perform a successful
retry. Link callbacks test the UI boundary, not a real platform browser launch.
The iOS `RunnerTests.swift` contains only an empty example test. No automated
camera decoding or Flutter-to-live-API integration test exists.

Verdict: **a reasonable backend/manual-lookup regression baseline, but insufficient
to certify the complete current scanning MVP**. Broad statement or line coverage
would not substitute for the missing boundary, evidence-transition, and device
checks. Current confidence is also limited by inability to rerun Flutter tests.

## 5. Current data model

| Concept | Representation | Strength and limitation |
| --- | --- | --- |
| Product | One `products` row; name, brand, company, role, demo flag | Simple facts are easy to inspect; there is no stable product identity independent of EAN or product revision history. |
| EAN | Text primary key and API path string | Preserves zeros; validates 8/13-digit checksum at lookup, but not at import. Other GTIN lengths are outside scope. |
| Brand | Required string | Displays a label, not a legal ownership assertion or shared brand identity. |
| Company | Required string per product | Supports today's attributed manufacturer; lacks identifiers, alias resolution, explicit nullable unknown company, and multiple companies. Empty/sentinel strings would be ambiguous. |
| Company role | Nullable free-text string | Unknown role can remain null; `manufacturer` is displayed nicely. No controlled vocabulary, relationship target, validity interval, or role-specific evidence link. |
| Source | `product_sources` row keyed by EAN + URL | Retains clickable provenance; the same URL cannot have multiple review snapshots for the same product. Sources are duplicated across products rather than shared. |
| Supported facts | Free-text `supports` | Communicates scope and limits well for a handful of reviewed records; cannot enforce claim-level attribution, conflicting facts, or structured uncertainty. |
| Review date | `checked_on` text, serialized as a Pydantic date | Records human review rather than restart time. Not a publication date, validity period, review identity, expiry, or assurance of current truth. |

The model correctly avoids inferring parent ownership or ethical quality from a
manufacturer listing. The API/UI retain unknown role and empty evidence, and the
notes explain company self-reporting. However, source type/independence is not a
structured field; it is communicated in prose. More products may introduce company
name variations, one brand with several manufacturers, multiple packaging EANs,
and disagreeing sources. Record these cases explicitly during the pilot rather
than forcing assumptions into existing strings. The current model does not yet
justify AI ethical summaries or ratings, and this audit proposes no major redesign.

## 6. Exactly five recommended next tasks

These are recommendations, not authorization to implement them. Scope estimates
exclude time waiting for a usable Flutter SDK or a physical device.

### 1. Decode API JSON explicitly as UTF-8

- **Objective:** remove the response-text charset ambiguity in R1.
- **Why now:** multilingual facts are basic data fidelity, and current ASCII-heavy
  fixtures conceal a concrete defect before the pilot grows.
- **Scope:** small, approximately 1-3 hours once Flutter is available; one focused fix
  and regression test. No dependency upgrade.
- **Likely files:** `frontend/lib/product_api.dart`, `frontend/test/widget_test.dart`
  or a focused API test, plus `docs/status.md` for actual verification.
- **Architecture:** unchanged; same HTTP contract and models.
- **Primary risks:** a String-based mock can accidentally hide the defect; invalid
  byte handling should remain a reported response error rather than silent repair.
- **Acceptance:** test UTF-8 `Response.bytes` with `application/json` and no charset,
  asserting exact accented product/company/source text; regression fails before
  the fix and passes after; Flutter analysis and relevant/full existing tests pass
  in a supported environment, or outstanding verification is explicitly recorded.

### 2. Validate the complete curated import before database writes

- **Objective:** reject malformed records and duplicate identifiers predictably.
- **Why now:** R2 affects the reliability of every additional manually curated row.
- **Scope:** small/medium, approximately half to one day; reuse EAN/domain logic,
  validate source metadata/nonempty text and uniqueness, and add failure/rollback
  tests. Define evidence requirements without guessing missing company facts.
- **Likely files:** `backend/app/database.py`, `backend/app/main.py` or a small shared
  validation module, `backend/tests/test_products.py`, and relevant status/architecture notes.
- **Architecture:** no topology or storage redesign; a small shared validation boundary.
- **Primary risks:** circular imports or accidentally rejecting preserved legacy/local
  rows. Validation should target import data while retaining existing-row protections.
- **Acceptance:** malformed EAN/date/URL/text and duplicate EANs fail with useful
  diagnostics; no partial import or overwritten existing row; current fixtures pass;
  repeat startup remains idempotent and dates do not advance automatically.

### 3. Strengthen evidence transitions and scanner verification

- **Objective:** establish reliable UI behavior at lookup and native boundaries.
- **Why now:** the current tests overstate retry/forbidden-link guarantees, and scanning
  remains underverified despite being a core MVP feature.
- **Scope:** medium, approximately one to two days plus Android device access; focused
  regression tests, explicit callback counters, and a dated manual acceptance record.
- **Likely files:** `frontend/test/widget_test.dart`, `frontend/test/product_details_test.dart`,
  a scanner test, possibly a minimal test seam in `frontend/lib/scanner_screen.dart`,
  and `docs/status.md`/a manual verification record.
- **Architecture:** unchanged; avoid a new state-management framework.
- **Primary risks:** mocked camera tests cannot establish native permission/decoding
  behavior; keep manual and automated evidence separate.
- **Acceptance:** forbidden callback count is zero; full-schema fixtures cover
  real-to-demo/error transitions, timeout, and successful retry; record permission
  denial/restoration, cancel, repeated detection, background/resume, and link return
  on Android with device/build identity. Report unresolved checks honestly.

### 4. Add an explicit, traceable curated correction workflow

- **Objective:** update reviewed facts and sources together without losing local edits.
- **Why now:** R3 blocks reliable corrections; complete before repeated data revisions.
- **Scope:** medium, approximately one to two days; preview/diff, explicit application,
  expected-existing-state conflict checks, transaction, and correction record.
- **Likely files:** a backend maintenance command, `backend/app/database.py`, backend
  correction tests, `docs/product-sources.md`, status/architecture/decision documentation.
- **Architecture:** adds maintenance tooling, preserving SQLite and the read API.
- **Primary risks:** silently overwriting local facts, attaching new evidence to old
  facts, or advancing dates without review.
- **Acceptance:** reviewed facts/sources change atomically; conflicts are reported;
  repeat application is safe; failure rolls back; corrections retain a traceable
  before/after record and never reset the database as a normal update strategy.

### 5. Establish reproducible automated checks

- **Objective:** run backend tests, Flutter analysis, and Flutter tests consistently
  for future pull requests.
- **Why now:** no tracked CI exists, and the local SDK gap prevents a current client
  verification result. Automation makes later pilot changes reviewable.
- **Scope:** medium, approximately one day after selecting the existing supported
  toolchain; add CI and concise environment/run instructions without blanket upgrades.
- **Likely files:** `.github/workflows/` workflow, README, `docs/status.md`, and, if
  separately justified, dependency constraints/lock metadata.
- **Architecture:** no application change.
- **Primary risks:** mismatched Flutter/native versions, hidden dependency drift,
  or presenting unit-test success as physical scanner acceptance.
- **Acceptance:** a clean checkout runs the three requested commands in CI, preserves
  data/configuration boundaries, surfaces the current deprecations, and records exact
  tool versions. Native device coverage remains explicitly outside these jobs.

## 7. One recommended next task

**Implement task 1: explicit UTF-8 JSON decoding with a byte-based regression test.**
It is the smallest concrete correctness fix, directly protects source-backed names
and evidence text, and does not alter schema or product scope. It should precede
the other four because more curated records will likely introduce non-ASCII text;
validation alone cannot prevent client-side corruption of valid server data.
Execution requires a usable Flutter environment to prove the regression. This
audit does not repair that environment or begin the implementation.

### Audit execution record

- Git commit inspected: `867ca5c4b7a37b33018446f8abe4f55b28113607` on updated `main`;
  audit performed on `docs/technical-audit-2026-10` derived from that commit.
- Working tree before audit: clean. No application/data/dependency/configuration
  edits were made; only this audit document is proposed for commit.
- Tests actually run: existing backend pytest suite; first invocation interrupted
  without a summary, retry outside sandbox **14 passed, 2 warnings, 0.49s**.
- Flutter commands actually attempted: `flutter analyze`, `flutter test`; neither
  could launch because Flutter was unavailable. Eleven test definitions reviewed,
  zero Flutter tests executed. No native build or physical-device check performed.
- Additional diagnostic: in-memory backend JSON encoding probe and read of pinned
  HTTP package decoding implementation support R1; no full Flutter reproduction.
- Unresolved uncertainties: initial sandbox stall cause; current camera/browser
  behavior; iOS build compatibility; exact current source-page contents; client
  regression results until the Flutter SDK is available. No security certification
  or claim that every possible defect was found is implied.
- Recommended next task: task 1, explicit UTF-8 JSON decoding and a byte-based test.
- Document validation: all 14 relative Markdown links resolved; exactly five task
  recommendations were confirmed; Git's staged whitespace check passed. The only
  changed repository file is `docs/audits/2026-10-09-technical-audit.md`.
- Completion boundary: audit/documentation PR only; do not merge or implement recommendations.
