# Tasks: add-scope-metadata

## TDD Workflow: RED → GREEN → REFACTOR

**CRITICAL: This workflow uses VERTICAL SLICES**

本变更的"测试"主要是对 SKILL.md 和模板文件的**静态内容验证**（正则匹配、语义匹配），辅以真实 agent smoke 测试。

```
WRONG (horizontal slicing - DO NOT USE):
  RED:   所有测试
  GREEN: 所有实现

RIGHT (vertical slices - USE THIS):
  RED→GREEN→REFACTOR: 一个行为 → 下一个行为
```

---

## Behavior 1: Page Frontmatter 模板新增 scope 字段

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试 `tests/run_scope_tests.py::Behavior 1`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-ingest/SKILL.md` 步骤 6 的页面模板
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** wiki-update 无引用旧页面模板格式，无需同步
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 2: scope_level 枚举校验规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-lint/SKILL.md` 步骤 2 Yellow Warnings 节
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 规则描述位置与现有语言规则风格一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 3: scope_code slug 格式校验规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-lint/SKILL.md` 步骤 2 Yellow Warnings 节
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要，直接继续

---

## Behavior 4: scope_level 与 scope_code 一致性校验规则

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-lint/SKILL.md` 步骤 2 Yellow Warnings 节
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要，直接继续

---

## Behavior 5: scope 字段缺失警告规则（向后兼容）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-lint/SKILL.md` 步骤 2 Yellow Warnings 节
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 运行全部 lint 相关测试确认通过

---

## Behavior 6: wiki-ingest 步骤 3 scope 确认交互

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-ingest/SKILL.md` 步骤 3
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** scope 确认交互与现有 key takeaways 确认交互风格一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 7: wiki-ingest 步骤 9 category_3 自动维护

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-ingest/SKILL.md` 步骤 9
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** category_3 更新描述与 category_1 描述风格一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 8: wiki-distill Phase 3 scope 推断和传递

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 编写静态测试
- [x] **1.3** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-distill/SKILL.md` Phase 3.1
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** distill scope 交互与现有决策交互风格一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 9: index.md 模板 category_3 列名正式化

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-init/templates/index.md` category_3 区域
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 列名与 category_1 的 "最后更新" 一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 10: wiki-query 利用 scope 辅助检索

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-query/SKILL.md` 步骤 1
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 无重构需要，直接继续

---

## Behavior 11: wiki-update scope 变更时同步 category_3

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-update/SKILL.md` 步骤 5
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 与 wiki-ingest 步骤 9 的 category_3 维护逻辑一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 12: scope_level 中文映射表统一定义

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写静态测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-ingest/SKILL.md` 步骤 3，新增中文映射表
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** distill 内联使用相同映射
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 13: 运行时 wiki/index.md category_3 实际填充

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写 smoke 测试
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新运行时 `wiki/index.md`，添加 category_3 区域
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** category_3 格式与 design.md 中的聚合格式一致
- [x] **3.2** 运行全部测试确认通过

---

## Verification

完成所有 behavior 后：

- [x] 运行完整静态测试套件：21/21 通过
- [x] 所有 6 个 SKILL.md 和 2 个模板文件的 scope 相关内容已验证
- [x] 所有 14 条 Acceptance Criteria 已覆盖
- [x] 与 `bilingual-wiki-config` 和 `wiki-lint-language-rules` 无冲突

## Test Quality Checklist

- [x] 测试描述行为（BEHAVIOR），非实现细节
- [x] 测试通过 SKILL.md 的公开文本接口验证
- [x] 测试能经受 SKILL.md 内部格式调整（语义匹配而非行号匹配）
- [x] 一个逻辑断言对应一个测试方法
