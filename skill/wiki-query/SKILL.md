---
name: wiki-query
description: Use when asking a question against a personal wiki built with wiki-init and wiki-ingest. Do not answer from general knowledge — always read the wiki pages first.
---

# Wiki Query

Ask a question. Read the wiki. Synthesize with citations. Offer to file the answer back.

## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, check `~/.wiki-config/WIKI.md`. If it exists and is valid, use it as the default wiki config.
3. If the default config is not found or invalid, search upward from the current working directory for `WIKI.md`.
4. If `WIKI.md` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.

If the default wiki config at `~/.wiki-config` is used, tell the user you are using the default wiki config.

Read `WIKI.md` to resolve the absolute `wiki_root` plus:

- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `concepts/`

Do not depend on legacy agent-specific files or compatibility directories.

## Process

### 1. Read `wiki/index.md` first

Scan the full index to identify which pages are likely relevant. Do not answer from general knowledge first.

### 2. Read relevant pages

Read the identified pages in full. Follow one level of `[[slug]]` links if they point to pages that seem relevant to the question.

### 3. Network supplement (if needed)

If local wiki information is insufficient or needs verification for time-sensitive content, use `agent-browser` to fetch current sources. Prioritize authoritative sites:

- **General concepts**: en.wikipedia.org / zh.wikipedia.org
- **Tech/Programming**: docs.python.org, developer.mozilla.org, arxiv.org, github.com
- **AI/ML Papers**: arxiv.org, paperswithcode.com, huggingface.co
- **News/Current Events**: reuters.com, bbc.com, theguardian.com
- **Academic**: scholar.google.com, semanticscholar.org

### 4. Synthesize the answer

Write a response that:

- is grounded in the wiki pages you read
- cites inline using `[[slug]]` for local pages and URLs for web sources
- notes agreements and disagreements between pages
- flags gaps like "The wiki has no page on X"
- suggests follow-up sources to ingest or questions to investigate

### 5. Always offer to save

After answering, say:

> "Worth saving to `concepts/<suggested-slug>.md`?"

If yes:

- write the page with frontmatter: `tags: [query, analysis]`, `sources: <number>`, `updated: <today>`
- update `wiki/index.md` under **Concepts Pages**
- append a `query` record to `wiki/log.md`

If no:

- still append a `query` record to `wiki/log.md` noting the pages read and whether web verification was used

## Common Mistakes

- **Answering from memory** — always read the wiki pages first
- **Skipping the save offer** — always offer
- **No citations** — every factual claim should trace back to a `[[slug]]` or URL
