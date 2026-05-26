# wiki-lint-language-rules

## Purpose

定义 `wiki-lint` 技能新增的 4 条中英文语言相关检查规则，全部归类为 Yellow Warning。同时定义英文豁免清单，明确哪些场景中的英文内容不触发警告。该 spec 是对 `wiki-lint` 现有检查体系的扩展，不改变已有的 Red Errors 和 Blue Info 规则。

## Requirements

### REQ-1: 新增 content-not-chinese-primary 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的正文内容（排除代码块、行内代码、URL、frontmatter 等豁免项）的中文占比。当中文占比低于阈值（默认 60%）时，输出 Yellow Warning：`content-not-chinese-primary`。

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

---

### REQ-2: 新增 missing-chinese-title 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的 h1 标题（`# Title`）。若 h1 标题不包含任何中文字符，输出 Yellow Warning：`missing-chinese-title`。

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

---

### REQ-3: 新增 missing-term-glossary 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的正文内容。当英文技术术语（2 个及以上单词的英文词组）在页面中首次出现时未附带中文解释（即未以 `中文术语（English Term）` 或 `English Term（中文术语）` 的形式标注），输出 Yellow Warning：`missing-term-glossary`。单字英文术语（如 "Go"、"Rust"）不触发此规则。

```
Given: wiki/pages/ 中包含一个正文有 "Dependency Injection" 但无中文解释的页面
When:  执行 wiki-lint
Then:  lint 报告中输出 Yellow Warning: missing-term-glossary
```

```
Given: wiki/pages/ 中包含一个正文有 "依赖注入（Dependency Injection）" 的页面
When:  执行 wiki-lint
Then:  不输出 missing-term-glossary 警告
```

---

### REQ-4: 新增 missing-bilingual-tags 规则

**Behavior**: `wiki-lint` 检查每个 wiki 页面的 frontmatter `tags` 字段。若 `tags` 中仅有英文标签而没有中文标签，输出 Yellow Warning：`missing-bilingual-tags`。此规则仅在 `primary_language` 为 `zh` 且 `secondary_language` 为 `en` 时启用。

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

---

### REQ-5: 英文豁免清单 — 代码块不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除围栏代码块的内容。

```
Given: wiki/pages/ 中包含一个页面，正文为中文但代码块为大量英文代码
When:  执行 wiki-lint
Then:  content-not-chinese-primary 仅基于正文（排除代码块）计算，不误报
```

---

### REQ-6: 英文豁免清单 — 行内代码不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除行内代码的内容。

```
Given: wiki/pages/ 中包含一个页面，正文为中文但包含大量 `function_name` 引用
When:  执行 wiki-lint
Then:  行内代码内容被排除，不误报 content-not-chinese-primary
```

---

### REQ-7: 英文豁免清单 — URL 不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除 URL 链接。

```
Given: wiki/pages/ 中包含一个页面，正文为中文但包含多个 https:// 链接
When:  执行 wiki-lint
Then:  URL 内容被排除，不误报 content-not-chinese-primary
```

---

### REQ-8: 英文豁免清单 — frontmatter 不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，必须排除 YAML frontmatter。`missing-chinese-title` 规则也不检查 frontmatter 中的 `title` 字段（仅检查 Markdown h1）。

```
Given: wiki/pages/ 中包含一个页面，frontmatter title 为英文，h1 为中文
When:  执行 wiki-lint
Then:  missing-chinese-title 仅检查 h1，不检查 frontmatter title
```

---

### REQ-9: 英文豁免清单 — 术语首次标注形式不触发语言规则

**Behavior**: `wiki-lint` 在计算 `content-not-chinese-primary` 规则时，术语标注形式（`中文术语（English）` 或 `English（中文术语）`）中括号内的英文部分不计入"非中文"内容。

```
Given: wiki/pages/ 中包含一个页面，正文有多处 "中文术语（English Term）" 标注
When:  执行 wiki-lint
Then:  术语标注中的英文不被计入非中文内容，不误报 content-not-chinese-primary
```

---

### REQ-10: 语言规则仅在 primary_language 为 zh 时启用

**Behavior**: 当 `WIKI.md` 中 `primary_language` 不为 `zh` 时，`wiki-lint` 的 4 条语言规则全部跳过。

```
Given: WIKI.md 中 primary_language: en，wiki/pages/ 中有多个语言违规页面
When:  执行 wiki-lint
Then:  lint 报告不包含任何语言规则警告
```

---

### REQ-11: 语言规则归类为 Yellow Warning

**Behavior**: 所有 4 条新增语言规则必须归类为 Yellow Warning，不阻断流程。

```
Given: skill/wiki-lint/SKILL.md Process 步骤 2
When:  读取 Yellow Warnings 节
Then:  包含 content-not-chinese-primary、missing-chinese-title、missing-term-glossary、missing-bilingual-tags 的描述
```

---

### REQ-12: wiki-lint SKILL.md 描述英文豁免清单

**Behavior**: `skill/wiki-lint/SKILL.md` 的 Process 步骤 2 中必须包含英文豁免清单。

```
Given: skill/wiki-lint/SKILL.md Process 步骤 2
When:  读取语言规则相关描述
Then:  包含英文豁免清单（代码块、行内代码、URL、frontmatter、术语首次标注形式）
```
