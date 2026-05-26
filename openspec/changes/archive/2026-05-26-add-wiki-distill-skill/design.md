# Design: add-wiki-distill-skill

## Overview

`wiki-distill` 是一个 AI 技能（SKILL.md），通过编排现有 wiki 技能实现从代码库到 wiki 的知识蒸馏。设计遵循 "Agent-agnostic" 原则：技能描述即接口，运行时产物（`raw/distill-<project>.md`、wiki 文件系统变更）即可观测输出。

核心设计理念：**分析自动化 + 决策人工化 + 执行委托化**。

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      wiki-distill SKILL.md                       │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────────┐  │
│  │  Phase 1     │    │  Phase 2     │    │  Phase 3              │  │
│  │  ANALYZE     │───▶│  COMPARE     │───▶│  DECIDE & MERGE       │  │
│  │  (自动)      │    │  (自动+人工)  │    │  (人工决策,自动执行)   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────┬───────────┘  │
│         │                   │                       │              │
│         ▼                   ▼                       ▼              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐   │
│  │raw/distill-  │   │  三分类输出    │   │ wiki-ingest (NEW)     │   │
│  │<project>.md  │   │  NEW/CONFLICT │   │ wiki-update (CONFLICT)│   │
│  │(结构化报告)   │   │  /EXISTS      │   │ wiki-lint  (收尾)     │   │
│  └──────────────┘   └──────────────┘   └──────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| Code Scanner | 遍历代码库，按深度参数选择文件 | 文件列表 → 分类文件内容 |
| Pattern Extractor | 从代码中识别设计模式、架构决策等 | 文件内容 → 结构化经验条目 |
| Sanitizer | 强制执行脱敏过滤 | 经验条目 → 脱敏后经验条目 |
| Report Writer | 生成 `raw/distill-<project>.md` | 脱敏经验 → 结构化 Markdown 报告 |
| Wiki Comparator | 声明级匹配经验与 wiki 内容 | (报告, wiki) → 三分类结果 |
| Decision Collector | 逐条展示分类结果，收集用户决策 | 三分类结果 → 用户决策列表 |
| Merge Orchestrator | 根据决策委托 wiki-ingest/wiki-update | 决策列表 → wiki 文件系统变更 |
| Post-merge Validator | 委托 wiki-lint 验证健康 | wiki → lint 报告 |

## Interface Design for Testability

### Phase 1: ANALYZE — 纯函数式设计

分析阶段的核心输出是 `raw/distill-<project>.md` 文件。所有输入通过参数控制，输出为文件系统产物。

```
输入:
  ├── project_path: 绝对路径 (默认: cwd)
  ├── depth: shallow | medium | deep (默认: medium)
  └── mode: full | incremental (默认: 首次 full, 后续 incremental)

输出:
  └── raw/distill-<project>.md (YAML frontmatter + 分类 Markdown)
```

**可测试性**：
- 给定 fixture 代码库 + 参数 → 断言报告文件存在、frontmatter 完整、分类正确
- 脱敏过滤可独立测试：给定含敏感信息的 fixture → 断言报告不含敏感模式
- 深度控制可独立测试：给定多层 fixture + depth 参数 → 断言分析文件范围

### Phase 2: COMPARE — 声明级匹配

比对阶段的输出是三分类结果。由于比对在 AI 上下文中执行（非独立代码模块），测试通过 fixture 验证。

```
输入:
  ├── raw/distill-<project>.md (经验报告)
  └── wiki/pages/*.md (wiki 知识库)

输出 (用户可见):
  ├── NEW 条目列表:     [(经验标题, 经验内容)]
  ├── CONFLICT 条目列表: [(经验标题, 当前wiki内容, 经验内容, 合并建议)]
  └── EXISTS 条目列表:  [(经验标题, 匹配的 wiki 页面)]
```

**可测试性**：
- 提供精心构造的经验报告 fixture + wiki fixture（包含已知的 NEW/CONFLICT/EXISTS 模式）
- 在真实 Agent smoke 测试中验证分类结果

### Phase 3: DECIDE & MERGE — 编排模式

合并阶段通过委托现有技能完成，`wiki-distill` 自身不直接操作 wiki 文件。

```
NEW 条目处理:
  用户确认 → 委托 wiki-ingest (source = 经验条目文本)

CONFLICT 条目处理:
  展示 diff → 用户确认 → 委托 wiki-update (source = 经验 + wiki 融合)

EXISTS 条目处理:
  告知用户 → 追加 wiki/log.md distill 记录

收尾:
  委托 wiki-lint → 生成 lint 报告
```

**可测试性**：
- NEW 条目：断言 `wiki/pages/<slug>.md` 被创建，`wiki/index.md` 和 `wiki/log.md` 被更新
- CONFLICT 条目：断言对应 wiki 页面被更新，内容融合了经验来源
- EXISTS 条目：断言无页面变更，`wiki/log.md` 有 distill 记录
- 收尾：断言 `concepts/lint-<today>.md` 存在

### Testability Guidelines

1. **输入参数化，输出文件化**
   - 分析阶段的深度、路径作为输入参数
   - 所有阶段的关键输出写入文件系统，便于断言

2. **委托而非内联**
   - 不直接在 `wiki-distill` 中实现页面写入逻辑
   - 通过委托 wiki-ingest/wiki-update 完成，保持职责边界

3. **结构化中间产物**
   - `raw/distill-<project>.md` 使用 YAML frontmatter，可被程序解析
   - 比对阶段的分类结果可被提取验证

## Data Flow

```
┌──────────┐     ┌───────────────┐     ┌──────────────────┐
│ 代码库    │────▶│ Phase 1       │────▶│ raw/distill-     │
│ (文件系统) │     │ ANALYZE       │     │ <project>.md     │
└──────────┘     └───────────────┘     └────────┬─────────┘
                                                │
                        ┌───────────────────────┘
                        ▼
┌──────────┐     ┌───────────────┐     ┌──────────────────┐
│ wiki/     │────▶│ Phase 2       │────▶│ 三分类结果        │
│ pages/    │     │ COMPARE       │     │ (用户可见输出)    │
└──────────┘     └───────────────┘     └────────┬─────────┘
                                                │
                                    ┌───────────┘
                                    ▼
                              ┌───────────┐
                              │ 用户决策    │
                              │ (逐条确认)  │
                              └─────┬─────┘
                                    │
                        ┌───────────┼───────────┐
                        ▼           ▼           ▼
                  ┌──────────┐ ┌──────────┐ ┌──────────┐
                  │ NEW      │ │ CONFLICT │ │ EXISTS   │
                  │ →ingest  │ │ →update  │ │ →log     │
                  └──────────┘ └──────────┘ └──────────┘
                                    │
                                    ▼
                              ┌───────────┐
                              │ wiki-lint │
                              │ (收尾验证) │
                              └───────────┘
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 代码库文件系统 | Temp directory fixture (含预置代码) |
| wiki 文件系统 | Temp directory fixture (含预置 wiki 页面) |
| git (增量检测) | Temp git repo fixture |
| wiki-ingest 流程 | Agent smoke test 中真实调用 |
| wiki-update 流程 | Agent smoke test 中真实调用 |
| wiki-lint 流程 | Agent smoke test 中真实调用 |

## Implementation Notes

### SKILL.md 结构

`skill/wiki-distill/SKILL.md` 遵循现有技能的模式：
- `---` frontmatter（name, description）
- Pre-condition（统一配置发现顺序）
- Process（三步流程，每步有明确的子步骤和输出）

### 与现有技能的接口约定

- **调用 wiki-ingest**：将经验条目作为 source 文本传入，遵循 ingest 的完整 12 步流程
- **调用 wiki-update**：识别目标页面 → 展示 diff → 确认 → 写入 → 检查下游影响 → 更新 index 和 log
- **调用 wiki-lint**：执行完整 lint 流程，生成报告

### 增量蒸馏的实现

通过 git 检测变更：
- 首次蒸馏：记录 HEAD commit hash 到 `raw/.distill-<project>-state`
- 后续蒸馏：读取上次 commit，`git diff --name-only <last-commit>..HEAD` 获取变更文件
- 无 git 仓库或首次提交：回退为全量分析
- 用户 `--full` 参数：忽略状态文件，全量分析

### 脱敏过滤的正则模式

在分析阶段应用以下过滤规则：

```
姓名模式:    (常见中英文姓名格式，需上下文确认)
邮箱模式:    /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/
手机号模式:  /1[3-9]\d{9}/
IP 模式:     /(10\.\d{1,3}|172\.(1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}/
密钥模式:    /(api[_-]?key|token|secret|password|private[_-]?key)\s*[:=]\s*['"]?\S+['"]?/i
```

过滤策略：匹配到的内容替换为 `<redacted>` 标注。
