# Ethico development principles

These instructions apply throughout this repository.

Before starting work, inspect the current Git status and branch. Read README.md,
docs/status.md, docs/roadmap.md, docs/decisions.md, docs/architecture.md, and any
other documentation relevant to the task. Treat roadmap proposals as proposals,
not automatic authorization to implement them.

## Product principle

Ethico is an evidence-first product.

- Prefer source-backed facts over assumptions.
- Never invent product, company, ownership, sustainability, or ethical claims.
- Missing information must remain explicitly unknown.
- Future AI features should summarize and organize evidence, not generate unsupported ethical judgments.
- Distinguish company self-reported claims from independent evidence where relevant.
- Preserve source URLs, scope, dates, and uncertainty.

## Engineering approach

- Understand the existing implementation before changing it.
- Prefer small, focused, reviewable changes.
- Avoid unnecessary abstractions, frameworks, dependencies, or architectural complexity.
- Do not refactor unrelated code while implementing a feature.
- Preserve existing behavior unless the task explicitly requires changing it.
- Reuse existing validation and domain logic where sensible.
- Never commit secrets, credentials, API keys, local databases, build artifacts, or environment-specific files.
- Do not upgrade dependencies unless the task specifically requires it or there is a clearly documented reason.

## Privacy and security hygiene

Repository content must not expose personal or machine-specific information unless it is deliberately required for the product.

- Never commit personal email addresses, phone numbers, street addresses, account identifiers, private usernames, device identifiers, or other personal contact data.
- Never commit absolute local home-directory paths; use repository-relative paths or neutral placeholders such as `<local-home>/...` or `<temporary-directory>/...`.
- Do not place a developer's personal repository/profile URL in outbound application headers, telemetry, provider metadata, or other runtime network requests.
- Never commit secrets, tokens, passwords, private keys, signing keys, keystores, `.env` files, local databases, or service credentials.
- Keep test logs and documentation sanitized before committing them; replace local paths with neutral placeholders.
- Do not add analytics, telemetry, crash reporting, or user/device tracking without an explicit product decision and privacy review.
- Minimize logged user activity. Do not introduce persistent scan/search history or raw identifiers into logs unless there is a documented operational need and retention policy.
- Treat external requests as data disclosure boundaries. Document exactly what is sent and avoid unnecessary identifying headers or metadata.
- Before finishing a task, check changed files for accidental personal data, secrets, local paths, generated databases, and signing material.

## Git workflow

For normal development work:

- Start from an up-to-date main branch.
- Create a descriptive feature/fix/chore branch.
- Do not develop directly on main.
- Keep each task scoped so it can be reviewed as one logical change.
- Use a clear commit message.
- Push the branch to GitHub when the task is complete.
- Prefer a pull request into main so the change can be reviewed before merging.

## Testing

Before considering a task complete:

- Run the relevant existing automated tests.
- For backend changes, run the relevant pytest suite.
- For Flutter changes, run flutter analyze and relevant flutter tests when the environment supports them.
- Add or update tests when behavior changes.
- Never claim a test passed if it was not actually run.
- Clearly report tests that could not be run and why.

## Documentation

Ethico uses its repository documentation as the shared project record.

When behavior, architecture, data structures, setup, or major decisions change:

- Update the relevant documentation.
- Keep docs/status.md truthful about what is implemented and verified.
- Update docs/architecture.md when architecture or data flow changes.
- Update docs/decisions.md for meaningful adopted product/architecture decisions.
- Update docs/roadmap.md when milestone status materially changes.

Do not rewrite project history merely to make documentation look current.

## Data and evidence

When modifying curated product, company, or source data:

- Validate identifiers such as EANs.
- Preserve provenance.
- Do not guess company relationships.
- Do not silently replace conflicting evidence.
- Make uncertainty representable rather than resolving it by assumption.
- Prefer traceable corrections over destructive replacements.

## Task completion

When finishing a Codex task:

1. Summarize what changed.
2. List files changed.
3. Report tests actually run and their results.
4. Report unresolved risks, assumptions, or questions.
5. Provide the branch name and commit SHA.
6. If possible, push the branch and create a pull request into main.
7. Stop after the requested task. Do not automatically begin another feature.
