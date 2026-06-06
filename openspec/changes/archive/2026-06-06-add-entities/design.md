# Design: add-entities

## Overview

在现有单目录（`wiki/pages/`）页面体系基础上，新增 `entities/` 和 `concepts/` 两个页面目录，形成三目录体系。核心改动集中在 `internal/wiki/page.go`（多目录读写）和 `internal/cli/page.go`（`--type` 参数），其他模块做最小化适配。

## Architecture

### 当前 vs 目标

```
当前                                    目标
──────                                  ──────
wiki/                                   wiki/
├── pages/          ← 唯一页面目录      ├── pages/       ← 源材料摘要（默认）
│   └── *.md                            │   └── *.md
├── index.md                            ├── entities/    ← 实体页面（新增）
├── log.md                              │   └── *.md
└── ...                                 ├── concepts/    ← 概念页面（启用）
                                        │   └── *.md
                                        ├── index.md
                                        ├── log.md
                                        └── ...
```

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| `internal/wiki/page.go` | 多目录页面 CRUD，类型感知的 index 更新 | `CreatePage`, `GetPage`, `ListPages`, `UpdatePage`, `DeletePage` |
| `internal/wiki/init.go` | 初始化时创建 `entities/` 目录 | `Init`, `InitForce` |
| `internal/cli/page.go` | 解析 `--type` flag，传递给 wiki 层 | `runPageCreate`, `runPageGet`, `runPageList`, `runPageUpdate`, `runPageDelete` |
| `skill/wiki-ingest/SKILL.md` | 步骤 7 按类型写入对应目录 | Skill 文档（静态） |
| `skill/wiki-query/SKILL.md` | 查询时跨目录发现页面 | Skill 文档（静态） |
| `skill/wiki-lint/SKILL.md` | 校验覆盖三个目录 | Skill 文档（静态） |

## Interface Design for Testability

### 新增类型定义

```go
// PageType 页面类型
type PageType string

const (
    PageTypePage    PageType = "page"    // 默认，wiki/pages/
    PageTypeEntity  PageType = "entity"  // entities/
    PageTypeConcept PageType = "concept" // concepts/
)

// pageDirs 定义每种类型的存储目录
var pageDirs = map[PageType]string{
    PageTypePage:    "wiki/pages",
    PageTypeEntity:  "entities",
    PageTypeConcept: "concepts",
}

// searchOrder 定义跨目录搜索的优先级
var searchOrder = []PageType{PageTypePage, PageTypeEntity, PageTypeConcept}
```

### 公共接口变更

```go
// 现有接口签名变更

// CreatePage 新增 pageType 参数
func CreatePage(fs FS, root string, page *Page, pageType PageType) error

// GetPage 跨目录搜索（内部使用 searchOrder）
func GetPage(fs FS, root, slug string) (*Page, error)  // 签名不变，行为扩展

// ListPages 返回的 PageMeta 新增 Type 字段
type PageMeta struct {
    Slug       string   `json:"slug"`
    Title      string   `json:"title"`
    Type       string   `json:"type"`        // 新增
    Tags       []string `json:"tags"`
    ScopeLevel string   `json:"scope_level"`
    ScopeCode  string   `json:"scope_code"`
    Updated    string   `json:"updated"`
}

// UpdatePage 新增 pageType 参数（可选，nil 表示保持原类型）
func UpdatePage(fs FS, root string, page *Page, newType *PageType) error

// DeletePage 跨目录搜索删除（签名不变，行为扩展）
func DeletePage(fs FS, root, slug string) error

// 新增辅助函数
func resolvePagePath(root, slug string) (string, PageType, error)  // 按 searchOrder 查找
func pageDir(root string, pt PageType) string                       // 获取类型对应的目录路径
```

### Testability Guidelines

1. **Accept dependencies, don't create them** — 所有函数接受 `FS` 接口参数，测试中使用 `MemFS`
2. **Return results, don't produce side effects** — `resolvePagePath` 返回路径和类型，不修改状态
3. **Small surface area** — 仅新增一个 `PageType` 类型和 `resolvePagePath` 辅助函数，核心 CRUD 签名做最小变更

## Data Flow

```
CLI (--type flag)
  │
  │  runPageCreate(args, --type=entity)
  │
  ▼
internal/wiki/page.go
  │
  │  CreatePage(fs, root, page, PageTypeEntity)
  │
  ├──▶ resolvePagePath() → entities/andrej-karpathy.md
  │
  ├──▶ fs.WriteFile(entities/andrej-karpathy.md)
  │
  └──▶ addToIndex(fs, root, page, PageTypeEntity)
       │
       └──▶ index.md 表格新增 "类型" 列，写入 "entity"
```

### GetPage 跨目录搜索流程

```
GetPage(fs, root, "andrej-karpathy")
  │
  ▼
resolvePagePath(root, "andrej-karpathy")
  │
  ├──▶ 尝试 wiki/pages/andrej-karpathy.md  → 不存在
  ├──▶ 尝试 entities/andrej-karpathy.md    → 找到！
  └──▶ 返回 (path, PageTypeEntity, nil)
  │
  ▼
parsePage(slug, path, content)  → Page{Type: "entity", ...}
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 文件系统 | `internal/wiki/fs.go` 的 `MemFS`（已有） |
| 配置文件 | `internal/config/config.go` 的测试 fixture |

## Implementation Notes

### 改动范围

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `internal/wiki/page.go` | 修改 | 核心改动：多目录 CRUD + 类型感知 index |
| `internal/wiki/page_test.go` | 修改 | 新增 entity/concept 测试用例 |
| `internal/wiki/init.go` | 修改 | `dirs` 列表新增 `entities/` |
| `internal/wiki/init_test.go` | 修改 | 验证 `entities/` 目录创建 |
| `internal/cli/page.go` | 修改 | `--type` flag 解析和传递 |
| `internal/cli/page_test.go` | 修改 | 新增 `--type` 参数测试 |
| `skill/wiki-ingest/SKILL.md` | 修改 | 步骤 7 描述按类型写入 |
| `skill/wiki-query/SKILL.md` | 修改 | 步骤 2 描述跨目录读取 |
| `skill/wiki-lint/SKILL.md` | 修改 | 校验范围扩展 + `invalid-entity-type` 规则 |
| `skill/wiki-lint/references/rules-catalog.md` | 修改 | 新增 `invalid-entity-type` 规则 |
| `skill/wiki-init/SKILL.md` | 修改 | 初始化产物描述含 `entities/` |

### 向后兼容策略

1. `CreatePage` 新增 `pageType` 参数，调用方需更新。CLI 默认 `--type page` 保持行为不变。
2. `GetPage` 签名不变，内部搜索顺序 `wiki/pages/` 优先，已有行为完全兼容。
3. `ListPages` 输出的 `PageMeta` 新增 `Type` 字段，JSON 消费者需适配新增字段（向后兼容，非破坏性）。
4. `DeletePage` 签名不变，跨目录搜索删除。
5. 旧格式 index.md（无"类型"列）在首次写入 entity/concept 页面时自动升级。

### 风险点

- `GetPage` 搜索顺序：`wiki/pages/` 优先。如果未来有同名 slug 跨目录，当前行为是返回 pages 下的。这是预期行为，spec 中已明确。
- `UpdatePage` 的 `newType` 参数：`nil` 表示保持原类型。CLI 中不传 `--type` 时传 `nil`。
