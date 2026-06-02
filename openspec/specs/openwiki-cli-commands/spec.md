# Specification: openwiki-cli-commands

## Overview

openwiki CLI 提供 6 组命令：init、config、status、page、log、sync。所有命令支持 `--json` 结构化输出和全局选项。

## Requirements

### REQ-1: init 命令

**Behavior**: `openwiki init [wiki-root]` 创建 wiki 实例的完整目录结构和 openwiki.toml 配置文件。

**Test Verification**: 执行 init 后检查目录存在性和文件内容。

```
Given: 目标路径 ./test-wiki 不存在
When:  执行 openwiki init ./test-wiki --primary-language zh --secondary-language en --non-interactive --json
Then:  创建以下目录和文件：
      - ./test-wiki/openwiki.toml（含 wiki_root = ./test-wiki）
      - ./test-wiki/wiki/index.md
      - ./test-wiki/wiki/log.md
      - ./test-wiki/wiki/pages/（空目录）
      - ./test-wiki/raw/（空目录）
      - ./test-wiki/concepts/（空目录）
      JSON 输出含 success: true 和 created 数组

Given: 目标路径已存在 wiki 实例
When:  执行 openwiki init ./test-wiki --non-interactive
Then:  返回错误，code 为 "WIKI_ALREADY_EXISTS"

Given: 目标路径已存在 wiki 实例
When:  执行 openwiki init ./test-wiki --force --non-interactive --json
Then:  覆盖已有配置，返回 success: true
```

**Interfaces to Test Through**: CLI 命令 `openwiki init`

---

### REQ-2: config 命令组

**Behavior**: `openwiki config` 提供配置的读写验证能力。

**Test Verification**: 通过 CLI 命令验证各项配置操作。

```
Given: 有效的 openwiki.toml
When:  执行 openwiki config show --json
Then:  返回完整配置的 JSON 表示

Given: 有效的 openwiki.toml
When:  执行 openwiki config get wiki_root --json
Then:  data.value 等于配置中的 wiki_root

Given: 有效的 openwiki.toml
When:  执行 openwiki config set wiki.primary_language en --json
Then:  文件已更新，data.old_value 和 data.new_value 正确

Given: 有效的 openwiki.toml
When:  执行 openwiki config validate --json
Then:  success: true

Given: 无效的 openwiki.toml（缺少 wiki_root）
When:  执行 openwiki config validate --json
Then:  success: false, error.code = "CONFIG_MISSING_FIELD"
```

**Interfaces to Test Through**: CLI 命令 `openwiki config show/get/set/validate/path`

---

### REQ-3: status 命令

**Behavior**: `openwiki status` 展示 wiki 健康状态快照，含配置来源、页面统计、健康指标。

**Test Verification**: 给定已知 wiki，验证状态输出正确。

```
Given: 一个包含 5 个页面的 wiki 实例
When:  执行 openwiki status --json
Then:  data.pages.total = 5
      data.config.source 非空
      data.config.path 非空

Given: 一个包含孤立页面的 wiki 实例
When:  执行 openwiki status --verbose
Then:  输出含孤立页面的 slug 名称
```

**Interfaces to Test Through**: CLI 命令 `openwiki status`

---

### REQ-4: page 命令组

**Behavior**: `openwiki page` 提供页面 CRUD 操作，自动维护 index.md 和 log.md。

**Test Verification**: 通过 CLI 命令验证页面操作和副作用。

```
Given: 一个包含 3 个页面的 wiki 实例
When:  执行 openwiki page list --json
Then:  data.pages 数组长度为 3，每项含 slug/title/tags/scope/updated

Given: 一个包含多 scope 页面的 wiki 实例
When:  执行 openwiki page list --scope repo --json
Then:  data.pages 中所有项的 scope_code 均为指定值

Given: 一个 wiki 实例，存在页面 test-page
When:  执行 openwiki page get test-page --json
Then:  data.frontmatter.title 非空
      data.body 非空
      data.cross_references 为数组

Given: 一个 wiki 实例，存在页面 page-a 和 page-b
When:  执行 openwiki page get page-a page-b --json
Then:  data.pages 数组长度为 2

Given: 一个 wiki 实例
When:  执行 openwiki page create new-page --file /tmp/content.md --title "新页面" --tags "test,demo" --scope-level repo --scope-code my-repo --json
Then:  创建 wiki/pages/new-page.md
      index.md 含 new-page 条目
      log.md 含 create 记录
      JSON 输出 success: true

Given: 一个 wiki 实例，存在页面 test-page
When:  执行 openwiki page update test-page --file /tmp/updated.md --json
Then:  wiki/pages/test-page.md 内容已更新
      index.md 中 test-page 的日期已更新
      log.md 含 update 记录

Given: 一个 wiki 实例，存在页面 test-page
When:  执行 openwiki page delete test-page --force --json
Then:  wiki/pages/test-page.md 已删除
      index.md 不含 test-page 条目
      log.md 含 delete 记录
```

**Interfaces to Test Through**: CLI 命令 `openwiki page list/get/create/update/delete`

---

### REQ-5: log 命令组

**Behavior**: `openwiki log` 提供操作日志的查看和追加。

**Test Verification**: 通过 CLI 命令验证日志操作。

```
Given: 一个 wiki 实例，log.md 含 10 条记录
When:  执行 openwiki log show --limit 5 --json
Then:  data.entries 数组长度 ≤ 5

Given: 一个 wiki 实例
When:  执行 openwiki log append "ingest | test-page" --json
Then:  log.md 末尾新增一条记录
      JSON 输出 success: true
```

**Interfaces to Test Through**: CLI 命令 `openwiki log show/append`

---

### REQ-6: sync 命令

**Behavior**: `openwiki sync` 执行云同步，`--dry-run` 预览变更。

**Test Verification**: 通过 CLI 命令验证同步操作。

```
Given: 一个 wiki 实例，配置了 remote.sync_path
When:  执行 openwiki sync --dry-run --json
Then:  data.changes 数组列出待同步的文件
      success: true
```

**Interfaces to Test Through**: CLI 命令 `openwiki sync`

---

### REQ-7: JSON 输出格式

**Behavior**: 所有命令在 `--json` 模式下输出统一格式的 JSON。

**Test Verification**: 验证 JSON schema 一致性。

```
Given: 任意命令执行成功
When:  添加 --json 选项
Then:  JSON 输出含以下字段：
      {
        "success": true,
        "data": { ... },
        "timestamp": "2026-06-01T12:00:00Z"
      }

Given: 任意命令执行失败
When:  添加 --json 选项
Then:  JSON 输出含以下字段：
      {
        "success": false,
        "error": {
          "code": "ERROR_CODE",
          "message": "发生了什么",
          "details": { ... }
        },
        "timestamp": "2026-06-01T12:00:00Z"
      }
```

**Interfaces to Test Through**: 所有 CLI 命令的 `--json` 输出

---

### REQ-8: 全局选项

**Behavior**: 所有命令支持标准全局选项。

**Test Verification**: 验证各选项生效。

```
Given: 任意命令
When:  添加 --help/-h
Then:  输出帮助信息

Given: 任意命令
When:  添加 --version/-v
Then:  输出版本号（通过 ldflags 注入）

Given: 任意命令
When:  添加 --config/-c /path/to/openwiki.toml
Then:  使用指定配置文件

Given: 任意命令
When:  添加 --quiet/-q
Then:  不输出非错误信息

Given: 任意命令
When:  添加 --verbose/-V
Then:  输出详细信息

Given: 需要确认的命令（如 delete）
When:  添加 --force/-f
Then:  跳过确认提示

Given: 任意命令
When:  添加 --no-color
Then:  输出不含 ANSI 颜色码
```

**Interfaces to Test Through**: 所有 CLI 命令

---

## Test Structure

### E2E 测试（Harness 模式）

```go
func TestInitCreatesDirectoryStructure(t *testing.T) {
    h := harness.New(t)
    defer h.Cleanup()

    output := h.Run("init", h.TempWikiRoot(),
        "--primary-language", "zh",
        "--secondary-language", "en",
        "--non-interactive", "--json")

    var resp Response
    json.Unmarshal([]byte(output), &resp)

    if !resp.Success {
        t.Fatalf("init failed: %v", resp.Error)
    }

    // 验证目录结构
    for _, dir := range []string{"wiki", "wiki/pages", "raw", "concepts"} {
        path := filepath.Join(h.TempWikiRoot(), dir)
        if _, err := os.Stat(path); os.IsNotExist(err) {
            t.Errorf("expected directory %s to exist", path)
        }
    }
}
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `internal/cli/init_test.go` | init 命令测试 |
| `internal/cli/config_test.go` | config 命令组测试 |
| `internal/cli/status_test.go` | status 命令测试 |
| `internal/cli/page_test.go` | page 命令组测试 |
| `internal/cli/log_test.go` | log 命令组测试 |
| `internal/cli/sync_test.go` | sync 命令测试 |
| `internal/output/json_test.go` | JSON 输出格式测试 |
| `tests/e2e/harness/harness.go` | E2E 测试框架 |
| `tests/e2e/init_test.go` | init E2E 测试 |
| `tests/e2e/page_test.go` | page CRUD E2E 测试 |

## Edge Cases

- `page create` 时 slug 已存在返回错误
- `page get` 不存在的 slug 返回 `PAGE_NOT_FOUND`
- `page delete` 不存在的 slug 返回 `PAGE_NOT_FOUND`
- `page delete` 不加 `--force` 时提示确认
- `log show` 在空日志时返回空数组
- `config set` 写入权限不足时返回 `IO_ERROR`
- 批量 `page get` 部分 slug 不存在时返回部分结果 + 错误列表
