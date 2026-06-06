# Design: add-backlinks-and-query-writeback

## Overview

两个独立特性：反向链接是 Go 代码改动（`internal/wiki/page.go` + `internal/cli/page.go`），Query 回写是 SKILL.md 文档改动（`skill/wiki-query/SKILL.md`）。两者通过 `--backlinks` CLI 标志在 query 流程中产生交集。

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| `Page` 结构体 | 页面数据模型，新增 `Backlinks` 字段 | `json:"backlinks"` |
| `ComputeBacklinks` | 扫描所有页面，计算反向链接 | `func ComputeBacklinks(fs FS, root, targetSlug string) ([]string, error)` |
| `GetPageWithBacklinks` | 读取页面 + 计算反向链接 | `func GetPageWithBacklinks(fs FS, root, slug string) (*Page, error)` |
| `runPageGet` (CLI) | 支持 `--backlinks` 标志 | `openwiki page get <slug> --backlinks --json` |
| wiki-query SKILL.md | Agent 查询 + 回写流程 | SKILL.md 文档 |

### 数据流

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CLI/Agent   │────▶│ GetPageWithLinks │────▶│    GetPage()    │
│ --backlinks  │     │                  │     │  (读取单页面)    │
└─────────────┘     │       │          │     └─────────────────┘
                    │       ▼          │
                    │ ComputeBacklinks │     ┌─────────────────┐
                    │ (扫描所有页面)    │────▶│ wiki/pages/*.md │
                    └──────────────────┘     └─────────────────┘
```

## Interface Design for Testability

### Public Interfaces

```go
// 核心接口：通过 FS 抽象注入依赖
func ComputeBacklinks(fs FS, root, targetSlug string) ([]string, error)

// 组合接口：读取 + 反向链接
func GetPageWithBacklinks(fs FS, root, slug string) (*Page, error)

// Page 结构体：JSON 序列化
type Page struct {
    // ... existing fields ...
    Backlinks []string `json:"backlinks"`
}
```

### Testability Guidelines

1. **Accept dependencies, don't create them**
   ```go
   // Testable: FS 通过参数注入
   func ComputeBacklinks(fs FS, root, targetSlug string) ([]string, error)
   
   // 测试时使用 MemFS，生产时使用 OsFS
   ```

2. **Return results, don't produce side effects**
   ```go
   // ComputeBacklinks 纯函数：读 FS → 返回结果，无副作用
   // GetPageWithBacklinks 在 Page 对象上设置 Backlinks 字段后返回
   ```

3. **Small surface area**
   - 仅 2 个新公开函数 + 1 个新字段
   - `GetPage` 默认行为不变（向后兼容）

## Data Flow

### 反向链接计算流程

```
1. CLI 解析 --backlinks 标志
2. 调用 GetPageWithBacklinks(fs, root, slug)
3.   ├── GetPage(fs, root, slug) → 读取单页面
4.   └── ComputeBacklinks(fs, root, slug)
5.         ├── fs.ReadDir("wiki/pages/") → 获取所有 .md 文件
6.         ├── 对每个文件：fs.ReadFile → 正则匹配 [[slug]]
7.         ├── 排除自身引用
8.         └── 返回 backlinks []string
9. 返回 Page{..., Backlinks: [...]}
```

### Query 回写流程

```
1. Agent 完成回答
2. 评估回写条件（多源综合/新关联/矛盾发现/知识空白）
3. 若满足 → 向用户提议保存
4. 用户确认 → 创建 wiki/pages/<slug>.md（含 query_date 等元数据）
5. 更新 wiki/index.md
6. 追加 wiki/log.md
7. 不修改源页面（反向链接自动展示引用关系）
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| File System | `MemFS`（内存文件系统，已在 `internal/wiki/fs.go` 中定义） |
| CLI 输出 | `bytes.Buffer` 捕获 stdout/stderr |
| 外部搜索（query 流程） | 不涉及（SKILL.md 文档改动） |

## Implementation Notes

- `ComputeBacklinks` 的 `re` 正则与 `parsePage` 中的保持一致：`\[\[([a-zA-Z0-9_-]+)\]\]`
- `--backlinks` 标志通过 `extractSubcommandFlags` 解析，与其他子命令标志（如 `--file`）一致
- 回写页面模板中的 `<today>` 占位符在执行时替换为实际日期
- 反向链接计算失败时降级返回空数组，不阻塞页面读取
