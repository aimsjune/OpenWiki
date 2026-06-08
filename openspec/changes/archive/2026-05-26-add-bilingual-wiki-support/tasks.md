# Tasks: add-bilingual-wiki-support

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

**Rules:**
1. Write ONE failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed, ensure tests pass
4. Only then move to next behavior

---

## Behavior 1: WIKI.md 模板包含语言配置字段 (AC #1)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_config_static.py` 中编写测试：读取 `skill/wiki-init/templates/WIKI.md`，解析 YAML frontmatter，断言存在 `primary_language: zh` 和 `secondary_language: en`
- [ ] **1.2** 运行测试确认 FAILS（当前模板不含语言字段）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-init/templates/WIKI.md` 的 frontmatter 中添加 `primary_language: zh` 和 `secondary_language: en` 字段
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保新增字段与现有 frontmatter 字段格式一致
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 2: index.md 和 log.md 模板中文化 (AC #5, AC #6)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_config_static.py` 中编写测试：读取 `skill/wiki-init/templates/index.md`，断言分类标题、列名（"页面"、"摘要"、"标签"、"最后更新"）、占位文本（"暂无"）为中文
- [ ] **1.2** 编写测试：读取 `skill/wiki-init/templates/log.md`，断言标题（"操作日志"）、格式说明、占位文本为中文
- [ ] **1.3** 运行测试确认 FAILS（当前模板为英文）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 修改 `skill/wiki-init/templates/index.md`：分类标题、列名、占位文本改为中文
- [ ] **2.2** 修改 `skill/wiki-init/templates/log.md`：标题改为"操作日志"，格式说明中文化
- [ ] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保中文模板结构与原英文模板逻辑一致
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 3: wiki-init 初始化时收集语言偏好 (AC #2, AC #3, AC #4)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_init.py` 中编写测试：模拟新 wiki 初始化流程，验证交互输出中包含语言偏好询问（`primary_language` / `secondary_language`，默认 zh/en）
- [ ] **1.2** 编写测试：验证生成的 `WIKI.md` 包含语言字段
- [ ] **1.3** 编写测试：提供包含语言字段的 fixture `WIKI.md`，验证复用路径不询问语言偏好（提问裁剪）
- [ ] **1.4** 编写测试：提供不含语言字段的 fixture `WIKI.md`（旧格式），验证补问且默认值为 zh/en
- [ ] **1.5** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-init/SKILL.md` 的 Process 步骤 1（配置收集）中，在 `domain` 询问之后增加语言偏好询问描述
- [ ] **2.2** 在复用已有配置的提问裁剪逻辑中，增加语言字段的裁剪描述
- [ ] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保语言偏好询问的措辞与 `domain`、`source_types` 等字段一致
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 4: wiki-ingest 生成中文页面模板 (AC #7)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_ingest.py` 中编写测试：提供 fixture 源，执行 wiki-ingest 流程，验证生成页面的章节标题（"核心定义"、"关键要点"、"相关主题"、"开放问题"）和字段标签（"来源"、"摄入日期"、"类型"）为中文
- [ ] **1.2** 编写测试：静态读取 `skill/wiki-ingest/SKILL.md` 步骤 6 的模板代码块，验证章节标题和字段标签为中文
- [ ] **1.3** 运行测试确认 FAILS（当前模板为英文）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 修改 `skill/wiki-ingest/SKILL.md` 步骤 6 的页面模板代码块：章节标题（`## 核心定义`、`## 关键要点`、`## 相关主题`、`## 开放问题`）和字段标签（`**来源：**`、`**摄入日期：**`、`**类型：**`）改为中文
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确认模板中文化不影响 wiki-ingest 的其他步骤
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 5: wiki-ingest slug 英文翻译策略 (AC #8)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_ingest.py` 中编写测试：提供中文标题 fixture（如"依赖注入模式"），验证生成的 slug 为英文翻译（`dependency-injection-pattern`）而非拼音（`yi-lai-zhu-ru-mo-shi`）
- [ ] **1.2** 运行测试确认 FAILS（当前无明确翻译策略描述）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-ingest/SKILL.md` 步骤 5（生成 slug）中增加说明：当源标题为中文时，slug 应翻译为英文（遵循小写、连字符、无特殊字符规则），而非使用拼音
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保 slug 翻译策略描述足够清晰，Agent 能一致执行
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 6: wiki-distill 报告中文描述确认 (AC #16)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_distill.py` 中编写测试：静态读取 `skill/wiki-distill/SKILL.md` 步骤 1.5 的报告模板代码块，验证分类标题为中文（"设计原则"、"代码模式"等）
- [ ] **1.2** 编写测试：提供 fixture 代码库，执行 wiki-distill 分析阶段，验证报告中的分类标题、经验标题、经验描述为中文，代码片段保留原文
- [ ] **1.3** 运行测试确认 FAILS（如果当前已有中文描述则测试直接通过）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 检查 `skill/wiki-distill/SKILL.md` 步骤 1.5 中的报告模板，确认分类标题已是中文（当前已使用中文模板，如无需修改则标记为完成）
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确认 wiki-distill 报告模板中文化与 spec 中 REQ-11 一致
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 7: wiki-lint 新增 content-not-chinese-primary 规则 (AC #9, AC #13)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_wiki_lint_language_rules.py` 中编写测试：提供中文占比低于 60% 的 fixture 页面（排除代码块、行内代码、URL、frontmatter 后计算），验证 lint 报告输出 Yellow Warning: `content-not-chinese-primary`
- [ ] **1.2** 编写测试：提供中文占比高于 60% 的 fixture 页面，验证不产生此警告
- [ ] **1.3** 编写测试：提供正文中文正常但含大量英文代码块的 fixture 页面，验证代码块内容被排除，不误报
- [ ] **1.4** 运行测试确认 FAILS（当前 wiki-lint 无此规则）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-lint/SKILL.md` 的 Process 步骤 2 的 **Yellow Warnings** 节中添加 `content-not-chinese-primary` 规则描述：正文中文占比低于 60% 时触发，排除代码块、行内代码、URL、frontmatter
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保规则描述清晰，中文占比计算的排除逻辑准确
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 8: wiki-lint 新增 missing-chinese-title 规则 (AC #10, AC #13)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_wiki_lint_language_rules.py` 中编写测试：提供 h1 为纯英文的 fixture 页面，验证 lint 报告输出 Yellow Warning: `missing-chinese-title`
- [ ] **1.2** 编写测试：提供 h1 包含中文的 fixture 页面，验证不产生此警告
- [ ] **1.3** 编写测试：提供 h1 为中英混合的 fixture 页面，验证不产生此警告（包含中文即满足）
- [ ] **1.4** 编写测试：提供 frontmatter `title` 为英文但 h1 为中文的 fixture 页面，验证不检查 frontmatter title
- [ ] **1.5** 运行测试确认 FAILS（当前 wiki-lint 无此规则）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-lint/SKILL.md` 的 Process 步骤 2 的 **Yellow Warnings** 节中添加 `missing-chinese-title` 规则描述：h1 标题不包含中文字符时触发，仅检查 Markdown h1，不检查 frontmatter title
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保规则描述明确"包含中文字符"的判断标准
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 9: wiki-lint 新增 missing-term-glossary 规则 (AC #11, AC #13)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_wiki_lint_language_rules.py` 中编写测试：提供包含 "Dependency Injection" 但无中文解释的 fixture 页面，验证 lint 报告输出 Yellow Warning: `missing-term-glossary`
- [ ] **1.2** 编写测试：提供包含 "依赖注入（Dependency Injection）" 的 fixture 页面，验证不产生此警告
- [ ] **1.3** 编写测试：提供包含 "Dependency Injection（依赖注入）" 的 fixture 页面，验证不产生此警告
- [ ] **1.4** 编写测试：提供包含单字术语 "Go" 的 fixture 页面，验证不产生此警告
- [ ] **1.5** 运行测试确认 FAILS（当前 wiki-lint 无此规则）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-lint/SKILL.md` 的 Process 步骤 2 的 **Yellow Warnings** 节中添加 `missing-term-glossary` 规则描述：英文多词术语（2 个及以上单词）首次出现未附中文解释时触发，支持两种标注形式
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保规则描述明确"多词术语"的判断标准和两种标注形式的识别规则
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 10: wiki-lint 新增 missing-bilingual-tags 规则 (AC #12, AC #13)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_wiki_lint_language_rules.py` 中编写测试：提供 tags 仅有英文标签的 fixture 页面（如 `tags: [go, design-pattern]`），primary_language 为 zh，验证 lint 报告输出 Yellow Warning: `missing-bilingual-tags`
- [ ] **1.2** 编写测试：提供 tags 包含中英文标签的 fixture 页面（如 `tags: [go, 设计模式]`），验证不产生此警告
- [ ] **1.3** 编写测试：提供 tags 有中文但概念不同的 fixture 页面（如 `tags: [go, 部署]`），验证不产生此警告（只要存在中文标签即可）
- [ ] **1.4** 运行测试确认 FAILS（当前 wiki-lint 无此规则）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-lint/SKILL.md` 的 Process 步骤 2 的 **Yellow Warnings** 节中添加 `missing-bilingual-tags` 规则描述：tags 中仅有英文标签无中文对应标签时触发，仅在 primary_language 为 zh 且 secondary_language 为 en 时启用
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保规则描述明确"只要存在中文标签即满足"的判断标准
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 11: wiki-lint 英文豁免清单与 primary_language 条件启用 (AC #13, AC #15)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_wiki_lint_language_exemptions.py` 中编写测试：提供包含各类豁免内容（代码块、行内代码、URL、frontmatter、术语标注）但中文占比正常的 fixture 页面，验证所有语言规则不误报
- [ ] **1.2** 编写测试：提供 `primary_language: en` 的 fixture 配置和包含语言违规的页面，验证所有 4 条语言规则被跳过
- [ ] **1.3** 编写测试：提供旧格式 `WIKI.md`（不含语言字段）的 fixture，验证 wiki-lint 不报错，语言字段默认视为 zh/en
- [ ] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `skill/wiki-lint/SKILL.md` 的 Process 步骤 2 中，在语言规则描述之后添加英文豁免清单：列出代码块、行内代码、URL、frontmatter、术语首次标注形式 5 项豁免
- [ ] **2.2** 添加 `primary_language` 条件启用说明：仅当 `primary_language` 为 `zh` 时启用语言规则
- [ ] **2.3** 添加向后兼容说明：旧格式 `WIKI.md`（不含语言字段）语言默认视为 zh/en
- [ ] **2.4** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保豁免清单和条件启用的描述清晰无歧义
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 12: wiki-lint SKILL.md 静态验证 (AC #14)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_wiki_lint_language_static.py` 中编写测试：静态读取 `skill/wiki-lint/SKILL.md` 的 Process 步骤 2，验证 **Yellow Warnings** 节包含 4 条语言规则（content-not-chinese-primary、missing-chinese-title、missing-term-glossary、missing-bilingual-tags）
- [ ] **1.2** 编写测试：验证语言规则之后包含英文豁免清单（代码块、行内代码、URL、frontmatter、术语标注）
- [ ] **1.3** 运行测试确认 FAILS（当前 SKILL.md 无语言规则）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 确认 Behavior 7-11 的 SKILL.md 修改已覆盖所有语言规则描述（此 behavior 验证汇总完整性）
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确保语言规则描述的结构与现有 Red Errors / Blue Info 一致
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 13: wiki-update 页面模板中文化确认 (AC 相关)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_config_static.py` 中编写测试：静态读取 `skill/wiki-update/SKILL.md`，验证若存在页面结构描述，其章节标题为中文
- [ ] **1.2** 运行测试确认 FAILS 或 PASSES（若 wiki-update 无显式页面模板则测试直接通过）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 检查 `skill/wiki-update/SKILL.md`，确认是否需要中文化（当前 wiki-update 通过 diff → 确认 → 写入工作，无显式页面模板，可能无需修改）
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确认 wiki-update 的中文化处理与整体策略一致
- [ ] **3.2** 运行所有测试确认通过

---

## Behavior 14: 当前运行时 WIKI.md 实例更新语言字段 (兼容性)

### Phase 1: RED - Write Failing Test

- [ ] **1.1** 在 `tests/test_bilingual_wiki_config_static.py` 中编写测试：读取 `<repo-root>/WIKI.md`，验证包含 `primary_language: zh` 和 `secondary_language: en`（或至少向后兼容）
- [ ] **1.2** 运行测试确认 FAILS（当前 WIKI.md 不含语言字段）

### Phase 2: GREEN - Make Test Pass

- [ ] **2.1** 在 `<repo-root>/WIKI.md` 的 frontmatter 中添加 `primary_language: zh` 和 `secondary_language: en`
- [ ] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [ ] **3.1** 确认运行时 WIKI.md 的其他字段未受影响
- [ ] **3.2** 运行所有测试确认通过

---

## Verification

完成所有 behavior 后：

- [ ] 运行完整测试套件
- [ ] 所有测试通过
- [ ] 实现与 acceptance criteria 匹配（proposal.md 中 16 条 AC）
- [ ] 各 SKILL.md 修改内容与 spec 中 REQ 一致
- [ ] 旧格式 WIKI.md 向后兼容验证通过

## Test Quality Checklist

- [ ] 测试描述 BEHAVIOR（行为），而非 implementation（实现）
- [ ] 测试通过 PUBLIC interfaces（SKILL.md 描述的流程、文件系统输出）
- [ ] 测试可在内部重构后仍然存活
- [ ] 测试命名描述 WHAT（什么），而非 HOW（怎么实现）
- [ ] 每个测试聚焦一个逻辑断言
- [ ] 不 mock 内部协作者
