# Proposal: add-scope-metadata

## Why

当前 wiki 页面是扁平的，所有知识条目存放在 `wiki/pages/` 下，仅通过 tags 和交叉引用组织。随着 wiki 规模增长，缺乏一个结构化的"适用范围"维度来帮助检索和分类。一条经验或知识条目到底适用于单个代码仓库、某个领域、整个公司，还是整个行业甚至跨行业？这个信息目前无处可查。

`wiki-init` 的模板 `index.md` 已经预留了 `category_3` 区域（列名为"范围代号 | 适用范围 | 日期"），说明设计之初就预见到了这个需求，但从未落地。

## What Changes

为每个 wiki 页面增加两个 frontmatter 字段，定义知识的适用范围：

- **`scope_level`**：适用范围层级（repo / domain / company / industry / wisdom）
- **`scope_code`**：对应层级的具体代号（slug 格式，如 `llm-wiki`、`fintech`、`wisdom`）

`wiki/index.md` 的 `category_3`（"适用范围"）区域由 `wiki-ingest` 和 `wiki-update` 自动维护，按 `scope_code` 聚合展示该范围内所有页面。

所有 6 个 wiki 技能同步更新以支持此新字段。

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | Page frontmatter 模板包含 `scope_level` 和 `scope_code` 字段 | 读取 `wiki-ingest` SKILL.md 步骤 6 的模板，验证 frontmatter 中包含 `scope_level` 和 `scope_code` |
| 2 | `scope_level` 仅接受 5 个枚举值 | 读取 `wiki-lint` SKILL.md，验证 Yellow Warning 规则检查 `scope_level` 不在 {repo, domain, company, industry, wisdom} 中 |
| 3 | `scope_code` 遵循 slug 规则（小写、连字符、无特殊字符） | 读取 `wiki-lint` SKILL.md，验证 Yellow Warning 规则检查 `scope_code` 格式 |
| 4 | `wiki-ingest` 在摄入时询问用户确认 scope | 读取 `wiki-ingest` SKILL.md 步骤 3（或新增步骤），验证包含 scope 确认交互 |
| 5 | `wiki-ingest` 步骤 9 自动维护 `index.md` category_3 | 读取 `wiki-ingest` SKILL.md 步骤 9，验证包含 category_3 的更新描述 |
| 6 | `wiki-distill` 委托 ingest 时传入 scope | 读取 `wiki-distill` SKILL.md Phase 3.1，验证委托 ingest 时传递 scope 信息 |
| 7 | `wiki-distill` 根据项目路径自动推断 scope | 读取 `wiki-distill` SKILL.md Phase 1.2 或 3.1，验证包含 scope 推断逻辑描述 |
| 8 | `wiki-init` 模板 `index.md` category_3 列名正式化 | 读取 `skill/wiki-init/templates/index.md`，验证 category_3 区域列名为"范围代号 | 适用范围 | 最后更新" |
| 9 | `wiki-lint` 检查 `scope_level` 与 `scope_code` 的一致性 | 读取 `wiki-lint` SKILL.md，验证 Yellow Warning 规则：wisdom 级的 `scope_code` 应为 "wisdom" |
| 10 | `wiki-update` 在 scope 变更时同步更新 category_3 | 读取 `wiki-update` SKILL.md 步骤 5，验证包含 scope 变更时的 category_3 同步描述 |
| 11 | `wiki-query` 扫描 index 时可利用 scope 过滤 | 读取 `wiki-query` SKILL.md 步骤 1，验证描述中提到可参考 scope 信息辅助检索 |
| 12 | scope 字段缺失不阻断流程（向后兼容） | 读取 `wiki-lint` SKILL.md，验证 `missing-scope-fields` 为 Yellow Warning 而非 Red Error |
| 13 | 运行时 `wiki/index.md` category_3 按 `scope_code` 聚合 | 读取 `wiki/index.md`，验证 category_3 区域（若存在）按 `scope_code` 分组，每组下展示相关页面 |
| 14 | scope 信息出现在页面正文的"适用范围"区域 | 读取 `wiki-ingest` SKILL.md 步骤 6 的页面模板，验证正文中包含 **适用范围：** 字段 |

## Impact

- **6 个技能**：`wiki-ingest`、`wiki-distill`、`wiki-lint`、`wiki-init`、`wiki-query`、`wiki-update` 全部需要更新
- **2 个模板**：`index.md`（category_3 正式化）、`wiki-ingest` 页面模板（新增 frontmatter 字段和正文区域）
- **1 个运行时文件**：`wiki/index.md`（category_3 区域自动填充）
- **新增 spec**：`scope-metadata`（scope 字段定义、枚举值、一致性规则）
- **依赖 spec**：`wiki-lint-language-rules` 已存在，新增的 scope lint 规则自然融入

## Non-Goals

- 不引入新的目录结构（`wiki/pages/` 保持扁平）
- 不改变现有 page slug 命名规则
- 不强制 scope 字段（向后兼容，Yellow Warning 级别）
- 不自动按 scope 创建子目录或分类页面（category_3 在 index.md 中聚合即可）

## Test Considerations

- 测试框架：静态 SKILL.md 分析 + 真实 agent smoke 测试
- 关键接口：各技能 SKILL.md 中的流程描述文本
- 静态验证：模板文件中的 frontmatter 字段、index.md 列名
- Smoke 验证：wiki-ingest 输入含 scope 的源，验证 category_3 更新
