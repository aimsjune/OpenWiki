# Specification: entity-pages

## Purpose

定义 entity 页面（实体页面）的完整行为规范。涵盖 entity 页面的目录结构、frontmatter 字段（含 `entity_type`）、CLI 的 `--type` 参数、index.md 的多类型分区展示、以及各 wiki skill 对 entity 页面的读写和校验行为。

## Requirements

### REQ-1: `wiki-init` 初始化时创建 `entities/` 目录

**Behavior**: `wiki-init` 在初始化 wiki 数据布局时，必须在 `wiki_root` 下创建 `entities/` 目录，与已有的 `wiki/pages/`、`concepts/` 并列。

**Test Verification**: 运行 `wiki-init` 初始化新 wiki，检查 `wiki_root/entities/` 目录存在。

```
Given: 一个空的 wiki_root 目录
When:  执行 wiki-init 初始化
Then:  wiki_root/entities/ 目录被创建
```

**Interfaces to Test Through**: `wiki-init` skill 入口、`internal/wiki/init.go` 的 `InitWiki` 函数

---

### REQ-2: Entity 页面 frontmatter 包含 `entity_type` 字段

**Behavior**: 存放在 `entities/` 目录下的页面，其 frontmatter 必须包含 `entity_type` 字段，值为以下枚举之一：`person`、`org`、`project`、`tool`。

**Test Verification**: 创建 entity 页面后，读取 frontmatter，验证 `entity_type` 字段存在且为合法枚举值。

```
Given: 一个 entity 页面，entity_type: "person"
When:  读取页面 frontmatter
Then:  entity_type 字段值为 "person"
```

```
Given: 一个 entity 页面，entity_type: "invalid_type"
When:  wiki-lint 校验该页面
Then:  输出 Yellow Warning: invalid-entity-type
```

**Interfaces to Test Through**: `openwiki page get --json` 输出、`skill/wiki-ingest/references/page-template.md` 静态分析

---

### REQ-3: `openwiki page create --type` 支持三种页面类型

**Behavior**: `openwiki page create` 新增 `--type` flag，接受 `page`（默认）、`entity`、`concept` 三种值。不同 type 将页面写入不同目录：

| --type | 写入目录 |
|--------|----------|
| `page`（默认） | `wiki/pages/` |
| `entity` | `entities/` |
| `concept` | `concepts/` |

**Test Verification**: 分别用三种 `--type` 创建页面，检查文件路径。

```
Given: 一个已初始化的 wiki
When:  执行 openwiki page create andrej-karpathy --type entity --file content.md
Then:  文件写入 entities/andrej-karpathy.md
```

```
Given: 一个已初始化的 wiki
When:  执行 openwiki page create transformer-architecture --type concept --file content.md
Then:  文件写入 concepts/transformer-architecture.md
```

```
Given: 一个已初始化的 wiki
When:  执行 openwiki page create some-article --file content.md（不指定 --type）
Then:  文件写入 wiki/pages/some-article.md（默认行为不变）
```

**Interfaces to Test Through**: `internal/cli/page.go` 的 `runPageCreate` 函数、`internal/wiki/page.go` 的 `CreatePage`

---

### REQ-4: `openwiki page get` 跨目录搜索页面

**Behavior**: `openwiki page get <slug>` 按以下顺序搜索页面：`wiki/pages/` → `entities/` → `concepts/`。找到第一个匹配即返回。若三个目录均不存在该 slug，返回"页面不存在"错误。

**Test Verification**: 在不同目录下创建同名 slug 的页面，验证搜索优先级。

```
Given: entities/foo.md 和 wiki/pages/foo.md 同时存在
When:  执行 openwiki page get foo
Then:  返回 wiki/pages/foo.md（pages 优先）
```

```
Given: entities/bar.md 存在，wiki/pages/bar.md 和 concepts/bar.md 不存在
When:  执行 openwiki page get bar
Then:  返回 entities/bar.md
```

```
Given: 三个目录均不存在 baz.md
When:  执行 openwiki page get baz
Then:  返回错误 "页面不存在: baz"
```

**Interfaces to Test Through**: `internal/cli/page.go` 的 `runPageGet`、`internal/wiki/page.go` 的 `GetPage`

---

### REQ-5: `openwiki page list` 输出包含 `type` 字段

**Behavior**: `openwiki page list --json` 输出的每个页面条目包含 `type` 字段，值为 `page`、`entity` 或 `concept`。

**Test Verification**: 创建三种类型的页面后，调用 `page list --json`，验证 type 字段。

```
Given: wiki 中存在 wiki/pages/a.md、entities/b.md、concepts/c.md
When:  执行 openwiki page list --json
Then:  输出包含 type 字段，a 为 "page"，b 为 "entity"，c 为 "concept"
```

**Interfaces to Test Through**: `internal/cli/page.go` 的 `runPageList`、`internal/wiki/page.go` 的 `ListPages`

---

### REQ-6: `openwiki page update` 保持页面类型不变

**Behavior**: 更新页面时，`--type` 参数可选。若指定 `--type`，页面可能移动到新目录；若不指定，页面保持在原目录。

**Test Verification**: 更新 entity 页面时不指定 `--type`，验证页面仍在 `entities/` 目录。

```
Given: entities/foo.md 已存在
When:  执行 openwiki page update foo --file new-content.md（不指定 --type）
Then:  页面仍在 entities/foo.md
```

```
Given: entities/foo.md 已存在
When:  执行 openwiki page update foo --type concept --file new-content.md
Then:  entities/foo.md 被删除，concepts/foo.md 被创建
```

**Interfaces to Test Through**: `internal/cli/page.go` 的 `runPageUpdate`、`internal/wiki/page.go` 的 `UpdatePage`

---

### REQ-7: `openwiki page delete` 跨目录删除

**Behavior**: `openwiki page delete <slug>` 按 `wiki/pages/` → `entities/` → `concepts/` 顺序搜索并删除页面。同时从 index.md 中移除对应条目。

**Test Verification**: 删除 entity 页面，验证文件被移除且 index.md 更新。

```
Given: entities/foo.md 存在且 index.md 中有对应条目
When:  执行 openwiki page delete foo
Then:  entities/foo.md 被删除，index.md 中 foo 条目被移除
```

**Interfaces to Test Through**: `internal/cli/page.go` 的 `runPageDelete`、`internal/wiki/page.go` 的 `DeletePage`

---

### REQ-8: index.md 按页面类型分区展示

**Behavior**: `wiki/index.md` 的 Wiki 页面表格新增 `类型` 列，展示 `page`、`entity` 或 `concept`。表格格式：

```markdown
| Slug | 标题 | 类型 | 标签 | 适用范围 | 最后更新 |
|------|------|------|------|----------|----------|
```

**Test Verification**: 创建三种类型的页面后，检查 index.md 表格结构。

```
Given: wiki 中存在三种类型的页面
When:  读取 wiki/index.md
Then:  表格包含 "类型" 列，每行正确标注 page/entity/concept
```

**Interfaces to Test Through**: `internal/wiki/page.go` 的 `addToIndex`、`updateIndexRow`

---

### REQ-9: wiki-ingest 步骤 7 按类型写入对应目录

**Behavior**: wiki-ingest 在步骤 7（Update related entity or concept pages）中，entity 页面写入 `entities/` 目录，concept 页面写入 `concepts/` 目录。SKILL.md 中需明确描述此行为。

**Test Verification**: 静态读取 `skill/wiki-ingest/SKILL.md` 步骤 7，验证描述了按类型写入不同目录。

```
Given: skill/wiki-ingest/SKILL.md 步骤 7
When:  读取步骤描述
Then:  明确说明 entity 页面写入 entities/，concept 页面写入 concepts/
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-10: wiki-query 查询时跨目录发现页面

**Behavior**: wiki-query 在步骤 1（Read index.md）和步骤 2（Read relevant pages）中，能够发现并读取 `entities/` 和 `concepts/` 目录下的页面。SKILL.md 中需明确描述跨目录搜索行为。

**Test Verification**: 静态读取 `skill/wiki-query/SKILL.md`，验证步骤 2 描述了跨目录读取。

```
Given: skill/wiki-query/SKILL.md 步骤 2
When:  读取步骤描述
Then:  明确说明使用 openwiki page get 读取页面（该命令已支持跨目录搜索）
```

**Interfaces to Test Through**: `skill/wiki-query/SKILL.md` 静态分析

---

### REQ-11: wiki-lint 校验覆盖 `entities/` 和 `concepts/` 目录

**Behavior**: wiki-lint 的校验范围从仅 `wiki/pages/` 扩展为 `wiki/pages/` + `entities/` + `concepts/`。新增 `invalid-entity-type` 规则：检查 entity 页面的 `entity_type` 是否为合法枚举值。

**Test Verification**: 静态读取 `skill/wiki-lint/references/rules-catalog.md`，验证包含 `invalid-entity-type` 规则。

```
Given: skill/wiki-lint/references/rules-catalog.md
When:  读取规则目录
Then:  包含 invalid-entity-type 规则，检查 entity_type 枚举值
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 和 `skill/wiki-lint/references/rules-catalog.md` 静态分析

---

### REQ-12: 向后兼容——现有页面不受影响

**Behavior**: 所有现有 `wiki/pages/` 下的页面读写行为不变。不指定 `--type` 时默认行为与之前完全一致。旧格式 index.md（无"类型"列）在首次添加 entity/concept 页面时自动升级。

**Test Verification**: 在已有 wiki 上执行 page create（不指定 --type），验证行为不变。

```
Given: 一个已有 wiki/pages/ 下页面的 wiki
When:  执行 openwiki page create new-page --file content.md（不指定 --type）
Then:  页面写入 wiki/pages/new-page.md，行为与之前一致
```

**Interfaces to Test Through**: `internal/wiki/page.go` 的 `CreatePage`、`GetPage`、`ListPages`

---

## Test Structure

### Integration Tests

```go
func TestCreateEntityPage(t *testing.T) {
    // Given: 一个已初始化的 wiki
    fs := newMemFS()
    root := initWiki(t, fs)

    // When: 创建 entity 页面
    page := &Page{
        Slug: "andrej-karpathy",
        Frontmatter: map[string]interface{}{
            "title":       "Andrej Karpathy",
            "entity_type": "person",
            "tags":        []string{"entity", "person"},
            "updated":     "2026-06-06",
        },
        Body: "# Andrej Karpathy\n\n核心身份...",
    }
    err := CreatePage(fs, root, page, PageTypeEntity)

    // Then
    assert.NoError(t, err)
    assert.FileExists(t, filepath.Join(root, "entities", "andrej-karpathy.md"))
}

func TestGetPageCrossDirectory(t *testing.T) {
    // Given: entity 页面存在于 entities/ 目录
    // When:  GetPage 搜索该 slug
    // Then:  返回 entity 页面，type 为 "entity"
}

func TestListPagesWithType(t *testing.T) {
    // Given: 三种类型的页面各一个
    // When:  ListPages
    // Then:  每个页面包含正确的 type 字段
}

func TestPageCreateDefaultType(t *testing.T) {
    // Given: 不指定 --type
    // When:  CreatePage
    // Then:  写入 wiki/pages/，行为与之前一致
}
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `internal/wiki/page_entity_test.go` | 测试 entity 页面的创建、读取、更新、删除 |
| `internal/cli/page_entity_test.go` | 测试 CLI --type 参数的解析和行为 |
| `tests/test_entity_pages_e2e.py` | e2e 测试：wiki-init → page create --type entity → page get → page list 完整链路 |

## Edge Cases

- 同名 slug 存在于多个目录：`wiki/pages/` 优先于 `entities/`，`entities/` 优先于 `concepts/`
- `--type` 传入非法值（如 `--type foo`）：返回错误，提示合法值为 page/entity/concept
- 更新页面时 `--type` 改变导致目录迁移：原目录文件删除，新目录文件创建，index.md 同步更新
- `entities/` 或 `concepts/` 目录不存在时创建页面：自动创建目录
- 旧格式 index.md（无"类型"列）首次添加 entity 页面时：自动添加"类型"列，已有页面默认标注为 "page"
- entity 页面缺少 `entity_type` 字段：wiki-lint 输出 Yellow Warning
- entity 页面的 `entity_type` 为非法值：wiki-lint 输出 Yellow Warning: invalid-entity-type
