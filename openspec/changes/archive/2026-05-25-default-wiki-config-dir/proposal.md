# Proposal: default-wiki-config-dir

## Why

当前所有 wiki workflow（`wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update`）在用户没有显式提供 `config-dir` 时，只做“从当前工作目录向上搜索 `WIKI.md`”。对于已将 wiki 初始化在固定位置（如 `~/wiki/.wiki-config`）的用户来说，每次在不同目录下执行 wiki 操作都需要手动传入 `config-dir` 或先 `cd` 到包含 `WIKI.md` 的目录，体验不友好。

用户应能一次初始化，之后在任何目录下都能自动连接到自己的默认 wiki。

## What Changes

- 为所有 wiki workflow 引入统一的默认用户级配置目录 `~/wiki/.wiki-config`。
- 在没有显式 `config-dir` 时，新发现顺序为：
  1. 检查 `~/wiki/.wiki-config/WIKI.md` 是否存在且有效
  2. 如果默认目录未初始化或无效，回退到从当前工作目录向上搜索 `WIKI.md`
  3. 仍找不到时，提示用户提供 `config-dir` 或先运行 `wiki-init`
- `wiki-init` 也应在用户未指定 `config-dir` 时，将 `~/wiki/.wiki-config` 作为默认推荐。
- 命中默认目录时，必须明确告知用户当前使用的是默认配置位置。

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `wiki-query` 在无显式 `config-dir` 且 `~/wiki/.wiki-config/WIKI.md` 有效时，自动使用该默认配置 | 创建 fixture `~/wiki/.wiki-config/WIKI.md`，在不传 `config-dir` 的情况下调用 `wiki-query`，验证技能输出包含默认配置路径 |
| 2 | `wiki-ingest`、`wiki-lint`、`wiki-update` 同样遵循统一的默认配置发现顺序 | 对每个 workflow 创建 fixture 并验证默认路径被优先于工作目录搜索命中 |
| 3 | 命中默认目录时，输出明确告知用户当前使用 `~/wiki/.wiki-config` | 解析技能输出，验证包含 "default wiki config" 或 `~/wiki/.wiki-config` 提示 |
| 4 | 默认目录无效时，回退到工作目录向上搜索，不直接失败 | 创建空或损坏的 `~/wiki/.wiki-config/WIKI.md`，在包含有效 `WIKI.md` 的项目目录中调用 workflow，验证回退到项目内配置 |
| 5 | `wiki-init` 在用户未指定 `config-dir` 时，将 `~/wiki/.wiki-config` 作为默认推荐 | 调用 `wiki-init` 不传 `config-dir`，验证交互或输出中包含 `~/wiki/.wiki-config` 作为建议路径 |
| 6 | 各 wiki workflow 的 SKILL.md 文档同步更新发现顺序 | 静态测试验证所有 4 个 workflow skill 的 Pre-condition 节包含 `~/wiki/.wiki-config` 步骤 |
| 7 | README 多语言文档说明默认配置目录 | 静态测试验证 `README.md`、`README.en.md`、`README.ja.md` 提及 `~/wiki/.wiki-config` |

## Impact

- **受影响技能文件**: `skill/wiki-query/SKILL.md`, `skill/wiki-ingest/SKILL.md`, `skill/wiki-lint/SKILL.md`, `skill/wiki-update/SKILL.md`, `skill/wiki-init/SKILL.md`
- **受影响文档**: `README.md`, `README.en.md`, `README.ja.md`
- **受影响规格**: `openspec/specs/standard-wiki-runtime/spec.md`
- **受影响测试**: `tests/test_wiki_runtime_resolution.py`, `tests/test_documentation_layout.py`, `tests/test_agent_skill_smoke_e2e.py`

## Non-Goals

- 不修改“显式 `config-dir` 始终是最高优先级”这条规则
- 不改变 `wiki_root` 的解析逻辑或数据布局
- 不改变 `wiki-init` 中已有 `WIKI.md` 时的复用逻辑
- 不自动创建 `~/wiki/.wiki-config` 目录（仅在 `wiki-init` 中作为默认推荐）

## Test Considerations

- 测试框架：`unittest` (Python)
- 关键接口：各 wiki skill 的 `SKILL.md` 文本内容、`wiki-init` 交互输出
- 静态测试：验证 `SKILL.md` 中的发现顺序描述是否包含 `~/wiki/.wiki-config`
- 行为测试：验证默认路径的优先级与回退逻辑
- Smoke E2E：在 `SKILL_AGENT_E2E=1` 条件下验证真实 agent 行为
- 注意：测试不应在用户真实 `~/.wiki-config` 下创建 fixture，应在临时目录中模拟
