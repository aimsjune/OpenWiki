# Proposal: reuse-existing-wiki-config

## Why

当前 `wiki-init` 已经承认“目标 `config-dir` 下已存在 `WIKI.md`”是合法场景，但只停留在“询问用户 reinitialize 或 continue”的表述，没有把 `continue` 分支定义成可验证的运行时行为。

这会带来两个问题：

- 用户显式给出一个已经存在的 `config-dir` 时，`wiki-init` 仍可能重复询问 `wiki_root`、领域、来源类型、分类等已经写在 `WIKI.md` 里的信息。
- 用户虽然已经把现有 wiki 的入口给出来了，但系统没有明确说明应如何复用这份配置，以及后续如何无缝转到 `wiki-query` 等基于同一运行时契约的工作流。

这个变更要把“已有配置快速路径”定义清楚：当用户显式提供一个有效的既有 `config-dir` 时，`wiki-init` 应优先复用现有 `WIKI.md`，跳过已知信息的重复采集，并给出继续使用同一 `config-dir` 进行检索和维护的明确指引。

## What Changes

- 为 `wiki-init` 增加“显式已有 `config-dir` 快速路径”。
- 当目标 `config-dir` 下存在有效 `WIKI.md` 时，要求 `wiki-init` 直接读取并复用已有 wiki 配置，而不是重复采集已知初始化信息。
- 要求 `wiki-init` 在复用成功后，明确向用户展示当前运行时摘要，并提示可以直接使用同一 `config-dir` 调用 `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update`。
- 明确损坏配置的默认策略：若 `WIKI.md` 缺失关键字段、`wiki_root` 非绝对路径、或指向的 wiki 布局无效，则流程必须报错并停止，而不是静默猜测、自动修复或直接覆盖。

## Acceptance Criteria (Testable)

For each criterion, specify WHAT behavior should be testable:

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | 当用户在 `wiki-init` 中显式提供一个已存在且有效的 `config-dir` 时，流程必须把它识别为现有 wiki 实例入口，并复用该目录下的 `WIKI.md`。 | 通过 `wiki-init` 公共入口传入一个包含有效 `WIKI.md` 的绝对 `config-dir`。断言流程进入 continue/复用路径，且不会重写 `WIKI.md` 或重新创建已存在的数据布局。 |
| 2 | 进入已有配置快速路径后，`wiki-init` 必须跳过所有能够从 `WIKI.md` 直接解析出的已知信息采集，包括 `wiki_root`、`domain`、`source_types`、`index_categories`。 | 使用带有完整字段的 `WIKI.md` 夹具运行 `wiki-init`。断言交互记录中不会再次要求输入上述字段，且输出摘要与 `WIKI.md` 中记录的信息一致。 |
| 3 | 复用已有配置成功后，`wiki-init` 必须明确告知用户当前已连接到现有 wiki，并提示可继续使用同一 `config-dir` 运行 `wiki-query` 及其他 wiki 工作流。 | 运行 `wiki-init` 的已有配置路径。断言最终提示中包含“已连接现有 wiki”语义，以及对 `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update` 的后续使用指引。 |
| 4 | 如果显式提供的 `config-dir` 中 `WIKI.md` 无效，例如缺失 `wiki_root`、`wiki_root` 不是绝对路径、或指向的 wiki 布局缺失，`wiki-init` 必须报错并停止，不得自动猜测、修复或覆盖。 | 分别构造损坏的 `WIKI.md` 夹具并通过 `wiki-init` 运行。断言流程返回清晰错误，且不修改现有配置文件、不自动创建新布局，除非用户显式选择 `reinitialize`。 |

## Impact

- 影响 `skill/wiki-init/SKILL.md` 的前置检查与 continue 分支说明。
- 影响 `standard-wiki-runtime` 规格，新增“已有配置复用”相关要求和边界条件。
- 影响 `README.md`、`README.en.md`、`README.ja.md` 中对 `wiki-init` 与 `wiki-query` 的衔接说明。
- 影响围绕 `wiki-init` 交互流程与运行时解析的测试夹具和 E2E/文档验证。

## Non-Goals

- 不把 `wiki-init` 改造成统一的多工作流分发入口。
- 不在检测到已有配置时自动执行 `wiki-query` 或代替用户发起查询。
- 不改变 `WIKI.md` 的核心结构，也不引入多 wiki 编排。
- 不在损坏配置上做隐式修复或推断式恢复。

## Test Considerations

- 继续使用当前仓库已有的 Python `unittest` 与真实 agent smoke/E2E 测试模式。
- 优先通过公共 skill 入口和可观察输出进行验证，而不是依赖内部实现细节。
- 需要为“有效已有配置”和“损坏配置”分别准备 `WIKI.md` 夹具。
- 需要验证交互是否跳过已知问题、最终提示是否包含后续 workflow 指引，以及错误路径是否保持非破坏性。
