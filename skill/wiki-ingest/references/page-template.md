# 页面模板规范

本文档定义 wiki-ingest 生成的 wiki 页面标准模板，包括 frontmatter 字段和正文结构。

---

## Frontmatter 字段

```yaml
---
title: <source title>
tags: [<relevant tags>]
sources: <number of sources>
updated: <today>
scope_level: <repo|domain|company|industry|wisdom>
scope_code: <slug>
---
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | 是 | 源标题，保持原文 |
| `tags` | 是 | 相关标签数组，中英文混合 |
| `sources` | 是 | 来源数量 |
| `updated` | 是 | 最后更新日期，格式 YYYY-MM-DD |
| `scope_level` | 是 | 适用范围级别 |
| `scope_code` | 是 | 适用范围代号，slug 格式 |

### scope_level 枚举

| 值 | 中文名 | 含义 |
|----|--------|------|
| `repo` | 代码仓库 | 单个代码仓库级别 |
| `domain` | 领域 | 跨若干个代码仓库适用 |
| `company` | 公司 | 跨若干个领域适用 |
| `industry` | 行业 | 跨若干个公司适用 |
| `wisdom` | 智慧 | 高度抽象，跨多行业多场景适用 |

---

## 正文结构

```markdown
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

### 章节说明

| 章节 | 说明 |
|------|------|
| 来源 | 原始 URL 或本地路径 |
| 摄入日期 | 内容摄入日期 |
| 类型 | paper / article / transcript / code / other |
| 适用范围 | scope_level 中文名 + scope_code |
| 核心定义 | 核心概念的精确定义 |
| 关键要点 | 要点列表，每条一个 bullet |
| 相关主题 | `[[slug]]` 交叉引用 + 关系描述 |
| 开放问题 | 待探索的问题（可选） |
