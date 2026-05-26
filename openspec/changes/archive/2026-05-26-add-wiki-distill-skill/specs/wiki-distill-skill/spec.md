# Specification: wiki-distill-skill

## Overview

定义 `wiki-distill` 技能的可观测运行时行为。该技能从代码库中提取设计经验，与现有 wiki 进行声明级比对，由用户逐条决策后调用 `wiki-ingest` 和 `wiki-update` 完成知识合并，最后委托 `wiki-lint` 验证。

## Requirements

### REQ-1: 技能资产遵循 ASSET-LAYOUT 所有权规则

**Behavior**: `skill/wiki-distill/SKILL.md` 必须存在，且不引用 `openspec/` 或根目录散落资产。如需技能私有模板、示例或辅助文件，必须放在 `skill/wiki-distill/` 目录树下。

**Test Verification**: 静态文件存在性检查；扫描 `SKILL.md` 内容，验证不包含对 `openspec/`、根目录 `README.md`、`assets/` 的路径引用。

```
Given: 仓库根目录
When:  检查 skill/wiki-distill/ 目录结构
Then:  SKILL.md 存在，且所有引用均在 skill/wiki-distill/ 或运行时 wiki 对象 (WIKI.md, wiki/, raw/, concepts/) 范围内
```

**Interfaces to Test Through**: `skill/wiki-distill/SKILL.md` 静态分析

---

### REQ-2: Pre-condition 遵循统一配置发现顺序

**Behavior**: `wiki-distill` 的 Pre-condition 节必须描述与 `wiki-ingest`、`wiki-update`、`wiki-lint`、`wiki-query` 完全一致的配置发现顺序：显式 `config-dir` → `~/wiki/.wiki-config` → 工作目录向上搜索 → 报错。

**Test Verification**: 静态文本比对：提取 `wiki-distill` SKILL.md 的 Pre-condition 节，与 `wiki-ingest` 的 Pre-condition 节逐句比对，验证发现步骤描述一致。

```
Given: skill/wiki-distill/SKILL.md 和 skill/wiki-ingest/SKILL.md
When:  提取两者的 Pre-condition 节
Then:  配置发现顺序描述一致（显式 config-dir → 默认目录 → 向上搜索 → 报错）
```

**Interfaces to Test Through**: `skill/wiki-distill/SKILL.md` 静态分析

---

### REQ-3: 分析阶段生成结构化经验报告

**Behavior**: `wiki-distill` 的分析阶段扫描代码库，按默认分类（设计原则、代码模式、错误处理、测试策略、架构决策、安全实践）及 AI 动态发现的分类，提取经验，生成经验报告到 `raw/distill-<project>.md`。报告使用 YAML frontmatter + 分类 Markdown 结构。默认分析当前仓库，接受用户指定项目路径。

**Test Verification**: 提供 fixture 代码库，执行分析流程，验证：
1. `raw/distill-<project>.md` 文件存在
2. frontmatter 包含 `project`、`distilled_at`、`depth`、`categories` 字段
3. 报告按分类组织，每个分类下有具体经验条目
4. 若用户指定路径，报告文件名和内容反映该路径对应的项目名

```
Given: 包含可识别设计模式的 fixture 代码库
When:  执行 wiki-distill 分析阶段
Then:  raw/distill-<project>.md 存在，frontmatter 完整，经验按分类组织
```

**Interfaces to Test Through**: `wiki-distill` 技能分析流程输出，`raw/distill-<project>.md` 文件内容

---

### REQ-4: 脱敏过滤强制执行

**Behavior**: 分析阶段生成的报告中不得包含以下敏感信息：
- 个人身份：姓名、邮箱地址、手机号码
- 认证凭据：API keys、tokens、passwords、private keys
- 网络标识：内网 IP 地址、内部域名、内部项目代号
- 加密细节：加密算法实现细节、专有算法描述

保留的通用信息：设计模式名称、公开库用法、代码组织方式、错误处理策略。

**Test Verification**: 构造包含敏感信息的 fixture 代码库（如含邮箱注释、硬编码 token、内网 IP 的配置），执行分析，验证报告不包含任何匹配敏感模式的字符串。

```
Given: 包含姓名、邮箱、token、内网 IP 的 fixture 代码库
When:  执行 wiki-distill 分析阶段
Then:  生成的报告中不包含上述敏感信息
```

**Interfaces to Test Through**: `raw/distill-<project>.md` 内容扫描

---

### REQ-5: 比对阶段执行三分类

**Behavior**: 比对阶段将经验报告中的每条经验与 wiki 进行声明级匹配，分为三类：
- **NEW**: 经验中有，wiki 中无对应内容
- **CONFLICT**: 经验中有，wiki 中也有但内容矛盾
- **EXISTS**: 经验中有，wiki 中已有完全一致的内容

匹配粒度必须在声明级别（具体主张/观点的语义比对），而非仅页面或段落级别。

**Test Verification**: 提供经验报告 fixture + wiki fixture，其中包含精心设计的 NEW、CONFLICT、EXISTS 场景。验证分类结果正确。

```
Given: 经验报告包含 3 条经验（分别对应 NEW、CONFLICT、EXISTS）
When:  执行比对阶段
Then:  输出分类结果，每条经验被正确归类
```

**Interfaces to Test Through**: `wiki-distill` 比对阶段的用户可见输出

---

### REQ-6: NEW 条目委托 wiki-ingest 写入

**Behavior**: 对于 NEW 条目，`wiki-distill` 逐条询问用户是否新增。用户确认后，委托 `wiki-ingest` 流程写入。一条经验对应一个 wiki page（slug = 经验标题的 slugify），遵循 `wiki-ingest` 的完整 12 步流程（含 cloud sync）。

**Test Verification**: 提供 NEW 条目 fixture，模拟用户确认，验证：
1. 调用了 `wiki-ingest` 流程
2. 生成了对应 slug 的 wiki page
3. `wiki/index.md` 和 `wiki/log.md` 被更新

```
Given: 比对结果为 NEW 的经验条目，用户确认新增
When:  执行合并
Then:  wiki/pages/<slug>.md 被创建，index.md 和 log.md 被更新
```

**Interfaces to Test Through**: `wiki-distill` 合并阶段的 wiki 文件系统输出

---

### REQ-7: CONFLICT 条目委托 wiki-update 合并（策略C）

**Behavior**: 对于 CONFLICT 条目，`wiki-distill` 展示差异（当前 wiki 内容 vs 经验内容），给出合并建议，询问用户意见。用户确认后，委托 `wiki-update` 流程，采用策略C：融合两者内容并标注来源（经验来源 + wiki 来源）。

**Test Verification**: 提供 CONFLICT 条目 fixture，验证：
1. 用户可见 diff 展示
2. 用户确认后调用了 `wiki-update`
3. 合并后的页面同时包含经验和 wiki 的内容，并标注了来源

```
Given: 比对结果为 CONFLICT 的经验条目
When:  用户确认合并建议
Then:  wiki 页面被更新，内容融合了经验和新信息，来源被标注
```

**Interfaces to Test Through**: `wiki-distill` 合并阶段的用户可见输出和 wiki 文件系统

---

### REQ-8: EXISTS 条目不写页面但记录日志

**Behavior**: 对于 EXISTS 条目，`wiki-distill` 告知用户该经验已被 wiki 覆盖，不创建或修改任何 wiki 页面，但在 `wiki/log.md` 中追加一条 `distill` 操作记录。

**Test Verification**: 提供 EXISTS 条目 fixture，验证：
1. 用户被告知经验已覆盖
2. 没有新页面或修改产生
3. `wiki/log.md` 中包含 `distill` 类型日志条目

```
Given: 比对结果为 EXISTS 的经验条目
When:  用户确认跳过
Then:  无页面变更，log.md 追加 distill 记录
```

**Interfaces to Test Through**: `wiki/log.md` 内容，wiki 文件系统状态

---

### REQ-9: 合并完成后委托 wiki-lint 验证

**Behavior**: 所有 NEW 和 CONFLICT 条目处理完毕后，`wiki-distill` 自动委托 `wiki-lint` 对整个 wiki 进行健康检查，确保交叉引用一致、无孤页、无矛盾。

**Test Verification**: 提供合并后的 wiki fixture，验证调用了 `wiki-lint` 流程，并生成了 lint 报告。

```
Given: 已完成 NEW 和 CONFLICT 合并的 wiki
When:  wiki-distill 进入收尾阶段
Then:  调用 wiki-lint 并生成 concepts/lint-<today>.md
```

**Interfaces to Test Through**: `wiki-distill` 收尾阶段的输出，`concepts/lint-<today>.md` 文件存在性

---

### REQ-10: 支持增量蒸馏

**Behavior**: 首次对项目执行蒸馏时进行全量分析。后续再次对同一项目执行蒸馏时，默认仅分析变更文件（通过 git diff 检测）。用户可通过参数强制全量分析。

**Test Verification**: 
1. 首次蒸馏验证全量分析
2. 修改少量文件后再次蒸馏，验证仅分析变更文件
3. 使用强制全量参数，验证全量分析

```
Given: 已执行过一次蒸馏的项目，后续有少量文件变更
When:  再次执行 wiki-distill（无强制参数）
Then:  仅分析变更文件，报告中标注 "incremental"
```

```
Given: 已执行过一次蒸馏的项目
When:  执行 wiki-distill --full
Then:  执行全量分析，报告中标注 "full"
```

**Interfaces to Test Through**: `wiki-distill` 分析阶段的输出和 `raw/distill-<project>.md` frontmatter

---

### REQ-11: 接受用户指定的分析深度和项目路径

**Behavior**: 用户可通过参数控制分析深度：
- `shallow`: 仅分析 README、配置文件、顶层结构
- `medium`（默认）: 分析关键模块的代码组织和接口设计
- `deep`: 分析具体实现细节和算法选择

用户可通过参数指定分析的项目路径，默认使用当前仓库。

**Test Verification**: 分别指定 shallow/medium/deep 深度和自定义路径，验证分析范围和行为符合预期。

```
Given: 包含多层级代码的 fixture 仓库
When:  指定 --depth shallow
Then:  仅分析顶层结构和配置文件
```

```
Given: 用户指定 --project /path/to/other/repo
When:  执行 wiki-distill
Then:  分析指定路径的仓库，报告文件名为 distill-other-repo.md
```

**Interfaces to Test Through**: `wiki-distill` 分析阶段的输出范围，`raw/distill-<project>.md` frontmatter 中的 `depth` 字段

---

### REQ-12: AI 动态发现新分类

**Behavior**: 在默认 6 个分类（设计原则、代码模式、错误处理、测试策略、架构决策、安全实践）之外，AI 可以在分析过程中动态发现并增加新分类。动态分类必须在报告中标注为 `dynamic`。

**Test Verification**: 提供包含独特模式（如特定的国际化策略、特定的日志规范）的 fixture，验证报告包含 AI 动态添加的分类且标注为 `dynamic`。

```
Given: 包含独特国际化策略模式的 fixture 代码库
When:  执行 wiki-distill 分析阶段
Then:  报告包含 "国际化策略" 等动态分类，且分类标注为 dynamic
```

**Interfaces to Test Through**: `raw/distill-<project>.md` 中的 categories frontmatter 字段和报告内容

---

### REQ-13: 经验报告 YAML frontmatter 结构

**Behavior**: `raw/distill-<project>.md` 的 frontmatter 必须包含以下字段：

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

**Test Verification**: 静态解析生成的报告文件，验证 frontmatter 字段完整。

```
Given: 执行完成的 wiki-distill 分析阶段
When:  解析 raw/distill-<project>.md 的 frontmatter
Then:  所有必需字段存在且类型正确
```

**Interfaces to Test Through**: `raw/distill-<project>.md` 的 YAML frontmatter 解析

---

## Test Structure

### Integration Tests

```python
def test_distill_skill_asset_exists_and_compliant(self):
    """验证 SKILL.md 存在且不引用禁止的资产路径"""
    # Given: 仓库根目录
    # When: 检查 skill/wiki-distill/SKILL.md
    # Then: 文件存在，内容不引用 openspec/ 或根目录散落资产
    pass

def test_precondition_matches_other_skills(self):
    """验证 Pre-condition 发现顺序与 wiki-ingest 一致"""
    # Given: skill/wiki-distill/SKILL.md 和 skill/wiki-ingest/SKILL.md
    # When: 提取 Pre-condition 节
    # Then: 发现顺序描述一致
    pass

def test_analyze_generates_structured_report(self):
    """验证分析阶段生成结构化经验报告"""
    # Given: fixture 代码库
    # When: 执行分析
    # Then: raw/distill-<project>.md 存在，frontmatter 完整
    pass

def test_sanitization_removes_sensitive_info(self):
    """验证脱敏过滤移除敏感信息"""
    # Given: 含敏感信息的 fixture
    # When: 执行分析
    # Then: 报告不含敏感字段
    pass

def test_compare_classifies_three_categories(self):
    """验证比对阶段正确执行三分类"""
    # Given: 经验报告 + wiki fixture
    # When: 执行比对
    # Then: NEW/CONFLICT/EXISTS 分类正确
    pass

def test_new_delegates_to_wiki_ingest(self):
    """验证 NEW 条目委托 wiki-ingest"""
    # Given: NEW 条目，用户确认
    # When: 执行合并
    # Then: wiki-ingest 被调用，页面生成
    pass

def test_conflict_delegates_to_wiki_update(self):
    """验证 CONFLICT 条目委托 wiki-update（策略C）"""
    # Given: CONFLICT 条目，用户确认合并
    # When: 执行合并
    # Then: wiki-update 被调用，内容融合并标注来源
    pass

def test_exists_logged_not_written(self):
    """验证 EXISTS 条目记录日志但不写页面"""
    # Given: EXISTS 条目
    # When: 用户确认跳过
    # Then: log.md 有记录，无页面变更
    pass

def test_post_merge_lint(self):
    """验证合并后调用 wiki-lint"""
    # Given: 合并完成的 wiki
    # When: wiki-distill 收尾
    # Then: wiki-lint 被调用
    pass

def test_incremental_distillation(self):
    """验证增量蒸馏"""
    # Given: 已蒸馏过的项目，后续有变更
    # When: 再次执行（无 --full）
    # Then: 仅分析变更文件
    pass

def test_depth_control(self):
    """验证深度控制参数"""
    # Given: 多层级 fixture
    # When: 指定 --depth shallow/medium/deep
    # Then: 分析范围符合预期
    pass

def test_dynamic_category_discovery(self):
    """验证 AI 动态发现新分类"""
    # Given: 含独特模式的 fixture
    # When: 执行分析
    # Then: 报告包含动态分类且标注为 dynamic
    pass
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_wiki_distill_static.py` | 静态验证：SKILL.md 资产合规性、Pre-condition 一致性、frontmatter 结构 |
| `tests/test_wiki_distill_analyze.py` | 分析阶段验证：报告生成、脱敏过滤、分类发现、深度控制 |
| `tests/test_wiki_distill_compare.py` | 比对阶段验证：三分类正确性 |
| `tests/test_wiki_distill_merge.py` | 合并阶段验证：NEW 委托 ingest、CONFLICT 委托 update、EXISTS 日志记录 |
| `tests/test_wiki_distill_e2e.py` | 端到端验证：完整蒸馏流程 + lint 收尾 |

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
