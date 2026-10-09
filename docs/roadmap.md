# Roadmap

Updated: **2026-10-09** (evidence-source strategy).
Current implementation and verification: [status](status.md).
Provider candidates and constraints: [source registry](data-sources.md).

Completed milestones reflect implemented work. Uncompleted steps are proposals,
not authorization to implement, and have no promised delivery dates. This revision
replaces the earlier 10–20-product expansion with a 3–5-product learning pilot,
after remaining hardening and traceable corrections. Existing P1/P2 labels are
retained for historical references; P2 now explicitly precedes P1.

## Completed implementation milestones

- [x] Flutter client and FastAPI health endpoint.
- [x] Manual EAN lookup backed by SQLite.
- [x] EAN-8/EAN-13 camera scanner and lookup/error UI.
- [x] Fictional demo records explicitly distinguished from real data.
- [x] First real product with manufacturer role and scoped, dated source links.
- [x] Backend and Flutter automated test suites.
- [x] Explicit UTF-8 response decoding and regression coverage.
- [x] Curated-data validation before database access, with a developer command.
- [x] Independent backend and Flutter checks in GitHub Actions.
- [x] Explicit curated corrections with expected-state checks, read-only preview,
  atomic facts/source replacement, conflict blocking and repeat-run safety.
- [x] Read-only Open Food Facts fallback on local misses, with attribution,
  retrieval dates, unknown legal company and no persistence.

Open Food Facts brand data does not establish company ownership. Its integration
does not complete the reviewed pilot, correction workflow or ethical evidence
milestones. Implementation completion does not imply all device checks passed;
see status for the actual verification record.

## Conservative development order

| Order | Milestone / gate |
| --- | --- |
| 1 | D1: source registry and evidence semantics (this documentation task) |
| 2 | P2: remaining MVP hardening, scanner/device verification and traceable corrections |
| 3 | P1: approximately 3–5 diverse, carefully reviewed real products |
| 4 | P3a: company identity resolution, PRH/YTJ first in Finland |
| 5 | P3b: stable legal entity, brand and sourced relationship model |
| 6 | P4: one small official Finnish evidence provider after design/terms review |
| 7 | P5: consolidate the evidence/event schema from the reviewed integration |
| 8 | P6: additional providers incrementally |
| 9 | P7: richer conflict and uncertainty tooling |
| 10 | P8: evaluated AI summaries of attributable evidence |
| 11 | P9: optional scoring only after separate methodology review |

Documentation/source research may run ahead. Deeper integrations must not bypass
hardening, the correction workflow or real-product learning. No exact order among
providers within a phase is committed. Minimum provenance, uncertainty and conflict
preservation apply from the first evidence record, not only at P5/P7.

## D0 — Documentation baseline

Completed in the 2026-09-05 documentation baseline: portable README setup,
implementation/test status, current architecture, proposals separated from adopted
decisions, and documentation maintenance/handoff instructions. This historical
milestone does not imply that later implementation or device checks were complete.

## D1 — Source registry and evidence semantics

Completed as documentation in this change: the [registry](data-sources.md) records
integrated/candidate/context/restricted uses, source classes, evidence statuses,
future provenance fields and license gates. [D008](decisions.md) adopts provenance
and legal/status fidelity. No new provider or evidence schema is implemented.

## P2 — Remaining MVP hardening and traceable corrections

Partially complete: the [traceable-correction workflow](curated-corrections.md)
is implemented and tested on temporary databases. Scanner/end-to-end hardening
and renewed physical-device verification remain unfinished.
Use the [technical audit](audits/2026-10-09-technical-audit.md)
as a historical reference; UTF-8 decoding, curated validation and CI findings have
already been addressed. Do not repeat completed work merely because it is in the audit.

Completion criteria:

- Strengthen scanner/end-to-end coverage where practical: cancellation, permission
  denial, lifecycle/background/resume, repeated scans and lookup failure/retry.
- Recheck the real Android barcode flow on a physical device when available.
  Record device/build/date and actual results; CI is not proof of camera behavior.
- [x] Implement a deliberate correction workflow with a reviewable diff,
  expected prior state and explicit conflict handling. Correct product facts and
  their sources together, with atomic writes, rollback and repeat-run safety.
- [x] Preserve before/after provenance and the meaning of review dates. Do not silently
  overwrite local edits, reset the database or refresh dates without human review.
- Keep CI green; address remaining meaningful error/timeout gaps and existing
  dependency warnings deliberately, without unnecessary upgrades.

## P1 — Small real-product learning pilot

After P2, aim for approximately **3–5 reviewed real products in total**, across
more than one product/company shape. Do not manually scale to dozens yet.

Completion criteria:

- Validate EANs and evidence for each product match. Distinguish brand,
  manufacturer and unresolved ownership; do not invent relationships for variety.
- Retain source scope and actual review dates. Exercise deliberate corrections.
- Check representative products by manual entry and real Android scanning.
- Record lookup success, incorrect matches, missing data and review/correction effort.
- Use findings to identify real entity/data-model requirements before broad ingestion.

Open Food Facts may help discovery; external retrieval remains distinct from
reviewed Ethico evidence. Product categories and users remain a scoped pilot choice.

## P3a — Company identity resolution

After pilot findings, investigate Finnish PRH/YTJ first for stable official company
identifiers. A product/brand-to-company match needs its own evidence; name similarity
alone is insufficient. Preserve matching basis, ambiguity and registry dates.
GLEIF/external identifiers and Wikidata may bridge identities where useful, subject
to coverage, primary-source checks and terms. Registry identity does not prove ownership.

## P3b — Stable entity and relationship model

Use the resolver/pilot findings to distinguish legal entities, brands, manufacturers,
brand owners and parents. Give identifiers namespaces and relationships attributable
sources, dates/validity and uncertainty. Support missing/conflicting relationships
without guessing. Review schema migration and API/UI implications before implementation;
preserve existing products and evidence.

## P4 — First official evidence-provider integration

Choose one small, high-confidence Finnish use case after a dedicated design review.
Candidates include Tukes's current Vaarallisettuotteet.fi service (MAREK successor),
KKV or Finlex. No provider is selected or authorized by this roadmap.

Review access/reuse/attribution, record coverage, legal status, entity matching and
user-visible wording. Bound the integration tightly and retain minimum provenance,
original status and uncertainty from the first record. Allegations, proposals,
settlements and final judgments must remain distinct. Evaluate a manually reviewed
example before expanding scope.

## P5 — Evidence/event schema

Consolidate and version a minimal schema using P4's concrete findings: status,
jurisdiction, dates, exact scope, source and entity, plus original language/status,
case/external identifiers, reporting role, license/attribution and uncertainty.
Do not strengthen a claim during ingestion or translation. Preserve corrections,
appeals and conflicting claims as separately attributable records.

## P6 — Incremental provider expansion

Add regulatory, human-rights, supply-chain and environmental providers one scoped,
reviewed integration at a time. Follow the registry's rights/access gates and prefer
originating authorities over aggregator-only references. Country/commodity risk,
facility emissions and benchmarks do not establish a company's misconduct or a
product's footprint without evidence supporting the exact claim and relationships.

Product-level carbon-footprint/LCA datasets remain a research TODO with **no named
or approved provider**. Separately verify legitimacy, methodology, coverage and
reuse rights, including units, boundaries, allocation, year/geography and uncertainty.

## P7 — Conflict and uncertainty tooling

Improve review/display workflows for contradictory sources, disputed entity matches,
corrections and stale records. Never silently merge contradictions. Basic preservation
and explicit unknowns are required from the outset; this phase adds richer tooling.

## P8 — AI evidence summaries, only later

Summaries must link material claims to attributable evidence and preserve status,
scope and uncertainty. Evaluate unsupported statements, omissions, translation errors
and conflicts. AI is not a fact source and may not invent or upgrade claims.

## P9 — Optional ethical scoring, separately reviewed

Data availability does not authorize a score. First design and review a documented,
reproducible, versioned, evidence-backed methodology with explicit normative choices,
coverage limits and uncertainty. Retain evidence visibility independently of a score.

## Other later work, subject to separate decisions

Hosted HTTPS operations/backups, Android release identity/signing, iOS builds/device
checks, offline support, alternatives, personalization, accounts and payments remain
outside this source-strategy task. Record adopted choices in the [decision log](decisions.md).
