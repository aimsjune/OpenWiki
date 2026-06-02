# Tasks: optimize-skill-structure

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

**Note:** 本变更是文件结构优化，测试为静态文件检查（行数统计、YAML 解析、文件存在性、文本匹配、硬链接 inode 一致性）。

---

## Behavior 1: wiki-lint 正文拆分到 references/

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_body_splitting.py` 中编写测试：
  - `test_wiki_lint_references_exist`: 检查 `skill/wiki-lint/references/rules-catalog.md` 和 `skill/wiki-lint/references/exemption-checklist.md` 不存在（预期失败）
  - `test_wiki_lint_body_lines`: 统计 SKILL.md 正文行数（预期超过 80 行）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 创建 `skill/wiki-lint/references/rules-catalog.md`，从 SKILL.md 提取所有 lint 规则详细定义（触发条件、检查逻辑、修复建议）
- [x] **2.2** 创建 `skill/wiki-lint/references/exemption-checklist.md`，提取 5 项豁免清单及示例
- [x] **2.3** 精简 `skill/wiki-lint/SKILL.md` 正文：规则仅保留名称 + 一行说明 + `references/rules-catalog.md` 引用

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查 references/ 文件内容完整性（所有规则都已提取）
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 2: wiki-ingest 正文拆分到 references/

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_body_splitting.py` 中编写测试：
  - `test_wiki_ingest_references_exist`: 检查 `skill/wiki-ingest/references/page-template.md` 和 `skill/wiki-ingest/references/slug-rules.md` 不存在（预期失败）
  - `test_wiki_ingest_body_lines`: 统计 SKILL.md 正文行数（预期超过 100 行）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 创建 `skill/wiki-ingest/references/page-template.md`，从 SKILL.md 提取页面模板规范（frontmatter 字段定义、正文结构、章节标题）
- [x] **2.2** 创建 `skill/wiki-ingest/references/slug-rules.md`，提取 slug 生成规则及正反示例
- [x] **2.3** 精简 `skill/wiki-ingest/SKILL.md` 正文：模板规范替换为 `references/page-template.md` 引用

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查 references/ 文件内容完整性
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 3: wiki-lint tests/ 目录 + fixtures

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_skill_tests_dir.py` 中编写测试：
  - `test_wiki_lint_tests_dir`: 检查 `skill/wiki-lint/tests/` 不存在（预期失败）
  - `test_wiki_lint_fixtures`: 检查 fixtures 子目录不存在（预期失败）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 创建 `skill/wiki-lint/tests/fixtures/healthy-wiki/`（含 WIKI.md、wiki/index.md、wiki/pages/valid-page.md）
- [x] **2.2** 创建 `skill/wiki-lint/tests/fixtures/broken-links/`（含指向不存在页面的 [[交叉引用]]）
- [x] **2.3** 创建 `skill/wiki-lint/tests/fixtures/missing-scope/`（含缺少 scope_level 的页面）
- [x] **2.4** 创建 `skill/wiki-lint/tests/test_cases.md`（至少 3 个测试用例描述）

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 验证每个 fixture 是自包含的（WIKI.md 的 wiki_root 指向自身）
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 4: wiki-ingest tests/ 目录 + fixtures

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_skill_tests_dir.py` 中编写测试：
  - `test_wiki_ingest_tests_dir`: 检查 `skill/wiki-ingest/tests/` 不存在（预期失败）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 创建 `skill/wiki-ingest/tests/fixtures/url-source/`（含输入 URL 描述和预期页面）
- [x] **2.2** 创建 `skill/wiki-ingest/tests/fixtures/file-source/`（含输入文件描述和预期页面）

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 验证每个 fixture 是自包含的
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 5: wiki-distill tests/ 目录 + fixtures

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_skill_tests_dir.py` 中编写测试：
  - `test_wiki_distill_tests_dir`: 检查 `skill/wiki-distill/tests/` 不存在（预期失败）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 创建 `skill/wiki-distill/tests/fixtures/go-project/`（迷你 Go 项目，含 main.go、go.mod）
- [x] **2.2** 创建 `skill/wiki-distill/tests/fixtures/python-project/`（迷你 Python 项目，含 main.py）

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 验证每个 fixture 是自包含的
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 6: composes 依赖声明

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_composes_declaration.py` 中编写测试：
  - `test_wiki_distill_composes`: 检查 frontmatter 无 composes 字段（预期失败）
  - `test_wiki_update_composes`: 检查 frontmatter 无 composes 字段（预期失败）
  - `test_independent_skills_no_composes`: 检查独立技能无 composes（预期通过）

- [x] **1.2** 运行测试确认 FAILS（前两个）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-distill/SKILL.md` frontmatter 中增加 `composes: [wiki-ingest, wiki-lint]`
- [x] **2.2** 在 `skill/wiki-update/SKILL.md` frontmatter 中增加 `composes: [wiki-ingest, wiki-lint, wiki-init]`

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 验证 composes 值对应的技能目录都存在
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 7: wiki-ingest 自我纠错步骤

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_self_correction.py` 中编写测试：
  - `test_wiki_ingest_has_verify_step`: 检查 SKILL.md 正文中不含"重读"或"重新读取"关键词（预期失败）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-ingest/SKILL.md` 步骤 6（写入页面）之后新增步骤 6.1（验证写入）：
  - 重新读取刚写入的页面文件
  - 检查 frontmatter 是否包含所有必填字段
  - 检查 [[交叉引用]] 是否指向存在的页面
  - 若验证失败，报告错误并建议修复

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查验证步骤包含条件分支（"若...则..."）
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 8: wiki-lint 自我纠错步骤

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_self_correction.py` 中编写测试：
  - `test_wiki_lint_has_verify_step`: 检查 SKILL.md 正文中不含"所有页面"或"页面数"关键词（预期失败）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-lint/SKILL.md` 步骤 2（运行检查）之后新增步骤 2.1（验证输出完整性）：
  - 检查是否所有页面都被扫描
  - 检查 Red Errors 是否都有对应的修复建议
  - 检查 Yellow Warnings 是否都有对应的说明

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查验证步骤包含条件分支
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 9: validate_wiki.py 验证脚本

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_validate_wiki_script.py` 中编写测试：
  - `test_script_exists`: 检查 `skill/wiki-lint/scripts/validate_wiki.py` 不存在（预期失败）
  - `test_script_no_external_deps`: 跳过（文件不存在）

- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 创建 `skill/wiki-lint/scripts/validate_wiki.py`：
  - 接受 `wiki_root` 位置参数
  - 检查 WIKI.md 必填字段（wiki_root、primary_language、secondary_language）
  - 检查 index.md 表格格式（表头、分隔行、数据行）
  - 检查 [[交叉引用]] 可达性
  - 输出 JSON 格式结果（checks 数组，每个含 name/status/message）
  - 全部通过 → exit 0，有失败 → exit 1
  - 仅使用 Python 标准库

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 对 healthy-wiki fixture 运行脚本，确认全部通过
- [x] **3.2** 对 broken-links fixture 运行脚本，确认检测到断链
- [x] **3.3** 对 missing-scope fixture 运行脚本，确认检测到缺 scope
- [x] **3.4** 运行所有测试确认通过

---

## Behavior 10: 硬链接同步 + description 验证

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_hardlink_sync.py` 中编写测试：
  - `test_wiki_update_references_synced`: 检查 `skill/wiki-update/wiki-lint/references/` 的 inode 是否与源一致
  - `test_wiki_update_tests_synced`: 检查 `skill/wiki-update/wiki-lint/tests/` 的 inode 是否与源一致

- [x] **1.2** 运行测试确认 FAILS（新增文件未同步）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 为 wiki-update 下新增的 references/、tests/、scripts/ 目录创建硬链接
- [x] **2.2** 验证所有 SKILL.md 的 `description` 字段仍准确描述「做什么」+「何时用」

- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查是否有遗漏的硬链接
- [x] **3.2** 运行所有测试确认通过

---

## Verification

完成所有 behavior 后：

- [x] 运行完整测试套件：`python -m pytest tests/ -v`
- [x] 所有测试通过
- [x] 实现匹配所有 10 条验收标准
- [x] 无实现细节泄露到测试中

## Test Quality Checklist

- [x] 测试描述 BEHAVIOR，不描述实现
- [x] 测试使用 PUBLIC 接口（文件系统、YAML 解析、脚本执行）
- [x] 测试可经受内部重构
- [x] 测试名称描述 WHAT，不描述 HOW
- [x] 每个测试一个逻辑断言
- [x] 不 mock 内部协作者
