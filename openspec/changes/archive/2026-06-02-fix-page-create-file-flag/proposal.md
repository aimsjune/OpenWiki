# Proposal: fix-page-create-file-flag

## Why

`openwiki page create <slug> --file <path>` 和 `openwiki page update <slug> --file <path>` 无法正确读取文件内容。原因是 Go 标准库 `flag.FlagSet.Parse()` 在遇到第一个非 flag 参数（slug）时立即停止解析，导致 `--file` flag 及其值从未被处理。结果页面文件被创建但内容为空（仅含一个换行符）。

这在 wiki-ingest 流程中已造成实际故障：Agent 通过 CLI 创建 7 个页面全部为空，被迫回退到直接文件写入，绕过了 CLI 的 index.md/log.md 原子更新机制。

## What Changes

修复 `page create` 和 `page update` 子命令的参数解析逻辑，使其在位置参数（slug）之后仍能正确识别 `--file` flag。采用预扫描方式提取 flag 值，再处理位置参数。

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `openwiki page create test-slug --file /tmp/content.md --json` 将文件内容完整写入 `wiki/pages/test-slug.md` | 单元测试：创建后读取页面文件，验证内容与源文件一致 |
| 2 | `openwiki page update test-slug --file /tmp/updated.md --json` 将更新内容写入已有页面 | 单元测试：更新后读取页面文件，验证内容已变更 |
| 3 | `openwiki page create test-slug --file /tmp/content.md --json` 同时更新 `wiki/index.md` 和 `wiki/log.md` | 单元测试：验证 index.md 含新条目，log.md 含 create 记录 |
| 4 | `openwiki page create test-slug --file /tmp/content.md`（无 --json）输出 "页面已创建: test-slug" | 单元测试：验证 stdout 输出正确 |
| 5 | `openwiki page create test-slug --file /nonexistent.md --json` 返回 IO_ERROR | 单元测试：验证错误码为 IO_ERROR |
| 6 | `openwiki page create`（不指定 slug）返回错误提示 | 单元测试：验证返回 slug 缺失错误 |

## Impact

**修改文件：**
- `internal/cli/page.go` — `runPageCreate` 和 `runPageUpdate` 的参数解析逻辑

**新增文件：**
- `internal/cli/page_test.go` — 补充 `--file` flag 的参数顺序测试

**不影响：**
- `page list`、`page get`、`page delete` — 无子命令级 flag
- 其他命令组（init、config、status、log、sync）

## Non-Goals

- 不修改全局 flag 的解析方式（`--json`、`--force` 等已在 `scanGlobalFlags` 中处理）
- 不引入第三方 CLI 框架（保持 Go 标准库 `flag`）
- 不修改 `page create` 的 `--title`/`--tags` 等参数（这些信息从文件 frontmatter 中解析）

## Test Considerations

- **测试框架**：Go 标准库 `testing` + `go test`
- **关键接口**：`runPageCreate(stdout, stderr, opts, args)` — 通过 `RunWithIO` 测试
- **Mock 策略**：使用 `t.TempDir()` 隔离文件系统，通过 Harness 构建并执行二进制
- **测试重点**：参数顺序（slug 在 `--file` 之前/之后）、文件不存在、空文件
