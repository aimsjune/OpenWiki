# Proposal: add-wiki-distill-skill

## Why

当前 wiki 技能生态中，知识摄入依赖于用户主动提供外部源（URL、文件、粘贴文本），但缺少从**代码库自身**萃取经验并沉淀为知识的能力。开发者在项目中积累的设计原则、代码模式、错误处理策略等隐性知识无法被系统化地提取、比对和合并到 wiki 中。

`wiki-distill` 填补这一空白：作为"元认知工具"，从代码库中蒸馏经验，与现有 wiki 进行声明级比对，由用户逐条决策后调用 `wiki-ingest` 和 `wiki-update` 完成知识合并。

## What Changes

- 新增 `skill/wiki-distill/` 技能，提供从代码库中提取、比对、合并经验到 wiki 的完整流程。
- 三步流程：**分析** (Analyze) → **比对** (Compare) → **决策合并** (Decide & Merge)。
- 分析阶段自动扫描代码库，识别设计原则、代码模式、错误处理、测试策略、架构决策、安全实践等经验，并强制执行脱敏过滤（去除个人信息、密钥、内网地址、加密算法等）。
- 比对阶段将逐条经验与现有 wiki 内容进行声明级匹配，分为三类：NEW（新增）、CONFLICT（冲突）、EXISTS（已覆盖）。
- 决策阶段逐条询问用户，NEW 条目委托 `wiki-ingest` 写入，CONFLICT 条目委托 `wiki-update` 合并（策略C：融合两者并标注来源），完成后委托 `wiki-lint` 验证。
- 支持增量蒸馏：首次全量分析，后续默认仅分析变更（git diff），接受用户强制全量。
- 默认分析深度为中层（关键模块/接口），接受用户深度控制。

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `skill/wiki-distill/SKILL.md` 存在且遵循 ASSET-LAYOUT 规则 | 静态文件存在性检查；验证不引用 `openspec/` 或根目录散落资产 |
| 2 | Pre-condition 节遵循统一配置发现顺序（显式 config-dir → `~/wiki/.wiki-config` → 工作目录向上搜索 → 报错） | 静态文本比对：与 `wiki-ingest`、`wiki-update`、`wiki-lint` 的 Pre-condition 节一致 |
| 3 | 分析阶段生成经验报告到 `raw/distill-<project>.md`，包含 YAML frontmatter 和分类 Markdown 结构 | 提供 fixture 代码库，执行分析流程，验证报告文件存在、frontmatter 完整、脱敏规则生效 |
| 4 | 脱敏过滤强制执行：不输出姓名、邮箱、手机号、密钥/Token、内网IP/域名、加密算法实现细节 | 构造含敏感信息的 fixture，验证报告不包含任何敏感字段 |
| 5 | 比对阶段正确执行三分类：NEW / CONFLICT / EXISTS | 提供经验报告 fixture + wiki fixture，验证每条经验被正确归类 |
| 6 | NEW 条目委托 `wiki-ingest` 写入，一条经验对应一个 wiki page | 提供 NEW 条目 fixture，验证调用了 `wiki-ingest` 流程且生成了对应页面 |
| 7 | CONFLICT 条目委托 `wiki-update` 合并，采用策略C（融合两者并标注来源） | 提供 CONFLICT 条目 fixture，验证调用了 `wiki-update` 且合并内容同时标注经验来源和 wiki 来源 |
| 8 | EXISTS 条目不写页面，但记录到 `wiki/log.md` | 提供 EXISTS 条目 fixture，验证 log 中记录了 distill 操作但不产生新页面 |
| 9 | 合并完成后委托 `wiki-lint` 进行健康验证 | 提供合并后 wiki fixture，验证调用了 `wiki-lint` 流程 |
| 10 | 支持增量蒸馏：首次全量，后续默认 git diff 变更 | 模拟两次蒸馏调用，验证第二次仅分析变更文件 |
| 11 | 接受用户指定的分析深度（shallow / medium / deep）和项目路径 | 传参验证：指定 `--depth deep` 或自定义项目路径，行为符合预期 |
| 12 | 允许 AI 在预设分类之外动态发现和增加新分类 | 提供包含独特模式的 fixture，验证报告包含 AI 动态添加的分类 |

## Impact

- 新增 `skill/wiki-distill/` 目录（含 `SKILL.md` 和可选的 `templates/`）
- 新增 `openspec/specs/wiki-distill-skill/spec.md` delta spec
- 无破坏性变更，不影响现有技能
- 需新增 E2E 测试用例覆盖蒸馏流程

## Non-Goals

- 不提供代码质量分析或 lint 功能（那是 `wiki-lint` 和现有工具的事）
- 不自动生成代码文档
- 不替代 `wiki-ingest` 或 `wiki-update`，仅编排它们
- 不处理非代码仓库（如纯文档仓库）

## Test Considerations

- 测试框架：Python（pytest），与现有 E2E 测试一致
- 关键接口：`skill/wiki-distill/SKILL.md` 中描述的流程步骤
- 需要 mock 的外部依赖：无（分析、比对均在本地执行）
- 需要 fixture：含敏感信息的代码库、含设计模式的代码库、含不同深度的代码库
