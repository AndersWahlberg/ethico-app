# Decision log

Recorded: **2026-09-05**.

D001–D005 capture choices already reflected in implementation baseline
[ab7bcf5](https://github.com/AndersWahlberg/my-new-project/commit/ab7bcf5e9b7fa2fa867f872915b344c94eaf211e)
and its architecture/source notes. Their recording date is not a claim about the
original decision date. D006 records the documentation-first direction agreed
with the project owner. Future proposals are kept separate below.

## D001 — Source-backed facts before ethical summaries

Status: adopted in current MVP.

Ethico first identifies products and presents sourced company facts. Future AI
should summarize evidence rather than invent ethical judgments.

Reason: product identity and attribution must be reliable before drawing conclusions.
Consequence: current source links support stated product facts only. Missing
information must not be presented as positive or negative ethical evidence.

## D002 — Keep the initial architecture small

Status: implemented.

Use Flutter for the mobile UI, FastAPI for HTTP/JSON, and SQLite for local backend
storage. Use setState for the current screen and explicit modules for scanning,
HTTP/parsing, result rendering, and database operations.

Reason: the current application has a small lookup flow.
Consequence: no ORM, microservices, or additional state-management framework is
required now. Revisit boundaries when concrete workflows justify them.

## D003 — EAN is text; the backend validates the check digit

Status: implemented.

Accept EAN-8 and EAN-13 with ASCII digits and a valid check digit. Store EAN as
text to preserve leading zeros. Flutter checks shape; FastAPI is authoritative.

Reason: identifiers are not numbers for arithmetic, and all clients need consistent validation.
Consequence: invalid codes return 422 and unknown valid codes return 404. Keep
invalid input distinct from missing coverage.

## D004 — Curated imports preserve existing data

Status: implemented, with an acknowledged update limitation.

Import missing curated products and their sources together in a transaction.
Do not overwrite existing rows or attach imported evidence to potentially edited
facts. Repeated startup must not refresh review dates.

Reason: protect local data and preserve the relationship between facts and sources.
Consequence: changing the JSON alone cannot correct an already imported record.
A deliberate correction workflow is proposed in roadmap P2; none exists yet.

## D005 — Android first, with local development networking

Status: implemented/documented platform scope.

Use an Android-focused development setup and compatible pinned Flutter plugins.
Decode barcodes on the device. Configure API_BASE_URL for emulator or USB testing.
Allow plain HTTP in Android debug builds only.

Reason: support the working development environment and test the core product flow.
Consequence: iOS is unverified, the backend still needs connectivity, and the
current Android release configuration is not ready for distribution.

## D006 — Maintain the documentation before the next feature

Status: agreed with the project owner on 2026-09-05.

Use README as the setup entry point and docs/status.md, architecture.md,
roadmap.md, and decisions.md as the shared project record. Keep source evidence
in product-sources.md and historical setup results in setup-notes.md.

Reason: implementation and product discussion need the same explicit baseline.
Consequence: update relevant documents alongside meaningful changes, distinguish
proposals from approved scope, and report test evidence without implying unrun
checks passed. Follow the [maintenance workflow](README.md).

## D007 — Read-only Open Food Facts fallback

Status: adopted 2026-10-09; implemented in `app/open_food_facts.py` and the lookup UI.

Keep local products authoritative. Use the Open Food Facts v3 product-read API
only on a local miss, without caching, writes, or mixing records into curated
SQLite. Promote the existing HTTPX 0.28.1 pin to runtime dependencies. Require a
matching barcode and nonblank name; keep missing brand and legal company unknown.

Reason: broaden product coverage without inventing legal identities or ethical
claims. Separate external retrieval dates from human review dates and show source,
scope and license. Failures/incomplete records return a retryable 503 rather than
a false 404. Consequence: live lookup depends on upstream availability and the
shared per-IP rate limit; company resolution remains a separate future layer.

## D008 — Evidence provenance and legal/status fidelity

Status: adopted 2026-10-09 as a project/architecture principle; documentation-only.
Implementation baseline: `b5274ecbc2b0ec290849f3dd3773d86d828f1704`; the containing
documentation PR records this decision.

Every material claim must be traceable to a source. Evidence status must not be
strengthened during ingestion, translation or summarization. Self-reported,
supplier-reported, independent and official evidence remain distinguishable;
missing facts stay unknown. Secondary aggregators must not erase primary-source
provenance. Conflicting claims remain separately attributable. License/reuse
constraints are part of integration design. AI may organize and summarize
evidence but may neither invent claims nor upgrade their evidentiary status.

Reason: complaints, investigations, proposals, settlements, recalls, benchmarks
and final judgments have different meanings. A shared display or ingestion path
must not turn them into a generic finding of misconduct or imply guilt through
an unsupported company/product relationship.

Consequences: the [source registry](data-sources.md) defines A–D source classes
(not a truth score), distinct statuses, future provenance metadata and rights
review gates. The [roadmap](roadmap.md) places hardening, deliberate corrections
and a small learning pilot before deeper evidence integrations. Ethical scoring
requires a separate transparent, reproducible, versioned methodology decision.
No connector, schema, API or dependency is changed by adopting this principle.

## Open proposals

The following are not adopted implementation decisions. Registry candidate
approval permits investigation/design, not automatic implementation or reuse:

- Complete a diverse 3–5-product learning pilot after remaining MVP hardening.
- Introduce stable company identities and sourced ownership relationships.
- Choose an ethical evidence schema, first category, and any rating methodology.
- Select and design candidate integrations, automated research, AI models or hosting
  through separately reviewed implementation scopes.
- Choose offline support, accounts, monetization, or an iOS milestone.

See the [roadmap](roadmap.md) for proposed order and completion criteria.

## Adding a decision

Assign the next D-number and record: date, status, decision, reason, consequences,
and code/issue/PR references. If a decision changes, mark the old one superseded
and link its replacement instead of silently rewriting the history.
