# Proposal: optimize-skill-structure

## Why

通过 wiki-query 检索 [[agent-skills-specification]]、[[skill-md-format]]、[[progressive-disclosure]]、[[ai-skill-development-testing-best-practices]]、[[pi-agent-extension-design]] 五个页面，对照 llm-wiki 项目的 6 个技能，发现以下结构性问题：

1. **正文未拆分** — wiki-ingest、wiki-distill 的 SKILL.md 正文接近 500 行上限，但重复出现的规则定义、模板示例、检查清单仍内联在正文中，违反 [[progressive-disclosure]] 的 Level 3 按需加载原则
2. **无 tests/ 目录** — 测试散落在项目根目录，不在技能目录内，违反 [[ai-skill-development-testing-best-practices]] 的测试金字塔原则和 [[pi-agent-extension-design]] 原则 12（可测试性设计）
3. **依赖关系隐含** — wiki-distill 委托 wiki-ingest、wiki-update 依赖 wiki-init/wiki-ingest/wiki-lint，但这些依赖隐含在正文中，Agent 需通读全文才能理解，违反 [[pi-agent-extension-design]] 原则 8（技能与实现分离）
4. **无自我纠错** — 各技能步骤是线性的「执行 → 下一步」，缺少验证环节，违反 [[ai-skill-development-testing-best-practices]] 原则 4（内置自我纠错）
5. **无验证脚本** — 没有自动化验证工具，完全依赖 Agent 手动检查，违反 [[agent-skills-specification]] 的验证工具建议

## What Changes

### 1. 正文拆分（references/）

将重复出现的规则定义、检查清单、模板示例从 SKILL.md 正文提取到 `references/` 目录：

- **wiki-lint**: 新增 `references/rules-catalog.md`（所有 lint 规则详细定义）、`references/exemption-checklist.md`（豁免清单）
- **wiki-ingest**: 新增 `references/page-template.md`（页面模板规范）、`references/slug-rules.md`（slug 生成规则）

### 2. 测试目录（tests/）

为每个技能增加 `tests/` 目录，包含测试用例描述和 fixtures：

- **wiki-lint/tests/**: 健康 wiki / 断链 wiki / 缺 scope wiki 等 fixtures + 测试用例描述
- **wiki-ingest/tests/**: 各种来源类型（URL/文件/文本）的 fixtures
- **wiki-distill/tests/**: 不同项目类型的 fixtures

### 3. 显式依赖声明

在 SKILL.md frontmatter 中增加 `composes` 字段，声明技能依赖：

- `wiki-distill` → `composes: [wiki-ingest, wiki-lint]`
- `wiki-update` → `composes: [wiki-ingest, wiki-lint, wiki-init]`

### 4. 自我纠错步骤

在关键步骤后增加验证环节：

- **wiki-ingest**: 步骤 6 写入页面后 → 新增步骤 6.1 验证写入（重读文件、检查 frontmatter、检查交叉引用）
- **wiki-lint**: 步骤 2 运行检查后 → 新增步骤 2.1 验证输出完整性（所有页面已扫描、Red Errors 有修复建议）

### 5. 验证脚本（scripts/）

为 wiki-lint 增加 `scripts/validate_wiki.py`，自动检查 wiki 结构完整性（WIKI.md 必填字段、index.md 表格格式、交叉引用可达性），输出 JSON 格式结果。

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | wiki-lint 的 SKILL.md 正文不超过 80 行，规则定义在 `references/rules-catalog.md` 中 | 行数统计 + 文件存在性检查 |
| 2 | wiki-ingest 的 SKILL.md 正文不超过 100 行，模板规范在 `references/page-template.md` 中 | 行数统计 + 文件存在性检查 |
| 3 | wiki-lint 存在 `tests/` 目录，包含至少 3 个 fixtures（healthy/broken-links/missing-scope） | 目录结构检查 |
| 4 | wiki-distill 的 frontmatter 包含 `composes: [wiki-ingest, wiki-lint]` | YAML 解析 + 字段值验证 |
| 5 | wiki-update 的 frontmatter 包含 `composes: [wiki-ingest, wiki-lint, wiki-init]` | YAML 解析 + 字段值验证 |
| 6 | wiki-ingest 步骤 6 后存在步骤 6.1（验证写入），包含重读文件、检查 frontmatter、检查交叉引用 | 文本匹配检查 |
| 7 | wiki-lint 步骤 2 后存在步骤 2.1（验证输出完整性），包含所有页面已扫描、Red Errors 有修复建议 | 文本匹配检查 |
| 8 | wiki-lint 存在 `scripts/validate_wiki.py`，可独立运行并输出 JSON | 脚本存在 + 执行测试 |
| 9 | 现有硬链接结构（wiki-update → wiki-init/wiki-ingest/wiki-lint）保持完整，新增文件自动同步 | 硬链接 inode 一致性检查 |
| 10 | 所有 SKILL.md 的 `description` 字段仍准确描述「做什么」+「何时用」 | 文本匹配检查 |

## Impact

| 组件 | 影响 |
|------|------|
| wiki-lint SKILL.md | 正文精简，规则定义移至 references/ |
| wiki-ingest SKILL.md | 正文精简，模板规范移至 references/ |
| wiki-distill SKILL.md | frontmatter 新增 composes |
| wiki-update SKILL.md | frontmatter 新增 composes |
| wiki-lint 目录 | 新增 references/、tests/、scripts/ |
| wiki-ingest 目录 | 新增 references/、tests/ |
| wiki-distill 目录 | 新增 tests/ |
| wiki-update 目录 | 硬链接自动同步新增文件 |
| wiki-init SKILL.md | 无变更（结构已简洁） |
| wiki-query SKILL.md | 无变更（结构已简洁） |

## Non-Goals

- 不修改硬链接策略（保持现有 inode 共享方式）
- 不新增或修改 lint 规则（仅重组现有规则）
- 不修改 wiki 运行时文件（WIKI.md、index.md、log.md、pages/）
- 不引入新的外部依赖（scripts/ 使用 Python 标准库）
- 不修改 wiki-distill 的三段式流程逻辑

## Test Considerations

- 测试框架：静态文件检查（行数统计、YAML 解析、文件存在性、硬链接 inode 一致性）
- 关键接口：SKILL.md frontmatter 的 composes 字段格式
- 外部依赖：无（scripts/validate_wiki.py 使用 Python 标准库）
- Mock 策略：fixtures 使用静态 wiki 目录结构，无需 mock
