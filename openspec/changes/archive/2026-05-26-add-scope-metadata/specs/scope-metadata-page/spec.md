# Specification: scope-metadata-page

## Purpose

定义 wiki 页面"适用范围"元数据的完整行为规范。涵盖 page frontmatter 中的 `scope_level` 和 `scope_code` 字段、`index.md` category_3 的聚合展示、各技能的 scope 交互流程、以及 `wiki-lint` 的 scope 校验规则。

## Requirements

### REQ-1: Page frontmatter 包含 scope 字段

**Behavior**: `wiki-ingest` 步骤 6 的页面模板 frontmatter 必须包含 `scope_level` 和 `scope_code` 两个字段。`wiki-update` 在修改页面时也遵循相同的 frontmatter 结构。

**Test Verification**: 静态读取 `skill/wiki-ingest/SKILL.md` 步骤 6 的模板代码块，验证 frontmatter 中包含 `scope_level: <repo|domain|company|industry|wisdom>` 和 `scope_code: <slug>`。

```
Given: skill/wiki-ingest/SKILL.md 步骤 6 的页面模板
When:  读取 frontmatter 代码块
Then:  包含 scope_level 和 scope_code 字段
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析、`skill/wiki-update/SKILL.md` 静态分析

---

### REQ-2: scope_level 仅接受 5 个枚举值

**Behavior**: `scope_level` 必须为以下 5 个值之一：`repo`、`domain`、`company`、`industry`、`wisdom`。其他值无效。

**Test Verification**: 读取 `skill/wiki-lint/SKILL.md`，验证 Yellow Warning 规则中存在 `invalid-scope-level`，检查 `scope_level` 是否在合法枚举值中。

```
Given: wiki/pages/ 中包含一个 scope_level: "global" 的页面（非法值）
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: invalid-scope-level
```

```
Given: wiki/pages/ 中包含一个 scope_level: "repo" 的页面（合法值）
When:  执行 wiki-lint
Then:  不输出 invalid-scope-level 警告
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

### REQ-3: scope_code 遵循 slug 规则

**Behavior**: `scope_code` 必须遵循 slug 规则：全小写、连字符分隔、无特殊字符、不使用拼音（中文代号翻译为英文 slug）。

**Test Verification**: 读取 `skill/wiki-lint/SKILL.md`，验证 Yellow Warning 规则中存在 `invalid-scope-code-format`，检查 `scope_code` 是否符合 slug 规则。

```
Given: wiki/pages/ 中包含一个 scope_code: "YiLaiZhuRu" 的页面（大写）
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: invalid-scope-code-format
```

```
Given: wiki/pages/ 中包含一个 scope_code: "dependency-injection" 的页面（合法）
When:  执行 wiki-lint
Then:  不输出 invalid-scope-code-format 警告
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

### REQ-4: scope_level 与 scope_code 一致性校验

**Behavior**: `wiki-lint` 检查 `scope_level` 与 `scope_code` 的逻辑一致性。当 `scope_level` 为 `wisdom` 时，`scope_code` 必须为 `wisdom`。当 `scope_level` 为 `repo` 时，`scope_code` 通常应为仓库名（非强制）。

**Test Verification**: 读取 `skill/wiki-lint/SKILL.md`，验证 Yellow Warning 规则中存在 `scope-level-code-mismatch`。

```
Given: wiki/pages/ 中包含一个 scope_level: "wisdom"、scope_code: "fintech" 的页面
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: scope-level-code-mismatch
```

```
Given: wiki/pages/ 中包含一个 scope_level: "wisdom"、scope_code: "wisdom" 的页面
When:  执行 wiki-lint
Then:  不输出 scope-level-code-mismatch 警告
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

### REQ-5: scope 字段缺失为 Yellow Warning（向后兼容）

**Behavior**: `wiki-lint` 检查每个页面的 frontmatter 是否包含 `scope_level` 和 `scope_code`。缺失时输出 Yellow Warning：`missing-scope-fields`。不阻断流程，保持与旧页面的向后兼容。

**Test Verification**: 读取 `skill/wiki-lint/SKILL.md`，验证 `missing-scope-fields` 归类为 Yellow Warning 而非 Red Error。

```
Given: wiki/pages/ 中包含一个 frontmatter 无 scope_level 和 scope_code 的旧页面
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: missing-scope-fields
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

### REQ-6: wiki-ingest 在摄入时确定 scope

**Behavior**: `wiki-ingest` 在步骤 3（展示摘要，等待用户确认）中，AI 根据源内容分析并建议 `scope_level` 和 `scope_code`，与 key takeaways 一同展示给用户确认。确认后的 scope 值写入步骤 6 的页面 frontmatter。

**Test Verification**: 读取 `skill/wiki-ingest/SKILL.md` 步骤 3，验证交互描述中包含 scope 建议和确认流程。

```
Given: 用户向 wiki-ingest 提交一个关于 "Go 并发模式" 的源
When:  AI 在步骤 3 展示摘要
Then:  摘要中包含 scope_level 和 scope_code 的建议，并询问用户确认
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 步骤 3 的交互描述

---

### REQ-7: wiki-ingest 步骤 9 维护 index.md category_3

**Behavior**: `wiki-ingest` 步骤 9（更新 `wiki/index.md`）除了维护 category_1（Wiki 页面）外，还必须维护 category_3（适用范围）。category_3 按 `scope_code` 分组，每组下以列表形式展示该范围内的所有页面 slug。

**Test Verification**: 读取 `skill/wiki-ingest/SKILL.md` 步骤 9，验证包含 category_3 的更新模板。

```
Given: wiki-ingest 摄入了一个 scope_code: "llm-wiki"、scope_level: "repo" 的页面
When:  步骤 9 更新 wiki/index.md
Then:  category_3 区域中 llm-wiki 组下新增该页面的 [[slug]] 条目
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 步骤 9 静态分析、真实 agent smoke 测试

---

### REQ-8: index.md category_3 模板列名正式化

**Behavior**: `skill/wiki-init/templates/index.md` 的 category_3 区域列名从当前占位符"范围代号 | 适用范围 | 日期"正式化为"范围代号 | 适用范围 | 最后更新"，与 category_1 列名风格保持一致。category_3 的标题占位符 `<category_3>` 保持不变（由 wiki-init 步骤 1 询问用户命名）。

**Test Verification**: 读取 `skill/wiki-init/templates/index.md`，验证 category_3 表格列名为"范围代号 | 适用范围 | 最后更新"。

```
Given: skill/wiki-init/templates/index.md
When:  读取 category_3 区域的表格头
Then:  列名为 "| 范围代号 | 适用范围 | 最后更新 |"
```

**Interfaces to Test Through**: `skill/wiki-init/templates/index.md` 静态分析

---

### REQ-9: category_3 聚合格式

**Behavior**: `index.md` 的 category_3 区域按 `scope_code` 分组聚合。每组以 scope_code 为标题（如 `### llm-wiki`），下方以列表形式展示该范围内所有页面。列表项格式：`- [[slug]] — <scope_level 中文名>`。

**Test Verification**: 静态验证 `skill/wiki-ingest/SKILL.md` 步骤 9 中的 category_3 模板格式。

```
Given: wiki/ 中有三个页面，分别属于 llm-wiki (repo)、fintech (industry)、wisdom (wisdom)
When:  wiki-ingest 步骤 9 更新 index.md category_3
Then:  category_3 按 scope_code 分组为三个 ### 区块，每个区块下列出对应页面
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 步骤 9 静态分析

---

### REQ-10: wiki-distill 委托 ingest 时传入 scope

**Behavior**: `wiki-distill` Phase 3.1（NEW 条目处理）在委托 `wiki-ingest` 写入新页面时，必须传递 scope 信息。scope 由项目上下文推断：当前分析的项目路径对应的 repo 名为 `scope_code`，`scope_level` 默认为 `repo`。用户可在 Phase 3 逐条决策时覆盖。

**Test Verification**: 读取 `skill/wiki-distill/SKILL.md` Phase 3.1，验证委托 ingest 时包含 scope 传递描述。

```
Given: wiki-distill 分析项目 "llm-wiki"，Phase 3.1 委托 ingest 写入 NEW 经验
When:  委托 wiki-ingest 时
Then:  传递 scope_level: "repo"、scope_code: "llm-wiki"
```

**Interfaces to Test Through**: `skill/wiki-distill/SKILL.md` Phase 3.1 静态分析

---

### REQ-11: wiki-distill 在 Phase 3 允许用户覆盖 scope

**Behavior**: `wiki-distill` 在 Phase 3（DECIDE & MERGE）逐条决策时，对于 NEW 条目，除了询问"是否新增"外，还应展示 AI 推断的 scope 并允许用户修改。

**Test Verification**: 读取 `skill/wiki-distill/SKILL.md` Phase 3.1，验证交互描述中包含 scope 展示和修改选项。

```
Given: wiki-distill Phase 3.1 处理一条 NEW 经验
When:  展示给用户确认
Then:  显示推断的 scope_level 和 scope_code，并允许用户修改
```

**Interfaces to Test Through**: `skill/wiki-distill/SKILL.md` Phase 3.1 静态分析

---

### REQ-12: wiki-update scope 变更时同步 category_3

**Behavior**: `wiki-update` 步骤 5（更新 `wiki/index.md`）中，若页面的 `scope_level` 或 `scope_code` 发生变更，必须同步更新 index.md 的 category_3 区域。旧 scope_code 组中移除该页面，新 scope_code 组中添加该页面。

**Test Verification**: 读取 `skill/wiki-update/SKILL.md` 步骤 5，验证包含 scope 变更时的 category_3 同步描述。

```
Given: 一个 scope_code 从 "llm-wiki" 变更为 "wiki-ecosystem" 的页面
When:  wiki-update 步骤 5 更新 index.md
Then:  category_3 中 llm-wiki 组移除该页面，wiki-ecosystem 组新增该页面
```

**Interfaces to Test Through**: `skill/wiki-update/SKILL.md` 步骤 5 静态分析

---

### REQ-13: wiki-query 利用 scope 辅助检索

**Behavior**: `wiki-query` 步骤 1（扫描 `wiki/index.md`）在识别相关页面时，可将 category_3 的 scope 信息作为辅助维度。例如，当用户问题涉及特定代码仓库或领域时，优先检索该 scope_code 下的页面。

**Test Verification**: 读取 `skill/wiki-query/SKILL.md` 步骤 1，验证描述中提到可参考 index.md 的 category_3（适用范围）区域辅助检索。

```
Given: skill/wiki-query/SKILL.md 步骤 1
When:  读取 index 扫描的描述
Then:  提到 category_3 的 scope 信息可作为辅助检索维度
```

**Interfaces to Test Through**: `skill/wiki-query/SKILL.md` 步骤 1 静态分析

---

### REQ-14: 页面正文包含适用范围信息

**Behavior**: `wiki-ingest` 步骤 6 的页面模板正文中，在 `**类型：**` 字段后新增 `**适用范围：**` 字段，展示 scope_level 的中文名和 scope_code。格式：`**适用范围：** <scope_level 中文名>（<scope_code>）`。

**Test Verification**: 读取 `skill/wiki-ingest/SKILL.md` 步骤 6 的页面模板，验证正文中包含适用范围字段。

```
Given: skill/wiki-ingest/SKILL.md 步骤 6 页面模板
When:  读取正文内容
Then:  包含 "**适用范围：** <scope_level 中文名>（<scope_code>）" 格式的字段
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 步骤 6 静态分析

---

### REQ-15: scope_level 中文名映射

**Behavior**: 在各技能的展示和页面正文中，scope_level 使用以下中文映射：

| scope_level | 中文名 | 含义 |
|-------------|--------|------|
| repo | 代码仓库 | 单个代码仓库级别 |
| domain | 领域 | 跨若干个代码仓库适用 |
| company | 公司 | 跨若干个领域适用 |
| industry | 行业 | 跨若干个公司适用 |
| wisdom | 智慧 | 高度抽象，跨多行业多场景适用 |

**Test Verification**: 读取 `skill/wiki-ingest/SKILL.md` 步骤 3 或步骤 6，验证 scope_level 建议或模板中使用上述中文名。

```
Given: skill/wiki-ingest/SKILL.md
When:  读取 scope 相关描述
Then:  scope_level 展示时使用中文名映射（如 "repo" → "代码仓库"）
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md`、`skill/wiki-distill/SKILL.md` 静态分析

---

## Test Structure

### Static Tests

```python
def test_ingest_page_template_has_scope_frontmatter(self):
    """验证 wiki-ingest SKILL.md 步骤 6 模板包含 scope_level 和 scope_code"""
    pass

def test_lint_has_invalid_scope_level_rule(self):
    """验证 wiki-lint SKILL.md 包含 invalid-scope-level Yellow Warning"""
    pass

def test_lint_has_invalid_scope_code_format_rule(self):
    """验证 wiki-lint SKILL.md 包含 invalid-scope-code-format Yellow Warning"""
    pass

def test_lint_has_scope_level_code_mismatch_rule(self):
    """验证 wiki-lint SKILL.md 包含 scope-level-code-mismatch Yellow Warning"""
    pass

def test_lint_has_missing_scope_fields_rule(self):
    """验证 wiki-lint SKILL.md 包含 missing-scope-fields Yellow Warning"""
    pass

def test_ingest_step3_asks_scope_confirmation(self):
    """验证 wiki-ingest SKILL.md 步骤 3 包含 scope 确认交互"""
    pass

def test_ingest_step9_maintains_category3(self):
    """验证 wiki-ingest SKILL.md 步骤 9 包含 category_3 维护描述"""
    pass

def test_index_template_category3_columns(self):
    """验证 index.md 模板 category_3 列名为正式中文名"""
    pass

def test_distill_phase3_passes_scope_to_ingest(self):
    """验证 wiki-distill SKILL.md Phase 3.1 委托 ingest 时传递 scope"""
    pass

def test_distill_phase3_allows_scope_override(self):
    """验证 wiki-distill SKILL.md Phase 3 允许用户覆盖 scope"""
    pass

def test_update_step5_syncs_scope_category3(self):
    """验证 wiki-update SKILL.md 步骤 5 包含 scope 变更同步描述"""
    pass

def test_query_step1_mentions_scope_filter(self):
    """验证 wiki-query SKILL.md 步骤 1 提到 scope 辅助检索"""
    pass

def test_page_template_has_scope_in_body(self):
    """验证 wiki-ingest SKILL.md 步骤 6 正文模板包含适用范围字段"""
    pass

def test_scope_level_chinese_mapping(self):
    """验证 scope_level 中文名映射在 SKILL.md 中有定义"""
    pass
```

### Integration Smoke Tests

```python
def test_ingest_with_scope_updates_category3(self):
    # Given: 一个带有 scope 的源
    # When: wiki-ingest 执行摄入
    # Then: wiki/index.md category_3 区域按 scope_code 聚合了该页面
    pass

def test_lint_detects_invalid_scope_on_page(self):
    # Given: wiki/pages/ 中有一个 scope_level 非法的页面
    # When: wiki-lint 执行
    # Then: 报告包含 invalid-scope-level 警告
    pass

def test_old_page_without_scope_triggers_warning(self):
    # Given: wiki/pages/ 中有一个无 scope 字段的旧页面
    # When: wiki-lint 执行
    # Then: 报告包含 missing-scope-fields 警告（Yellow，非 Red）
    pass
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_scope_metadata_static.py` | 静态验证所有 6 个 SKILL.md 和 2 个模板中的 scope 相关内容 |
| `tests/test_agent_skill_smoke_e2e.py` | 扩展 smoke 测试：wiki-ingest 含 scope 的源 → 验证 category_3 更新 |
| `tests/test_wiki_lint_scope_rules.py` | 静态验证 wiki-lint SKILL.md 中的 4 条 scope 规则 |

## Edge Cases

- `scope_code` 在 category_3 中不存在时，创建新的 `### scope_code` 区块
- `scope_code` 组下最后一个页面被移除时，删除该 `### scope_code` 区块
- `scope_level` 和 `scope_code` 同时变更时，旧组删除 + 新组添加应原子化
- 页面同时出现在 category_1（Wiki 页面）和 category_3（适用范围）中，两处应保持一致的 slug 引用
- 旧格式 `index.md` 没有 category_3 区域时，wiki-ingest 应创建该区域
- 旧页面没有 scope 字段时，wiki-lint 发出 Yellow Warning 但不影响其他检查
- `scope_code` 包含中文时（如未翻译的拼音），wiki-lint 应报告 `invalid-scope-code-format`
