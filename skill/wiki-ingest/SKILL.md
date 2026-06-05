---
name: wiki-ingest
description: Use when adding a new source to a wiki — a paper, article, URL, file, transcript, or any document. One ingest may touch 5-15 wiki pages.
---
# Wiki Ingest

Add a source to the wiki. Read it, discuss with the user, write or update wiki pages, update the index, and log the operation.

## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, check `~/.openwiki/openwiki.toml`. If it exists and is valid, use it as the default wiki config.
3. If the default config is not found or invalid, search upward from the current working directory for `openwiki.toml`.
4. If `openwiki.toml` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.

If the default wiki config at `~/.openwiki` is used, tell the user you are using the default wiki config.

Read `openwiki.toml` to resolve:

- the absolute `wiki_root`
- `raw/`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `concepts/`
- `remote_sync_path`
- `auto_sync`

Do not infer these paths from `cwd`, legacy agent-specific files, or compatibility directories.

> **日期占位符说明：** 本文档中的 `<today>` 在执行时必须替换为实际当前日期，格式为 YYYY-MM-DD（如 `2026-05-26`）。

## Process

### 1. Accept the source

The source can be:

- **File path** — read it directly from `raw/` or another user-provided local path
- **URL** — use the `agent-browser` skill to fetch it; snapshot to `raw/` if needed
- **Pasted text** — use what the user provided
- **当前会话上下文** — discussion history so far
### 2. Read the source in full

Read all content. For long sources, read in sections. Do not skip.

### 3. Surface takeaways before writing anything

Tell the user:

- 3-5 bullet points of key takeaways
- what entities or concepts this introduces or updates
- whether it contradicts anything already in the wiki (read `wiki/index.md` and relevant pages to check)

**建议适用范围**：分析源内容，建议 `scope_level` 和 `scope_code`。枚举定义详见 `references/page-template.md`。

展示格式：`适用范围: <scope_level 中文名>（<scope_code>）`。

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

详见 `references/slug-rules.md`。核心规则：全小写、连字符、无特殊字符。中文源标题翻译为英文后 slugify，不使用拼音。

### 6. Write or update wiki pages

Use the CLI to create pages:

```bash
openwiki page create <slug> --file <content-file> --json
```

页面模板详见 `references/page-template.md`。

### 6.1 验证写入

Use the CLI to read back the page:

```bash
openwiki page get <slug> --json
```

执行以下检查：

- frontmatter 是否包含所有必填字段（title、tags、updated、scope_level、scope_code）
- [[交叉引用]] 是否指向存在的页面（在 `wiki/pages/` 中可找到对应文件）
- 若验证失败，报告具体错误并建议修复方案

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

Use the CLI:

```bash
openwiki log append "ingest | <source title> - Created/Updated pages: xxx, yyy"
```

### 11. Report to the user

- Summary page: `wiki/pages/<slug>.md`
- Entity or concept pages created or updated: <list>
- Pages that received backlinks: <list>
- Index updated

### 12. Cloud Sync

详见 `references/cloud-sync.md`。使用 `pcloud` 将 `wiki_root` 同步到远程对象存储。同步失败不阻塞 ingest。
