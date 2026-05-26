# Specification: wiki-lint-language-rules

## Overview

定义 `wiki-lint` 技能新增的 4 条语言相关检查规则，全部归类为 Yellow Warning。同时定义英文豁免清单，明确哪些场景中的英文内容不触发警告。该 spec 是对 `wiki-lint` 现有检查体系的扩展，不改变已有的 Red Errors 和 Blue Info 规则。

## Requirements

### REQ-1: 新增 content-not-chinese-primary 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的正文内容（排除代码块、行内代码、URL、frontmatter 等豁免项）的中文占比。当中文占比低于阈值（默认 60%）时，输出 Yellow Warning：`content-not-chinese-primary`。

**Test Verification**: 
1. 提供中文占比低于 60% 的 fixture 页面，验证 lint 报告输出 Yellow Warning
2. 提供中文占比高于 60% 的 fixture 页面，验证不产生此警告
3. 提供全英文的 fixture 页面，验证必定输出此警告

```
Given: wiki/pages/ 中包含一个正文中文占比低于 60% 的页面
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: content-not-chinese-primary
```

```
Given: wiki/pages/ 中包含一个正文中文占比高于 60% 的页面
When:  执行 wiki-lint
Then:  不输出 content-not-chinese-primary 警告
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-2: 新增 missing-chinese-title 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的 h1 标题（`# Title`）。若 h1 标题不包含任何中文字符，输出 Yellow Warning：`missing-chinese-title`。

**Test Verification**:
1. 提供 h1 为纯英文的 fixture 页面，验证 lint 报告输出 Yellow Warning
2. 提供 h1 包含中文的 fixture 页面，验证不产生此警告
3. 提供 h1 为中英混合的 fixture 页面，验证不产生此警告（包含中文即满足）

```
Given: wiki/pages/ 中包含一个 h1 标题为 "Dependency Injection Pattern" 的页面
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: missing-chinese-title
```

```
Given: wiki/pages/ 中包含一个 h1 标题为 "依赖注入模式" 的页面
When:  执行 wiki-lint
Then:  不输出 missing-chinese-title 警告
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-3: 新增 missing-term-glossary 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的正文内容。当英文技术术语（2 个及以上单词的英文词组，如 "Dependency Injection"、"Repository Pattern"）在页面中首次出现时未附带中文解释（即未以 `中文术语（English Term）` 或 `English Term（中文术语）` 的形式标注），输出 Yellow Warning：`missing-term-glossary`。

单字英文术语（如 "Go"、"Rust"）不触发此规则。

**Test Verification**:
1. 提供包含 "Dependency Injection" 但无中文解释的 fixture 页面，验证输出 Yellow Warning
2. 提供包含 "依赖注入（Dependency Injection）" 的 fixture 页面，验证不产生此警告
3. 提供包含 "Dependency Injection（依赖注入）" 的 fixture 页面，验证不产生此警告
4. 提供包含单字术语 "Go" 的 fixture 页面，验证不产生此警告

```
Given: wiki/pages/ 中包含一个正文有 "Dependency Injection" 但无中文解释的页面
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: missing-term-glossary（标注术语 "Dependency Injection"）
```

```
Given: wiki/pages/ 中包含一个正文有 "依赖注入（Dependency Injection）" 的页面
When:  执行 wiki-lint
Then:  不输出 missing-term-glossary 警告
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-4: 新增 missing-bilingual-tags 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的 frontmatter `tags` 字段。若 `tags` 中仅有英文标签而没有对应的中文标签（如同一概念的中文表述），输出 Yellow Warning：`missing-bilingual-tags`。

此规则仅在 `primary_language` 为 `zh` 且 `secondary_language` 为 `en` 时启用。对于单语言 wiki（如 `primary_language` 和 `secondary_language` 相同），此规则不适用。

**Test Verification**:
1. 提供 tags 仅有英文标签的 fixture 页面（如 `tags: [go, design-pattern]`），验证输出 Yellow Warning
2. 提供 tags 包含中英文标签的 fixture 页面（如 `tags: [go, 设计模式]`），验证不产生此警告
3. 提供 `primary_language` 和 `secondary_language` 均为 `en` 的 fixture，验证此规则被跳过

```
Given: wiki/pages/ 中包含一个 tags: [dependency-injection, go] 的页面，primary_language: zh
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: missing-bilingual-tags
```

```
Given: wiki/pages/ 中包含一个 tags: [依赖注入, dependency-injection] 的页面，primary_language: zh
When:  执行 wiki-lint
Then:  不输出 missing-bilingual-tags 警告
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-5: 英文豁免清单 — 代码块不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除围栏代码块（`` ```...``` ``）的内容。代码块中的英文不影响中文占比计算。

**Test Verification**: 提供包含大量英文代码块但正文中文占比正常的 fixture 页面，验证不触发 `content-not-chinese-primary`。

```
Given: wiki/pages/ 中包含一个页面，正文为中文但代码块为大量英文代码
When:  执行 wiki-lint
Then:  content-not-chinese-primary 仅基于正文（排除代码块）计算，不误报
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-6: 英文豁免清单 — 行内代码不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除行内代码（`` `code` ``）的内容。

**Test Verification**: 提供包含大量行内代码引用但正文中文占比正常的 fixture 页面，验证不误报。

```
Given: wiki/pages/ 中包含一个页面，正文为中文但包含大量 `function_name` 引用
When:  执行 wiki-lint
Then:  行内代码内容被排除，不误报 content-not-chinese-primary
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-7: 英文豁免清单 — URL 不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除 URL 链接（如 `https://...`）。

**Test Verification**: 提供包含多个 URL 但正文中文占比正常的 fixture 页面，验证不误报。

```
Given: wiki/pages/ 中包含一个页面，正文为中文但包含多个 https:// 链接
When:  执行 wiki-lint
Then:  URL 内容被排除，不误报 content-not-chinese-primary
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-8: 英文豁免清单 — frontmatter 不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除 YAML frontmatter（`---...---` 之间的内容）。`missing-chinese-title` 规则也不检查 frontmatter 中的 `title` 字段（仅检查 Markdown h1）。

**Test Verification**: 提供 frontmatter 中 `title` 为英文但 h1 为中文的 fixture 页面，验证不误报。

```
Given: wiki/pages/ 中包含一个页面，frontmatter title 为英文，h1 为中文
When:  执行 wiki-lint
Then:  missing-chinese-title 仅检查 h1，不检查 frontmatter title
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-9: 英文豁免清单 — 术语首次标注形式不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，`中文术语（English Term）` 或 `English Term（中文术语）` 形式的标注文本中，括号内的英文部分不应被计入"非中文"内容。即术语标注形式在中文占比计算中视为中文内容。

**Test Verification**: 提供包含多个 "依赖注入（Dependency Injection）" 标注但正文中文占比正常的 fixture 页面，验证不误报。

```
Given: wiki/pages/ 中包含一个页面，正文有多处 "中文术语（English Term）" 标注
When:  执行 wiki-lint
Then:  术语标注中的英文不被计入非中文内容，不误报 content-not-chinese-primary
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-10: 语言规则仅在 primary_language 为 zh 时启用

**Behavior**: 当 `WIKI.md` 中 `primary_language` 不为 `zh` 时（如为 `en`），`wiki-lint` 的 4 条语言规则全部跳过，不产生任何语言相关的 Yellow Warning。

**Test Verification**: 提供 `primary_language: en` 的 fixture 配置和包含上述所有违规的页面，验证 lint 不输出任何语言规则警告。

```
Given: WIKI.md 中 primary_language: en，wiki/pages/ 中有多个语言违规页面
When:  执行 wiki-lint
Then:  lint 报告不包含任何语言规则（content-not-chinese-primary / missing-chinese-title / missing-term-glossary / missing-bilingual-tags）警告
```

**Interfaces to Test Through**: `wiki-lint` 输出的 `concepts/lint-<today>.md` 报告内容

---

### REQ-11: 语言规则归类为 Yellow Warning

**Behavior**: 所有 4 条新增语言规则（content-not-chinese-primary、missing-chinese-title、missing-term-glossary、missing-bilingual-tags）必须归类为 Yellow Warning。它们不阻断流程，仅作为建议性警告。

**Test Verification**: 静态读取 `skill/wiki-lint/SKILL.md` 的 Process 步骤 2，验证新增的 4 条规则出现在 **Yellow Warnings** 节下。

```
Given: skill/wiki-lint/SKILL.md Process 步骤 2
When:  读取 Yellow Warnings 节
Then:  包含 content-not-chinese-primary、missing-chinese-title、missing-term-glossary、missing-bilingual-tags 的描述
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

### REQ-12: wiki-lint SKILL.md 描述英文豁免清单

**Behavior**: `skill/wiki-lint/SKILL.md` 的 Process 步骤 2 中，在语言规则描述之后，必须包含英文豁免清单，列出不触发语言规则的场景。

**Test Verification**: 静态读取 `skill/wiki-lint/SKILL.md`，验证豁免清单包含：代码块、行内代码、URL、frontmatter、术语首次标注形式。

```
Given: skill/wiki-lint/SKILL.md Process 步骤 2
When:  读取语言规则相关描述
Then:  包含英文豁免清单（代码块、行内代码、URL、frontmatter、术语首次标注形式）
```

**Interfaces to Test Through**: `skill/wiki-lint/SKILL.md` 静态分析

---

## Test Structure

### Integration Tests

```python
def test_content_not_chinese_primary_warns(self):
    """验证中文占比低时输出 Yellow Warning"""
    # Given: 中文占比 < 60% 的 fixture 页面
    # When: wiki-lint
    # Then: 输出 content-not-chinese-primary 警告
    pass

def test_content_not_chinese_primary_no_warn(self):
    """验证中文占比正常时不输出警告"""
    # Given: 中文占比 > 60% 的 fixture 页面
    # When: wiki-lint
    # Then: 不输出 content-not-chinese-primary 警告
    pass

def test_missing_chinese_title_warns(self):
    """验证 h1 非中文时输出 Yellow Warning"""
    # Given: h1 为纯英文的 fixture 页面
    # When: wiki-lint
    # Then: 输出 missing-chinese-title 警告
    pass

def test_missing_chinese_title_no_warn(self):
    """验证 h1 含中文时不输出警告"""
    # Given: h1 含中文的 fixture 页面
    # When: wiki-lint
    # Then: 不输出 missing-chinese-title 警告
    pass

def test_missing_term_glossary_warns(self):
    """验证英文术语无中文解释时输出 Yellow Warning"""
    # Given: 含 "Dependency Injection" 但无中文解释的 fixture 页面
    # When: wiki-lint
    # Then: 输出 missing-term-glossary 警告
    pass

def test_missing_term_glossary_no_warn(self):
    """验证术语有中文解释时不输出警告"""
    # Given: 含 "依赖注入（Dependency Injection）" 的 fixture 页面
    # When: wiki-lint
    # Then: 不输出 missing-term-glossary 警告
    pass

def test_single_word_term_no_warn(self):
    """验证单字术语不触发 missing-term-glossary"""
    # Given: 含 "Go" 但无中文解释的 fixture 页面
    # When: wiki-lint
    # Then: 不输出 missing-term-glossary 警告
    pass

def test_missing_bilingual_tags_warns(self):
    """验证 tags 仅有英文时输出 Yellow Warning"""
    # Given: tags: [go, design-pattern]，primary_language: zh
    # When: wiki-lint
    # Then: 输出 missing-bilingual-tags 警告
    pass

def test_missing_bilingual_tags_no_warn(self):
    """验证 tags 有中英文时不输出警告"""
    # Given: tags: [go, 设计模式]，primary_language: zh
    # When: wiki-lint
    # Then: 不输出 missing-bilingual-tags 警告
    pass

def test_code_block_exempted(self):
    """验证代码块内容不触发语言规则"""
    # Given: 正文中文正常，代码块大量英文
    # When: wiki-lint
    # Then: 不误报 content-not-chinese-primary
    pass

def test_inline_code_exempted(self):
    """验证行内代码不触发语言规则"""
    # Given: 正文中文正常，大量行内代码
    # When: wiki-lint
    # Then: 不误报 content-not-chinese-primary
    pass

def test_url_exempted(self):
    """验证 URL 不触发语言规则"""
    # Given: 正文中文正常，多个 URL
    # When: wiki-lint
    # Then: 不误报 content-not-chinese-primary
    pass

def test_frontmatter_exempted(self):
    """验证 frontmatter 不触发语言规则"""
    # Given: frontmatter title 为英文，h1 为中文
    # When: wiki-lint
    # Then: missing-chinese-title 不检查 frontmatter title
    pass

def test_glossary_pattern_exempted(self):
    """验证术语标注形式不触发语言规则"""
    # Given: 多处 "中文术语（English Term）" 标注
    # When: wiki-lint
    # Then: 术语标注中的英文不计入非中文
    pass

def test_language_rules_disabled_for_en_primary(self):
    """验证 primary_language: en 时语言规则被跳过"""
    # Given: primary_language: en，页面有多处语言违规
    # When: wiki-lint
    # Then: 不输出任何语言规则警告
    pass

def test_language_rules_in_yellow_warnings_section(self):
    """验证语言规则归类为 Yellow Warning"""
    # Given: skill/wiki-lint/SKILL.md
    # When: 读取 Yellow Warnings 节
    # Then: 包含 4 条语言规则
    pass

def test_exemption_list_in_skill_md(self):
    """验证 SKILL.md 包含英文豁免清单"""
    # Given: skill/wiki-lint/SKILL.md
    # When: 读取语言规则相关描述
    # Then: 包含豁免清单
    pass
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_wiki_lint_language_static.py` | 静态验证：SKILL.md 中语言规则描述和豁免清单 |
| `tests/test_wiki_lint_language_rules.py` | 行为验证：4 条语言规则的触发和不触发场景 |
| `tests/test_wiki_lint_language_exemptions.py` | 豁免验证：各类豁免内容不误报 |
| `tests/test_wiki_lint_language_config.py` | 配置验证：primary_language 影响规则启用 |

## Edge Cases

- 页面完全为空（无正文）：`content-not-chinese-primary` 和 `missing-chinese-title` 均触发
- 页面只有代码块无正文：`content-not-chinese-primary` 应触发（正文为空，占比 0%）
- 页面只有 frontmatter 无正文：同空页面处理
- 术语标注跨行（如中文术语在前一行，英文在下一行括号中）：视为未标注，触发 `missing-term-glossary`
- 同一个术语在页面中出现多次：仅检查首次出现
- 标签中有中英文但不同概念（如 `tags: [go, 部署]`）：不触发 `missing-bilingual-tags`（只要存在中文标签即可）
- `primary_language` 为 `zh` 但 `secondary_language` 为空：`missing-bilingual-tags` 规则跳过
- 中文占比恰好等于 60%：不触发 `content-not-chinese-primary`（阈值是"低于 60%"）
