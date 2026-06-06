# Proposal: add-backlinks-and-query-writeback

## Why

当前 OpenWiki 的知识网络是单向的——页面通过 `[[slug]]` 声明"我引用了谁"，但被引用的页面不知道"谁引用了我"。这违背了 Zettelkasten 和现代 PKM 工具（Obsidian、Logseq）的核心实践：双向链接让知识网络可见，帮助发现隐藏关联。

同时，wiki-query 的回答产出没有被系统化地沉淀回知识库。ByteTech 上字节内部同学的实践表明，查询本身是知识生产的重要环节——当一次回答综合了多个页面、建立了新关联或发现了矛盾，这些洞察应该被持久化。

## What Changes

1. **反向链接（Backlinks）**：`Page` 结构体新增 `Backlinks` 字段，`GetPageWithBacklinks()` 和 `ComputeBacklinks()` 函数动态计算哪些页面引用了当前页面。CLI 通过 `--backlinks` 标志启用。

2. **Query 回写机制**：`wiki-query/SKILL.md` 的 Step 5 从简单的 "Worth saving?" 升级为结构化的回写判断（多源综合 / 新关联 / 矛盾发现 / 知识空白），回写页面存入 `wiki/pages/` 并包含 `query_date`、`query_sources`、`external_refs` 等元数据。

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `openwiki page get <slug> --backlinks --json` 返回包含 `backlinks` 数组的 JSON | e2e 测试：创建两个互相引用的页面，验证 backlinks 正确 |
| 2 | 不带 `--backlinks` 时 `GetPage` 行为不变 | 现有测试全部通过 |
| 3 | `ComputeBacklinks` 正确排除自身引用 | 单元测试：页面引用自身不计入 backlinks |
| 4 | wiki-query SKILL.md 包含结构化的回写判断条件 | 文档审查：Step 5 包含 4 个判断条件表格 |
| 5 | 回写页面模板包含 `query_date`、`query_sources`、`external_refs` 字段 | 文档审查：模板包含这些 frontmatter 字段 |

## Impact

- **`internal/wiki/page.go`**：`Page` 结构体 + `GetPageWithBacklinks` + `ComputeBacklinks`
- **`internal/cli/page.go`**：`runPageGet` 支持 `--backlinks` 标志
- **`skill/wiki-query/SKILL.md`**：Step 5 重写，Step 2 新增 `--backlinks` 用法

## Non-Goals

- 不实现反向链接的索引缓存（懒计算方案起步）
- 不回写后自动修改源页面的"相关主题"
- 不改变 `GetPage` 的默认行为（向后兼容）

## Test Considerations

- 测试框架：Go 标准 `testing` + e2e harness
- 关键接口：`wiki.GetPageWithBacklinks()`、`wiki.ComputeBacklinks()`、CLI `page get --backlinks`
- Mock：使用 `MemFS` 进行单元测试
