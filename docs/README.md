# Ethico project documentation

Start here when joining the project or resuming work after a break.

| Document | Purpose |
| --- | --- |
| [Project status](status.md) | Implemented behavior, verification, limitations, and the reviewed code version |
| [Architecture](architecture.md) | Components, API contract, storage, and platform constraints |
| [Roadmap](roadmap.md) | Completed milestones and proposed next steps with completion criteria |
| [Decision log](decisions.md) | Recorded decisions, reasons, consequences, and open questions |
| [Product sources](product-sources.md) | Evidence and limits for the first real product |
| [Original project idea](project-idea.md) | Long-term product vision; not a list of implemented features |
| [Setup history](setup-notes.md) | Historical tooling and milestone results; not current verification |
| [Repository README](../README.md) | Setup, run commands, sample EANs, and test commands |

## How to keep this useful

The repository is the shared project record. Documents are maintained manually;
they do not automatically track code changes or update a separate conversation.

For each meaningful implementation or data change:

1. Read status, architecture, roadmap, and relevant decisions before changing code.
2. Update status in the same commit or pull request: behavior added or changed,
   limitations, validation date, commands, outcomes, and anything not tested.
3. Update architecture when the API, schema, component boundaries, or dependencies change.
4. Update the roadmap only when its completion criteria are met. Keep proposals
   distinct from approved work and completed implementation.
5. Add a dated decision when product scope or architecture changes. Preserve older
   decisions; mark them superseded and link the replacement.
6. Review product facts and their supporting sources together. Never advance a
   source check date without an actual source review.
7. Update setup instructions when the way to run the project changes.

For a documentation-only update, state which implementation commit was reviewed.
For documents committed with code, use the containing commit/PR as the change
reference; add a fixed verification SHA after testing that version when useful.
Do not invent a future commit hash or copy old test results as if newly run.

## Handoff between implementation and product discussion

A useful handoff includes the commit or PR link, user-visible changes, test
results, remaining limitations, and the next decision needed. Point to these
documents instead of maintaining conflicting summaries in several places.

Codex records implementation and verification. Product discussions use that
record to challenge assumptions and propose scope. The project owner chooses
product priorities; proposed roadmap entries are not automatic authorization.

## Documentation check

Before committing, check that relative links resolve, examples match the API,
setup commands use the correct working directories, and status agrees with the
code. Documentation-only edits do not establish a new application test result.
