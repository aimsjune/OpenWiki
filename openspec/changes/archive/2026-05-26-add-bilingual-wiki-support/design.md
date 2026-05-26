# Design: add-bilingual-wiki-support

## Overview

为 wiki 生态引入中英文结合的语言策略。核心设计思路是将语言偏好配置化（`WIKI.md` 新增字段）、模板中文化（`templates/` 静态文本改为中文）、lint 规则化（`wiki-lint` 新增 4 条 Yellow Warning）。设计遵循最小侵入原则：旧格式 `WIKI.md` 完全向后兼容，语言规则仅在 `primary_language: zh` 时启用。

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| WIKI.md 模板 | 定义语言配置字段的默认值和格式 | `skill/wiki-init/templates/WIKI.md` frontmatter |
| wiki-init 配置收集 | 初始化时询问语言偏好，复用已有配置时执行提问裁剪 | `skill/wiki-init/SKILL.md` Process 步骤 1 |
| wiki-init 模板 | index.md 和 log.md 的中文化静态文本 | `skill/wiki-init/templates/index.md`、`log.md` |
| wiki-ingest 页面生成 | 生成中文页面模板，slug 从中文标题翻译为英文 | `skill/wiki-ingest/SKILL.md` 步骤 5、6 |
| wiki-distill 报告生成 | 生成中文经验报告（已满足，需确认） | `skill/wiki-distill/SKILL.md` 步骤 1.5 |
| wiki-update 页面模板 | 如有页面结构描述，同步中文化 | `skill/wiki-update/SKILL.md` |
| wiki-lint 语言规则 | 4 条 Yellow Warning + 英文豁免清单 | `skill/wiki-lint/SKILL.md` Process 步骤 2 |
| wiki-lint 运行时检查 | 基于 `WIKI.md` 的 `primary_language` 决定是否启用语言规则 | wiki-lint 流程步骤 2 |

### 语言策略决策树

```
WIKI.md 中 primary_language 是什么？
  │
  ├── zh → 启用全部 4 条语言规则
  │        │
  │        ├── wiki-lint: content-not-chinese-primary (正文中文占比 >= 60%)
  │        ├── wiki-lint: missing-chinese-title (h1 含中文)
  │        ├── wiki-lint: missing-term-glossary (英文术语附中文解释)
  │        └── wiki-lint: missing-bilingual-tags (tags 含中文标签)
  │
  └── 其他 (en, ja, ...) → 跳过全部语言规则
```

### 中文占比计算流程

```
读取 wiki 页面正文
        │
        ▼
排除豁免内容：
  - 围栏代码块 (```...```)
  - 行内代码 (`code`)
  - URL (https://...)
  - YAML frontmatter (---...---)
  - 术语标注括号内英文 (中文术语（English）)
        │
        ▼
计算剩余正文的中文字符占比
        │
        ▼
占比 < 60% → content-not-chinese-primary (Yellow Warning)
占比 >= 60% → 通过
```

## Interface Design for Testability

### Public Interfaces

本次变更的核心"接口"是 `SKILL.md` 文件中的文本内容和模板文件内容。AI agent 通过读取这些文本执行行为，因此测试应验证文本的准确性和一致性。

**WIKI.md 模板新增字段**（`skill/wiki-init/templates/WIKI.md`）：

```yaml
---
wiki_root: /absolute/path/to/wiki-root
domain: <user domain description>
primary_language: zh
secondary_language: en
source_types:
  - papers
  - urls
index_categories:
  - <category_1>
remote_sync_path: wiki
auto_sync: false
---
```

**wiki-ingest 中文页面模板**（`skill/wiki-ingest/SKILL.md` 步骤 6）：

```markdown
---
title: <source title>
tags: [<relevant tags>]
sources: <number of sources>
updated: <today>
---

# <Source Title>

**来源：** <original URL or local path>
**摄入日期：** <today>
**类型：** <paper | article | transcript | code | other>

## 核心定义

<Definition of core concepts>

## 关键要点

- <bullet>

## 相关主题

- [[related-slug]] — <relationship>

## 开放问题

<If any>
```

**wiki-lint 新增语言规则**（`skill/wiki-lint/SKILL.md` Process 步骤 2）：

```markdown
### 2. Run all checks

**Red Errors**

- broken links
- missing frontmatter

**Yellow Warnings**

- orphan pages
- contradictions
- stale claims
- content-not-chinese-primary — 页面正文中文占比低于 60%（排除代码块、行内代码、URL、frontmatter、术语标注）
- missing-chinese-title — h1 标题不包含中文字符
- missing-term-glossary — 英文多词术语首次出现未附中文解释
- missing-bilingual-tags — tags 中仅有英文标签无中文对应标签

**英文豁免清单**（以下内容不触发语言规则）：
- 围栏代码块（```...```）
- 行内代码（`code`）
- URL 链接（https://...）
- YAML frontmatter（---...---）
- 术语首次标注形式（中文术语（English）或 English（中文术语））

**Blue Info**

- missing concept pages
- missing cross-references
```

### Testability Guidelines

1. **Accept dependencies, don't create them**
   - 静态测试直接读取 `SKILL.md` 和模板文件文本，不依赖运行时环境。
   - 行为测试通过 fixture 目录模拟 wiki 页面和 `WIKI.md`，不依赖真实 wiki 数据。

2. **Return results, don't produce side effects**
   - 模板变更的验证产物是更新后的文件文本。
   - lint 规则的验证产物是 `concepts/lint-<today>.md` 报告内容。

3. **Small surface area**
   - 3 个模板文件（`WIKI.md`、`index.md`、`log.md`）的静态文本变更是最小改动点。
   - 5 个 `SKILL.md` 文件的特定节是唯一需要修改的流程描述。
   - 2 个 delta spec 文件定义所有需求。

## Data Flow

```
wiki-init 初始化流程：
  用户调用 wiki-init（新实例）
          │
          ▼
  Agent 询问 domain → 询问语言偏好（zh/en）
          │
          ▼
  Agent 写入 WIKI.md（含 primary_language + secondary_language）
          │
          ▼
  Agent 从模板写入 index.md（中文）、log.md（中文）

wiki-ingest 摄入流程：
  用户提供源（URL/文件/文本）
          │
          ▼
  Agent 读取 WIKI.md → 获取 primary_language: zh
          │
          ▼
  Agent 生成中文页面模板（章节标题、字段标签为中文）
          │
          ▼
  源标题为中文 → slug 翻译为英文（依赖注入模式 → dependency-injection-pattern）

wiki-lint 检查流程：
  Agent 读取 WIKI.md → 获取 primary_language
          │
          ├── primary_language: zh → 启用语言规则
          │        │
          │        ├── 读取每个 wiki 页面
          │        ├── 排除豁免内容
          │        ├── 执行 4 条检查
          │        └── 生成 lint 报告（Yellow Warning）
          │
          └── primary_language: 其他 → 跳过语言规则
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 真实 `WIKI.md` 配置 | 使用 fixture `WIKI.md`（含/不含语言字段） |
| 真实 wiki 页面 | 使用 fixture 页面（中文/英文/混合/各种豁免场景） |
| AI agent 执行 | 静态测试只验证 `SKILL.md` 文本；E2E 测试验证 agent 行为 |
| 文件系统 | `tempfile.TemporaryDirectory` 模拟 wiki_root |

## Implementation Notes

- **向后兼容是最高优先级**：旧格式 `WIKI.md`（不含语言字段）在所有 workflow 中必须正常运行，语言字段默认视为 `zh`/`en`。
- **模板中文化是纯文本变更**：`templates/index.md` 和 `templates/log.md` 仅修改静态文本（分类标题、列名、占位文本），不改变结构和逻辑。
- **wiki-lint 语言规则必须按 primary_language 条件启用**：当 `primary_language` 不为 `zh` 时，4 条规则全部跳过，避免对英文 wiki 产生大量误报。
- **中文占比阈值 60% 是经验值**：对于技术类 wiki 页面，60% 的阈值在"正文中文为主"和"代码/配置引用较多"之间取得平衡。阈值不配置化（不需要用户调整），保持在 `SKILL.md` 中描述即可。
- **术语标注形式支持两种**：`中文术语（English Term）` 和 `English Term（中文术语）` 均视为已标注。检查时通过括号匹配识别。
- **slug 翻译依赖 AI 能力**：`wiki-ingest` 步骤 5 中"从中文标题生成英文 slug"依赖 AI agent 的翻译能力，不是调用外部翻译 API。如果 AI 翻译结果不理想，用户可以手动修改 slug。
- **wiki-distill 的 SKILL.md 已使用中文模板**（步骤 1.5 中的报告模板代码块），本次变更主要是验证和确认一致性，可能无需实际修改。
- **wiki-update 的 SKILL.md 中目前没有显式的页面模板**（它通过 diff → 确认 → 写入的方式工作），可能无需修改，但需检查确认。
- **所有 4 条语言规则均为 Yellow Warning**：不阻断流程，不改变现有 wiki-lint 的错误级别体系（Red Error / Yellow Warning / Blue Info）。
