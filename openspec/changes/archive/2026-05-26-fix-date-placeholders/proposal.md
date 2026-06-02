# Proposal: fix-date-placeholders

## Why

wiki 生态中存在两类日期问题：

**问题 1：列名不一致。** `index.md` 中 category_1 使用"最后更新"，但 category_2 使用"日期"。同一文件内同一语义使用不同列名，造成混淆。模板 `skill/wiki-init/templates/index.md` 同样存在此问题。

**问题 2：`<today>` 占位符语义不清。** 12 处 `<today>` 分布在 5 个 SKILL.md 和 1 个模板中，但没有一处明确说明"`<today>` 必须在执行时替换为实际当前日期（YYYY-MM-DD 格式）"。这导致 AI Agent 执行技能时可能将 `<today>` 原样写入生成的文件，或使用错误的日期格式。

| 文件 | `<today>` 出现次数 | 用途 |
|------|-------------------|------|
| `skill/wiki-ingest/SKILL.md` | 6 | frontmatter updated、摄入日期、index 更新、log 追加、sync log |
| `skill/wiki-distill/SKILL.md` | 3 | 蒸馏日期、log 追加 |
| `skill/wiki-query/SKILL.md` | 1 | concepts 页面 frontmatter |
| `skill/wiki-lint/SKILL.md` | 1 | lint 报告文件名 |
| `skill/wiki-init/templates/log.md` | 1 | init log 条目 |

## What Changes

1. **统一列名**：`wiki/index.md` 和 `skill/wiki-init/templates/index.md` 的 category_2 列名从"日期"改为"最后更新"
2. **明确 `<today>` 语义**：在每个使用 `<today>` 的 SKILL.md 文件中，添加显式说明："`<today>` 表示执行时的实际当前日期，格式为 YYYY-MM-DD"
3. **新增 lint 规则**：`wiki-lint` 增加 Blue Info 规则 `hardcoded-or-literal-today`，检测生成文件中是否残留字面量 `<today>` 或使用非当前日期的硬编码日期

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `wiki/index.md` category_2 列名为"最后更新" | 读取 `wiki/index.md`，验证 category_2 表格头为 `\| 页面 \| 类型 \| 最后更新 \|` |
| 2 | `skill/wiki-init/templates/index.md` category_2 列名为"最后更新" | 读取模板，验证 category_2 表格头为 `\| 页面 \| 类型 \| 最后更新 \|` |
| 3 | `wiki-ingest` SKILL.md 明确 `<today>` 替换规则 | 读取 SKILL.md，验证 `<today>` 首次出现附近有"执行时替换为实际当前日期（YYYY-MM-DD）"的说明 |
| 4 | `wiki-distill` SKILL.md 明确 `<today>` 替换规则 | 同上 |
| 5 | `wiki-query` SKILL.md 明确 `<today>` 替换规则 | 同上 |
| 6 | `wiki-lint` SKILL.md 明确 `<today>` 替换规则 | 同上 |
| 7 | `wiki-lint` 新增 `hardcoded-or-literal-today` Blue Info 规则 | 读取 `skill/wiki-lint/SKILL.md`，验证 Blue Info 节包含该规则 |
| 8 | `wiki-init/templates/log.md` 明确 `<today>` 替换规则 | 读取模板，验证 `<today>` 附近有格式说明 |

## Impact

- **5 个 SKILL.md**：`wiki-ingest`、`wiki-distill`、`wiki-query`、`wiki-lint`、`wiki-update`（仅 lint 规则）
- **2 个模板**：`skill/wiki-init/templates/index.md`、`skill/wiki-init/templates/log.md`
- **1 个运行时文件**：`wiki/index.md`
- **新增 lint 规则**：`hardcoded-or-literal-today`（Blue Info）

## Non-Goals

- 不改变日期格式（保持 YYYY-MM-DD）
- 不引入自动化日期填充脚本（AI Agent 在执行时替换）
- 不修改已归档的 OpenSpec artifacts 中的硬编码日期

## Test Considerations

- 测试框架：静态 SKILL.md 分析
- 关键接口：各 SKILL.md 中的 `<today>` 说明文本、index.md 列名
- 静态验证：模板文件中的列名字符串精确匹配
