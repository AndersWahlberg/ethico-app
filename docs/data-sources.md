# Ethico source registry

Reviewed **2026-10-09**, against implementation `b5274ecbc2b0ec290849f3dd3773d86d828f1704`
(Open Food Facts v1 merged). This is the official source registry and future
integration map, not a list of implemented connectors or a legal clearance.

**Ethico does not create facts. It identifies entities, gathers attributable
evidence, preserves provenance/status/licensing, and later explains that evidence
to users.** AI may summarize evidence; it must never supply an unsupported claim.

## Integration status and review discipline

| Status | Meaning |
| --- | --- |
| Integrated | A source is used by existing application code; scope is stated explicitly. |
| Approved candidate | Approved for future investigation/design, not implementation or unrestricted reuse. Must pass access, rights, entity-matching and evidence review first. |
| Research/context only | May inform research; not company-specific evidence or an approved product integration. |
| Restricted / on hold | A stated access, rights or reliability question blocks the proposed use. This can qualify a candidate without rejecting the provider's legitimacy. |
| Rejected use | The inference or acquisition method is unacceptable; the underlying source may still be useful for another purpose. |

Only Open Food Facts is an integrated external API. Kespro and Leader are existing
manually reviewed references, not API connectors; see [product sources](product-sources.md).
No other source below is called, ingested, cached or scored by Ethico.

Provider links below are first-party evidence for descriptions/access/terms, checked
where accessible on the review date. An advertised API is not a tested integration.
HTML-only means public search/documents were verified but a supported machine feed
was not established; it does not mean an API cannot exist. Blank JavaScript pages,
blocked pages and incomplete terms remain limitations, not grounds for bypassing them.
Recheck the selected dataset/version and terms before implementation and record the
review date, URL, applicable license, restrictions and decision in this registry.

For all entries, Ethico retains provider, original URL, date and document/record ID
even where legal attribution is optional. CC BY reuse requires credit, a license
link and indication of changes; CC0 has no attribution condition, but Ethico still
attributes. A general site policy does not automatically clear third-party files,
images, company statements or an entire underlying database.

## Source and evidence classification

| Class | Description | Examples and claim boundary |
| --- | --- | --- |
| A — Primary authoritative evidence | An authority's own record within its competence | Court judgment, regulator decision, register entry, recall notice, sanctions/debarment decision. Establishes what the record actually decides or records, within its jurisdiction and status. |
| B — Official/self-reported or structured institutional data | Officially hosted or structured reporting, with the original reporter retained | Company filings, modern-slavery statements, supplier product information and sustainability disclosures. Hosting or registration does not independently verify each assertion. |
| C — Independent secondary/benchmark/aggregated evidence | Attributed research, assessments or aggregation | NGO benchmarks, research platforms and source-linked aggregators. Preserve methodology and follow cited primary evidence when practical. Community aggregation is not an independent audit. |
| D — Context/research only | Evidence about populations or general conditions, not a specific entity's act | World Values Survey and similar research. Useful for design/research, not accusations about a company. |

A–D is **not a truth score, ranking of moral quality, or universal confidence
scale**. Authority depends on the claim. An official register can be A for the
existence of a filing and B for the company's assertions in that filing. An
official complaint establishes that a complaint was filed, not that its allegations
were proved. Assess exact subject, scope, date, completeness and supporting record.

## Evidence status model (future, not implemented)

Preserve the original status wording alongside a normalized status. These are
distinct events, not a progression every case follows or an ordinal severity scale.

| Status | Minimum interpretation to preserve |
| --- | --- |
| `allegation` | An identified party made a claim; no finding implied. |
| `investigation_open` | An authority is investigating; outcome unknown. |
| `regulator_notice` | A notice was issued; retain its exact type and legal effect. |
| `authority_proposal` | A proposed action/penalty, not an adopted outcome. |
| `enforcement_action` | The named authority took the stated action; retain appeal/review state. |
| `settlement` | An agreement on the stated terms; record admissions or no-admission terms explicitly. |
| `recall` | Identified products/batches/markets are subject to the stated recall; no intent inferred. |
| `court_judgment` | A court ruled; finality and appeal status may remain unknown. |
| `final_judgment` | Finality is supported by the source under the relevant procedure; never inferred just from age. |
| `sanction` | A specified sanction with grounds, authority, scope and effective dates. |
| `debarment` | Exclusion from specified procurement/activities for the stated period and conditions. |
| `self_report` | An entity's own disclosure, not independent verification. |
| `supplier_report` | Supplier-provided product/facility information; preserve submitter role. |
| `independent_assessment` | An assessor's finding under a named method, not a legal judgment. |
| `benchmark_result` | A result under a named methodology/version/year and comparison scope. |
| `scientific_or_statistical_context` | Research/statistics with population, methodology and limitations. |

An allegation, investigation, proposal, settlement, regulatory action and final
judgment are not equivalent. Never collapse them into “Company X committed
misconduct” unless the authoritative record supports exactly that claim. Retain
withdrawals, corrections, appeals, reversals and expiry as separately dated changes.
Unknown status remains unknown rather than being forced into a stronger category.

## Future provenance metadata

This is a design target, not a migration or current API/schema promise.

| Field | Intended meaning |
| --- | --- |
| `provider`, `source_url`, `source_type` | Publisher, original accessible record and A–D/record type; keep aggregator and originating source separately. |
| `retrieved_at` | Retrieval timestamp/time zone; never substitute for publication or human review. |
| `publication_date`, `decision_date` | Original dates where supplied; keep distinct, nullable and unguessed. |
| `jurisdiction` | Applicable authority/territory, not inferred from a company's address. |
| `entity_identifier` | Identifier plus namespace, entity type, matching basis and uncertainty; do not join solely on name. |
| `claim_type`, `evidence_status`, `original_status` | What event/claim is represented and its precise evidentiary/legal state. |
| `supported_claim`, `scope` | Exact supported proposition, subject, product/batch/facility, period and limitations. |
| `license`, `attribution` | Applicable terms/version/URL, rights holder, required credit and cache/redistribution/combination constraints. |
| `self_reported`, `reporter_role` | True/false/unknown plus company/supplier/authority/assessor origin; not guessed from host domain. |
| `original_language` | Original language, with translations labelled and linked to the original. |
| `external_id`, `case_number` | Stable record ID, court/authority and version when available. |
| `uncertainty`, `limitations` | Missing links, contested identity, coverage gaps, methodology and date limits. |
| `reviewed_at`, `supersedes`, `conflicts_with` | Separate human review and traceable correction/conflict relationships, where appropriate. |

Do not silently merge contradictory evidence. Keep each claim separately
attributable, with dates and status. An entity-match hypothesis is not evidence of
ownership or guilt. Absence of a record is not evidence of compliance or innocence.
Current `checked_on` and `retrieved_on` semantics remain as described in
[architecture](architecture.md); the richer model is future work.

## Product identity and safety

### S01 — Open Food Facts

- **Official source/access:** [API documentation](https://openfoodfacts.github.io/openfoodfacts-server/api/), HTTPS product-read API v3 and provider downloads. Ethico currently requests only `code,product_name,brands` on local misses; no persistence.
- **Scope/category/purpose:** International food-product identity/name/brand. Community-maintained aggregate (**C**, with supplier contributions **B**); not a legal register or independent ethical audit.
- **Terms/attribution:** [Licensing guide](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/tutorials/license-be-on-the-legal-side/): database ODbL 1.0; individual contents DbCL. Retain Open Food Facts, product URL and license. Images have separate rights and are not used. Review share-alike/database-combination obligations before any new storage/reuse. Terms/wiki bot protection prevented full inspection; **Needs license/terms review before integration** of additional uses. Existing v1 limits remain unchanged.
- **Safe claim / prohibited inference:** Name/brand as reported for a matched barcode; no legal company identity, ownership, ethical performance or guaranteed completeness. Custom User-Agent and the documented 15 product reads/minute/IP limit apply.
- **Ethico role/status:** **Integrated**, read-only product discovery fallback; reviewed local facts remain separate.

### S02 — Tukes MAREK / Vaarallisettuotteet.fi

- **Official source/access:** [Current portal](https://vaarallisettuotteet.fi/); [Tukes replacement announcement](https://tukes.fi/-/tunnista-vaarallinen-tuote-uudelta-vaarallisettuotteet.fi-sivustolta) confirms MAREK was replaced in 2022. Public HTML/search; reusable API/download and limits need investigation.
- **Scope/category/purpose:** Finland; market surveillance, dangerous/non-compliant products, withdrawals and recalls. **A** for authority notices; **B** for voluntary company reports. Multiple authorities and businesses contribute; retain issuer.
- **Terms/attribution:** Dataset-specific reuse/redistribution terms were not established from the portal/announcement. **Needs license/terms review before integration**. Preserve issuing authority/business, notice URL/date and original wording; exact required credit remains to be verified.
- **Safe claim / prohibited inference:** The identified product/model is subject to the specified notice/measure in Finland. Do not infer all products of a brand are unsafe, intentional misconduct, or that every entry is a Tukes order.
- **Ethico role/status:** **Approved candidate; rights/access on hold**. Possible small Finnish evidence pilot after design review. Legacy MAREK is a historical reference, not the preferred new connector target.

### S03 — EU Safety Gate

- **Official source/access:** [Safety Gate](https://ec.europa.eu/safety-gate-alerts/screen/webReport). Public alert search. An [official interface explanation](https://webgate.ec.europa.eu/safety/consumers/consumers_safety_gate/ProductSafetyLegislation/documents/Questions%20and%20answers%20on%20implementing%20and%20delegated%20regulations%20adopted%20by%20the%20Commission%20under%20the%20General%20Product%20Safety%20Regulation.pdf) describes an interface for registered online marketplaces; Ethico eligibility is unverified, not an assumed anonymous API.
- **Scope/category/purpose:** European dangerous non-food product alerts and measures; **A** for notifications from national authorities. Preserve notifying country and whether a measure is authority-ordered or voluntary.
- **Terms/attribution:** [Commission legal notice](https://commission.europa.eu/legal-notice_en) provides CC BY 4.0 for EU-owned website content with exceptions. It does not alone clear all national/third-party alert data or photos. **Needs license/terms review before integration**. Credit Commission and originating authority, alert ID and changes; verify record rights.
- **Safe claim / prohibited inference:** Specific risk/measure for a matching model/batch/market; not a global brand verdict or proof of intent.
- **Ethico role/status:** **Approved candidate; interface eligibility and record rights on hold**.

### S04 — RASFF / RASFF Window

- **Official source/access:** [Commission overview](https://food.ec.europa.eu/food-safety/rasff_en) and [public Window](https://webgate.ec.europa.eu/rasff-window/screen/search). Public search/summary notices; supported public API/bulk export not verified. Restricted authority access is out of scope.
- **Scope/category/purpose:** European food/feed safety notifications, hazards and measures (**A** for authority notification). Public records omit commercial details such as brands and business operators; coverage/date restrictions apply.
- **Terms/attribution:** Commission reuse policy is a starting point, not clearance for the notification dataset. **Needs license/terms review before integration**. Retain notification reference, origin/issuing authority, date and public URL; verify required credit and export rights.
- **Safe claim / prohibited inference:** State exactly what the public notification identifies. Never infer a company/brand from commodity, origin country or similar recalls; follow a linked public recall only for facts it identifies.
- **Ethico role/status:** **Approved candidate; access/rights review pending**. Limited safety context unless a reliable entity/product link exists.

### S05 — OECD GlobalRecalls

- **Official source/access:** [GlobalRecalls portal](https://globalrecalls.oecd.org/). International public consumer-product recall search; supported API/bulk reuse route unverified.
- **Scope/category/purpose:** Multi-jurisdiction recall discovery, **C** aggregation of originating **A** notices. The originating authority remains the evidence authority.
- **Terms/attribution:** [OECD terms, Data section](https://www.oecd.org/en/about/terms-conditions.html) permit reuse subject to dataset/third-party restrictions and citation. Portal content originates elsewhere: **Needs license/terms review before integration**. Retain OECD, dataset/year/URL/access date and original notice credit; verify each origin's terms.
- **Safe claim / prohibited inference:** A specified jurisdiction published a recall. Lookalike products may differ between markets; translations do not supersede the original notice. Do not universalize a recall.
- **Ethico role/status:** **Approved candidate; rights/access on hold**. Discovery bridge with primary-source links, not a replacement for them.

### S06 — ECHA SCIP

- **Official source/access:** [SCIP overview](https://echa.europa.eu/scip), [public database](https://echa.europa.eu/scip-database). Public search/factsheets; a public read API or bulk-download entitlement is not verified. Submission interfaces are not evidence of public read access.
- **Scope/category/purpose:** EU-market articles containing Candidate List SVHCs above **0.1% w/w**. **B**, supplier notifications in an official ECHA registry, not independently measured values for every product.
- **Terms/attribution:** [ECHA legal notice](https://echa.europa.eu/legal-notice) returned 403 during review. **Needs license/terms review before integration**. Preserve ECHA, SCIP number, supplier-reported origin, factsheet URL/date and exact scope; confirm required attribution and redistribution permissions.
- **Safe claim / prohibited inference:** A notification reports a substance in a specified article at the stated threshold/scope. No unsupported exposure/health claim, product-wide concentration extrapolation or inferred legal supplier identity from undisclosed fields. Public dissemination may omit submitter links/components and may lag submissions.
- **Ethico role/status:** **Approved candidate; access/rights on hold** for substance evidence, also relevant to environmental research.

### S07 — EPREL

- **Official source/access:** [EPREL](https://eprel.ec.europa.eu/), [Commission explanation](https://energy-efficient-products.ec.europa.eu/what-eprel_en), [supplier documentation](https://energy-efficient-products.ec.europa.eu/suppliers_en). Public model search, labels/product sheets and documented public API availability; Ethico credentials/conditions/coverage need investigation.
- **Scope/category/purpose:** EU energy-labelled product groups; energy-label/model parameters. **B**, supplier-submitted data in an official registry. Supplier verification does not independently verify every performance assertion.
- **Terms/attribution:** General Commission CC BY policy has exceptions; supplier content/API terms need dataset-level confirmation. **Needs license/terms review before integration**. Retain EPREL model ID, supplier, regulation/product-group context, date and label attribution.
- **Safe claim / prohibited inference:** Supplier-declared model values under the relevant label scheme, not a product carbon footprint, overall sustainability rating or independent audit.
- **Ethico role/status:** **Approved candidate; API/rights review pending** for product and environmental evidence.

## Company identity and relationships

### S08 — PRH / YTJ Open Data

- **Official source/access:** [Service and terms](https://avoindata.prh.fi/PRH%20Avoin%20data/info/swagger-ui), [YTJ API documentation](https://avoindata.prh.fi/fi/ytj/swagger-ui). JSON API and daily all-companies download; covered registered/pending Trade Register companies, not every entity type or every register field.
- **Scope/category/purpose:** Finland; Business IDs, registered names and basic registry information. **A** for registry identity/status; **B** where an underlying field is a filing assertion.
- **Terms/attribution:** CC BY 4.0, source attribution required. Provider prohibits use of PRH/YTJ logos or misleading service appearance. Preserve date and field provenance; confirm endpoint limits and coverage before implementation.
- **Safe claim / prohibited inference:** Registered identity/status as recorded; not that an EAN/brand belongs to that company, or that it is a product's manufacturer/owner. No guessed parent relationships. Sole traders/contact fields are excluded from the documented open dataset.
- **Ethico role/status:** **Approved candidate**, first Finnish company resolver after hardening/correction/pilot gates; not integrated.

### S09 — GLEIF / Global LEI Index

- **Official source/access:** [GLEIF API](https://www.gleif.org/en/lei-data/gleif-api/), [Global LEI Index](https://www.gleif.org/lei-data/global-lei-index), API plus Golden Copy/download files.
- **Scope/category/purpose:** Global entities with LEIs; structured identity and reported parent relationships (**B**, institutional LEI system, not a universal national register).
- **Terms/attribution:** [GLEIF open-data policy](https://www.gleif.org/en/about/open-data) states CC0. No CC0 attribution condition; Ethico still retains GLEIF/LEI, source/date, validation and registration status.
- **Safe claim / prohibited inference:** Identity and relationship as recorded. [Level 2](https://www.gleif.org/en/lei-data/access-and-use-lei-data/level-2-data-who-owns-whom) and [reporting exceptions](https://www.gleif.org/en/about-lei/common-data-file-format/current-versions/level-2-data-reporting-exceptions-2-1-format) concern accounting-consolidation parents and exceptions, not complete beneficial ownership. Absence is not absence of a parent.
- **Ethico role/status:** **Approved candidate** for identifier reconciliation and sourced relationships when available.

### S10 — Wikidata

- **Official source/access:** [Data access](https://www.wikidata.org/wiki/Wikidata:Data_access), [licensing](https://www.wikidata.org/wiki/Wikidata:Licensing). APIs, SPARQL/query service and dumps; choose a documented route and respect service limits.
- **Scope/category/purpose:** Global community knowledge graph, **C**; cross-dataset identifiers and discovery, not official company registration.
- **Terms/attribution:** Structured entity data CC0; other namespaces have different terms. Credit Wikidata under Ethico policy and preserve statement references, qualifiers, rank and retrieval/revision information.
- **Safe claim / prohibited inference:** A referenced identifier/linking hypothesis. Important legal/ownership claims require primary evidence where practical; do not treat a community statement or missing property as a verified legal conclusion.
- **Ethico role/status:** **Approved candidate** identifier bridge; not the authoritative company resolver.

## Courts, regulators and sanctions

### S11 — Finlex

- **Official source/access:** [Finlex open data](https://www.finlex.fi/fi/avoin-data), REST API, Akoma Ntoso XML and downloadable packages, plus public case-law search.
- **Scope/category/purpose:** Finland; legislation and published judicial/authority material. **A** for the underlying court/authority record; Finlex is a publication channel, not a guarantee of complete case coverage or entity identifiability.
- **Terms/attribution:** [Finlex policy](https://www.finlex.fi/fi/tietosuoja) states CC BY 4.0 for open data, with privacy-protective use constraints. Credit Finlex and issuing court, case ID/date, license and changes; do not reconstruct anonymized persons.
- **Safe claim / prohibited inference:** The court's specific holding with procedural status, jurisdiction, date and case number. Publication alone does not prove finality; match legal entities carefully and preserve appeals.
- **Ethico role/status:** **Approved candidate** for a narrowly reviewed Finnish judgment-discovery pilot; scope/API coverage still need design review.

### S12 — KKV / Finnish Consumer Ombudsman

- **Official source/access:** [KKV decisions](https://www.kkv.fi/paatokset/). Public HTML decision lists/documents and releases; supported reusable API/download feed not verified.
- **Scope/category/purpose:** Finland; competition and consumer-protection enforcement. **A** for KKV/Ombudsman actions, proposals and decisions; court outcomes must retain the court as issuer.
- **Terms/attribution:** No dataset-specific reuse grant established from the decisions page. **Needs license/terms review before integration**. Retain authority, decision/case ID, source URL/date and status; confirm required credit and document rights.
- **Safe claim / prohibited inference:** KKV investigated, proposed, decided or obtained the stated court outcome. A penalty proposal, commitment or investigation is not a final finding of misconduct.
- **Ethico role/status:** **Approved candidate; access/rights on hold**, possible small Finnish provider after a dedicated review.

### S13 — European Commission Competition case data

- **Official source/access:** [Case search](https://competition-cases.ec.europa.eu/), [antitrust search guide](https://competition-policy.ec.europa.eu/antitrust-and-cartels/cases-search-user-guide_en). HTML search and published documents; supported public API/bulk feed unverified.
- **Scope/category/purpose:** EU competition/antitrust/cartels (other case areas must stay separate). **A** for Commission acts, not automatic final court outcomes.
- **Terms/attribution:** [Commission policy](https://commission.europa.eu/legal-notice_en): CC BY 4.0 for EU-owned content unless excepted. **Needs license/terms review before integration** for case-dataset exports and third-party exhibits. Credit Commission, case number/document/date, license and modifications.
- **Safe claim / prohibited inference:** The specific procedural act/decision and legal scope. Keep objections, commitments, settlements, fines and appeals distinct; do not treat case appearance as infringement or a merger clearance as an ethical endorsement.
- **Ethico role/status:** **Approved candidate**, after company matching and evidence-status design.

### S14 — OECD NCP specific instances

- **Official source/access:** [NCP database](https://www.oecd.org/en/networks/national-contact-points-for-responsible-business-conduct/database.html), public searchable cases and linked NCP statements; reusable API/bulk export unverified.
- **Scope/category/purpose:** International responsible-business-conduct cases under OECD Guidelines. **C** for central aggregation; **A** for what an NCP officially states, not a court finding of guilt.
- **Terms/attribution:** [OECD data terms](https://www.oecd.org/en/about/terms-conditions.html) require citation and checking third-party/additional restrictions. **Needs license/terms review before integration** for case data and originating NCP documents. Retain OECD, NCP, case ID, statement/date/URL and access date.
- **Safe claim / prohibited inference:** A case was filed/accepted/closed and the NCP reported a specified outcome. Acceptance or mediation is not proof of allegations; preserve agreement, non-agreement and recommendations separately.
- **Ethico role/status:** **Approved candidate; dataset rights/access on hold** for traceable case discovery.

### S15 — World Bank debarred firms and sanctions

- **Official source/access:** [Ineligible firms/individuals list](https://documents.worldbank.org/en/projects-operations/procurement/debarred-firms), searchable tables and linked notes/decisions; stable public machine interface not verified.
- **Scope/category/purpose:** World Bank-financed procurement and applicable cross-debarment; **A** for Bank sanctions, not a universal criminal blacklist.
- **Terms/attribution:** [World Bank terms](https://www.worldbank.org/ext/en/legal/terms-conditions) do not establish a specific open license for this list in this review. **Needs license/terms review before integration**. Preserve Bank attribution, listing/decision URL, dates, grounds, notes and restrictions; verify redistribution rights.
- **Safe claim / prohibited inference:** The named legal entity is ineligible under the listed scope, period and conditions. Distinguish conditional non-debarment, cross-debarment and other sanctions; do not extend automatically to similarly named firms or every affiliate/product.
- **Ethico role/status:** **Approved candidate; rights/access on hold** for precisely matched procurement sanctions.

### S16 — US Federal Trade Commission (FTC)

- **Official source/access:** [Cases and proceedings](https://www.ftc.gov/legal-library/browse/cases-proceedings), public search/documents; a supported case-data API not established.
- **Scope/category/purpose:** US advertising, consumer protection and competition; **A** for agency proceedings/decisions and attributed court orders.
- **Terms/attribution:** [Website policy](https://www.ftc.gov/policy-notices/website-policy): most federal material is public domain; attribute FTC where feasible, do not imply endorsement, and clear third-party material separately.
- **Safe claim / prohibited inference:** Specific complaint, proposed/final order or settlement and its terms. Allegations, consent terms and litigated findings are different; no generic misconduct flag.
- **Ethico role/status:** **Approved candidate** when US entity/product relevance warrants; document-level rights and machine access still require design review.

### S17 — US Department of Justice (DOJ)

- **Official source/access:** [Developer resources/API](https://www.justice.gov/developer), news/press-release API and linked legal documents; not a complete court-docket API.
- **Scope/category/purpose:** US criminal/civil enforcement; **A** for DOJ's statements about its actions, with the court/order as primary source for adjudication.
- **Terms/attribution:** [Legal policies](https://www.justice.gov/legalpolicies): public domain unless otherwise indicated; source citation appreciated. Third-party material/insignia have separate restrictions; no implied endorsement.
- **Safe claim / prohibited inference:** Charge, complaint, plea, conviction, settlement or judgment exactly as documented. A charge is not guilt; press-release language must not erase court status or appeal.
- **Ethico role/status:** **Approved candidate** for discovery plus linked primary documents, scoped to relevant companies.

### S18 — US Securities and Exchange Commission (SEC)

- **Official source/access:** [Developer resources](https://www.sec.gov/about/developer-resources), [EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), public filings/downloads and agency enforcement documents. EDGAR filing APIs are not an enforcement-outcomes API.
- **Scope/category/purpose:** US securities; **A** for SEC actions, **B** for issuer-submitted filings. Retain CIK and filing/accession or case identifier.
- **Terms/attribution:** Automated access must follow [SEC access/security policy](https://www.sec.gov/about/privacy-information). Dataset/document reuse rights, especially company exhibits, were not fully verified: **Needs license/terms review before integration**. Retain SEC/issuer attribution, URL/date and source role; do not assume government hosting clears every exhibit.
- **Safe claim / prohibited inference:** Filing disclosure or exact enforcement status, not SEC verification of a company's every statement. Separate alleged securities violations, settlements and adjudicated findings.
- **Ethico role/status:** **Approved candidate; rights/endpoint scope on hold**.

### S19 — US Environmental Protection Agency (EPA / ECHO)

- **Official source/access:** [ECHO web services](https://echo.epa.gov/tools/web-services): public query APIs and linked bulk downloads for facilities, compliance and enforcement.
- **Scope/category/purpose:** US environmental regulatory programs; **A** for authority actions, **B** for reported facility measurements. Preserve source program, facility/permit ID and reporting period.
- **Terms/attribution:** [EPA disclaimers](https://www.epa.gov/web-policies-and-procedures/epa-disclaimers) explicitly vary by material and are not a blanket commercial-data license. **Needs license/terms review before integration** for the selected ECHO dataset. Retain EPA/originating program attribution and version/date.
- **Safe claim / prohibited inference:** Specified facility report, noncompliance status or enforcement event; not an adjudicated violation in every case and not a product carbon footprint. Ownership/product links require separate evidence.
- **Ethico role/status:** **Approved candidate; selected-dataset rights review pending**.

### S20 — US Consumer Product Safety Commission (CPSC)

- **Official source/access:** [Recall API documentation](https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information): REST JSON/XML recall data and public notices.
- **Scope/category/purpose:** US consumer-product recalls; **A** for official notices, retaining company/voluntary-recall origin where applicable.
- **Terms/attribution:** [CPSC policy](https://www.cpsc.gov/About-CPSC/Policies-Statements-and-Directives/Privacy-Policy) permits copying/linking recall notices and asks for CPSC credit, without endorsement. Image rights vary outside permitted recall-notice uses; images are not a proposed Ethico requirement.
- **Safe claim / prohibited inference:** Identified model/batch/market has the stated recall/remedy. No inferred intent, all-brand risk or worldwide recall scope.
- **Ethico role/status:** **Approved candidate** for precisely matched US product safety evidence.

### S21 — US Food and Drug Administration (FDA / openFDA)

- **Official source/access:** [Enforcement API documentation](https://open.fda.gov/apis/drug/enforcement/understanding-the-api-results/); openFDA APIs/downloads for relevant food/drug/device datasets. Choose the correct endpoint; linked original FDA recall records remain primary.
- **Scope/category/purpose:** US FDA-regulated products and recalls/enforcement reports, **A** for official record/status; preserve reporting firm, recall classification/status, dates and product identifiers.
- **Terms/attribution:** [openFDA license](https://open.fda.gov/license/): generally CC0/public domain unless noted, subject to service terms and other rights. GMDN content has explicit licensing restrictions and is excluded from candidate reuse until separately cleared. Ethico attributes FDA/openFDA and the original record despite CC0.
- **Safe claim / prohibited inference:** Exact recall/enforcement facts, not medical advice, intentional misconduct or every product sold by the named firm. Harmonized identifiers may be incomplete; verify matches and source dates.
- **Ethico role/status:** **Approved candidate** for applicable recall datasets; **restricted** for separately licensed fields such as GMDN.

## Human rights, labour and supply chains

### S22 — US Department of Labor ILAB

- **Official source/access:** [List of Goods Produced by Child Labor or Forced Labor](https://www.dol.gov/agencies/ilab/reports/child-labor/list-of-goods), HTML, reports, spreadsheets and bibliographies; API access for this exact list is not assumed.
- **Scope/category/purpose:** Global country/commodity risk compiled by a US authority. **A** for ILAB's official listing; underlying research remains attributable, not a company-specific judgment.
- **Terms/attribution:** [DOL copyright policy](https://www.dol.gov/general/aboutdol/copyright): federal-created material generally public domain, third-party text/images may not be. Credit DOL/ILAB, edition and country/good; check rights before reproducing cited research.
- **Safe claim / prohibited inference:** ILAB lists a named good/country for a specified risk. This **does not prove a particular company or supply chain uses child/forced labour**; no automatic company flags from country/commodity overlap.
- **Ethico role/status:** **Approved candidate for risk context only**, requiring separately evidenced supply-chain links before any company-specific use.

### S23 — UK Modern Slavery Statement Registry

- **Official source/access:** [Home Office registry](https://modern-slavery-statement-registry.service.gov.uk/), searchable statements and CSV statement-data downloads; public API unverified.
- **Scope/category/purpose:** Disclosures by organizations with UK business scope and voluntary participants. **B**, company/self-reported statements hosted by government; registry coverage is incomplete.
- **Terms/attribution:** CSV availability does not establish rights over company statement PDFs. Dataset-specific reuse terms/third-party statement permissions not confirmed: **Needs license/terms review before integration**. Attribute registry plus submitting company, statement year and original URL; do not apply a generic GOV.UK license to all attachments.
- **Safe claim / prohibited inference:** Company published or reported specified policies/actions for a given year. Neither publication nor absence of a statement proves abuse is absent/present.
- **Ethico role/status:** **Approved candidate; rights review pending** for transparently labelled disclosures.

### S24 — Open Supply Hub

- **Official source/access:** [Open data model](https://info.opensupplyhub.org/resources/an-open-data-model), [FAQs](https://info.opensupplyhub.org/faqs), search/downloads and paid API/bulk offerings. Facility IDs and contributor-linked records are available; access level depends on service terms.
- **Scope/category/purpose:** Global production facilities/supply-chain links; **C** aggregate with contributor-origin **B** assertions, not a legal company register.
- **Terms/attribution:** FAQs describe CC ShareAlike 4.0 data; [API terms](https://info.opensupplyhub.org/resources/api-terms-of-service) impose contractual conditions, including restrictions on sharing facility information with data brokers. **Needs license/terms review before integration** to reconcile selected data license, attribution/share-alike and API/redistribution terms. Preserve OS Hub/OS ID, contributor and record date.
- **Safe claim / prohibited inference:** A contributor reported a facility relationship at a date. Not independently verified legal ownership or proof that every product of a brand came from that facility.
- **Ethico role/status:** **Approved candidate; access/terms on hold** for facility/entity discovery.

### S25 — Wikirate

- **Official source/access:** [Data](https://wikirate.org/Data), [reuse/export guide](https://wikirate.org/How_to_Use_Data); API and CSV exports.
- **Scope/category/purpose:** Global ESG/CSR research and metrics, **C** aggregation; underlying company disclosures stay **B**. Preserve contributor, metric definition, year and cited source.
- **Terms/attribution:** Content generally CC BY 4.0 unless otherwise indicated; database infrastructure CC BY-SA 4.0 per the reuse guide. Attribute Wikirate/metric/source and changes; examine each metric/data license and primary document before redistribution or database combination.
- **Safe claim / prohibited inference:** A cited metric answer/assessment for a stated year and method. Follow primary sources when practical; do not transform sourced self-report or a metric score into independent proof of misconduct.
- **Ethico role/status:** **Approved candidate** for discovery/structured evidence, subject to per-metric rights review.

### S26 — World Benchmarking Alliance (WBA)

- **Official source/access:** [WBA](https://www.worldbenchmarkingalliance.org/), benchmark publications, methodologies and results; confirm exact dataset export/API terms for the chosen benchmark.
- **Scope/category/purpose:** Selected global companies and thematic benchmarks, including human rights. **C**, independent benchmark assessment; underlying evidence can include company disclosures and third-party sources.
- **Terms/attribution:** [Current disclaimer](https://www.worldbenchmarkingalliance.org/disclaimer) states CC BY 4.0 for work/publications/benchmarks. Some [older scorecards](https://assets.worldbenchmarkingalliance.org/app/uploads/2022/11/Nvidia-CHRB-scorecard-2022.pdf) carry CC BY-NC-ND 4.0: do not assume the current general notice relicenses every historical file. **Needs license/terms review before integration** of the chosen edition/tools. Credit WBA, benchmark/methodology/version/year and changes.
- **Safe claim / prohibited inference:** An assessment result for that benchmark/year/scope, not a court/regulator finding or universal ethical score. Missing disclosure and proven poor conduct are distinct.
- **Ethico role/status:** **Approved candidate; edition/tool rights on hold**.

## Environmental and emissions evidence

### S27 — EEA / European Industrial Emissions Portal

- **Official source/access:** [Portal](https://industry.eea.europa.eu/), [dataset catalogue](https://www.eea.europa.eu/en/datahub/datahubitem-view/9405f714-8015-4b5b-a63c-280b82861b3d/folder_contents). Tabular/spatial downloads and documented map/data services; choose a version and reporting year.
- **Scope/category/purpose:** Reporting European countries/facilities; pollutant releases/transfers, industrial emissions and selected energy data. Official EEA aggregation (**B** for operator/national reporting, **A** for the publication record); not a finding of illegality merely because emissions are reported.
- **Terms/attribution:** [EEA reuse policy](https://www.eea.europa.eu/en/legal-notice): CC BY for EEA-owned material unless otherwise specified, acknowledge EEA and preserve meaning; third-party content may differ. **Needs license/terms review before integration** of the selected dataset/version metadata. Retain EEA, reporting authority, facility ID, year, units and dataset citation/license.
- **Safe claim / prohibited inference:** The reported quantity for the facility/pollutant/period, preserving measurement/estimation and threshold limits. No automatic attribution to a brand/product or conversion into product carbon footprint without sourced relationships and an appropriate method.
- **Ethico role/status:** **Approved candidate**, environmental evidence after entity/facility linkage design. S06 SCIP and S07 EPREL also contribute only within their specific scopes.

### Research TODO — Product carbon footprints / life-cycle assessment

No provider is named or approved here. Separately verify legitimacy, methodology,
coverage and reuse rights before adding one. Require functional unit, system
boundary, allocation method, geography/year, version, primary versus modelled data
and uncertainty. Non-comparable footprints must not manufacture numerical precision
or support an unreviewed ethical score. Facility pollution is not product LCA.

## Research/context only

### S28 — World Values Survey (WVS)

- **Official source/access:** [WVS](https://www.worldvaluessurvey.org/), [download registration](https://www.worldvaluessurvey.org/AJDownloadLicense.jsp); survey downloads/documentation and analysis tools, with edition-specific conditions. No product-integration API verified.
- **Scope/category/purpose:** Cross-national academic/social-science population surveys (**D**). Potential user-values, weighting-preference or cross-cultural design research, with sampling/year limitations.
- **Terms/attribution:** [Integrated survey conditions](https://www.worldvaluessurvey.org/WVSContents.jsp?CMSID=intconduse) require non-profit use, no data-file redistribution and prescribed citations/reporting for the described edition. Do not generalize that grant to all waves. **Needs license/terms review before integration**, especially commercial use; no raw-data redistribution without permission.
- **Safe claim / prohibited inference:** Population-level responses under the study's method. Never evidence that a specific company committed an act, nor a basis for projecting national attitudes onto an individual/company.
- **Ethico role/status:** **Research/context only; commercial/product reuse restricted pending terms review**. Company-misconduct use is **rejected**.

## General integration rules

1. **Prefer primary sources.** When an aggregator cites a regulator, court,
   register, company filing or scientific publication, retain/link that original
   alongside or instead of the aggregator, preserving who made which assertion.
2. **No guilt by association.** Commodity labour-risk listing is not proof about
   a company's supply chain; facility presence is not proof about every branded
   product; a complaint is not a finding; a recall is not intent; facility pollution
   is not a product carbon footprint. Each relationship requires its own evidence.
3. **Label self-reports.** Company sustainability statements, slavery statements
   and supplier submissions remain visibly distinguishable from independent and
   official findings, even when hosted on a regulator's domain.
4. **No silent scoring.** Data availability does not authorize ethical scoring.
   Any scoring methodology needs separate review, documentation, reproducibility,
   versioning, evidence and explicit normative choices/uncertainty. AI summaries
   come later and may neither invent facts nor strengthen source status.
5. **License compliance before copying/integrating.** Verify current provider and
   dataset terms, required attribution, redistribution/cache/database-combination
   restrictions and third-party rights. Prefer intentionally offered APIs/downloads.
   Public accessibility alone is not permission to redistribute. Do not bypass
   authentication, paywalls, rate limits or bot protection, or scrape around access
   restrictions. If rights are unclear, use the exact label
   **Needs license/terms review before integration** and do not copy the dataset.
6. **Transparency.** Users must eventually be able to see where a claim came from,
   who said it, when, source type, event/status, exact supported scope and what it
   does not establish. Preserve conflicting claims separately rather than silently
   resolving them. Keep source corrections and entity-match decisions traceable.

## Restricted uses and open verification queue

- No provider above is rejected wholesale without evidence; restrictions apply to
  specific uses. Reject invented company links, status inflation, untraceable
  accusations, unsupported AI claims, and circumvention of access controls.
- Confirm reusable feeds/API eligibility and terms for S02–S07, S12–S15 and S18;
  a browser search page is not a stable scraping contract. ECHA terms were blocked;
  several portals expose JavaScript shells, and UK statement rights remain unclear.
- Confirm selected-dataset rights for EPA/EEA, company statement PDFs, Open Supply
  Hub API/data terms, WBA historical editions and any third-party exhibits. Exclude
  restricted GMDN fields until licensed. Recheck OFF rights before extending v1.
- Verify WVS wave-specific non-profit/commercial and redistribution conditions;
  keep it outside company evidence. Carbon-footprint provider research has no
  approved provider yet.
- General licensing facts above are not blanket clearance: every future integration
  still needs a scoped design/terms review and explicit implementation task after
  the [roadmap](roadmap.md) gates. No provider order within a phase is promised.
