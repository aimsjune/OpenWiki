# Specification: 反向链接

## Overview

为 Page 模型增加反向链接能力，使页面能够展示"哪些页面引用了我"。

## Requirements

### REQ-BL-1: Page 结构体包含 Backlinks 字段

**Behavior**: `Page` 结构体新增 `Backlinks []string` 字段，JSON 序列化时输出为 `"backlinks"`。

**Test Verification**: 通过 `GetPageWithBacklinks` 获取页面后，JSON 输出包含 `backlinks` 数组。

```
Given: wiki 中有 page-a.md（引用了 [[page-b]]）和 page-b.md
When:  调用 GetPageWithBacklinks(fs, root, "page-b")
Then:  返回的 Page.Backlinks 包含 "page-a"
```

**Interfaces to Test Through**: `wiki.GetPageWithBacklinks()`

---

### REQ-BL-2: ComputeBacklinks 动态计算反向链接

**Behavior**: `ComputeBacklinks(fs, root, targetSlug)` 扫描 `wiki/pages/` 下所有 `.md` 文件，解析 `[[slug]]` 引用，返回所有引用了 `targetSlug` 的页面 slug 列表。

**Test Verification**: 单元测试验证扫描逻辑。

```
Given: wiki/pages/ 下有 a.md（引用 [[b]]）、c.md（引用 [[b]] 和 [[d]]）、b.md（无引用）
When:  调用 ComputeBacklinks(fs, root, "b")
Then:  返回 ["a", "c"]（顺序不重要）
```

**Interfaces to Test Through**: `wiki.ComputeBacklinks()`

---

### REQ-BL-3: 自身引用不计入反向链接

**Behavior**: 如果页面引用了自身（`[[自身slug]]`），不计入反向链接。

**Test Verification**: 单元测试验证排除逻辑。

```
Given: wiki/pages/ 下有 self-ref.md，内容包含 [[self-ref]]
When:  调用 ComputeBacklinks(fs, root, "self-ref")
Then:  返回 []（空列表）
```

**Interfaces to Test Through**: `wiki.ComputeBacklinks()`

---

### REQ-BL-4: CLI --backlinks 标志

**Behavior**: `openwiki page get <slug> --backlinks --json` 返回包含 `backlinks` 的 JSON。不带 `--backlinks` 时行为不变。

**Test Verification**: e2e 测试验证 CLI 输出。

```
Given: wiki 中有两个互相引用的页面
When:  执行 openwiki page get page-a --backlinks --json
Then:  JSON 输出包含 "backlinks" 字段
When:  执行 openwiki page get page-a --json（不带 --backlinks）
Then:  JSON 输出不包含 "backlinks" 字段（或为空数组）
```

**Interfaces to Test Through**: CLI `page get` 命令

---

### REQ-BL-5: 反向链接计算失败不影响页面读取

**Behavior**: 如果 `ComputeBacklinks` 出错（如 pages 目录不存在），`GetPageWithBacklinks` 仍返回页面，`Backlinks` 为空数组。

**Test Verification**: 单元测试使用不存在的目录路径。

```
Given: wiki_root 下没有 wiki/pages/ 目录
When:  调用 GetPageWithBacklinks(fs, root, "any-slug")
Then:  返回错误（页面不存在），而非 panic
```

**Interfaces to Test Through**: `wiki.GetPageWithBacklinks()`

---

## Test Structure

### 单元测试

```go
func TestComputeBacklinks(t *testing.T) {
    fs := NewMemFS()
    // 创建测试页面
    fs.WriteFile("wiki/pages/a.md", []byte("... [[b]] ..."), 0644)
    fs.WriteFile("wiki/pages/b.md", []byte("..."), 0644)
    fs.WriteFile("wiki/pages/c.md", []byte("... [[b]] ..."), 0644)

    backlinks, err := ComputeBacklinks(fs, "/root", "b")
    assert.NoError(t, err)
    assert.ElementsMatch(t, []string{"a", "c"}, backlinks)
}

func TestComputeBacklinksExcludesSelf(t *testing.T) { ... }

func TestGetPageWithBacklinks(t *testing.T) { ... }
```

### e2e 测试

```go
func TestPageGetWithBacklinks(t *testing.T) {
    h := harness.New(t)
    h.InitWiki()
    h.CreatePage("a", "[[b]]")
    h.CreatePage("b", "...")

    out := h.Run("page", "get", "b", "--backlinks", "--json")
    // 验证 JSON 包含 backlinks
}
```

### 测试文件

| 文件 | 目的 |
|------|------|
| `internal/wiki/page_test.go` | ComputeBacklinks / GetPageWithBacklinks 单元测试 |
| `tests/e2e/page_test.go` | CLI --backlinks e2e 测试 |

## Edge Cases

- pages 目录为空时，ComputeBacklinks 返回空数组
- pages 目录不存在时，GetPageWithBacklinks 返回页面读取错误
- 页面内容包含无效的 `[[` 语法（不闭合）时，不计入引用
- 多个页面引用同一目标时，每个页面在 backlinks 中只出现一次
