# Proposal: add-entities

## Why

当前 OpenWiki 的页面体系只有一种通用模板，所有页面扁平存放在 `wiki/pages/` 下。与 Karpathy LLM Wiki 的五类页面体系对比，OpenWiki 缺少 **实体页面（entity pages）**——专门描述人物、组织、项目、工具等"实体"的知识卡片。

这导致以下问题：
- 知识图谱扁平化：无法区分"一篇论文摘要"和"关于某个人的知识卡片"
- 实体关系不显式：虽然已有 `[[slug]]` 交叉引用，但没有类型维度来区分引用的是实体还是概念
- wiki-ingest 的步骤 7-8 已经隐含了 entity/concept 的概念，但缺少目录结构来承载

## What Changes

1. **新增 `entities/` 目录**：在 wiki 数据布局中新增 `entities/` 目录，存放实体页面
2. **新增 entity 页面模板**：定义 entity 页面的 frontmatter 字段（含 `entity_type`）和正文结构
3. **启用 `concepts/` 目录**：将已有的 `concepts/` 目录正式纳入页面体系
4. **更新 wiki-ingest 流程**：步骤 7 中创建/更新的 entity 页面写入 `entities/` 目录，concept 页面写入 `concepts/` 目录
5. **更新 wiki-query 流程**：查询时能够发现并读取 `entities/` 和 `concepts/` 目录下的页面
6. **更新 wiki-lint 流程**：校验覆盖 `entities/` 和 `concepts/` 目录
7. **更新 index.md 结构**：在索引中区分 entities 和 concepts 条目

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `wiki-init` 初始化时创建 `entities/` 目录 | 检查 `wiki_root/entities/` 目录存在 |
| 2 | Entity 页面包含 `entity_type` frontmatter 字段（person/org/project/tool） | 读取 entity 页面，验证 frontmatter 含 `entity_type` |
| 3 | `openwiki page create` 支持 `--type entity` 将页面写入 `entities/` 目录 | 创建 entity 页面后，检查文件路径为 `entities/<slug>.md` |
| 4 | `openwiki page create` 支持 `--type concept` 将页面写入 `concepts/` 目录 | 创建 concept 页面后，检查文件路径为 `concepts/<slug>.md` |
| 5 | `openwiki page get` 能从 `entities/` 和 `concepts/` 目录读取页面 | 读取 entity 和 concept 页面，返回正确内容 |
| 6 | `openwiki page list` 返回的页面列表包含 `type` 字段（page/entity/concept） | 列表输出中 entity 页面 type 为 "entity"，concept 页面 type 为 "concept" |
| 7 | wiki-ingest 步骤 7 将 entity 页面写入 `entities/` 目录 | 摄入源材料后，检查生成的 entity 页面路径 |
| 8 | wiki-query 查询时能发现 `entities/` 和 `concepts/` 目录下的页面 | 查询涉及实体时，返回 entity 页面内容 |
| 9 | wiki-lint 校验覆盖 `entities/` 和 `concepts/` 目录 | lint 检查能发现 entity 页面中的断链等问题 |
| 10 | index.md 按页面类型分区展示 | index.md 包含 entities 和 concepts 分区 |
| 11 | 向后兼容：现有 `wiki/pages/` 下的页面不受影响 | 已有页面的读写行为不变 |

## Impact

- **CLI**: `openwiki page create` 新增 `--type` 参数；`openwiki page get` 搜索路径扩展；`openwiki page list` 输出新增 `type` 字段
- **内部包**: `internal/wiki/page.go` 需支持多目录读写；`internal/wiki/fs.go` 需支持 `entities/` 和 `concepts/` 路径
- **Skill**: `wiki-ingest`、`wiki-query`、`wiki-lint`、`wiki-init` 的 SKILL.md 和流程需更新
- **数据布局**: `wiki_root` 下新增 `entities/` 目录

## Non-Goals

- 不新增 `summaries/`、`synthesis/`、`queries/` 目录（Karpathy 的其他三类页面暂不引入）
- 不修改现有 `wiki/pages/` 下页面的 frontmatter 格式
- 不强制要求所有 entity/concept 页面必须通过 `--type` 创建（默认 `--type page` 行为不变）

## Test Considerations

- 测试框架：Go 标准 `testing` 包 + 现有 e2e 测试框架
- 关键接口：`internal/wiki/page.go` 的 `CreatePage`、`GetPage`、`ListPages`、`DeletePage`
- 需要 mock 的文件系统：`internal/wiki/fs.go` 的 FS 接口
- e2e 测试：验证 `wiki-init` → `page create --type entity` → `page get` → `page list` 完整链路
