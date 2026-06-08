# Design: init-default-wiki-root

## Overview

将 `openwiki init` 的 `wiki-root` 参数从必填改为可选，默认值为 `"./openwiki/"`。改动范围极小，仅涉及参数解析逻辑。

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| `internal/cli/init.go:runInit` | 解析 init 子命令参数并调用 wiki 初始化 | `runInit(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error` |
| `internal/wiki/init.go:Init` | 创建 wiki 目录结构和配置文件 | `Init(fs FS, root string, cfg interface{}) error` |

### 变更点

```
runInit() 参数解析:
  变更前: remaining 为空 → 报错 "缺少 wiki-root 参数"
  变更后: remaining 为空 → wikiRoot = "./openwiki/"
```

`wiki.Init` / `wiki.InitForce` 完全不变。

## Interface Design for Testability

### Public Interfaces

`cli.RunWithIO` 是测试入口，通过传入不同的 `args` 验证行为：

```go
// 测试默认路径
cli.RunWithIO([]string{"init", "--json"}, ...)

// 测试显式路径（不变）
cli.RunWithIO([]string{"init", "/custom/path", "--json"}, ...)

// 测试默认路径 + force
cli.RunWithIO([]string{"init", "--force", "--json"}, ...)
```

### Testability Guidelines

1. **Accept dependencies, don't create them**: `runInit` 已通过参数接收 `stdout`、`stderr`、`opts`，wiki 初始化通过 `wiki.NewOsFS()` 使用真实文件系统。测试使用 `t.TempDir()` 隔离。

2. **Return results, don't produce side effects**: `runInit` 通过 `stdout` 输出结果，不依赖全局状态。

3. **Small surface area**: 仅修改一处条件分支，不引入新接口。

## Data Flow

```
用户输入 args
    │
    ▼
runInit(stdout, stderr, opts, args)
    │
    ├─ remaining = initFlags.Args()
    │
    ├─ [变更] remaining 为空 → wikiRoot = "./openwiki/"
    ├─ remaining 非空 → wikiRoot = remaining[0]
    │
    ▼
wiki.Init(fs, wikiRoot, cfg)  ← 不变
    │
    ▼
输出结果到 stdout
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 文件系统 | `t.TempDir()` 临时目录隔离 |
| 标准输出/错误 | `bytes.Buffer` 捕获 |

## Implementation Notes

- 修改位置：`internal/cli/init.go#L27-L35`
- 将 `if len(remaining) == 0 { return error }` 改为 `if len(remaining) == 0 { wikiRoot = "./openwiki/" } else { wikiRoot = remaining[0] }`
- 测试修改：`TestInitMissingWikiRoot` 需要从"期望报错"改为"期望成功创建在默认路径"
- 新增 3 个测试用例覆盖默认路径场景
