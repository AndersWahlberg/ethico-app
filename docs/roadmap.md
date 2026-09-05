# Roadmap

Updated: **2026-09-05**.
Current implementation and test evidence: [status](status.md).

Only the documentation-first step is currently agreed in this discussion.
The development steps below are proposals, ordered to reduce uncertainty.
There are no promised delivery dates.

## Completed implementation milestones

- [x] Flutter client and FastAPI health endpoint.
- [x] Manual EAN lookup backed by SQLite.
- [x] EAN-8/EAN-13 camera scanner and lookup/error UI.
- [x] Fictional demo records explicitly distinguished from real data.
- [x] First real product with manufacturer role and scoped, dated source links.
- [x] Backend and Flutter automated test suites added.

Implementation completion does not imply every device/platform check passed.
See status for the exact verification record.

## D0 — Documentation baseline

Status: completed by this documentation change, before new feature work.

Completion criteria:

- README provides portable setup instructions and links to the documentation index.
- Status separates implemented behavior, test evidence, owner reports, and unknowns.
- Architecture describes the current API and storage.
- Roadmap distinguishes proposed work from completed milestones.
- Decisions record current choices and open product questions.
- Documentation maintenance and handoff instructions are available.

## P1 — Small real-product pilot

Proposed next product milestone: grow to 10–20 manually reviewed real products
across several brands and product categories.

Completion criteria:

- Each new EAN passes validation and has a source supporting the product match.
- Company roles have explicit evidence; unknown roles remain unknown.
- Source scope and review date are visible for every reviewed record.
- Representative products are checked by both scan and manual entry on Android.
- Record lookup success rate, incorrect matches, missing data, and review effort.
- Verify source links, permission denial, cancellation, repeated scans, and
  background/resume behavior using a dated manual test record.

The pilot should reveal which data source and company relationships are actually
needed before broader automated ingestion is chosen.

## P2 — Reliable data corrections and automated checks

Proposed engineering milestone, before repeated edits to existing curated data.

Completion criteria:

- Define and implement an explicit way to update product facts and sources together.
- Test corrections, repeat runs, conflicts with local edits, and rollback on failure.
- Preserve the meaning of source review dates and make changes traceable.
- Run backend tests, Flutter analysis, and Flutter tests in GitHub Actions.
- Add targeted coverage for timeout behavior and remaining meaningful error cases.
- Record supported tool versions and results; address dependency warnings deliberately.

## P3 — Company identity and relationships

Proposed after pilot findings.

Completion criteria:

- Stable company identifiers support a shared company profile across products.
- Manufacturer, brand owner, and parent company are distinct sourced relationships.
- Unknown and conflicting relationships can be represented without guessing.
- Schema migration preserves existing product/source data.
- UI and API make the scope and uncertainty of each relationship understandable.

## P4 — First ethical evidence profile

Proposed after company identity is sufficiently reliable.

Completion criteria:

- Agree the initial topic/category and one pilot company.
- Model each claim with its subject, source, relevant dates, scope, and uncertainty.
- Distinguish company statements from independent evidence and record conflicts.
- Manually review the first profile and validate that users understand its limits.
- Decide whether a rating is useful only after defining a defensible methodology.

## Later, subject to separate decisions

- AI summaries derived from reviewed evidence, with claim-level traceability and
  evaluation for unsupported statements, omissions, and conflicting sources.
- Automated source discovery/import after choosing sources and update rules.
- Wider deployment: hosted HTTPS backend, operations, backups, and release builds.
- Android application ID and proper release signing; iOS build and device checks.
- Offline behavior, alternatives, personalization, accounts, and payments only if
  supported by user needs and an explicit scope decision.

## Decisions needed before the next implementation

1. Which product categories and users should the first pilot serve?
2. Is manufacturer identity enough for the pilot, or is brand ownership essential?
3. What evidence is sufficient to display a company relationship?
4. Which ethical topic should the first manually reviewed profile address?

Record resolved choices in the [decision log](decisions.md).
