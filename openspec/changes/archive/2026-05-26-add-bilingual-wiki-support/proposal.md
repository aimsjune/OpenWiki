# Proposal: add-bilingual-wiki-support

## Why

当前 wiki 生态系统的所有产出物（模板、页面模板、技能文档）几乎全为英文，但实际使用中 wiki 页面内容以中文为主（如 `wiki/index.md` 中分类标题已改为中文）。这导致三个问题：

1. **模板与实例不一致**：`skill/wiki-init/templates/` 中的 `index.md` 和 `log.md` 是英文模板，但初始化后用户需要手动改为中文。
2. **无语言规范约束**：`wiki-lint` 不检查语言相关规则，无法确保 wiki 页面内容以中文为主。
3. **无语言配置入口**：`WIKI.md` 中没有语言偏好配置，各技能无法感知用户的语言偏好。

本变更为 wiki 生态引入中英文结合的全局语言策略：以中文为主（primary），以英文为辅（secondary），将语言偏好配置化、模板中文化、lint 规则化。

## What Changes

- **WIKI.md 新增语言配置字段**：`primary_language`（默认 `zh`）和 `secondary_language`（默认 `en`），向后兼容（旧格式不含这些字段时视为 `zh/en`）。
- **模板全面中文化**：`index.md`、`log.md`、`WIKI.md` 模板的静态文本（分类标题、列名、占位文本）改为中文。
- **wiki-ingest 页面模板中文化**：生成的页面标题、章节标题、字段标签默认使用中文；slug 采用英文翻译策略（中文标题 → 英文 slug）。
- **wiki-distill 报告模板确认中文化**：经验标题、分类标题、描述文本使用中文，代码片段保留原文。
- **wiki-lint 新增 4 条语言检查规则**：全部归类为 Yellow Warning，不阻断流程但产生警告。同时定义英文豁免清单（代码块、行内代码、URL、tags、slug、术语首次标注等场景不触发警告）。
- **wiki-init 初始化时询问语言偏好**：新 wiki 初始化时收集 `primary_language` 和 `secondary_language`，复用已有配置时跳过已存在的语言字段。

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `WIKI.md` 模板包含 `primary_language: zh` 和 `secondary_language: en` 字段 | 静态读取 `skill/wiki-init/templates/WIKI.md`，验证 frontmatter 包含这两个字段且默认值正确 |
| 2 | `wiki-init` 初始化新 wiki 时询问语言偏好，生成的 `WIKI.md` 包含语言字段 | 执行 wiki-init 初始化流程，验证输出 `WIKI.md` 包含 `primary_language` 和 `secondary_language` |
| 3 | `wiki-init` 复用已有配置时，若 `WIKI.md` 已有语言字段则跳过询问 | 提供包含语言字段的 fixture `WIKI.md`，验证复用路径不询问语言偏好 |
| 4 | `wiki-init` 复用已有配置时，若 `WIKI.md` 缺少语言字段则补问（默认 zh/en） | 提供不含语言字段的 fixture `WIKI.md`，验证补问且默认值为 zh/en |
| 5 | `index.md` 模板的静态文本全部为中文 | 静态读取 `skill/wiki-init/templates/index.md`，验证分类标题、列名、占位文本为中文 |
| 6 | `log.md` 模板的静态文本全部为中文 | 静态读取 `skill/wiki-init/templates/log.md`，验证标题、格式说明为中文 |
| 7 | `wiki-ingest` 生成的页面使用中文模板（标题、章节、字段标签为中文） | 提供 fixture 源，执行 wiki-ingest，验证生成页面的 h1、章节标题、字段标签为中文 |
| 8 | `wiki-ingest` 从中文标题生成英文 slug（翻译策略） | 提供中文标题 fixture，验证生成的 slug 为英文翻译而非拼音 |
| 9 | `wiki-lint` 新增 `content-not-chinese-primary` 规则（Yellow Warning） | 提供中文占比低于阈值的 fixture 页面，验证 lint 报告输出 Yellow Warning |
| 10 | `wiki-lint` 新增 `missing-chinese-title` 规则（Yellow Warning） | 提供 h1 标题非中文的 fixture 页面，验证 lint 报告输出 Yellow Warning |
| 11 | `wiki-lint` 新增 `missing-term-glossary` 规则（Yellow Warning） | 提供英文术语出现但无中文解释的 fixture 页面，验证 lint 报告输出 Yellow Warning |
| 12 | `wiki-lint` 新增 `missing-bilingual-tags` 规则（Yellow Warning） | 提供 tags 仅有英文无中文对应标签的 fixture 页面，验证 lint 报告输出 Yellow Warning |
| 13 | `wiki-lint` 语言规则不检查英文豁免内容（代码块、行内代码、URL、tags、slug、术语首次标注形式） | 提供包含各类豁免内容的 fixture 页面，验证不产生误报 |
| 14 | `wiki-lint` SKILL.md 的 Process 节包含 4 条新增语言规则及英文豁免清单 | 静态读取 `skill/wiki-lint/SKILL.md`，验证 Yellow Warnings 节包含语言规则描述 |
| 15 | 旧格式 `WIKI.md`（不含语言字段）向后兼容，所有 wiki workflow 正常运行 | 提供不含语言字段的 fixture `WIKI.md`，验证各 workflow 不报错 |
| 16 | `wiki-distill` 报告中的分类标题、经验标题、经验描述使用中文 | 提供 fixture 代码库，执行 wiki-distill 分析阶段，验证报告文本为中文 |

## Impact

- `skill/wiki-init/templates/` 下 3 个模板文件（`WIKI.md`、`index.md`、`log.md`）静态文本中文化
- `skill/wiki-init/SKILL.md`：新增语言偏好收集步骤及提问裁剪逻辑
- `skill/wiki-lint/SKILL.md`：Process 节新增 4 条语言检查规则及英文豁免清单
- `skill/wiki-ingest/SKILL.md`：页面模板中文化，slug 生成增加中→英翻译步骤
- `skill/wiki-distill/SKILL.md`：确认报告模板中文描述（已满足，需验证一致性）
- `skill/wiki-update/SKILL.md`：如有页面模板，同步中文化
- `WIKI.md`（运行时实例）：新增 `primary_language` 和 `secondary_language` 字段
- `openspec/specs/standard-wiki-runtime/spec.md`：新增语言配置相关需求

## Non-Goals

- 不提供多语言版本的 wiki 页面（同一页面不生成中英双语版本）
- 不改变现有 wiki 页面的内容（仅影响新生成的页面和模板）
- 不改变代码块、配置文件等原文内容
- 不改变 wiki-query 的行为（仅消费 wiki 内容）
- 不提供自动翻译功能（slug 翻译由 AI 在生成时完成，非机器翻译 API）

## Test Considerations

- 测试框架：Python（pytest），与现有 E2E 测试一致
- 关键接口：各 wiki skill 的 `SKILL.md` 文档、模板文件、运行时产物
- 静态测试：模板文件文本验证、SKILL.md 规则描述验证
- E2E 测试：wiki-init 初始化流程（含语言偏好收集）、wiki-ingest 页面生成流程、wiki-lint 语言规则触发
- 需要 fixture：含语言字段/不含语言字段的 `WIKI.md`、中文/英文混合页面、含英文术语的页面
