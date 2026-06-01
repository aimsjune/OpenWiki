---
name: wiki-update
description: Use when revising existing wiki pages because knowledge has changed, a new piece of information updates or contradicts existing content, or the user wants to directly edit wiki content with LLM assistance.
---

# Wiki Update

Revise existing wiki pages. Always show diffs before writing. Always log. Always cite the source of new information.

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

Do not depend on legacy agent-specific files or compatibility directories.

## Process

### 1. Identify what to update

The user may provide:

- specific page names
- new information
- a lint report

### 2. For each page to update

Read the current content in full. Propose the change with:

> **Current:** `<quote the existing text>`  
> **Proposed:** `<replacement text>`  
> **Reason:** `<why this change is warranted>`  
> **Source:** `<URL, raw/ path, or other source>`

Ask for confirmation before writing each page.

### 3. Check downstream effects

After identifying the primary pages to update, search for `[[slug]]` references across all of `wiki/pages/`. Flag any linked pages that may also need updating.

### 4. Contradiction sweep

If the new information contradicts existing wiki content, search all pages for the contradicted claim and update all affected occurrences.

### 5. Update `wiki/index.md`

If a page summary changes, update its row and update the `updated` date in frontmatter.

如果页面的 `scope_level` 或 `scope_code` 发生变更，同步更新 category_3（适用范围）区域：
- category_3 中旧 scope_code 组移除该页面的 `[[slug]]`
- category_3 中新 scope_code 组新增该页面的 `[[slug]]`
- 若旧组变为空则删除该 `### scope_code` 区块
- 若新组不存在则创建 `### scope_code` 区块

### 6. Append to `wiki/log.md`

Always append an `update` record that includes the reason and source.

## Common Mistakes

- updating without a source
- skipping downstream checks
- skipping the log
- batch-writing without per-page confirmation
