# Specification: date-placeholder-consistency

## Overview

统一 wiki 生态中日期相关字段的命名和占位符语义。修复 `index.md` 中 category_2 列名不一致问题，并在所有使用 `<today>` 占位符的 SKILL.md 和模板中明确替换规则。

## Requirements

### REQ-1: index.md category_2 列名统一为"最后更新"

**Behavior**: `wiki/index.md` 的 category_2（Concepts 页面）表格列名从"日期"改为"最后更新"，与 category_1（Wiki 页面）的列名保持一致。

**Test Verification**: 读取 `wiki/index.md`，验证 category_2 表格头为 `| 页面 | 类型 | 最后更新 |`。

```
Given: wiki/index.md 的 category_2 区域
When:  读取表格头
Then:  列名为 "| 页面 | 类型 | 最后更新 |"
```

**Interfaces to Test Through**: `wiki/index.md` 静态分析

---

### REQ-2: 模板 index.md category_2 列名统一为"最后更新"

**Behavior**: `skill/wiki-init/templates/index.md` 的 category_2 表格列名从"日期"改为"最后更新"。

**Test Verification**: 读取 `skill/wiki-init/templates/index.md`，验证 category_2 表格头为 `| 页面 | 类型 | 最后更新 |`。

```
Given: skill/wiki-init/templates/index.md 的 category_2 区域
When:  读取表格头
Then:  列名为 "| 页面 | 类型 | 最后更新 |"
```

**Interfaces to Test Through**: `skill/wiki-init/templates/index.md` 静态分析

---

### REQ-3: wiki-ingest SKILL.md 明确 `<today>` 替换规则

**Behavior**: `skill/wiki-ingest/SKILL.md` 中首次出现 `<today>` 占位符时（或 Pre-condition 附近），必须包含显式说明：`<today>` 在执行时替换为实际当前日期，格式 YYYY-MM-DD。

**Test Verification**: 读取 `skill/wiki-ingest/SKILL.md`，验证包含 `<today>` 替换为当前日期的说明文本。

```
Given: skill/wiki-ingest/SKILL.md
When:  读取全文
Then:  包含 "YYYY-MM-DD" 且上下文涉及 <today> 替换
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-4: wiki-distill SKILL.md 明确 `<today>` 替换规则

**Behavior**: `skill/wiki-distill/SKILL.md` 中首次出现 `<today>` 占位符时，必须包含显式说明。

**Test Verification**: 读取 `skill/wiki-distill/SKILL.md`，验证包含 `<today>` 替换为当前日期的说明文本。

```
Given: skill/wiki-distill/SKILL.md
When:  读取全文
Then:  包含 "YYYY-MM-DD" 且上下文涉及 <today> 替换
```

**Interfaces to Test Through**: `skill/wiki-distill/SKILL.md` 静态分析

---

### REQ-5: wiki-query SKILL.md 明确 `<today>` 替换规则

**Behavior**: `skill/wiki-query/SKILL.md` 中首次出现 `<today>` 占位符时，必须包含显式说明。

**Test Verification**: 读取 `skill/wiki-query/SKILL.md`，验证包含 `<today>` 替换为当前日期的说明文本。

```
Given: skill/wiki-query/SKILL.md
When:  读取全文
Then:  包含 "YYYY-MM-DD" 且上下文涉及 <today> 替换
```

**Interfaces to Test Through**: `skill/wiki-query/SKILL.md` 静态分析

---

### REQ-6: wiki-lint SKILL.md 明确 `<today>` 替换规则

**Behavior**: `skill/wiki-lint/SKILL.md` 中首次出现 `<today>` 占位符时，必须包含显式说明。

**Test Verification**: 读取 `skill/wiki-lint/SKILL.md`，验证包含 `<today>` 替换为当前日期的说明文本。

```
Given: skill/wiki-lint/SKILL.md
When:  读取全文
Then:  包含 "YYYY-MM-DD" 且上下文涉及 <today> 替换
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

### REQ-7: wiki-lint 新增 `hardcoded-or-literal-today` Blue Info 规则

**Behavior**: `wiki-lint` 在 Blue Info 节中新增规则 `hardcoded-or-literal-today`，检查生成文件（`wiki/pages/*.md`、`concepts/*.md`、`wiki/index.md`、`wiki/log.md`）中是否残留字面量 `<today>` 或使用了明显非当前日期的硬编码日期。该规则为 Blue Info 级别（仅建议，不阻断）。

**Test Verification**: 读取 `skill/wiki-lint/SKILL.md`，验证 Blue Info 节包含 `hardcoded-or-literal-today` 规则。

```
Given: skill/wiki-lint/SKILL.md 步骤 2 Blue Info 节
When:  读取规则列表
Then:  包含 hardcoded-or-literal-today 规则
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

### REQ-8: wiki-init/templates/log.md 明确 `<today>` 替换规则

**Behavior**: `skill/wiki-init/templates/log.md` 中 `<today>` 占位符附近必须包含格式说明：`<today>` 在执行时替换为实际当前日期（YYYY-MM-DD）。

**Test Verification**: 读取 `skill/wiki-init/templates/log.md`，验证 `<today>` 附近有 YYYY-MM-DD 格式说明。

```
Given: skill/wiki-init/templates/log.md
When:  读取全文
Then:  包含 "YYYY-MM-DD" 格式说明
```

**Interfaces to Test Through**: `skill/wiki-init/templates/log.md` 静态分析

---

## Test Structure

### Static Tests

```python
def test_index_category2_column_is_last_updated(self):
    """验证 wiki/index.md category_2 列名为"最后更新" """
    pass

def test_template_index_category2_column_is_last_updated(self):
    """验证模板 index.md category_2 列名为"最后更新" """
    pass

def test_ingest_has_today_replacement_rule(self):
    """验证 wiki-ingest SKILL.md 包含 <today> 替换说明"""
    pass

def test_distill_has_today_replacement_rule(self):
    """验证 wiki-distill SKILL.md 包含 <today> 替换说明"""
    pass

def test_query_has_today_replacement_rule(self):
    """验证 wiki-query SKILL.md 包含 <today> 替换说明"""
    pass

def test_lint_has_today_replacement_rule(self):
    """验证 wiki-lint SKILL.md 包含 <today> 替换说明"""
    pass

def test_lint_has_hardcoded_today_rule(self):
    """验证 wiki-lint SKILL.md Blue Info 包含 hardcoded-or-literal-today"""
    pass

def test_log_template_has_today_replacement_rule(self):
    """验证 log.md 模板包含 <today> 替换说明"""
    pass
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_date_placeholder_static.py` | 静态验证所有日期相关的一致性和替换规则 |

## Edge Cases

- 已有 `wiki/log.md` 中已写入的历史条目不受影响（不回溯修改）
- `openspec/changes/archive/` 中的硬编码日期不受影响（归档文件不修改）
- `skill/wiki-update/SKILL.md` 中如使用 `<today>` 也需添加说明
