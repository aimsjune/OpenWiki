# Specification: skill-body-splitting

## Overview

将 wiki-lint 和 wiki-ingest 的 SKILL.md 正文中重复出现的规则定义、检查清单、模板示例提取到 `references/` 目录，使正文保持简洁（<100 行），遵循 [[progressive-disclosure]] 的 Level 3 按需加载原则。

## Requirements

### REQ-1: wiki-lint 规则定义提取到 references/

**Behavior**: wiki-lint 的 SKILL.md 正文仅保留规则名称和简要说明，所有规则的详细定义（触发条件、检查逻辑、修复建议）存放在 `references/rules-catalog.md` 中。

**Test Verification**: 检查 `skill/wiki-lint/references/rules-catalog.md` 是否存在，且包含所有现有 lint 规则的详细定义。

```
Given: wiki-lint 的 SKILL.md 正文包含规则定义
When:  提取规则定义到 references/rules-catalog.md
Then:  SKILL.md 正文中每个规则仅保留名称 + 一行简要说明 + 指向 references/rules-catalog.md 的引用
       references/rules-catalog.md 包含每个规则的完整定义（触发条件、检查逻辑、修复建议）
```

**Interfaces to Test Through**: 文件存在性检查、行数统计、文本匹配

---

### REQ-2: wiki-lint 豁免清单提取到 references/

**Behavior**: wiki-lint 的豁免清单（代码块、行内代码、URL、frontmatter、术语标注）从 SKILL.md 正文提取到 `references/exemption-checklist.md`。

**Test Verification**: 检查 `skill/wiki-lint/references/exemption-checklist.md` 是否存在，且包含完整的 5 项豁免清单。

```
Given: wiki-lint 的 SKILL.md 正文包含豁免清单
When:  提取豁免清单到 references/exemption-checklist.md
Then:  SKILL.md 正文中豁免清单替换为一行引用
       references/exemption-checklist.md 包含完整的 5 项豁免及示例
```

**Interfaces to Test Through**: 文件存在性检查、文本匹配

---

### REQ-3: wiki-ingest 页面模板规范提取到 references/

**Behavior**: wiki-ingest 的页面模板规范（frontmatter 字段、正文结构、章节标题）从 SKILL.md 正文提取到 `references/page-template.md`。

**Test Verification**: 检查 `skill/wiki-ingest/references/page-template.md` 是否存在，且包含完整的页面模板规范。

```
Given: wiki-ingest 的 SKILL.md 正文包含页面模板规范
When:  提取模板规范到 references/page-template.md
Then:  SKILL.md 正文中模板规范替换为一行引用
       references/page-template.md 包含完整的 frontmatter 字段定义和正文结构
```

**Interfaces to Test Through**: 文件存在性检查、文本匹配

---

### REQ-4: wiki-ingest slug 规则提取到 references/

**Behavior**: wiki-ingest 的 slug 生成规则（小写、连字符、中文翻译、拼音排除）从 SKILL.md 正文提取到 `references/slug-rules.md`。

**Test Verification**: 检查 `skill/wiki-ingest/references/slug-rules.md` 是否存在，且包含完整的 slug 规则。

```
Given: wiki-ingest 的 SKILL.md 正文包含 slug 生成规则
When:  提取 slug 规则到 references/slug-rules.md
Then:  SKILL.md 正文中 slug 规则替换为一行引用
       references/slug-rules.md 包含完整的 slug 规则及正反示例
```

**Interfaces to Test Through**: 文件存在性检查、文本匹配

---

### REQ-5: wiki-lint SKILL.md 正文不超过 80 行

**Behavior**: 提取后，wiki-lint 的 SKILL.md 正文（不含 frontmatter 和注释）不超过 80 行。

**Test Verification**: 统计 `skill/wiki-lint/SKILL.md` 中 frontmatter 结束标记 `---` 之后的行数。

```
Given: wiki-lint 的 SKILL.md 已完成正文拆分
When:  统计 frontmatter 之后的行数
Then:  行数 ≤ 80
```

**Interfaces to Test Through**: 行数统计

---

### REQ-6: wiki-ingest SKILL.md 正文不超过 100 行

**Behavior**: 提取后，wiki-ingest 的 SKILL.md 正文（不含 frontmatter 和注释）不超过 100 行。

**Test Verification**: 统计 `skill/wiki-ingest/SKILL.md` 中 frontmatter 结束标记 `---` 之后的行数。

```
Given: wiki-ingest 的 SKILL.md 已完成正文拆分
When:  统计 frontmatter 之后的行数
Then:  行数 ≤ 100
```

**Interfaces to Test Through**: 行数统计

---

### REQ-7: SKILL.md 正文保留对 references/ 的引用

**Behavior**: 提取后，SKILL.md 正文中保留对 `references/` 文件的明确引用，Agent 可按需加载。

**Test Verification**: 检查 SKILL.md 正文是否包含 `references/` 路径引用。

```
Given: wiki-lint 和 wiki-ingest 的 SKILL.md 已完成正文拆分
When:  搜索正文中的 "references/"
Then:  每个被提取的规则/模板/清单在正文中至少有一处引用
```

**Interfaces to Test Through**: 文本匹配

---

## Test Structure

### 静态检查

```python
def test_wiki_lint_body_lines():
    """wiki-lint SKILL.md 正文不超过 80 行"""
    body = extract_body("skill/wiki-lint/SKILL.md")
    assert len(body.split("\n")) <= 80

def test_wiki_ingest_body_lines():
    """wiki-ingest SKILL.md 正文不超过 100 行"""
    body = extract_body("skill/wiki-ingest/SKILL.md")
    assert len(body.split("\n")) <= 100

def test_references_files_exist():
    """references/ 文件存在"""
    assert os.path.exists("skill/wiki-lint/references/rules-catalog.md")
    assert os.path.exists("skill/wiki-lint/references/exemption-checklist.md")
    assert os.path.exists("skill/wiki-ingest/references/page-template.md")
    assert os.path.exists("skill/wiki-ingest/references/slug-rules.md")

def test_body_references_exist():
    """正文包含对 references/ 的引用"""
    body = read_file("skill/wiki-lint/SKILL.md")
    assert "references/" in body
    body = read_file("skill/wiki-ingest/SKILL.md")
    assert "references/" in body
```

### Test Files to Create

| File | Purpose |
|------|---------|
| tests/test_body_splitting.py | 行数统计 + 文件存在性 + 引用检查 |

## Edge Cases

- references/ 文件为空时，正文引用是否仍然有效
- 提取后正文过短（<10 行）是否影响 Agent 理解流程
- 硬链接同步后 wiki-update 的 references/ 是否与源文件一致
