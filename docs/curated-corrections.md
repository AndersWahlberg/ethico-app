# Reviewed curated-data corrections

Normal initialization imports missing products and sources but deliberately keeps
existing rows unchanged. Editing `backend/app/curated_products.json` alone must
not overwrite unexpected local facts or attach new evidence to them. Corrections
are an explicit maintenance command, never part of FastAPI startup.

## Registry format and history

`backend/app/curated_corrections.json` starts as `[]`: no factual correction was
needed to implement this feature. Each entry contains exactly these fields:

- `ean`: the unchanged EAN, used as the unique active correction identifier.
- `reason`: a nonblank human explanation of the reviewed change.
- `expected`: complete previous reviewed product state.
- `replacement`: complete newly reviewed product state.

Both states contain `ean`, `product_name`, `brand`, `company`, nullable
`company_role`, and `sources`. Each source contains exactly `title`, `url`,
`checked_on`, and `supports`. Empty source lists are allowed. No additional keys
are accepted in correction entries/states/sources, to avoid silently ignoring
purported correction fields. Existing curated validation supplies EAN, required
text, HTTP(S) URL, duplicate-source and calendar-date checks.

The correction EAN must equal both state EANs. Known demo EANs are forbidden;
an existing database row marked as a demo also blocks the batch. Every replacement
must equal the corresponding current curated product's stored fields and sources.
Only source-list ordering is ignored. Text, whitespace, URLs and dates are not
rewritten. Additional curated fields not stored by the current importer remain
outside the correction model.

Keep **one active correction per EAN**; duplicate EANs are rejected rather than
interpreted as an ordered migration chain. For a later correction, deliberately
revise that EAN's expected/replacement/reason and curated entry together. Git
retains the earlier definitions and review history. A database still at an older,
unrecognized state will conflict; review that state and a suitable correction
explicitly, rather than forcing it to the latest version. There is no persistent
execution log or hidden history file. CLI output records the outcome for that run;
it is not proof of who previously applied a matching replacement.

## Making a correction

1. Re-review the facts and sources, including the intended database's prior state.
   A local difference is not permission to discard it.
2. Update the desired product in `backend/app/curated_products.json`.
3. Record the complete expected → replacement states and reason in the registry.
   Preserve historical source dates unless an actual review supports new dates.
4. Validate both complete files without opening SQLite.
5. Preview the intended existing database and inspect every outcome alongside the
   registry diff. Resolve conflicts by evidence-backed review, never by force.
6. Explicitly apply the safe batch to the intended database.
7. Review `git diff` for the desired product and correction definition together.
8. Commit those reviewed source/correction changes. Never commit the local database.

From `backend` (Windows Command Prompt; use `python` in an activated environment):

```cmd
.venv\Scripts\python.exe -m app.validate_curated
.venv\Scripts\python.exe -m app.apply_curated_corrections --validate-only
.venv\Scripts\python.exe -m app.apply_curated_corrections --database "C:\path\to\ethico.sqlite3"
.venv\Scripts\python.exe -m app.apply_curated_corrections --database "C:\path\to\ethico.sqlite3" --apply
```

Omitting `--database` selects the existing `backend/data/ethico.sqlite3`.
`--curated PATH` and `--corrections PATH` override the input files.
`--dry-run` explicitly selects the default read-only preview. `--apply`,
`--dry-run` and `--validate-only` are mutually exclusive. Validation never edits
files. Preview/apply require an existing initialized database; they never create,
reset or upgrade one. Normal initialization is responsible for first import.

## Outcomes and transaction safety

| Outcome | Meaning |
| --- | --- |
| `needs_application` | All current facts and sources match expected; preview would apply it if the entire batch is safe. |
| `applied` | Explicit apply replaced facts and sources and committed the entire batch. |
| `already_applied` | Current state already equals replacement; successful no-op, not a historical execution assertion. |
| `conflict` | Current state matches neither expected nor replacement, or row is marked as a demo. |
| `missing_product` | Target is absent; corrections never insert it. |

Both files are completely validated before database access. All targets are
inspected before any update. A single conflict or missing product blocks **every**
pending correction. Preview uses a read-only SQLite connection and a consistent
read transaction. Apply uses `BEGIN IMMEDIATE` before inspecting targets, so another
writer cannot change them between comparison and update. Foreign keys are enabled.
Facts and source replacements across the whole batch commit in one transaction;
SQL or commit failure rolls everything back. Busy/locked or incompatible databases
fail clearly; there is no force option or automatic schema migration.

Repeated apply is a successful no-op when replacement already matches. A fresh
database initialized from the desired curated dataset also matches replacement.
No command refreshes `checked_on`; only the reviewer-supplied dates are written.

Exit codes: **0** valid/safe preview, successful apply or already-applied no-op;
**1** invalid input/read/database operation; **2** blocked conflict/missing batch
(also argparse usage errors). Expected errors are concise, without stack traces.

This completes the traceable-correction portion of roadmap P2. Scanner/end-to-end
hardening and physical-device verification remain separate, unfinished work.
