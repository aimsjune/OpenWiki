---
name: wiki-ingest
description: Use when adding a new source to a wiki — a paper, article, URL, file, transcript, or any document. One ingest may touch 5-15 wiki pages.
---

# Wiki Ingest

Add a source to the wiki. Read it, discuss with the user, write or update wiki pages, update the index, and log the operation.

## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, search upward from the current working directory for `WIKI.md`.
3. If `WIKI.md` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.

Read `WIKI.md` to resolve:

- the absolute `wiki_root`
- `raw/`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `concepts/`

Do not infer these paths from `cwd`, legacy agent-specific files, or compatibility directories.

## Process

### 1. Accept the source

The source can be:

- **File path** — read it directly from `raw/` or another user-provided local path
- **URL** — use the `agent-browser` skill to fetch it; snapshot to `raw/` if needed
- **Pasted text** — use what the user provided

### 2. Read the source in full

Read all content. For long sources, read in sections. Do not skip.

### 3. Surface takeaways before writing anything

Tell the user:

- 3-5 bullet points of key takeaways
- what entities or concepts this introduces or updates
- whether it contradicts anything already in the wiki (read `wiki/index.md` and relevant pages to check)

Ask: **"Anything specific you want me to emphasize or de-emphasize?"**

Wait for the user's response before proceeding.

### 4. Network supplement (recommended)

For core concepts or key claims, use `agent-browser` to fetch current authoritative sources. Prioritize by category:

- **General concepts**: en.wikipedia.org / zh.wikipedia.org
- **Tech/Programming**: docs.python.org, developer.mozilla.org, arxiv.org, github.com
- **AI/ML Papers**: arxiv.org, paperswithcode.com, huggingface.co
- **News/Current Events**: reuters.com, bbc.com, theguardian.com
- **Academic**: scholar.google.com, semanticscholar.org
- **Official docs**: prefer the official site for the topic

### 5. Generate the slug

Lowercase, hyphens, no special characters.
Example: `Attention Is All You Need` -> `attention-is-all-you-need`

### 6. Write or update wiki pages

Write to `wiki/pages/<slug>.md` under `wiki_root`:

```markdown
---
title: <source title>
tags: [<relevant tags>]
sources: <number of sources>
updated: <today>
---

# <Source Title>

**Source:** <original URL or local path>
**Date ingested:** <today>
**Type:** <paper | article | transcript | code | other>

## Core Definition

<Definition of core concepts>

## Key Takeaways

- <bullet>

## Related Topics

- [[related-slug]] — <relationship>

## Open Questions

<If any>
```

### 7. Update related entity or concept pages

For each entity or concept touched by this source:

- **Page exists:** read it, update the relevant section, update `updated`
- **Page does not exist:** create it with the same frontmatter format

### 8. Backlink audit

Scan all existing pages in `wiki/pages/` for any that mention this source's entities or concepts but do not yet link to the new page. Add `[[new-slug]]` references where appropriate.

### 9. Update `wiki/index.md`

Add or update entries in the table format:

```markdown
## Wiki Pages
| Page | Summary | Tags | Last Updated |
|------|---------|------|--------------|
| [[<slug>]] | One-line description | tag1, tag2 | <today> |
```

### 10. Append to `wiki/log.md`

Always append:

```markdown
## [<today>] ingest | <source title>
- Created/Updated pages: xxx, yyy
- Web verification: yes/no, source: <url>
- Key findings: ...
```

### 11. Report to the user

- Summary page: `wiki/pages/<slug>.md`
- Entity or concept pages created or updated: <list>
- Pages that received backlinks: <list>
- Index updated
