# Specification: bilingual-wiki-config

## Overview

定义 wiki 生态系统的语言配置能力。该 spec 涵盖 `WIKI.md` 中新增的 `primary_language` / `secondary_language` 字段、`wiki-init` 初始化时收集语言偏好的流程、模板中文化、以及 `wiki-ingest` 页面生成时的语言行为。

## Requirements

### REQ-1: WIKI.md 模板包含语言配置字段

**Behavior**: `skill/wiki-init/templates/WIKI.md` 的 frontmatter 必须包含 `primary_language: zh` 和 `secondary_language: en` 作为默认值。

**Test Verification**: 静态读取 `skill/wiki-init/templates/WIKI.md`，解析 YAML frontmatter，验证两个字段存在且默认值分别为 `zh` 和 `en`。

```
Given: skill/wiki-init/templates/WIKI.md
When:  读取并解析 YAML frontmatter
Then:  primary_language 字段值为 "zh"，secondary_language 字段值为 "en"
```

**Interfaces to Test Through**: `skill/wiki-init/templates/WIKI.md` 静态分析

---

### REQ-2: wiki-init 初始化时询问语言偏好

**Behavior**: `wiki-init` 在收集配置阶段（步骤 1），当创建新 wiki 实例时，必须在询问 `domain` 之后增加语言偏好询问。收集 `primary_language`（默认 `zh`）和 `secondary_language`（默认 `en`），写入生成的 `WIKI.md`。

**Test Verification**: 执行 wiki-init 初始化新 wiki 流程，验证：
1. 交互输出中包含语言偏好询问
2. 生成的 `WIKI.md` frontmatter 包含 `primary_language` 和 `secondary_language`

```
Given: 用户启动 wiki-init 创建新 wiki
When:  初始化进入配置收集阶段
Then:  输出中包含语言偏好询问（默认 zh/en），生成的 WIKI.md 包含对应字段
```

**Interfaces to Test Through**: `wiki-init` 技能交互输出，生成的 `<config-dir>/WIKI.md` 文件内容

---

### REQ-3: wiki-init 复用已有配置时跳过已存在的语言字段

**Behavior**: 当 `wiki-init` 进入已有配置复用路径时，若 `WIKI.md` 已包含 `primary_language` 和 `secondary_language`，不应重复询问这些字段。

**Test Verification**: 提供包含完整语言字段的 fixture `WIKI.md`，验证复用路径不询问语言偏好。

```
Given: 已有 WIKI.md 包含 primary_language: zh 和 secondary_language: en
When:  wiki-init 识别为已有配置并进入复用路径
Then:  不询问 primary_language 和 secondary_language（提问裁剪）
```

**Interfaces to Test Through**: `wiki-init` 技能交互输出

---

### REQ-4: wiki-init 复用已有配置时补问缺失的语言字段

**Behavior**: 当 `wiki-init` 进入已有配置复用路径时，若 `WIKI.md` 缺失 `primary_language` 或 `secondary_language`（旧格式），应补问这些字段，默认值为 `zh` / `en`。

**Test Verification**: 提供不含语言字段的旧格式 fixture `WIKI.md`，验证补问时展示默认值。

```
Given: 已有 WIKI.md 不包含 primary_language 和 secondary_language（旧格式）
When:  wiki-init 识别为已有配置并进入复用路径
Then:  补问语言字段，默认值分别为 "zh" 和 "en"
```

**Interfaces to Test Through**: `wiki-init` 技能交互输出，更新后的 `WIKI.md` 文件内容

---

### REQ-5: wiki-init SKILL.md 文档描述语言偏好收集步骤

**Behavior**: `skill/wiki-init/SKILL.md` 的 Process 步骤 1（配置收集）中必须描述语言偏好询问，与 `domain`、`source_types` 等字段并列。

**Test Verification**: 静态读取 `skill/wiki-init/SKILL.md`，验证配置收集步骤中包含语言偏好询问描述。

```
Given: skill/wiki-init/SKILL.md
When:  读取 Process 步骤 1 的配置收集描述
Then:  包含 primary_language 和 secondary_language 的询问描述，默认值标注为 zh/en
```

**Interfaces to Test Through**: `skill/wiki-init/SKILL.md` 静态分析

---

### REQ-6: index.md 模板中文化

**Behavior**: `skill/wiki-init/templates/index.md` 的所有静态文本（分类标题、列名、占位文本）必须为中文。

**Test Verification**: 静态读取 `skill/wiki-init/templates/index.md`，验证所有非模板占位符的文本为中文。

```
Given: skill/wiki-init/templates/index.md
When:  读取文件内容
Then:  分类标题、列名（如"页面"、"摘要"、"标签"、"最后更新"）、占位文本（如"暂无"）为中文
```

**Interfaces to Test Through**: `skill/wiki-init/templates/index.md` 静态分析

---

### REQ-7: log.md 模板中文化

**Behavior**: `skill/wiki-init/templates/log.md` 的所有静态文本（标题、格式说明、占位文本）必须为中文。

**Test Verification**: 静态读取 `skill/wiki-init/templates/log.md`，验证标题和描述文本为中文。

```
Given: skill/wiki-init/templates/log.md
When:  读取文件内容
Then:  标题为"操作日志"或等效中文，格式说明为中文，占位文本为中文
```

**Interfaces to Test Through**: `skill/wiki-init/templates/log.md` 静态分析

---

### REQ-8: wiki-ingest 生成的页面使用中文模板

**Behavior**: `wiki-ingest` 在步骤 6（写入 wiki 页面）中，生成的页面必须使用中文模板：h1 标题、章节标题（"核心定义"、"关键要点"、"相关主题"、"开放问题"）、字段标签（"来源"、"摄入日期"、"类型"）为中文。

**Test Verification**: 提供 fixture 源，执行 wiki-ingest 流程，验证生成的页面：
1. h1 标题为中文（或原文翻译）
2. 章节标题为中文
3. 字段标签为中文

```
Given: 一个待摄入的英文源
When:  wiki-ingest 生成页面
Then:  页面的章节标题（## 核心定义、## 关键要点、## 相关主题、## 开放问题）和字段标签（**来源**、**摄入日期**、**类型**）为中文
```

**Interfaces to Test Through**: `wiki-ingest` 生成的 `wiki/pages/<slug>.md` 文件内容

---

### REQ-9: wiki-ingest SKILL.md 描述中文页面模板

**Behavior**: `skill/wiki-ingest/SKILL.md` 的步骤 6（写入 wiki 页面）中的模板示例必须使用中文章节标题和字段标签。

**Test Verification**: 静态读取 `skill/wiki-ingest/SKILL.md`，验证步骤 6 的模板代码块中章节标题和字段标签为中文。

```
Given: skill/wiki-ingest/SKILL.md 步骤 6
When:  读取模板代码块
Then:  章节标题（如 ## 核心定义）和字段标签（如 **来源：**）为中文
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-10: wiki-ingest slug 生成策略：中文标题 → 英文翻译 slug

**Behavior**: `wiki-ingest` 在步骤 5（生成 slug）中，当源标题为中文时，slug 必须为英文翻译而非拼音。slug 遵循小写、连字符、无特殊字符的规则。

**Test Verification**: 提供中文标题 fixture（如"依赖注入模式"），验证生成的 slug 为 `dependency-injection-pattern` 而非 `yi-lai-zhu-ru-mo-shi`。

```
Given: 源标题为中文（如"依赖注入模式"）
When:  wiki-ingest 执行步骤 5 生成 slug
Then:  slug 为英文翻译（如 dependency-injection-pattern），非拼音
```

**Interfaces to Test Through**: `wiki-ingest` 生成的 slug 值

---

### REQ-11: wiki-distill 报告使用中文描述

**Behavior**: `wiki-distill` 在步骤 1.5（生成经验报告）中，报告的静态文本（分类标题、字段标签、说明文字）必须为中文。代码片段、来源文件路径保留原文。

**Test Verification**: 提供 fixture 代码库，执行 wiki-distill 分析阶段，验证：
1. 报告中的分类标题（"设计原则"、"代码模式"等）为中文
2. 经验标题和描述为中文
3. 代码片段保留原文

```
Given: 包含可识别设计模式的 fixture 代码库
When:  执行 wiki-distill 分析阶段
Then:  报告中的分类标题为中文，经验描述为中文，代码片段保留原文
```

**Interfaces to Test Through**: `raw/distill-<project>.md` 文件内容

---

### REQ-12: wiki-distill SKILL.md 报告模板使用中文

**Behavior**: `skill/wiki-distill/SKILL.md` 步骤 1.5 中的报告模板代码块必须使用中文分类标题和字段标签。

**Test Verification**: 静态读取 `skill/wiki-distill/SKILL.md`，验证步骤 1.5 的模板代码块中分类标题为中文。

```
Given: skill/wiki-distill/SKILL.md 步骤 1.5
When:  读取报告模板代码块
Then:  分类标题（如 "## 设计原则"、"## 代码模式"）为中文
```

**Interfaces to Test Through**: `skill/wiki-distill/SKILL.md` 静态分析

---

### REQ-13: 旧格式 WIKI.md 向后兼容

**Behavior**: 当 `WIKI.md` 不包含 `primary_language` 或 `secondary_language` 字段时（旧格式），所有 wiki workflow（wiki-init、wiki-ingest、wiki-query、wiki-lint、wiki-update、wiki-distill）必须正常运行，不应报错。缺失的语言字段视为 `zh` / `en`。

**Test Verification**: 提供不含语言字段的 fixture `WIKI.md`，依次执行各 wiki workflow 的前置检查，验证均不报错。

```
Given: WIKI.md frontmatter 不包含 primary_language 或 secondary_language（旧格式）
When:  任意 wiki workflow 读取 WIKI.md 解析运行时状态
Then:  workflow 正常运行，不报错，语言字段视为 zh/en
```

**Interfaces to Test Through**: 各 wiki skill 的 pre-condition 解析逻辑

---

### REQ-14: wiki-update 页面模板中文化（如有）

**Behavior**: 如果 `wiki-update` SKILL.md 中包含页面模板或建议的页面结构，其章节标题和字段标签必须为中文。

**Test Verification**: 静态读取 `skill/wiki-update/SKILL.md`，验证其中出现的页面结构描述为中文。

```
Given: skill/wiki-update/SKILL.md
When:  读取文件内容
Then:  若有页面结构描述，其章节标题为中文
```

**Interfaces to Test Through**: `skill/wiki-update/SKILL.md` 静态分析

---

## Test Structure

### Integration Tests

```python
def test_wiki_md_template_contains_language_fields(self):
    """验证 WIKI.md 模板包含语言字段"""
    # Given: skill/wiki-init/templates/WIKI.md
    # When: 解析 YAML frontmatter
    # Then: primary_language: zh, secondary_language: en
    pass

def test_wiki_init_collects_language_preference(self):
    """验证 wiki-init 新实例初始化时收集语言偏好"""
    # Given: 新 wiki 初始化流程
    # When: 执行 wiki-init
    # Then: 交互包含语言偏好询问，生成的 WIKI.md 包含语言字段
    pass

def test_wiki_init_skips_language_when_reusing(self):
    """验证复用已有配置时跳过已存在的语言字段"""
    # Given: 已有 WIKI.md 包含 language 字段
    # When: wiki-init 进入复用路径
    # Then: 不询问语言偏好
    pass

def test_wiki_init_asks_language_when_missing(self):
    """验证复用已有配置时补问缺失的语言字段"""
    # Given: 已有 WIKI.md 不含 language 字段（旧格式）
    # When: wiki-init 进入复用路径
    # Then: 补问语言偏好，默认 zh/en
    pass

def test_index_template_is_chinese(self):
    """验证 index.md 模板中文化"""
    # Given: skill/wiki-init/templates/index.md
    # When: 读取内容
    # Then: 分类标题、列名为中文
    pass

def test_log_template_is_chinese(self):
    """验证 log.md 模板中文化"""
    # Given: skill/wiki-init/templates/log.md
    # When: 读取内容
    # Then: 标题和说明为中文
    pass

def test_ingest_generates_chinese_page_template(self):
    """验证 wiki-ingest 生成中文页面模板"""
    # Given: 待摄入的源
    # When: wiki-ingest 生成页面
    # Then: 章节标题和字段标签为中文
    pass

def test_ingest_slug_is_english_translation(self):
    """验证 slug 为英文翻译而非拼音"""
    # Given: 中文标题
    # When: 生成 slug
    # Then: slug 为英文翻译
    pass

def test_ingest_skill_md_has_chinese_template(self):
    """验证 wiki-ingest SKILL.md 模板为中文"""
    # Given: skill/wiki-ingest/SKILL.md
    # When: 读取步骤 6 模板
    # Then: 章节标题为中文
    pass

def test_distill_report_uses_chinese(self):
    """验证 wiki-distill 报告使用中文描述"""
    # Given: fixture 代码库
    # When: 执行分析
    # Then: 分类标题、经验描述为中文
    pass

def test_distill_skill_md_has_chinese_template(self):
    """验证 wiki-distill SKILL.md 报告模板为中文"""
    # Given: skill/wiki-distill/SKILL.md
    # When: 读取步骤 1.5 模板
    # Then: 分类标题为中文
    pass

def test_old_wiki_md_backward_compatible(self):
    """验证旧格式 WIKI.md 向后兼容"""
    # Given: 不含语言字段的 WIKI.md
    # When: 各 wiki workflow 执行前置检查
    # Then: 不报错，语言默认 zh/en
    pass

def test_wiki_update_skill_md_chinese(self):
    """验证 wiki-update SKILL.md 页面结构为中文"""
    # Given: skill/wiki-update/SKILL.md
    # When: 读取内容
    # Then: 若有页面结构描述，为中文
    pass
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_bilingual_wiki_config_static.py` | 静态验证：模板文件语言字段和中文文本 |
| `tests/test_bilingual_wiki_init.py` | wiki-init 语言偏好收集流程验证 |
| `tests/test_bilingual_wiki_ingest.py` | wiki-ingest 中文页面模板和 slug 翻译验证 |
| `tests/test_bilingual_wiki_distill.py` | wiki-distill 中文报告验证 |

## Edge Cases

- `WIKI.md` 中 `primary_language` 为未知值（非 `zh`、`en` 等常见值）：不报错，按实际值处理
- `primary_language` 和 `secondary_language` 设为相同值：不报错，视为单语言 wiki
- `primary_language` 为空字符串：视为 `zh`
- 用户初始化时跳过语言询问（直接回车使用默认值）：使用 `zh` / `en`
- wiki-ingest 摄入的源标题本身就是英文：slug 直接使用英文标题的 slugify，章节标题仍用中文
- wiki-ingest 摄入的源标题为中英混合：slug 使用英文部分或翻译，章节标题为中文
- wiki-distill 分析的代码库注释为英文：报告描述仍为中文，代码片段保留英文原文
