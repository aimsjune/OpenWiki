# Design: default-wiki-config-dir

## Overview

为所有 wiki workflow 引入统一的默认用户级配置目录 `~/wiki/.wiki-config`。核心设计思路是将发现顺序从两段式（显式 → 工作目录搜索）扩展为三段式（显式 → 默认目录 → 工作目录搜索），并保持与现有运行时契约的完全兼容。

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| wiki workflow Pre-condition | 定义配置发现顺序，AI agent 据此执行 | `skill/<name>/SKILL.md` 中的 Pre-condition 节 |
| wiki-init recommendation | 在用户未指定 config-dir 时推荐默认路径 | `skill/wiki-init/SKILL.md` 中的 Process 节 |
| wiki-init reuse path | 复用已有 config-dir（含默认目录）的现有逻辑 | `skill/wiki-init/SKILL.md` 中的 Pre-flight 节（已有，无需修改） |
| runtime resolution test | 静态验证四个 workflow 的发现顺序一致 | `tests/test_wiki_runtime_resolution.py` |
| documentation layout test | 静态验证 README 提及默认目录 | `tests/test_documentation_layout.py` |
| agent smoke E2E test | 真实 agent 行为验证 | `tests/test_agent_skill_smoke_e2e.py` |

### 发现顺序决策树

```
用户是否显式提供了 config-dir？
  ├── 是 → 直接使用
  └── 否 → ~/wiki/.wiki-config/WIKI.md 存在且有效？
            ├── 是 → 使用默认配置 + 告知用户
            └── 否 → 从 cwd 向上搜索 WIKI.md？
                      ├── 找到 → 使用项目内配置
                      └── 未找到 → 提示用户提供 config-dir 或运行 wiki-init
```

## Interface Design for Testability

### Public Interfaces

本次变更的核心"接口"是 `SKILL.md` 文件中的文本内容。AI agent 通过读取这些文本执行行为，因此测试应验证文本的准确性和一致性。

**四个 wiki workflow 的 Pre-condition 节（统一模板）**：

```markdown
## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, check `~/wiki/.wiki-config/WIKI.md`. If it exists and is valid, use it as the default wiki config.
3. If the default config is not found or invalid, search upward from the current working directory for `WIKI.md`.
4. If `WIKI.md` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.
```

**wiki-init 的默认推荐（追加到 Process 节）**：

```markdown
If the user does not provide a `config-dir`, recommend `~/wiki/.wiki-config` as the default location.
```

### Testability Guidelines

1. **Accept dependencies, don't create them**
   - 测试不依赖真实的 `~/.wiki-config` 目录。行为测试通过 fixture 目录模拟，静态测试通过读取 `SKILL.md` 文本断言。

2. **Return results, don't produce side effects**
   - 本次变更的核心产物是文本更新。测试验证更新后的文本内容，不产生副作用。

3. **Small surface area**
   - 五个 `SKILL.md` 文件的 Pre-condition/Process 节是唯一需要修改的接口。
   - 三个 README 文件是文档同步点。
   - 一个主规格 delta spec 是规格同步点。

## Data Flow

```
用户调用 wiki workflow（无显式 config-dir）
        │
        ▼
Agent 读取 SKILL.md Pre-condition 节
        │
        ▼
Agent 按发现顺序检查：
  1. ~/wiki/.wiki-config/WIKI.md
  2. cwd 向上搜索 WIKI.md
        │
        ▼
Agent 解析命中的 WIKI.md，继续执行 workflow
```

测试流程：

```
测试读取 SKILL.md 文本
        │
        ▼
断言 Pre-condition 节包含 ~/wiki/.wiki-config
        │
        ▼
断言四个 workflow 的发现顺序描述一致
        │
        ▼
（可选 SKILL_AGENT_E2E=1）真实 agent 行为验证
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 真实 `~/.wiki-config` 目录 | 静态测试不触碰文件系统；行为测试使用 `tempfile.TemporaryDirectory` 模拟 |
| 真实 `wiki_root` 数据 | 使用 fixture 目录，不依赖真实 wiki 数据 |
| AI agent 执行 | 静态测试只验证 `SKILL.md` 文本；E2E 测试通过 `SKILL_AGENT_E2E=1` 可选启用 |

## Implementation Notes

- 四个 wiki workflow（`wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update`）的 Pre-condition 节应保持文本完全一致，确保 AI agent 在不同 workflow 间获得相同的发现行为。
- `wiki-init` 的已有 `config-dir` 复用逻辑（Pre-flight 节）无需修改：当用户显式传入 `~/wiki/.wiki-config` 时，已能正确复用。本次只需在 Process 节追加"未指定时的默认推荐"。
- `~/wiki/.wiki-config` 是约定路径，不写入配置文件或环境变量。修改默认路径只需更新 `SKILL.md` 文本。
- 不需要引入新的配置文件或运行时状态文件。
