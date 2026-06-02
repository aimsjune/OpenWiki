# Design: fix-date-placeholders

## Overview

修复两类日期问题：(1) `index.md` 中 category_2 列名从"日期"统一为"最后更新"；(2) 在所有使用 `<today>` 占位符的 SKILL.md 和模板中明确替换规则（执行时替换为实际当前日期，YYYY-MM-DD 格式）。

## Architecture

### 变更范围

```
受影响文件:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  列名修复 (2 文件):                                           │
│  ├── wiki/index.md                      "日期" → "最后更新"   │
│  └── skill/wiki-init/templates/index.md  "日期" → "最后更新"   │
│                                                              │
│  <today> 说明 (6 文件):                                       │
│  ├── skill/wiki-ingest/SKILL.md         新增替换规则说明       │
│  ├── skill/wiki-distill/SKILL.md        新增替换规则说明       │
│  ├── skill/wiki-query/SKILL.md          新增替换规则说明       │
│  ├── skill/wiki-lint/SKILL.md           新增替换规则说明       │
│  │                                      + hardcoded 规则     │
│  └── skill/wiki-init/templates/log.md   新增格式说明           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### `<today>` 说明放置策略

在每个文件的 **首次出现 `<today>` 之前**（或 Pre-condition 区域）添加说明：

```markdown
> **日期占位符说明：** 本文档中的 `<today>` 在执行时必须替换为实际当前日期，格式为 YYYY-MM-DD（如 `2026-05-26`）。
```

### 新增 Lint 规则

`wiki-lint` Blue Info 新增：

```
hardcoded-or-literal-today — 生成文件中残留字面量 <today> 或使用明显非当前日期的硬编码日期
```

检查范围：`wiki/pages/*.md`、`concepts/*.md`、`wiki/index.md`、`wiki/log.md`

## Interface Design for Testability

所有变更通过静态文本验证测试：

| 被测接口 | 验证方式 |
|---------|---------|
| `wiki/index.md` category_2 列名 | 字符串精确匹配 `\| 页面 \| 类型 \| 最后更新 \|` |
| 模板 `index.md` category_2 列名 | 同上 |
| 各 SKILL.md 的 `<today>` 说明 | 语义匹配 "YYYY-MM-DD" + "today" |
| `wiki-lint` 的 hardcoded 规则 | 语义匹配 "hardcoded-or-literal-today" |
| `log.md` 模板的格式说明 | 语义匹配 "YYYY-MM-DD" |

## Implementation Notes

1. 列名修改是纯字符串替换，不涉及逻辑变更
2. `<today>` 说明放在 Pre-condition 或首次出现之前，不影响现有流程步骤
3. 新增 lint 规则为 Blue Info 级别，不阻断流程
4. 不回溯修改已归档文件和已写入的历史 log 条目
