# Proposal: init-default-wiki-root

## Why

当前 `openwiki init` 命令要求必须传入 `wiki-root` 参数，不传则直接报错。这导致最简单的使用场景（在当前目录下初始化 wiki）需要用户多输入一个路径参数，体验不够友好。`git init`、`npm init` 等主流 CLI 工具都支持不带参数时使用当前目录作为默认值，`openwiki init` 应遵循同样的惯例。

## What Changes

- `openwiki init` 不带 `wiki-root` 参数时，默认使用 `./openwiki/` 作为 wiki 根目录
- 如果 `./openwiki/` 目录不存在，自动创建
- 如果 `./openwiki/openwiki.toml` 已存在，报错 "wiki 实例已存在"（与现有行为一致）
- 传入 `wiki-root` 参数时行为不变

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `openwiki init`（无参数）在 `./openwiki/` 下创建完整的 wiki 目录结构 | 检查 `./openwiki/openwiki.toml`、`./openwiki/wiki/index.md`、`./openwiki/wiki/log.md`、`./openwiki/wiki/pages/`、`./openwiki/raw/`、`./openwiki/concepts/` 均存在 |
| 2 | `openwiki init`（无参数）在 `./openwiki/` 已存在时返回 `WIKI_ALREADY_EXISTS` 错误 | 连续执行两次 `openwiki init`，第二次返回错误且 code 为 `WIKI_ALREADY_EXISTS` |
| 3 | `openwiki init <path>` 传入路径时行为不变 | 与现有测试 `TestInitCreatesDirectoryStructure` 行为一致 |
| 4 | `openwiki init --force`（无参数）覆盖已存在的 `./openwiki/` | 先 init 再 `init --force`，第二次成功 |
| 5 | `--json` 输出中 `wiki_root` 字段为 `./openwiki/`（默认情况） | JSON 输出中 `data.wiki_root` 等于 `"./openwiki/"` |

## Impact

- 仅修改 `internal/cli/init.go` 中的参数解析逻辑
- 需更新 `internal/cli/init_test.go` 中 `TestInitMissingWikiRoot` 测试用例

## Non-Goals

- 不修改目录结构、配置文件模板、选项定义
- 不修改 `--force`、`--json` 等其他行为
- 不添加交互式确认流程

## Test Considerations

- 测试框架：Go 标准 `testing` 包
- 关键接口：`cli.RunWithIO` 函数
- 无外部依赖需要 mock
