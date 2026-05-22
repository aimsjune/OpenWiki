---
name: wiki-init
description: Use when bootstrapping a new personal wiki for any knowledge domain. Initialize a neutral `skill.io`-compatible wiki contract with a configurable `config-dir` and `wiki-root`.
---
# Wiki Init

Bootstrap a new LLM-maintained wiki using a neutral runtime contract.

## Pre-flight

Check whether a `WIKI.md` already exists in the target configuration directory. If yes, ask the user whether to reinitialize or continue with the existing wiki instance.

## Process

### 1. Gather configuration (one question at a time)

Ask:

1. **Where should the configuration directory live?** (absolute path, e.g. `~/wiki-config/ml-research`)
2. **Where should the wiki root directory live?** (absolute path, may be different from the configuration directory)
3. **What is the domain/purpose?** (one sentence)
4. **What types of sources will you add?** (papers, URLs, code files, transcripts, etc.)
5. **What categories should `index.md` use?**
   - Research default: `Wiki Pages | Concepts Pages | Topic Relations | Quick Navigation`
   - Codebase default: `Modules | APIs | Decisions | Flows`
   - Or specify custom

### 2. Validate paths

- The configuration directory must be writable.
- The wiki root directory must be an absolute path.
- The wiki root directory may be the same as or different from the configuration directory.
- The wiki root target must be writable or creatable.

### 3. Write `WIKI.md`

Write `WIKI.md` into the configuration directory. It must record an absolute `wiki_root` path explicitly.

Use the local starter template at `skill/wiki-init/templates/WIKI.md` as the owning skill asset, then fill in the user-specific fields.

### 4. Create wiki data layout under `wiki_root`

```text
<wiki-root>/
├── raw/              ← immutable source documents
├── wiki/
│   ├── index.md      ← content catalog: page, summary, tags, updated
│   ├── log.md        ← append-only operation log
│   └── pages/        ← flat topic pages, one slug per file
└── concepts/         ← generated reports, analyses, and answers
```

**Critical:** `wiki/pages/` is flat. All pages live here as `<slug>.md`. No subdirectories. Slugs are lowercase and hyphen-separated.

### 5. Write `wiki/index.md`

Write `wiki_root/wiki/index.md` from the local starter template at `skill/wiki-init/templates/index.md`, then replace the placeholders with the user-selected categories.

### 6. Write `wiki/log.md`

Write `wiki_root/wiki/log.md` from the local starter template at `skill/wiki-init/templates/log.md`, then fill in the current date and domain.

### 7. Confirm

Tell the user:

- Configuration initialized at `<config-dir>/WIKI.md`
- Wiki data initialized under `<wiki-root>`
- Add sources to `raw/` manually, or run `wiki-ingest` with a file path, URL, or pasted text
- Run `wiki-lint` periodically to keep the wiki healthy
- `skill/` is the canonical public skill directory for this repository
