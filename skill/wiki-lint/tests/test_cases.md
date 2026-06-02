# wiki-lint 测试用例

## 用例 1: 健康 wiki 全通过

- **Fixture**: `fixtures/healthy-wiki/`
- **输入**: 一个包含有效页面、完整 frontmatter、无断链的 wiki
- **预期输出**: 零 Red Error，零 Yellow Warning
- **验证点**: 所有检查通过

## 用例 2: 断链检测

- **Fixture**: `fixtures/broken-links/`
- **输入**: 一个包含指向不存在页面的 [[交叉引用]] 的 wiki
- **预期输出**: 至少 1 个 Red Error（broken-links）
- **验证点**: `[[non-existent-page]]` 被检测为断链

## 用例 3: 缺少 scope 字段

- **Fixture**: `fixtures/missing-scope/`
- **输入**: 一个页面缺少 `scope_level` 和 `scope_code` 字段的 wiki
- **预期输出**: 至少 1 个 Yellow Warning（missing-scope-fields）
- **验证点**: 缺少 scope 字段的页面被检测到
