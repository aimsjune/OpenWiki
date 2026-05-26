# wiki-distill-skill

## Purpose

定义 `wiki-distill` 技能的可观测运行时行为。该技能从代码库中提取设计经验，与现有 wiki 进行声明级比对，由用户逐条决策后调用 `wiki-ingest` 和 `wiki-update` 完成知识合并，最后委托 `wiki-lint` 验证。

## Requirements

### REQ-1: 技能资产遵循 ASSET-LAYOUT 所有权规则

`skill/wiki-distill/SKILL.md` 必须存在，且不引用 `openspec/` 或根目录散落资产。如需技能私有模板、示例或辅助文件，必须放在 `skill/wiki-distill/` 目录树下。

#### Scenario: 静态资产合规

- **GIVEN** 仓库根目录
- **WHEN** 检查 skill/wiki-distill/ 目录结构
- **THEN** SKILL.md 存在，且所有引用均在 skill/wiki-distill/ 或运行时 wiki 对象 (WIKI.md, wiki/, raw/, concepts/) 范围内

### REQ-2: Pre-condition 遵循统一配置发现顺序

`wiki-distill` 的 Pre-condition 节必须描述与 `wiki-ingest`、`wiki-update`、`wiki-lint`、`wiki-query` 完全一致的配置发现顺序：显式 `config-dir` → `~/wiki/.wiki-config` → 工作目录向上搜索 → 报错。

#### Scenario: 发现顺序一致

- **GIVEN** skill/wiki-distill/SKILL.md 和 skill/wiki-ingest/SKILL.md
- **WHEN** 提取两者的 Pre-condition 节
- **THEN** 配置发现顺序描述一致（显式 config-dir → 默认目录 → 向上搜索 → 报错）

### REQ-3: 分析阶段生成结构化经验报告

`wiki-distill` 的分析阶段扫描代码库，按默认分类（设计原则、代码模式、错误处理、测试策略、架构决策、安全实践）及 AI 动态发现的分类，提取经验，生成经验报告到 `raw/distill-<project>.md`。报告使用 YAML frontmatter + 分类 Markdown 结构。默认分析当前仓库，接受用户指定项目路径。

#### Scenario: 生成报告

- **GIVEN** 包含可识别设计模式的 fixture 代码库
- **WHEN** 执行 wiki-distill 分析阶段
- **THEN** raw/distill-<project>.md 存在，frontmatter 完整，经验按分类组织

### REQ-4: 脱敏过滤强制执行

分析阶段生成的报告中不得包含以下敏感信息：
- 个人身份：姓名、邮箱地址、手机号码
- 认证凭据：API keys、tokens、passwords、private keys
- 网络标识：内网 IP 地址、内部域名、内部项目代号
- 加密细节：加密算法实现细节、专有算法描述

保留的通用信息：设计模式名称、公开库用法、代码组织方式、错误处理策略。

#### Scenario: 脱敏

- **GIVEN** 包含姓名、邮箱、token、内网 IP 的 fixture 代码库
- **WHEN** 执行 wiki-distill 分析阶段
- **THEN** 生成的报告中不包含上述敏感信息

### REQ-5: 比对阶段执行三分类

比对阶段将经验报告中的每条经验与 wiki 进行声明级匹配，分为三类：
- **NEW**: 经验中有，wiki 中无对应内容
- **CONFLICT**: 经验中有，wiki 中也有但内容矛盾
- **EXISTS**: 经验中有，wiki 中已有完全一致的内容

匹配粒度必须在声明级别（具体主张/观点的语义比对），而非仅页面或段落级别。

#### Scenario: 三分类

- **GIVEN** 经验报告包含 3 条经验（分别对应 NEW、CONFLICT、EXISTS）
- **WHEN** 执行比对阶段
- **THEN** 输出分类结果，每条经验被正确归类

### REQ-6: NEW 条目委托 wiki-ingest 写入

对于 NEW 条目，`wiki-distill` 逐条询问用户是否新增。用户确认后，委托 `wiki-ingest` 流程写入。一条经验对应一个 wiki page（slug = 经验标题的 slugify），遵循 `wiki-ingest` 的完整流程（含 cloud sync）。

#### Scenario: NEW 写入

- **GIVEN** 比对结果为 NEW 的经验条目，用户确认新增
- **WHEN** 执行合并
- **THEN** wiki/pages/<slug>.md 被创建，index.md 和 log.md 被更新

### REQ-7: CONFLICT 条目委托 wiki-update 合并（策略C）

对于 CONFLICT 条目，`wiki-distill` 展示差异（当前 wiki 内容 vs 经验内容），给出合并建议，询问用户意见。用户确认后，委托 `wiki-update` 流程，采用策略C：融合两者内容并标注来源（经验来源 + wiki 来源）。

#### Scenario: CONFLICT 合并

- **GIVEN** 比对结果为 CONFLICT 的经验条目
- **WHEN** 用户确认合并建议
- **THEN** wiki 页面被更新，内容融合了经验和 wiki 内容，来源被标注

### REQ-8: EXISTS 条目不写页面但记录日志

对于 EXISTS 条目，`wiki-distill` 告知用户该经验已被 wiki 覆盖，不创建或修改任何 wiki 页面，但在 `wiki/log.md` 中追加一条 `distill` 操作记录。

#### Scenario: EXISTS 日志记录

- **GIVEN** 比对结果为 EXISTS 的经验条目
- **WHEN** 用户确认跳过
- **THEN** 无页面变更，log.md 追加 distill 记录

### REQ-9: 合并完成后委托 wiki-lint 验证

所有 NEW 和 CONFLICT 条目处理完毕后，`wiki-distill` 自动委托 `wiki-lint` 对整个 wiki 进行健康检查，确保交叉引用一致、无孤页、无矛盾。

#### Scenario: lint 收尾

- **GIVEN** 已完成 NEW 和 CONFLICT 合并的 wiki
- **WHEN** wiki-distill 进入收尾阶段
- **THEN** 调用 wiki-lint 并生成 concepts/lint-<today>.md

### REQ-10: 支持增量蒸馏

首次对项目执行蒸馏时进行全量分析。后续再次对同一项目执行蒸馏时，默认仅分析变更文件（通过 git diff 检测）。用户可通过参数强制全量分析。

#### Scenario: 增量蒸馏

- **GIVEN** 已执行过一次蒸馏的项目，后续有少量文件变更
- **WHEN** 再次执行 wiki-distill（无强制参数）
- **THEN** 仅分析变更文件，报告中标注 "incremental"

#### Scenario: 强制全量

- **GIVEN** 已执行过一次蒸馏的项目
- **WHEN** 执行 wiki-distill --full
- **THEN** 执行全量分析，报告中标注 "full"

### REQ-11: 接受用户指定的分析深度和项目路径

用户可通过参数控制分析深度：
- `shallow`: 仅分析 README、配置文件、顶层结构
- `medium`（默认）: 分析关键模块的代码组织和接口设计
- `deep`: 分析具体实现细节和算法选择

用户可通过参数指定分析的项目路径，默认使用当前仓库。

#### Scenario: 深度控制

- **GIVEN** 包含多层级代码的 fixture 仓库
- **WHEN** 指定 --depth shallow
- **THEN** 仅分析顶层结构和配置文件

#### Scenario: 路径指定

- **GIVEN** 用户指定 --project /path/to/other/repo
- **WHEN** 执行 wiki-distill
- **THEN** 分析指定路径的仓库，报告文件名为 distill-other-repo.md

### REQ-12: AI 动态发现新分类

在默认 6 个分类（设计原则、代码模式、错误处理、测试策略、架构决策、安全实践）之外，AI 可以在分析过程中动态发现并增加新分类。动态分类必须在报告中标注为 `dynamic`。

#### Scenario: 动态分类

- **GIVEN** 包含独特国际化策略模式的 fixture 代码库
- **WHEN** 执行 wiki-distill 分析阶段
- **THEN** 报告包含动态分类，且分类标注为 dynamic

### REQ-13: 经验报告 YAML frontmatter 结构

`raw/distill-<project>.md` 的 frontmatter 必须包含以下字段：

```yaml
---
project: <项目名>
distilled_at: <ISO 日期>
depth: shallow | medium | deep
mode: full | incremental
categories: [<分类列表>]
dynamic_categories: [<AI 动态发现的分类>]
---
```

#### Scenario: frontmatter 完整

- **GIVEN** 执行完成的 wiki-distill 分析阶段
- **WHEN** 解析 raw/distill-<project>.md 的 frontmatter
- **THEN** 所有必需字段存在且类型正确

## Edge Cases

- 用户指定的项目路径不存在或无读取权限：报错并停止
- 代码库为空（无任何可分析文件）：报告为空，告知用户
- 代码库中所有内容均被脱敏过滤：报告只含分类标题，无经验条目
- wiki 尚未初始化（无 WIKI.md）：按 Pre-condition 第 4 步报错提示先运行 wiki-init
- wiki 已初始化但 wiki/pages/ 为空：所有经验均为 NEW
- 经验报告与 wiki 无任何交集：所有经验均为 NEW
- 经验报告与 wiki 完全一致：所有经验均为 EXISTS
- 同一项目多次蒸馏：增量模式自动检测 git diff，无变更时告知用户
- 用户指定深度为 deep 但代码库只有浅层结构：按实际可分析内容输出
- 动态发现的分类与默认分类名称冲突：合并为同一分类，不重复
- 脱敏过滤后经验内容完全为空：跳过该经验，报告中标注 "filtered"
- 用户中途取消合并：已写入的内容不回滚，log 中记录部分完成状态
- git 仓库无历史（首次提交后）：增量模式回退为全量分析
