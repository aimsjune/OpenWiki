# Tasks: fix-date-placeholders

## TDD Workflow: RED → GREEN → REFACTOR

**CRITICAL: This workflow uses VERTICAL SLICES**

本变更全部为静态文本修改，测试通过文本内容验证。

---

## Behavior 1: wiki/index.md category_2 列名统一

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试，验证 `wiki/index.md` category_2 表格头为 `| 页面 | 类型 | 最后更新 |`
- [x] **1.2** 运行测试确认 FAILS（当前为"日期"）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `wiki/index.md` category_2 列名 "日期" → "最后更新"
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认与 category_1 列名一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 2: 模板 index.md category_2 列名统一

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试，验证 `skill/wiki-init/templates/index.md` category_2 表格头
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改模板 category_2 列名 "日期" → "最后更新"
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 3: wiki-ingest SKILL.md 明确 `<today>` 替换规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试，验证 `skill/wiki-ingest/SKILL.md` 包含 "YYYY-MM-DD" 且上下文涉及 `<today>`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 Pre-condition 或首次 `<today>` 出现前添加说明
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 4: wiki-distill SKILL.md 明确 `<today>` 替换规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在首次 `<today>` 出现前添加说明
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 5: wiki-query SKILL.md 明确 `<today>` 替换规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在首次 `<today>` 出现前添加说明
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 6: wiki-lint SKILL.md 明确 `<today>` 替换规则 + 新增 hardcoded 规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试，验证包含 `<today>` 替换说明
- [x] **1.2** 编写静态测试，验证 Blue Info 包含 `hardcoded-or-literal-today`
- [x] **1.3** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在首次 `<today>` 出现前添加说明
- [x] **2.2** 在 Blue Info 节新增 `hardcoded-or-literal-today` 规则
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 7: wiki-init/templates/log.md 明确 `<today>` 替换规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试，验证模板包含 YYYY-MM-DD 格式说明
- [x] **1.2** 运行测试确认 FAILS（log.md 已有 YYYY-MM-DD，此 behavior 跳过）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** log.md 模板已包含 YYYY-MM-DD 格式说明，无需修改
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 8: 检查 wiki-update SKILL.md 是否需要 `<today>` 说明

### Phase 1: RED - Write Failing Test

- [x] **1.1** 检查 `skill/wiki-update/SKILL.md` — 不使用 `<today>`，无需测试
- [x] **1.2** 无需实施

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 无需修改
- [x] **2.2** 无需测试

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要
- [x] **3.2** 无需测试

---

## Verification

完成所有 behavior 后：

- [x] 运行完整静态测试套件：8/8 通过
- [x] 所有 8 条 Acceptance Criteria 已覆盖
- [x] 所有使用 `<today>` 的文件均已添加替换规则说明

## Test Quality Checklist

- [x] 测试描述行为（BEHAVIOR），非实现细节
- [x] 测试通过文本内容验证
- [x] 一个逻辑断言对应一个测试方法
