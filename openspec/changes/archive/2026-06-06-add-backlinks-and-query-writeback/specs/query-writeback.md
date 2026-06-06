# Specification: Query 回写机制

## Overview

升级 wiki-query 的 Step 5，从简单的 "Worth saving?" 升级为结构化的回写判断与保存流程。

## Requirements

### REQ-QW-1: 结构化回写判断条件

**Behavior**: wiki-query SKILL.md 的 Step 5 包含 4 个回写判断条件：多源综合、新关联、矛盾发现、知识空白。Agent 在回答完成后自动评估是否满足任一条件。

**Test Verification**: 文档审查——SKILL.md Step 5 包含条件表格。

```
Given: Agent 完成了一次回答，综合了 [[page-a]] 和 [[page-b]]
When:  评估回写条件
Then:  满足"多源综合"条件，Agent 向用户提议保存
```

**Interfaces to Test Through**: SKILL.md 文档内容

---

### REQ-QW-2: 回写页面格式模板

**Behavior**: 回写页面包含特定的 frontmatter 字段（`query_date`、`query_sources`、`external_refs`）和正文结构（原始问题、分析、来源、外部参考）。

**Test Verification**: 文档审查——模板包含所有必需字段。

```
Given: 用户确认保存回写
When:  Agent 创建回写页面
Then:  frontmatter 包含 query_date、query_sources、external_refs
       正文包含"原始问题"、"分析"、"来源"、"外部参考"四个章节
```

**Interfaces to Test Through**: SKILL.md 文档内容

---

### REQ-QW-3: 回写页面存入 wiki/pages/

**Behavior**: 回写页面存入 `wiki/pages/`（非 `concepts/`），更新 `wiki/index.md` 的 Wiki 页面区域。

**Test Verification**: 文档审查——SKILL.md 指定路径为 `wiki/pages/`。

```
Given: 用户确认保存回写
When:  Agent 创建回写页面
Then:  页面创建在 wiki/pages/<slug>.md
       index.md 的 Wiki 页面区域新增一行
```

**Interfaces to Test Through**: SKILL.md 文档内容

---

### REQ-QW-4: 回写后不修改源页面

**Behavior**: 回写页面创建后，不自动修改源页面的"相关主题"区域。反向链接功能会自动展示引用关系。

**Test Verification**: 文档审查——SKILL.md Step 5.3 明确说明"不修改源页面"。

**Interfaces to Test Through**: SKILL.md 文档内容

---

### REQ-QW-5: 单源提取不触发回写

**Behavior**: 如果回答仅从单个 wiki 页面提取信息，不触发回写建议，仅追加 query 日志。

**Test Verification**: 文档审查——SKILL.md Step 5.1 包含此判断逻辑。

```
Given: Agent 完成了一次回答，仅引用了 [[page-a]]
When:  评估回写条件
Then:  不满足任何条件，跳过回写建议，仅追加日志
```

**Interfaces to Test Through**: SKILL.md 文档内容

---

### REQ-QW-6: Step 2 包含 --backlinks 用法

**Behavior**: wiki-query SKILL.md 的 Step 2 包含 `openwiki page get <slug> --backlinks --json` 用法说明。

**Test Verification**: 文档审查——Step 2 包含 `--backlinks` 命令示例。

**Interfaces to Test Through**: SKILL.md 文档内容

---

## Test Structure

### 文档审查

| 检查项 | 位置 | 预期内容 |
|--------|------|---------|
| 回写判断条件表格 | SKILL.md Step 5.1 | 4 行条件（多源综合/新关联/矛盾发现/知识空白） |
| 回写页面模板 | SKILL.md Step 5.2 | 包含 query_date、query_sources、external_refs |
| 存放路径 | SKILL.md Step 5.3 | 指定 wiki/pages/ |
| 不修改源页面 | SKILL.md Step 5.3 | 明确说明 |
| 单源跳过逻辑 | SKILL.md Step 5.1 | 说明仅追加日志 |
| --backlinks 用法 | SKILL.md Step 2 | 命令示例 |

## Edge Cases

- 用户拒绝回写建议时，仅追加 query 日志
- 用户修改 slug 时，使用用户指定的 slug
- 回写页面引用的源页面不存在时，query_sources 中仍记录 slug（由反向链接发现断链）
