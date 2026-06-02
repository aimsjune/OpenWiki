---
name: wiki-lint
description: Use when auditing a wiki for health issues — contradictions between pages, orphan pages, broken cross-references, stale claims, missing pages, or coverage gaps.
---
# Wiki Lint

Audit the wiki. Produce a categorized report. Offer concrete fixes. Log the operation.

## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, check `~/.openwiki/openwiki.toml`. If it exists and is valid, use it as the default wiki config.
3. If the default config is not found or invalid, search upward from the current working directory for `openwiki.toml`.
4. If `openwiki.toml` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.

If the default wiki config at `~/.openwiki` is used, tell the user you are using the default wiki config.

Read `openwiki.toml` to resolve the absolute `wiki_root` plus:

- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `concepts/`
- `primary_language`
- `secondary_language`

Do not depend on legacy agent-specific files or compatibility directories.

> **日期占位符说明：** 本文档中的 `<today>` 在执行时必须替换为实际当前日期，格式为 YYYY-MM-DD（如 `2026-05-26`）。

## Process

### 1. Build the page inventory

Use the CLI to list all pages:

```bash
openwiki page list --json
```

Read `wiki/index.md` and all files in `wiki/pages/`. Build a map of:

- all existing slugs
- all `[[slug]]` references
- all `sources` listed in frontmatter

### 2. Run all checks

详见 `references/rules-catalog.md`。按严重程度分为三级：

**Red Errors**: broken-links, missing-frontmatter

**Yellow Warnings**: orphan-pages, contradictions, stale-claims, content-not-chinese-primary, missing-chinese-title, missing-term-glossary, missing-bilingual-tags, missing-scope-fields, invalid-scope-level, invalid-scope-code-format, scope-level-code-mismatch

**语言规则启用条件**：仅当 `openwiki.toml` 中 `primary_language` 为 `zh` 时启用语言规则。若 `openwiki.toml` 不含 `primary_language` 字段（旧格式），默认视为 `zh`。

**英文豁免清单**：详见 `references/exemption-checklist.md`。

**Blue Info**: missing-concept-pages, missing-cross-references, hardcoded-or-literal-today

### 2.1 验证输出完整性

检查是否所有页面都被扫描（页面数与 `wiki/pages/` 中文件数一致），所有 Red Errors 是否都有对应的修复建议，所有 Yellow Warnings 是否都有对应的说明。若发现遗漏，补充后再生成报告。

### 3. Write the lint report

Write `concepts/lint-<today>.md` and summarize all findings with concrete remediation suggestions.

### 4. Update `wiki/index.md`

Add a row for the lint report under **Concepts Pages**.

### 5. Offer concrete fixes

For each fixable category, offer precise edits and show diffs before writing.

### 6. Append to `wiki/log.md`

Always append a `lint` entry with issue counts and any fixes applied.
