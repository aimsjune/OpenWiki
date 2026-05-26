---
name: wiki-lint
description: Use when auditing a wiki for health issues — contradictions between pages, orphan pages, broken cross-references, stale claims, missing pages, or coverage gaps.
---

# Wiki Lint

Audit the wiki. Produce a categorized report. Offer concrete fixes. Log the operation.

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
- `primary_language`
- `secondary_language`

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
- content-not-chinese-primary — 页面正文中文占比低于 60%。排除：代码块（` ```...``` `）、行内代码（`` `code` ``）、URL（`https://...`）、YAML frontmatter（`---...---`）、术语首次标注括号内英文（`中文术语（English）`）
- missing-chinese-title — h1 标题不包含任何中文字符。仅检查 Markdown h1，不检查 frontmatter 中的 `title` 字段
- missing-term-glossary — 英文多词术语（2 个及以上单词）在页面中首次出现时未附中文解释。支持两种标注形式：`中文术语（English Term）` 或 `English Term（中文术语）`。单字术语（如 "Go"、"Rust"）不触发
- missing-bilingual-tags — frontmatter 中 `tags` 仅有英文标签无中文标签。仅当 `primary_language` 为 `zh` 且 `secondary_language` 为 `en` 时启用。只要存在任意中文标签即满足

**语言规则启用条件**：仅当 `WIKI.md` 中 `primary_language` 为 `zh` 时启用以上 4 条语言规则。若 `primary_language` 不为 `zh`，跳过全部语言规则。若 `WIKI.md` 不含 `primary_language` 字段（旧格式），默认视为 `zh`。

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
