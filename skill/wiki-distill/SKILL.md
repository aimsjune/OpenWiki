---
name: wiki-distill
description: 从代码库中蒸馏设计经验，与现有 wiki 比对后合并。适用于从已完成项目中提取设计原则、代码模式、架构决策等隐性知识并沉淀到 wiki 中。
---

# Wiki Distill

从代码库中提取经验，与 wiki 比对，用户决策后合并知识。

## Pre-condition

使用以下顺序发现配置目录：

1. 如果用户显式提供了 `config-dir`，使用它。
2. 否则，检查 `~/wiki/.wiki-config/WIKI.md`。如果存在且有效，将其作为默认 wiki 配置。
3. 如果默认配置未找到或无效，从当前工作目录向上搜索 `WIKI.md`。
4. 如果仍未找到 `WIKI.md`，请用户提供绝对 `config-dir` 或告知其先运行 `wiki-init`。

如果使用了默认 wiki 配置（`~/wiki/.wiki-config`），告知用户当前使用的是默认 wiki 配置。

读取 `WIKI.md` 解析：

- 绝对 `wiki_root`
- `raw/`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `concepts/`
- `remote_sync_path`
- `auto_sync`

不要从 `cwd`、旧 agent 特定文件或兼容目录推断这些路径。

## 参数

用户可通过以下参数控制蒸馏行为：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--project <path>` | 要分析的项目路径（绝对路径） | 当前仓库 |
| `--depth <level>` | 分析深度：`shallow` / `medium` / `deep` | `medium` |
| `--full` | 强制全量分析（忽略增量状态） | 首次全量，后续增量 |

## Process

### Phase 1: ANALYZE — 分析代码库，提取经验

#### 1.1 确定分析范围

**项目路径**：如果用户通过 `--project` 指定了路径，使用该路径。否则使用当前仓库根目录。

**分析深度**：

- `shallow`：仅分析 README、配置文件、顶层目录结构
- `medium`（默认）：分析关键模块的代码组织、接口设计、核心逻辑
- `deep`：分析具体实现细节、算法选择、微观模式

**分析模式**：

- 首次蒸馏：全量分析
- 后续蒸馏：检查 `raw/.distill-<project>-state`，获取上次 HEAD commit，通过 `git diff --name-only <last-commit>..HEAD` 获取变更文件，仅分析变更部分
- 无 git 仓库或首次提交：回退为全量分析
- 用户指定 `--full`：忽略状态文件，全量分析
- 无变更时：告知用户并跳过分析

#### 1.2 扫描代码库

按深度参数遍历代码库文件。优先关注：
- 配置文件（TOML、YAML、JSON、ENV 模板）
- 核心模块入口和接口定义
- 错误处理模式
- 测试文件和测试策略
- 架构决策记录（ADR）

#### 1.3 识别经验模式

从代码中提取经验，按以下分类组织。**默认分类**：

| 分类 | 识别目标 |
|------|---------|
| 设计原则 | 配置与代码分离、显式优于隐式、单一职责等 |
| 代码模式 | Repository 模式、Factory 模式、依赖注入等 |
| 错误处理 | fail-fast 策略、错误包装、重试机制等 |
| 测试策略 | 分层测试、mock 策略、fixture 管理等 |
| 架构决策 | 技术选型原因、模块划分逻辑、数据流设计等 |
| 安全实践 | 输入校验、权限控制、敏感信息保护等 |

**动态分类**：在分析过程中，AI 可以动态发现并增加上述 6 个分类之外的新分类。动态分类必须在报告中标注来源为 `dynamic`。如果动态发现的分类与默认分类名称冲突，合并为同一分类。

#### 1.4 强制执行脱敏过滤

在将经验写入报告前，必须执行脱敏过滤。**必须移除**以下敏感信息：

- **个人身份**：姓名、邮箱地址、手机号码
- **认证凭据**：API keys、tokens、passwords、private keys
- **网络标识**：内网 IP 地址（10.x, 172.16-31.x, 192.168.x）、内部域名
- **加密细节**：加密算法实现细节、专有算法描述

匹配到的敏感内容替换为 `<redacted>`。如果某条经验脱敏后内容完全为空，跳过该经验并在报告中标注 "filtered"。

**可以保留**：通用设计模式名称、公开库用法、代码组织方式、通用错误处理策略。

#### 1.5 生成经验报告

将提取的经验写入 `raw/distill-<project>.md`。使用以下结构：

```markdown
---
project: <项目名>
distilled_at: <ISO 日期>
depth: shallow | medium | deep
mode: full | incremental
categories: [设计原则, 代码模式, ...]
dynamic_categories: [<AI 动态发现的分类>]
---

# 经验蒸馏报告: <项目名>

> 蒸馏日期: <today>
> 分析深度: <depth>
> 分析模式: <mode>

## 设计原则

### <经验标题 1>

<经验描述：从代码中提取的具体原则、上下文、示例>

**来源文件**: <相对路径>

### <经验标题 2>

...

## 代码模式

...

## <动态分类> [dynamic]

...
```

#### 1.6 展示报告摘要

向用户展示：
- 报告路径：`raw/distill-<project>.md`
- 发现的分类和每类经验数量
- 脱敏过滤统计（如有被过滤的敏感信息）

询问用户是否继续进入比对阶段。

---

### Phase 2: COMPARE — 与 wiki 比对

#### 2.1 加载 wiki 内容

读取 `wiki/index.md` 和所有 `wiki/pages/*.md`，构建 wiki 知识库的完整视图。

#### 2.2 逐条声明级比对

对于经验报告中的每条经验，执行声明级匹配：

1. 从经验中提取核心声明（具体的观点、原则、模式描述）
2. 在 wiki 中搜索相关页面（通过 index.md 的 tags 和摘要匹配）
3. 读取相关页面，在**声明级别**进行语义比对（判断 wiki 中是否有相同或矛盾的具体主张）

#### 2.3 三分类

| 分类 | 判定标准 | 图标 |
|------|---------|------|
| **NEW** | wiki 中无对应页面，或对应页面不涉及该声明 | 🆕 |
| **CONFLICT** | wiki 中有对应声明但内容矛盾 | ⚠️ |
| **EXISTS** | wiki 中有完全一致的声明 | ✅ |

#### 2.4 展示比对结果

逐条展示比对结果：

对于 **NEW** 条目：
```
🆕 NEW: <经验标题>
   经验: <经验内容摘要>
   Wiki 状态: 无对应内容
```

对于 **CONFLICT** 条目：
```
⚠️ CONFLICT: <经验标题>
   当前 wiki (<页面名>): <当前 wiki 中的内容>
   经验: <经验内容>
   建议: <合并建议 — 策略C：融合两者并标注来源>
```

对于 **EXISTS** 条目：
```
✅ EXISTS: <经验标题>
   已覆盖于: <wiki 页面名>
```

---

### Phase 3: DECIDE & MERGE — 决策与合并

逐条询问用户，根据分类不同采取不同的处理方式。

#### 3.1 NEW 条目处理

对于每条 NEW 经验，AI 根据项目路径自动推断适用范围：

- `scope_level` 默认为 `repo`（从代码仓库蒸馏）
- `scope_code` 默认为项目目录名（如 `llm-wiki`），遵循 slug 规则
- scope_level 中文名映射：`repo`→代码仓库、`domain`→领域、`company`→公司、`industry`→行业、`wisdom`→智慧

展示格式：

```
🆕 NEW: <经验标题>
   经验: <经验内容摘要>
   Wiki 状态: 无对应内容
   适用范围: <scope_level 中文名>（<scope_code>）
```

询问用户：

> "是否将这条经验新增到 wiki？[Y/n/修改适用范围]"

用户确认后，委托 `wiki-ingest` 写入。传递确认后的 scope_level 和 scope_code：

- slug = 经验标题的 slugify（小写、连字符、无特殊字符）
- source = 经验描述文本
- scope_level = 确认后的值
- scope_code = 确认后的值
- 遵循 `wiki-ingest` 的完整流程（含 cloud sync）

#### 3.2 CONFLICT 条目处理

对于每条 CONFLICT 经验，展示 diff 和合并建议后，询问用户：

> "是否按建议合并？[Y/n/skip]"

用户确认后，委托 `wiki-update` 执行合并。采用**策略C**：

- 融合经验和 wiki 内容
- 在合并后的页面中标注 `经验来源: distill-<project>` 和 `wiki 来源: <原页面名>`
- 遵循 `wiki-update` 的完整流程（diff → 确认 → 写入 → 下游检查）

#### 3.3 EXISTS 条目处理

对于 EXISTS 条目，告知用户该经验已被 wiki 覆盖，无需操作。追加 `wiki/log.md` 记录：

```markdown
## [<today>] distill | <project>
- EXISTS: <N> 条经验已覆盖，跳过
- 来源页面: <页面列表>
```

#### 3.4 收尾：委托 wiki-lint

所有 NEW 和 CONFLICT 条目处理完毕后，委托 `wiki-lint` 对整个 wiki 进行健康检查，验证：
- 交叉引用一致性
- 无孤立页面
- 无新增矛盾

#### 3.5 追加完整日志

在 `wiki/log.md` 中追加本次蒸馏的完整操作记录：

```markdown
## [<today>] distill | <project>
- 分析深度: <depth>, 模式: <mode>
- 总经验数: <N>
- NEW: <N> 条 → 新增页面: <页面列表>
- CONFLICT: <N> 条 → 更新页面: <页面列表>
- EXISTS: <N> 条 → 跳过
- 脱敏过滤: <N> 条
- 收尾验证: wiki-lint <结果>
```

#### 3.6 更新增量状态

更新 `raw/.distill-<project>-state`，记录当前 HEAD commit hash，供下次增量蒸馏使用。

## 常见错误

- 分析深度不合适导致遗漏或噪音过多 — 默认用 `medium`，按需调整
- 脱敏过滤遗漏 — 必须在写入报告前二次确认
- 比对粒度太粗 — 必须在声明级别比对，而非仅页面或段落级别
- 跳过用户决策直接合并 — 每条 NEW 和 CONFLICT 必须经用户确认
- 合并后忘记委托 wiki-lint — 收尾步骤不可省略
- 增量状态丢失导致重复全量分析 — 蒸馏完成后必须更新状态文件
