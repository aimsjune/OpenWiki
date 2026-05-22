---
name: wiki-lint
description: Use when auditing a wiki for health issues — contradictions between pages, orphan pages, broken cross-references, stale claims, missing pages, or coverage gaps.
---

# Wiki Lint

Audit the wiki. Produce a categorized report. Offer concrete fixes. Log the operation.

## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, search upward from the current working directory for `WIKI.md`.
3. If `WIKI.md` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.

Read `WIKI.md` to resolve the absolute `wiki_root` plus:

- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `concepts/`

Do not depend on legacy agent-specific files or compatibility directories.

## Process

### 1. Build the page inventory

Read `wiki/index.md` and all files in `wiki/pages/`. Build a map of:

- all existing slugs
- all `[[slug]]` references
- all `sources` listed in frontmatter

### 2. Run all checks

**Red Errors**

- broken links
- missing frontmatter

**Yellow Warnings**

- orphan pages
- contradictions
- stale claims

**Blue Info**

- missing concept pages
- missing cross-references

### 3. Write the lint report

Write `concepts/lint-<today>.md` and summarize all findings with concrete remediation suggestions.

### 4. Update `wiki/index.md`

Add a row for the lint report under **Concepts Pages**.

### 5. Offer concrete fixes

For each fixable category, offer precise edits and show diffs before writing.

### 6. Append to `wiki/log.md`

Always append a `lint` entry with issue counts and any fixes applied.
