# Design: add-openwiki-cli

## Overview

openwiki CLI 是一个 Go 语言实现的命令行工具，提供 wiki 实例的初始化、配置管理、状态查看、页面 CRUD、操作日志和云同步能力。设计遵循 [[agent-friendly-cli-design]] 的三条第一优先级原则（一致性 > 一切、可预测的确定行为、机器友好 > 人类可读），参考 [[flat-internal-package-organization]] 的垂直切分包结构，以及 [[go-stdlib-first-minimal-deps]] 的最小依赖原则。

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        cmd/openwiki/main.go                     │
│                    (入口 + ldflags 版本注入)                       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      internal/cli/ (命令路由层)                    │
│                                                                 │
│  root.go ──→ 全局选项解析 + 配置发现 + 子命令注册                    │
│  init.go     config.go    status.go    page.go    log.go   sync.go│
└──────┬──────────┬──────────────┬──────────┬─────────┬───────────┘
       │          │              │          │         │
       ▼          ▼              ▼          ▼         ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  config/ │ │  wiki/   │ │  wiki/   │ │  wiki/   │ │  output/ │
│          │ │  init.go │ │  page.go │ │  log.go  │ │          │
│ config.go│ │          │ │ index.go │ │          │ │ json.go  │
│discovery │ │          │ │          │ │          │ │ text.go  │
│validate  │ │          │ │          │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
     │
     ▼
┌──────────┐
│  TOML    │  (github.com/BurntSushi/toml — 唯一外部依赖)
└──────────┘
```

**依赖方向（单向无环）**：
```
cli → config + wiki + output
wiki → config
config → TOML 库
output → 无内部依赖
```

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| `internal/config/` | openwiki.toml 解析、配置发现、校验 | `Load(path)`, `Discover(explicitPath)`, `Validate(cfg)` |
| `internal/wiki/` | wiki 目录初始化、页面 CRUD、index.md 维护、log.md 维护 | `Init(root, cfg)`, `ListPages(root)`, `GetPage(root, slugs)`, `CreatePage(root, slug, page)`, `UpdatePage(root, slug, page)`, `DeletePage(root, slug)`, `ShowLog(root, limit)`, `AppendLog(root, entry)` |
| `internal/cli/` | 命令路由、参数解析、调用 wiki/config/output | 通过 `flag.FlagSet` 注册子命令 |
| `internal/output/` | JSON 和人类可读文本输出 | `JSON(success, data, err)`, `Text(format, args)` |

## Interface Design for Testability

### 1. 文件系统抽象

所有文件操作通过 `wiki.FS` 接口，支持真实文件系统和内存文件系统两种实现：

```go
// internal/wiki/fs.go

// FS 抽象文件系统操作，便于测试时替换为内存实现
type FS interface {
    ReadFile(path string) ([]byte, error)
    WriteFile(path string, data []byte, perm os.FileMode) error
    MkdirAll(path string, perm os.FileMode) error
    Remove(path string) error
    Stat(path string) (os.FileInfo, error)
    ReadDir(path string) ([]os.DirEntry, error)
    Glob(pattern string) ([]string, error)
}

// OsFS 真实文件系统实现
type OsFS struct{}

// MemFS 内存文件系统实现（用于测试）
type MemFS struct {
    mu    sync.RWMutex
    files map[string][]byte
    dirs  map[string]bool
}
```

**测试策略**：单元测试使用 `MemFS`，集成测试使用 `t.TempDir()` + `OsFS`。

### 2. 依赖注入

所有 wiki 操作函数接受依赖作为参数，不内部创建：

```go
// 可测试：接受 FS 接口
func Init(fs FS, root string, cfg *config.Config) error { ... }

// 可测试：接受 FS 接口
func ListPages(fs FS, root string) ([]PageMeta, error) { ... }

// 可测试：接受 FS 接口
func GetPage(fs FS, root string, slugs []string) ([]Page, error) { ... }
```

### 3. 配置发现可注入

```go
// internal/config/discovery.go

// Discoverer 配置发现策略接口
type Discoverer interface {
    Discover(explicitPath string) (*DiscoveryResult, error)
}

// DefaultDiscoverer 默认实现（4 级优先级链）
type DefaultDiscoverer struct {
    HomeDir string   // 可注入，测试时替换
    Getenv  func(string) string  // 可注入，测试时替换
    Getwd   func() (string, error)  // 可注入，测试时替换
}
```

### 4. 命令函数返回结果而非直接输出

```go
// internal/cli/status.go

// 可测试：返回结构化结果
func runStatus(fs wiki.FS, cfg *config.Config, verbose bool) (*StatusResult, error) {
    pages, err := wiki.ListPages(fs, cfg.WikiRoot)
    if err != nil {
        return nil, err
    }
    return &StatusResult{
        Pages:  pages,
        Config: cfg,
    }, nil
}

// CLI 入口：调用 runStatus 然后格式化输出
func statusCmd(fs wiki.FS, cfg *config.Config, args []string) error {
    result, err := runStatus(fs, cfg, isVerbose(args))
    if err != nil {
        return output.JSON(os.Stdout, false, nil, err)
    }
    if isJSON(args) {
        return output.JSON(os.Stdout, true, result, nil)
    }
    return output.Text(os.Stdout, result)
}
```

### 5. 小接口面积

每个包的公开接口保持最小：

| 包 | 公开函数/类型 | 数量 |
|----|-------------|------|
| `config` | `Config`, `Load`, `Discover`, `Validate`, `Set`, `DiscoveryResult` | 6 |
| `wiki` | `FS`, `OsFS`, `MemFS`, `Init`, `ListPages`, `GetPage`, `CreatePage`, `UpdatePage`, `DeletePage`, `ShowLog`, `AppendLog`, `PageMeta`, `Page` | 13 |
| `output` | `JSON`, `Text`, `Response`, `ErrorInfo` | 4 |
| `cli` | 各命令的 `run*` 函数 | ~10 |

## Data Flow

### init 命令流程

```
openwiki init ./my-wiki --non-interactive --json
    │
    ▼
cli/init.go: runInit(fs, root, opts)
    │
    ├──→ config.NewDefault(root, opts.Language)    创建默认配置
    │
    ├──→ wiki.Init(fs, root, cfg)                  创建目录结构
    │       ├── fs.MkdirAll("wiki/pages/")
    │       ├── fs.MkdirAll("raw/")
    │       ├── fs.MkdirAll("concepts/")
    │       ├── fs.WriteFile("wiki/index.md", template)
    │       ├── fs.WriteFile("wiki/log.md", template)
    │       └── fs.WriteFile("openwiki.toml", toml)
    │
    └──→ output.JSON(stdout, true, result, nil)    输出 JSON
```

### page create 命令流程

```
openwiki page create my-page --file /tmp/content.md --title "标题" --json
    │
    ▼
cli/page.go: runCreatePage(fs, root, slug, opts)
    │
    ├──→ wiki.GetPage(fs, root, [slug])            检查是否已存在
    │       └── 如果存在 → 返回 PAGE_ALREADY_EXISTS 错误
    │
    ├──→ fs.ReadFile(opts.File)                    读取页面内容
    │
    ├──→ wiki.CreatePage(fs, root, slug, page)     创建页面
    │       ├── fs.WriteFile("wiki/pages/my-page.md", content)
    │       ├── index.Update(fs, root, slug, page.Meta)  更新 index.md
    │       └── log.Append(fs, root, entry)              追加 log.md
    │
    └──→ output.JSON(stdout, true, result, nil)
```

### status 命令流程

```
openwiki status --json
    │
    ▼
cli/status.go: runStatus(fs, cfg, verbose)
    │
    ├──→ wiki.ListPages(fs, cfg.WikiRoot)          解析 index.md
    │       └── 返回 []PageMeta（slug/title/tags/scope/updated）
    │
    ├──→ 统计：按 scope_level 分组、孤立页面检测、过期页面检测
    │
    ├──→ wiki.ShowLog(fs, cfg.WikiRoot, 1)         获取最后操作时间
    │
    └──→ output.JSON(stdout, true, result, nil)
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 文件系统 | `wiki.MemFS`（内存实现）或 `t.TempDir()` + `wiki.OsFS` |
| 环境变量 | `config.DefaultDiscoverer.Getenv` 注入测试函数 |
| 当前工作目录 | `config.DefaultDiscoverer.Getwd` 注入测试函数 |
| HOME 目录 | `config.DefaultDiscoverer.HomeDir` 注入测试路径 |
| 云同步（pcloud） | `syncCmd` 接受 `Syncer` 接口，测试用 stub |
| TOML 解析 | 真实解析（BurntSushi/toml 是纯函数，无需 mock） |

### 测试分层

```
┌─────────────────────────────────────────────┐
│           E2E (10%)                          │
│  tests/e2e/                                 │
│  Harness 构建二进制 → 执行命令 → 断言输出       │
│  例：init → page create → status 完整流程      │
├─────────────────────────────────────────────┤
│           Integration / Stub E2E (20%)       │
│  internal/cli/*_test.go                      │
│  使用 t.TempDir() + OsFS，直接调用 run* 函数    │
│  例：runCreatePage 创建页面后验证 index.md      │
├─────────────────────────────────────────────┤
│           Unit (70%)                         │
│  internal/config/*_test.go                   │
│  internal/wiki/*_test.go                     │
│  internal/output/*_test.go                   │
│  使用 MemFS，纯函数测试                        │
│  例：config.Load 解析 TOML，wiki.ListPages 解析 │
└─────────────────────────────────────────────┘
```

## Implementation Notes

### 构建与版本注入

```makefile
# Makefile
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BUILD_TIME ?= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
LDFLAGS = -X main.Version=$(VERSION) -X main.BuildTime=$(BUILD_TIME)

build:
	go build -ldflags "$(LDFLAGS)" -o bin/openwiki ./cmd/openwiki/

test:
	go test ./internal/...

test-e2e:
	go test ./tests/e2e/...
```

### 错误码体系

```go
// internal/output/errors.go

const (
    ErrCodeInternal         = "INTERNAL"
    ErrCodeInvalidArg       = "INVALID_ARG"
    ErrCodeConfigNotFound   = "CONFIG_NOT_FOUND"
    ErrCodeConfigMissing    = "CONFIG_MISSING_FIELD"
    ErrCodeConfigInvalid    = "CONFIG_INVALID_FIELD"
    ErrCodeConfigInvalidPath = "CONFIG_INVALID_PATH"
    ErrCodeWikiNotInit      = "WIKI_NOT_INITIALIZED"
    ErrCodeWikiAlreadyExists = "WIKI_ALREADY_EXISTS"
    ErrCodePageNotFound     = "PAGE_NOT_FOUND"
    ErrCodePageAlreadyExists = "PAGE_ALREADY_EXISTS"
    ErrCodeScopeInvalid     = "SCOPE_INVALID"
    ErrCodeIOError          = "IO_ERROR"
    ErrCodePermission       = "PERMISSION"
)

// 退出码映射
var ExitCodes = map[string]int{
    ErrCodeInternal:         1,
    ErrCodeInvalidArg:       2,
    ErrCodeConfigNotFound:   3,
    ErrCodeConfigMissing:    3,
    ErrCodeConfigInvalid:    3,
    ErrCodeConfigInvalidPath: 3,
    ErrCodeWikiNotInit:      4,
    ErrCodePageNotFound:     4,
    ErrCodePermission:       5,
    ErrCodeIOError:          6,
    ErrCodeScopeInvalid:     7,
}
```

### index.md 自动维护

`page create/update/delete` 自动维护 `wiki/index.md`。index.md 结构：

```markdown
# Wiki 索引

## 资料页

| Slug | 标题 | 标签 | 适用范围 | 最后更新 |
|------|------|------|----------|----------|
| agent-friendly-cli-design | 智能体友好的CLI设计规范 | cli, agent, design | industry/cli-design | 2026-05-26 |
```

`CreatePage` 时在对应 category 表格追加一行，`UpdatePage` 时更新日期和标签，`DeletePage` 时移除对应行。

### page get 批量模式

```go
// GetPage 支持单个或多个 slug
// 返回的 Page 结构含预解析的 cross_references
type Page struct {
    Slug             string   `json:"slug"`
    Path             string   `json:"path"`
    Frontmatter      map[string]interface{} `json:"frontmatter"`
    Body             string   `json:"body"`
    CrossReferences  []string `json:"cross_references"`  // [[ref]] 解析结果
}
```

`cross_references` 通过正则 `\[\[([a-z0-9-]+)\]\]` 从 body 中提取，省去 Skill 手动解析。

### 配置发现实现

```go
// Discover 按优先级链发现配置
func (d *DefaultDiscoverer) Discover(explicitPath string) (*DiscoveryResult, error) {
    // 1. --config 显式指定
    if explicitPath != "" {
        path := expandPath(explicitPath)
        if _, err := os.Stat(path); err != nil {
            return nil, fmt.Errorf("%w: %s", ErrConfigNotFound, path)
        }
        return &DiscoveryResult{Path: path, Source: "explicit"}, nil
    }

    // 2. OPENWIKI_CONFIG 环境变量
    if envPath := d.Getenv("OPENWIKI_CONFIG"); envPath != "" {
        path := expandPath(envPath)
        if _, err := os.Stat(path); err != nil {
            return nil, fmt.Errorf("%w: OPENWIKI_CONFIG=%s", ErrConfigNotFound, envPath)
        }
        return &DiscoveryResult{Path: path, Source: "env"}, nil
    }

    // 3. ~/.openwiki/openwiki.toml
    globalPath := filepath.Join(d.HomeDir, ".openwiki", "openwiki.toml")
    if _, err := os.Stat(globalPath); err == nil {
        return &DiscoveryResult{Path: globalPath, Source: "global"}, nil
    }

    // 4. CWD 向上搜索
    cwd, err := d.Getwd()
    if err != nil {
        return nil, fmt.Errorf("getwd: %w", err)
    }
    for dir := cwd; dir != "/"; dir = filepath.Dir(dir) {
        candidate := filepath.Join(dir, "openwiki.toml")
        if _, err := os.Stat(candidate); err == nil {
            return &DiscoveryResult{Path: candidate, Source: "local"}, nil
        }
    }

    return nil, ErrConfigNotFound
}
```
