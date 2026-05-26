---
wiki_root: /Users/bytedance/git/llm-wiki
domain: AI-maintained personal wiki scaffold
primary_language: zh
secondary_language: en
source_types:
  - notes
  - web-clippings
  - papers
  - journals
  - code-files
index_categories:
  - Wiki Pages
  - Concepts Pages
  - Topic Relations
  - Quick Navigation
remote_sync_path: wiki
auto_sync: false
---

# WIKI

This file is the canonical runtime contract for this wiki instance.

## Runtime Contract

- `wiki_root` is the absolute path to the wiki data root.
- `raw/`, `wiki/`, and `concepts/` live under `wiki_root`.
- Wiki workflows should resolve runtime paths from this file instead of agent-specific files.

## Data Layout

Under `wiki_root`:

- `raw/` stores immutable source material
- `wiki/index.md` stores the global index
- `wiki/log.md` stores the append-only operation log
- `wiki/pages/` stores topic pages
- `concepts/` stores generated analyses and reports
