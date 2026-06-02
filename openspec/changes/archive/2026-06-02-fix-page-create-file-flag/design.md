# Design: fix-page-create-file-flag

## Overview

修复 `runPageCreate` 和 `runPageUpdate` 中 `flag.FlagSet.Parse()` 的参数解析问题。核心改动：用预扫描替代 `flag.Parse()`，先提取 `--file` flag 值，再将剩余参数作为位置参数处理。

## Architecture

### 当前问题

```
args: ["test-slug", "--file", "/tmp/content.md"]
         │
         ▼
    flag.Parse(args)
         │
         ├── 遇到 "test-slug"（非 flag）→ 立即停止
         ├── "--file" 从未被处理
         └── *filePath = ""  ← BUG
```

### 修复后

```
args: ["test-slug", "--file", "/tmp/content.md"]
         │
         ▼
    extractSubcommandFlags(args, "file")
         │
         ├── 扫描 "--file" → filePath = "/tmp/content.md"
         ├── 扫描 "test-slug" → positional = ["test-slug"]
         └── slug = positional[0]
```

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| `extractSubcommandFlags` | 从参数列表中提取已知 flag 及其值，返回 flag 值和剩余位置参数 | `func extractSubcommandFlags(args []string, flagNames ...string) (map[string]string, []string)` |
| `runPageCreate` | 处理 `page create` 命令 | `func runPageCreate(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error` |
| `runPageUpdate` | 处理 `page update` 命令 | `func runPageUpdate(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error` |

## Interface Design for Testability

### 提取辅助函数

```go
// extractSubcommandFlags 从参数列表中提取指定 flag 及其值。
// 返回 flag 名到值的映射，以及剩余的位置参数。
// 例如: args=["test-slug", "--file", "/tmp/a.md"], flagNames=["file"]
//       返回: flags={"file": "/tmp/a.md"}, positional=["test-slug"]
func extractSubcommandFlags(args []string, flagNames ...string) (flags map[string]string, positional []string) {
    flags = make(map[string]string)
    for i := 0; i < len(args); i++ {
        arg := args[i]
        matched := false
        for _, name := range flagNames {
            if arg == "--"+name || arg == "-"+name {
                if i+1 < len(args) {
                    flags[name] = args[i+1]
                    i++
                }
                matched = true
                break
            }
        }
        if !matched {
            positional = append(positional, arg)
        }
    }
    return
}
```

### runPageCreate 改造

```go
func runPageCreate(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
    flags, positional := extractSubcommandFlags(args, "file")
    filePath := flags["file"]

    if len(positional) == 0 {
        return fmt.Errorf("page create 需要指定 slug")
    }
    slug := positional[0]

    // ... 后续逻辑不变（config 发现、文件读取、页面创建）
}
```

### Testability Guidelines

1. **接受依赖，不创建依赖**：`extractSubcommandFlags` 是纯函数，无外部依赖，易于单元测试
2. **返回结果，不产生副作用**：返回 `(flags, positional)` 而非修改外部状态
3. **小接口面积**：`extractSubcommandFlags` 只有 2 个参数，1 个返回值对

## Data Flow

```
用户输入
  │
  ▼
openwiki page create test-slug --file /tmp/content.md --json
  │
  ▼
RunWithIO() → scanGlobalFlags() 提取 --json
  │
  ▼
runPageCreate(args=["test-slug", "--file", "/tmp/content.md"])
  │
  ├── extractSubcommandFlags(args, "file")
  │     ├── flags = {"file": "/tmp/content.md"}
  │     └── positional = ["test-slug"]
  │
  ├── slug = "test-slug"
  ├── content = fs.ReadFile("/tmp/content.md")  ← 现在能正确读取
  ├── page = ParsePageContent(slug, content)
  ├── CreatePage(fs, root, page)
  │     ├── 写入 wiki/pages/test-slug.md
  │     ├── 更新 wiki/index.md
  │     └── (log.md 由调用方处理)
  │
  └── JSON 输出 {"success": true, "data": {"slug": "test-slug", "status": "created"}}
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 文件系统 | `t.TempDir()` 隔离，通过 `wiki.NewOsFS()` 操作 |
| 配置文件 | 在 TempDir 中创建 `openwiki.toml` |
| 页面内容文件 | 在 TempDir 中创建测试用 `.md` 文件 |

## Implementation Notes

- `extractSubcommandFlags` 放在 `internal/cli/page.go` 中，与 `runPageCreate`/`runPageUpdate` 同文件
- 移除对 `flag.FlagSet` 的依赖（`runPageCreate` 和 `runPageUpdate` 不再使用 `flag.NewFlagSet`）
- `--file` 和 `-file` 两种写法都支持
- 如果 `--file` 后无值（如 `page create test-slug --file`），`filePath` 为空字符串，行为与不传 `--file` 一致
- 不引入 `flag` 包以外的依赖，保持零外部依赖
