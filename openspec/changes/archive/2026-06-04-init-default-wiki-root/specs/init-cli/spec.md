# Specification: init-cli

## Overview

定义 `openwiki init` 命令在未指定 `wiki-root` 参数时的默认行为。

## Requirements

### REQ-1: 默认 wiki-root 路径

**Behavior**: 当 `openwiki init` 不带 `wiki-root` 位置参数时，默认使用 `./openwiki/` 作为 wiki 根目录。

**Test Verification**: 调用 `cli.RunWithIO([]string{"init", "--non-interactive", "--json"}, ...)` 不传路径参数，验证 JSON 输出中 `data.wiki_root` 为 `"./openwiki/"` 且 `success` 为 `true`。

```
Given: 当前工作目录下不存在 ./openwiki/ 目录
When:  执行 openwiki init --json
Then:  在 ./openwiki/ 下创建完整 wiki 结构，JSON 返回 success=true, data.wiki_root="./openwiki/"
```

**Interfaces to Test Through**: `cli.RunWithIO`

---

### REQ-2: 默认路径已存在检测

**Behavior**: 当 `./openwiki/openwiki.toml` 已存在时，不带参数的 `openwiki init` 应返回 `WIKI_ALREADY_EXISTS` 错误。

**Test Verification**: 连续调用两次 `cli.RunWithIO([]string{"init", "--json"}, ...)`，第二次返回 `success=false` 且 `error.code` 为 `"WIKI_ALREADY_EXISTS"`。

```
Given: ./openwiki/openwiki.toml 已存在
When:  执行 openwiki init --json
Then:  返回 success=false, error.code="WIKI_ALREADY_EXISTS"
```

**Interfaces to Test Through**: `cli.RunWithIO`

---

### REQ-3: 传入路径时行为不变

**Behavior**: 当 `openwiki init <path>` 传入显式路径时，行为与现有实现完全一致。

**Test Verification**: 现有测试 `TestInitCreatesDirectoryStructure` 保持通过。

```
Given: 传入显式 wiki-root 路径
When:  执行 openwiki init <path> --json
Then:  在指定路径创建 wiki 结构，行为与变更前一致
```

**Interfaces to Test Through**: `cli.RunWithIO`

---

### REQ-4: --force 覆盖默认路径

**Behavior**: `openwiki init --force`（无 wiki-root 参数）应覆盖已存在的 `./openwiki/`。

**Test Verification**: 先执行 `init`，再执行 `init --force`，第二次返回 `success=true`。

```
Given: ./openwiki/ 已存在
When:  执行 openwiki init --force --json
Then:  覆盖成功，返回 success=true
```

**Interfaces to Test Through**: `cli.RunWithIO`

---

## Test Structure

### 单元测试

测试文件: `internal/cli/init_test.go`

需要新增/修改的测试用例:

| 测试函数 | 目的 |
|---------|------|
| `TestInitDefaultWikiRoot` | 验证无参数时默认使用 `./openwiki/` |
| `TestInitDefaultWikiRootAlreadyExists` | 验证默认路径已存在时报错 |
| `TestInitDefaultWikiRootForceOverwrite` | 验证 `--force` 覆盖默认路径 |
| `TestInitMissingWikiRoot` | 修改为验证默认行为（不再期望报错） |

### 测试文件

| File | Purpose |
|------|---------|
| `internal/cli/init_test.go` | 修改现有测试，新增默认路径测试用例 |

## Edge Cases

- `./openwiki/` 父目录不存在但可写：正常创建（`os.MkdirAll` 自动处理）
- `./openwiki/` 路径包含符号链接：遵循文件系统行为
- 当前目录无写权限：返回文件系统错误
