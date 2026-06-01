---
name: wiki-ingest
description: Use when adding a new source to a wiki — a paper, article, URL, file, transcript, or any document. One ingest may touch 5-15 wiki pages.
---

# Wiki Ingest

Add a source to the wiki. Read it, discuss with the user, write or update wiki pages, update the index, and log the operation.

## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, check `~/.wiki-config/WIKI.md`. If it exists and is valid, use it as the default wiki config.
3. If the default config is not found or invalid, search upward from the current working directory for `WIKI.md`.
4. If `WIKI.md` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.

If the default wiki config at `~/.wiki-config` is used, tell the user you are using the default wiki config.

Read `WIKI.md` to resolve:

- the absolute `wiki_root`
- `raw/`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `concepts/`
- `remote_sync_path`
- `auto_sync`

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

**建议适用范围**：分析源内容，建议 `scope_level` 和 `scope_code`。参考下表：

| scope_level | 中文名 | 含义 |
|-------------|--------|------|
| repo | 代码仓库 | 单个代码仓库级别 |
| domain | 领域 | 跨若干个代码仓库适用 |
| company | 公司 | 跨若干个领域适用 |
| industry | 行业 | 跨若干个公司适用 |
| wisdom | 智慧 | 高度抽象，跨多行业多场景适用 |

展示格式：`适用范围: <scope_level 中文名>（<scope_code>）`。scope_code 遵循 slug 规则（小写、连字符、无特殊字符）。

Ask: **"Anything specific you want me to emphasize or de-emphasize? 适用范围是否合适？"**

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

- **英文源标题**：直接 slugify。
  Example: `Attention Is All You Need` -> `attention-is-all-you-need`
- **中文源标题**：翻译为英文后 slugify，不使用拼音。
  Example: `依赖注入模式` -> `dependency-injection-pattern`（非 `yi-lai-zhu-ru-mo-shi`）

### 6. Write or update wiki pages

Write to `wiki/pages/<slug>.md` under `wiki_root`:

```markdown
---
title: <source title>
tags: [<relevant tags>]
sources: <number of sources>
updated: <today>
scope_level: <repo|domain|company|industry|wisdom>
scope_code: <slug>
---

# <Source Title>

**来源：** <original URL or local path>
**摄入日期：** <today>
**类型：** <paper | article | transcript | code | other>
**适用范围：** <scope_level 中文名>（<scope_code>）

## 核心定义

<Definition of core concepts>

## 关键要点

- <bullet>

## 相关主题

- [[related-slug]] — <relationship>

## 开放问题

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
## Wiki 页面
| 页面 | 摘要 | 标签 | 最后更新 |
|------|------|------|----------|
| [[<slug>]] | One-line description | tag1, tag2 | <today> |
```

同步更新 category_3（适用范围）区域。按 `scope_code` 分组聚合，每组以 `### scope_code` 三级标题开头，组内按最后更新日期倒序排列：

```markdown
## 适用范围

### <scope_code>
- [[<slug>]] — <scope_level 中文名> | <today>
```

- scope_code 组已存在时追加 `[[slug]]` 条目到该组
- scope_code 组不存在时创建新的 `### scope_code` 区块
- scope_code 组下最后一个页面被移除时删除该区块

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

### 12. Cloud Sync

Sync the entire `wiki_root` to remote object storage using `pcloud`.

**Pre-check**: If `remote_sync_path` is empty, skip sync silently. If `pcloud` CLI is not available (not installed or not configured at `~/.config/pcloud/config.toml`), warn the user and skip sync — do not block ingest.

**If `auto_sync` is `true`**:

Run `pcloud sync <wiki_root> <remote_sync_path>` directly without confirmation.

**If `auto_sync` is `false` (default)**:

1. Run `pcloud sync <wiki_root> <remote_sync_path> --dry-run` to preview changes
2. Show the user a summary of uploads and downloads
3. Ask: **"Execute sync? [Y/n]"**
4. On confirmation, run `pcloud sync <wiki_root> <remote_sync_path>`
5. On skip, report "cloud sync skipped" and continue

**After sync succeeds**, append to `wiki/log.md`:

```markdown
## [<today>] sync | <remote_sync_path>
- Upload: N files
- Download: M files
```

**On failure**: Report the error but do NOT roll back ingest. The ingest pages, index, and log are already committed. Sync failure does not affect the wiki state.
