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

## Open proposals

The following are not adopted decisions:

- Expand the pilot to 10–20 reviewed products.
- Introduce stable company identities and sourced ownership relationships.
- Choose an ethical evidence schema, first category, and any rating methodology.
- Select external data sources, automated research, AI models, or hosting.
- Choose offline support, accounts, monetization, or an iOS milestone.

See the [roadmap](roadmap.md) for proposed order and completion criteria.

## Adding a decision

Assign the next D-number and record: date, status, decision, reason, consequences,
and code/issue/PR references. If a decision changes, mark the old one superseded
and link its replacement instead of silently rewriting the history.
