# Tasks: standardize-skill-private-assets

## TDD Workflow: RED → GREEN → REFACTOR

**CRITICAL: This workflow uses VERTICAL SLICES (tracer bullets)**

```text
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

## Behavior 1: 区分允许的 runtime 引用与禁止的仓库级依赖

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_skill_private_assets_boundary.py` 编写失败用例
  - 验证 `WIKI.md`、`raw/`、`wiki/`、`concepts/`、`wiki/index.md`、`wiki/log.md`、`wiki/pages/` 被视为允许的 runtime 引用
  - 验证根级 `README*`、根级 `assets/`、根级脚本、`openspec/` 被视为禁止的直接 skill 依赖
  - 仅通过公共 `skill/*/SKILL.md` 入口验证

- [x] **1.2** 运行测试并确认它 FAILS
  - 预期：在未实现校验规则前，测试失败且失败原因可解释

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 最小实现 skill 依赖边界校验与相应仓库规则
  - 为公共 wiki skill 建立允许/禁止引用分类
  - 不修改 wiki runtime 语义

- [x] **2.2** 运行测试并确认它 PASSES
  - 预期：公共 wiki skill 的边界校验通过

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取重复规则并统一命名
  - 合并允许 runtime 引用与禁止仓库级依赖的规则常量或校验辅助逻辑

- [x] **3.2** 运行相关测试，确认重构后仍通过
  - 预期：边界测试稳定通过

---

## Behavior 2: 约束 skill 私有资产必须位于 owning skill 目录下

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_skill_private_assets_boundary.py` 增加失败用例
  - 验证 skill 私有模板、示例、夹具、媒体、脚本若被引用，必须位于对应 `skill/<name>/`
  - 验证跨 skill 私有资产引用被视为违规

- [x] **1.2** 运行测试并确认它 FAILS
  - 预期：在未收敛私有资产布局前，测试失败

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 最小实现私有资产布局规范
  - 约束 `skill/<name>/` 为私有资产所有权边界
  - 如需要，迁移散落的 skill 私有资产到 owning skill 目录

- [x] **2.2** 运行测试并确认它 PASSES
  - 预期：skill 私有资产布局符合规范

### Phase 3: REFACTOR - Improve

- [x] **3.1** 清理多余路径假设与重复校验
  - 统一 skill 私有资产路径词汇与检查方式

- [x] **3.2** 运行全部边界相关测试
  - 预期：所有边界测试仍通过

---

## Behavior 3: 标准化 skill-local 目录词汇并在文档中说明边界

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_skill_private_assets_docs.py` 编写失败用例
  - 验证文档明确区分 runtime wiki 对象与 skill 私有资产
  - 验证 skill-local 目录词汇限定为 `templates/`、`examples/`、`fixtures/`、`assets/`、`scripts/`

- [x] **1.2** 运行测试并确认它 FAILS
  - 预期：在文档或约束未更新前，测试失败

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 最小修改 README 或 skill 布局说明文档
  - 写清允许依赖边界
  - 写清标准 skill-local 目录词汇

- [x] **2.2** 运行测试并确认它 PASSES
  - 预期：文档与布局规则一致

### Phase 3: REFACTOR - Improve

- [x] **3.1** 统一文档术语
  - 使用一致表述区分 runtime object、skill-private asset、repository-level asset

- [x] **3.2** 运行全部测试
  - 预期：回归测试全部通过

---

## Verification

After completing all behaviors:

- [x] 运行完整测试集
- [x] 所有测试通过
- [x] 实现满足 `proposal.md` 与 `specs/skill-private-assets-layout/spec.md`
- [x] 公共 wiki skill 不再直接依赖仓库级散落资产
- [x] runtime wiki 对象仍保持在 `skill/` 外部

## Test Quality Checklist

- [x] 测试描述行为，而不是实现细节
- [x] 测试仅通过公共入口验证
- [x] 内部重构后测试仍应稳定
- [x] 测试名称表达 WHAT，而不是 HOW
- [x] 每个测试聚焦一个清晰行为
- [x] 不 mock 内部协作者，只替换外部依赖
