# Tasks: add-entities

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

---

## Behavior 1: `wiki-init` 创建 `entities/` 目录

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/init_test.go` 中新增测试：验证 `Init` 后 `entities/` 目录存在
  - 测试名称: `TestInitCreatesEntitiesDir`
  - 使用 `MemFS`，调用 `Init`，检查 `entities/` 目录

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/init.go` 的 `initInternal` 中，`dirs` 列表新增 `filepath.Join(root, "entities")`

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无需重构（改动极小）

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 2: `CreatePage` 支持 `--type entity` 写入 `entities/` 目录

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 中新增测试：`TestCreateEntityPage`
  - 调用 `CreatePage(fs, root, page, PageTypeEntity)`
  - 验证文件路径为 `entities/<slug>.md`

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 中：
  - 新增 `PageType` 类型和常量
  - 新增 `pageDirs` 映射
  - 修改 `CreatePage` 签名：新增可变参数 `pageType ...PageType`（向后兼容）
  - 使用 `pageDirs[pt]` 计算路径

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保 `CreatePage` 的默认调用方（CLI）传入 `PageTypePage`

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 3: `CreatePage` 支持 `--type concept` 写入 `concepts/` 目录

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 中新增测试：`TestCreateConceptPage`
  - 调用 `CreatePage(fs, root, page, PageTypeConcept)`
  - 验证文件路径为 `concepts/<slug>.md`

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 验证 Behavior 2 的实现已覆盖此行为（`pageDirs` 已包含 `PageTypeConcept`）

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无需额外重构

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 4: `GetPage` 跨目录搜索

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 中新增测试：
  - `TestGetPageFromEntitiesDir`：entity 页面存在于 `entities/`，`GetPage` 能找到
  - `TestGetPagePriorityPagesFirst`：同名 slug 在 `wiki/pages/` 和 `entities/` 都存在时，返回 pages 下的

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 中：
  - 新增 `resolvePagePath(fs, root, slug) (string, PageType, error)` 函数，按 `searchOrder` 查找
  - 修改 `GetPage`：使用 `resolvePagePath` 替代直接拼接 `wiki/pages/` 路径

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 `searchOrder` 为包级变量

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 5: `ListPages` 返回 `type` 字段

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 中新增测试：`TestListPagesWithType`
  - 创建三种类型的页面各一个
  - 调用 `ListPages`
  - 验证每个 `PageMeta` 的 `Type` 字段正确

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 中：
  - `PageMeta` 新增 `Type string` 字段
  - 修改 `parseIndexTable`：兼容新旧 index.md 格式（检测"类型"列）
  - 修复 `addToIndex` 插入位置 bug（改为在分隔线后插入）

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** `ListPages` 输出保持 index.md 中的顺序

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 6: `UpdatePage` 保持或变更页面类型

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 中新增测试：
  - `TestUpdatePagePreserveType`：不传 newType，entity 页面更新后仍在 `entities/`
  - `TestUpdatePageChangeType`：传 `PageTypeConcept`，entity 页面迁移到 `concepts/`

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 中：
  - 修改 `UpdatePage` 签名：新增可变参数 `newType ...PageType`
  - 若 `newType` 指定且与原类型不同：删除原文件，写入新目录
  - 若未指定：保持原目录

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** index.md 在类型变更时同步更新（`updateIndexRow` 已处理）

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 7: `DeletePage` 跨目录删除

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 中新增测试：`TestDeleteEntityPage`
  - 创建 entity 页面，调用 `DeletePage`，验证文件被删除且 index 更新

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 中：
  - 修改 `DeletePage`：使用 `resolvePagePath` 查找页面位置后删除

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无需额外重构

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 8: CLI `--type` flag 集成

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/page_test.go` 中新增测试：
  - `TestPageCreateWithTypeFlag`：`--type entity` 参数解析正确
  - `TestPageCreateDefaultType`：不传 `--type` 时默认 `page`
  - `TestPageCreateInvalidType`：`--type foo` 返回错误

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/page.go` 中：
  - `extractSubcommandFlags` 新增 `"type"` 到 flagNames
  - `runPageCreate`：解析 `--type`，映射到 `PageType`，传入 `CreatePage`
  - `runPageUpdate`：解析 `--type`，传入 `UpdatePage`
  - 非法 `--type` 值返回错误

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 `parsePageType(s string) (PageType, error)` 辅助函数

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 9: index.md 按类型分区

### Phase 1: RED - Write Failing Test

- [x] **1.1** 已有测试覆盖（`TestListPagesWithType` 验证了 index 中的类型列，`addToIndex` 按类型分区插入）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 中：
  - 修改 `addToIndex`：按类型选择正确的分隔线位置插入（page→第1个, entity→第2个, concept→第3个）
  - `updateIndexRow`：已支持"类型"列

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** indexTemplate 新增"实体页"分区

- [x] **3.2** 运行全部测试确认通过

---

## Behavior 10: Skill 文档更新

### Phase 1: RED - Write Failing Test

- [x] **1.1** 静态验证：
  - `wiki-ingest/SKILL.md` 步骤 7 描述了按类型写入不同目录
  - `wiki-query/SKILL.md` 步骤 2 描述了跨目录读取
  - `wiki-lint/references/rules-catalog.md` 包含 `invalid-entity-type` 规则
  - `wiki-init/SKILL.md` 描述了 `entities/` 目录创建

- [x] **1.2** 文档已更新

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新 `skill/wiki-ingest/SKILL.md` 步骤 7：entity → `entities/`，concept → `concepts/`
- [x] **2.2** 更新 `skill/wiki-query/SKILL.md` 步骤 2：使用 `openwiki page get` 跨目录读取
- [x] **2.3** 更新 `skill/wiki-lint/SKILL.md`：校验范围扩展 + 新增 `invalid-entity-type` 规则
- [x] **2.4** 更新 `skill/wiki-lint/references/rules-catalog.md`：新增 `invalid-entity-type` 规则
- [x] **2.5** 更新 `skill/wiki-init/SKILL.md`：初始化产物描述含 `entities/`
- [x] **2.6** 更新 `skill/wiki-ingest/references/page-template.md`：新增 entity 页面模板

- [x] **2.7** 文档更新完成

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无需重构

- [x] **3.2** 运行全部测试确认通过

---

## Verification

完成所有 behavior 后：

- [x] 运行完整测试套件: `go test ./...` — 全部通过
- [ ] 运行 e2e 测试: `python3 tests/test_agent_skill_smoke_e2e.py`
- [x] 所有 Go 测试通过
- [x] 实现与 acceptance criteria 一致
- [x] 向后兼容：现有 `wiki/pages/` 下页面行为不变
