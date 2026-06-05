# Tasks: init-default-wiki-root

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

## Behavior 1: 默认路径创建 wiki

### Phase 1: RED - Write Failing Test

- [x] **1.1** 修改 `TestInitMissingWikiRoot` 为 `TestInitDefaultWikiRoot`，验证无 `wiki-root` 参数时默认在 `./openwiki/` 下创建 wiki
  - 测试文件: `internal/cli/init_test.go`
  - 调用 `cli.RunWithIO([]string{"init", "--non-interactive", "--json"}, ...)`
  - 验证 `success=true`，`data.wiki_root="./openwiki/"`，目录结构完整

- [x] **1.2** 运行测试确认 FAILS
  - 命令: `go test ./internal/cli/ -run TestInitDefaultWikiRoot -v`
  - 预期: 测试失败（当前代码仍报错 "缺少 wiki-root 参数"）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `internal/cli/init.go` 中 `runInit` 函数，将 `wiki-root` 默认值设为 `"./openwiki/"`
  - 位置: [init.go#L27-L35](file:///Users/bytedance/git/OpenWiki/internal/cli/init.go#L27-L35)
  - 变更: `remaining` 为空时 `wikiRoot = "./openwiki/"` 而非报错

- [x] **2.2** 运行测试确认 PASSES
  - 命令: `go test ./internal/cli/ -run TestInitDefaultWikiRoot -v`

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查代码是否简洁，无需额外重构（改动极小）
- [x] **3.2** 运行全部 cli 测试确保无回归
  - 命令: `go test ./internal/cli/ -v`

---

## Behavior 2: 默认路径已存在检测

### Phase 1: RED - Write Failing Test

- [x] **1.1** 新增 `TestInitDefaultWikiRootAlreadyExists` 测试
  - 测试文件: `internal/cli/init_test.go`
  - 先执行一次 init 创建 `./openwiki/`，再执行第二次 init
  - 验证第二次返回 `success=false`，`error.code="WIKI_ALREADY_EXISTS"`

- [x] **1.2** 运行测试确认 PASSES（已存在检测逻辑不变）
  - 命令: `go test ./internal/cli/ -run TestInitDefaultWikiRootAlreadyExists -v`

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 无需额外实现（`wiki.Init` 的已存在检测逻辑不变，默认路径自然适用）
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无需重构
- [x] **3.2** 运行全部 cli 测试

---

## Behavior 3: 默认路径 force 覆盖

### Phase 1: RED - Write Failing Test

- [x] **1.1** 新增 `TestInitDefaultWikiRootForceOverwrite` 测试
  - 测试文件: `internal/cli/init_test.go`
  - 先执行 `init`，再执行 `init --force`
  - 验证第二次返回 `success=true`

- [x] **1.2** 运行测试确认 PASSES（force 逻辑不变）
  - 命令: `go test ./internal/cli/ -run TestInitDefaultWikiRootForceOverwrite -v`

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 无需额外实现（`--force` 逻辑不变）
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无需重构
- [x] **3.2** 运行全部 cli 测试

---

## Verification

- [x] 运行完整 cli 测试套件: `go test ./internal/cli/ -v`
- [x] 运行 e2e 测试: `go test ./tests/e2e/ -v`
- [x] 所有测试通过
- [x] 实现与 acceptance criteria 一致
- [x] 手动验证: `go run . init` 在空目录下创建 `./openwiki/`

## Test Quality Checklist

- [x] 测试描述行为，非实现
- [x] 测试使用公共接口 `cli.RunWithIO`
- [x] 测试能经受内部重构
- [x] 测试命名描述 WHAT，非 HOW
- [x] 每个测试一个逻辑断言
- [x] 不 mock 内部协作者
