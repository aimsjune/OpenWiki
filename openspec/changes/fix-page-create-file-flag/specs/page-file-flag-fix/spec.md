# Specification: page-file-flag-fix

## Overview

修复 `openwiki page create` 和 `openwiki page update` 子命令中 `--file` flag 的参数解析 bug。当前 Go 标准库 `flag.FlagSet.Parse()` 在遇到第一个非 flag 参数（slug）时立即停止解析，导致 `--file` 及其值从未被处理，页面内容始终为空。

## Requirements

### REQ-1: page create 正确读取 --file 内容

**Behavior**: `openwiki page create <slug> --file <path>` 将指定文件的内容完整写入 wiki 页面，无论 slug 在 `--file` 之前还是之后。

**Test Verification**: 通过 CLI 命令验证文件内容被正确写入。

```
Given: 一个 wiki 实例，/tmp/test-content.md 包含 "## 测试标题\n\n测试正文。"
When:  执行 openwiki page create test-slug --file /tmp/test-content.md --json
Then:  wiki/pages/test-slug.md 内容包含 "## 测试标题" 和 "测试正文。"
      JSON 输出 success: true, data.slug = "test-slug"

Given: 一个 wiki 实例，/tmp/test-content.md 包含 "## 测试标题\n\n测试正文。"
When:  执行 openwiki page create --file /tmp/test-content.md test-slug --json
Then:  同上，内容正确写入（flag 在 slug 之前也有效）
```

**Interfaces to Test Through**: CLI 命令 `openwiki page create <slug> --file <path>`

---

### REQ-2: page update 正确读取 --file 内容

**Behavior**: `openwiki page update <slug> --file <path>` 将更新内容写入已有页面。

**Test Verification**: 通过 CLI 命令验证更新内容被正确写入。

```
Given: 一个 wiki 实例，存在页面 test-slug（原始内容 "旧内容"）
When:  执行 openwiki page update test-slug --file /tmp/updated.md --json
Then:  wiki/pages/test-slug.md 内容已变更为 /tmp/updated.md 的内容
      JSON 输出 success: true
```

**Interfaces to Test Through**: CLI 命令 `openwiki page update <slug> --file <path>`

---

### REQ-3: page create 维护 index.md 和 log.md

**Behavior**: `page create --file` 在写入页面内容的同时，自动更新 `wiki/index.md` 和 `wiki/log.md`。

**Test Verification**: 创建页面后检查 index.md 和 log.md。

```
Given: 一个 wiki 实例，index.md 不含 test-slug
When:  执行 openwiki page create test-slug --file /tmp/content.md --json
Then:  wiki/index.md 含 test-slug 条目（含标题、标签、适用范围、更新日期）
      wiki/log.md 末尾含 "create | test-slug" 记录
```

**Interfaces to Test Through**: CLI 命令 + 文件系统检查

---

### REQ-4: 文件不存在时返回 IO_ERROR

**Behavior**: 当 `--file` 指定的文件不存在时，返回明确的错误码。

**Test Verification**: 指定不存在的文件路径。

```
Given: 一个 wiki 实例，/nonexistent.md 不存在
When:  执行 openwiki page create test-slug --file /nonexistent.md --json
Then:  success: false, error.code = "IO_ERROR"
      error.message 含文件路径信息
```

**Interfaces to Test Through**: CLI 命令 `openwiki page create <slug> --file <nonexistent>`

---

### REQ-5: 无 slug 时返回错误

**Behavior**: 不指定 slug 时返回明确的错误提示。

**Test Verification**: 只传 --file 不传 slug。

```
Given: 任意 wiki 实例
When:  执行 openwiki page create --file /tmp/content.md
Then:  返回错误，提示 "page create 需要指定 slug"
```

**Interfaces to Test Through**: CLI 命令 `openwiki page create --file <path>`

---

### REQ-6: 空文件内容正确处理

**Behavior**: 当 `--file` 指定的文件为空时，创建空 body 的页面（仅含 frontmatter 或仅换行符）。

**Test Verification**: 指定空文件。

```
Given: 一个 wiki 实例，/tmp/empty.md 为空文件
When:  执行 openwiki page create test-slug --file /tmp/empty.md --json
Then:  success: true
      wiki/pages/test-slug.md 存在（内容为 "\n"）
```

**Interfaces to Test Through**: CLI 命令 `openwiki page create <slug> --file <empty>`

---

## Test Structure

### 单元测试

```go
func TestPageCreateWithFileFlag(t *testing.T) {
    // Given: 临时 wiki 实例 + 内容文件
    dir := t.TempDir()
    // ... 初始化 wiki 实例
    contentFile := filepath.Join(t.TempDir(), "content.md")
    os.WriteFile(contentFile, []byte("## 测试\n\n内容"), 0644)

    // When: 执行 page create（slug 在 --file 之前）
    var stdout, stderr bytes.Buffer
    opts := &GlobalOptions{JSON: true}
    args := []string{"test-slug", "--file", contentFile}
    err := runPageCreate(&stdout, &stderr, opts, args)

    // Then
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    // 验证 JSON 输出
    // 验证页面文件内容
    pageContent, _ := os.ReadFile(filepath.Join(dir, "wiki", "pages", "test-slug.md"))
    if !strings.Contains(string(pageContent), "## 测试") {
        t.Error("页面内容不包含预期文本")
    }
}
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `internal/cli/page_test.go` | page create/update --file flag 参数顺序测试 |

## Edge Cases

- `--file` 在 slug 之前：`page create --file /tmp/a.md test-slug` — 应正确解析
- `--file` 在 slug 之后：`page create test-slug --file /tmp/a.md` — 应正确解析
- `--file` 路径含空格：`page create test-slug --file "/tmp/my content.md"` — 应正确处理
- 重复指定 `--file`：`page create test-slug --file a.md --file b.md` — 使用最后一个值
- `--file` 无值：`page create test-slug --file` — 返回参数错误
