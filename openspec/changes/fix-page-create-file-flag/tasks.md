# Tasks: fix-page-create-file-flag

## TDD Workflow: RED → GREEN → REFACTOR

**CRITICAL: This workflow uses VERTICAL SLICES (tracer bullets)**

```
WRONG (horizontal slicing - DO NOT USE):
  RED:   test1, test2, test3
  GREEN: impl1, impl2, impl3

RIGHT (vertical slices - USE THIS):
  RED→GREEN→REFACTOR: test1→impl1
  RED→GREEN→REFACTOR: test2→impl2
  RED→GREEN→REFACTOR: test3→impl3
```

**Rules:**
1. Write ONE failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed, ensure tests pass
4. Only then move to next behavior

---

## Behavior 1: extractSubcommandFlags 辅助函数

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/page_test.go` 编写 `TestExtractSubcommandFlags` 测试
  - 测试：`args=["test-slug", "--file", "/tmp/a.md"]` → `flags={"file": "/tmp/a.md"}`, `positional=["test-slug"]`
  - 测试：`args=["--file", "/tmp/a.md", "test-slug"]` → 同上（flag 在前）
  - 测试：`args=["test-slug"]` → `flags={}`, `positional=["test-slug"]`
  - 测试：`args=["--file"]` → `flags={"file": ""}`, `positional=[]`（flag 无值）
  - 测试：`args=["--file", "/tmp/a.md", "--file", "/tmp/b.md"]` → 使用最后一个值
- [x] **1.2** 运行测试确认 FAILS（函数尚未定义）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/page.go` 实现 `extractSubcommandFlags` 函数
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查代码清晰度，确保函数签名和注释完整
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 2: page create --file 正确写入内容

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/page_test.go` 编写 `TestPageCreateWithFileFlag` 测试
  - 测试：创建 wiki 实例 + 内容文件，执行 `page create test-slug --file /tmp/content.md --json`
  - 验证：页面文件内容与源文件一致
  - 验证：JSON 输出 `success: true`, `data.slug = "test-slug"`
  - 验证：index.md 含新条目
- [x] **1.2** 运行测试确认 FAILS（当前 --file 不会被解析）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 改造 `runPageCreate`：用 `extractSubcommandFlags` 替代 `flag.FlagSet.Parse()`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 移除 `runPageCreate` 中不再使用的 `flag` 包引用
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 3: page update --file 正确更新内容

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/page_test.go` 编写 `TestPageUpdateWithFileFlag` 测试
  - 测试：创建 wiki 实例 + 已有页面，执行 `page update test-slug --file /tmp/updated.md --json`
  - 验证：页面文件内容已更新
  - 验证：JSON 输出 `success: true`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 改造 `runPageUpdate`：用 `extractSubcommandFlags` 替代 `flag.FlagSet.Parse()`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 移除 `runPageUpdate` 中不再使用的 `flag` 包引用
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 4: 错误处理（文件不存在、无 slug、空文件）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/page_test.go` 编写错误处理测试
  - 测试：`page create test-slug --file /nonexistent.md --json` → `error.code = "IO_ERROR"`
  - 测试：`page create --file /tmp/a.md`（无 slug）→ 返回 slug 缺失错误
  - 测试：`page create test-slug --file /tmp/empty.md --json` → `success: true`，页面存在
- [x] **1.2** 运行测试确认 FAILS（部分可能已通过，确认新测试正确）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 确认现有错误处理逻辑覆盖所有场景（无需额外代码，验证通过即可）
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查错误消息是否清晰、包含足够上下文
- [x] **3.2** 运行全部测试确认通过

---

## Verification

完成所有 Behavior 后：

- [x] 运行 `make test` 确认全部 Go 单元测试通过
- [x] 运行 `make test-e2e` 确认全部 E2E 测试通过
- [x] 运行 `python3 -m unittest discover -s tests -p "test_*.py" -v` 确认全部 Python 测试通过
- [x] 手动执行 `openwiki page create test-slug --file /tmp/content.md --json` 验证内容正确写入

## Test Quality Checklist

- [x] 测试描述 BEHAVIOR，而非实现细节
- [x] 测试使用 PUBLIC 接口（CLI 命令或公开函数）
- [x] 测试在内部重构后仍然有效
- [x] 测试名称描述 WHAT，而非 HOW
- [x] 每个测试一个逻辑断言
- [x] 不 mock 内部协作者（使用 TempDir 替代 mock）
