# Tasks: standard-wiki

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

## Behavior 1: `wiki-init` 生成 `WIKI.md` 并支持分离的 `config-dir` / `wiki-root`

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/wiki-init/standard-wiki-runtime.test.*` 编写失败用例
  - 通过公开初始化入口驱动 `wiki-init`
  - 断言 `<config-dir>/WIKI.md` 被创建
  - 断言 `WIKI.md` 中记录绝对路径 `wiki_root`
  - 断言 `raw/`、`wiki/`、`wiki/index.md`、`wiki/log.md`、`wiki/pages/`、`concepts/` 创建在 `wiki-root`

- [x] **1.2** 运行该测试并确认它 FAILS
  - 预期失败原因：当前初始化流程仍依赖旧布局或未生成 `WIKI.md`

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 最小实现 `wiki-init` 的新初始化行为
  - 询问并接收独立的 `config-dir` 与 `wiki-root`
  - 在 `config-dir` 写入 `WIKI.md`
  - 在 `wiki-root` 创建 wiki 数据目录和初始文件

- [x] **2.2** 再次运行初始化测试并确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 抽取初始化中的路径校验、配置写入、目录规划逻辑
  - 减少重复
  - 提升错误信息可读性

- [x] **3.2** 运行相关测试，确认重构后仍全部通过

---

## Behavior 2: wiki 工作流通过 `WIKI.md` 解析运行时上下文

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/wiki-skills/wiki-runtime-resolution.test.*` 编写失败用例
  - 构造仅包含 `skill/` 和 `<config-dir>/WIKI.md` 的测试夹具
  - 覆盖 `wiki-ingest`、`wiki-query`、`wiki-lint`、`wiki-update` 的前置解析
  - 断言它们不再要求 `CLAUDE.md`、`.claude/skills/`、`.agents/skills/`

- [x] **1.2** 运行该测试并确认它 FAILS
  - 预期失败原因：当前 pre-condition 仍查找旧入口文件或旧目录

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 最小实现共享运行时解析逻辑
  - 从 `WIKI.md` 读取并校验绝对路径 `wiki_root`
  - 归一化返回 `raw/`、`wiki/`、`wiki/pages/`、`wiki/index.md`、`wiki/log.md`、`concepts/` 路径
  - 让各 wiki workflow 只依赖该解析结果

- [x] **2.2** 再次运行运行时解析测试并确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 合并重复的前置检查逻辑
  - 统一错误文案
  - 保持单一入口解析

- [x] **3.2** 运行所有相关测试，确认无回归

---

## Behavior 3: 仓库只通过 `skill/` 暴露公开技能

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/repo-layout/skill-layout.test.*` 编写失败用例
  - 断言 `skill/` 下存在 `wiki-init`、`wiki-ingest`、`wiki-query`、`wiki-lint`、`wiki-update`、`agent-browser`
  - 断言公开运行时规范不再依赖 `.claude/skills/` 与 `.agents/skills/`

- [x] **1.2** 运行该测试并确认它 FAILS
  - 预期失败原因：当前 canonical skill 仍在 `.claude/skills/`

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 最小实现 skill 目录迁移
  - 将所有公开 wiki skill 与 `agent-browser` 迁移到 `skill/`
  - 删除旧兼容层目录及其 source-of-truth 叙事

- [x] **2.2** 再次运行 skill 布局测试并确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 清理迁移后的仓库结构与引用
  - 修正残留路径引用
  - 统一 skill 名称与说明

- [x] **3.2** 运行全部相关测试，确认结构迁移未破坏行为

---

## Behavior 4: 文档与初始化说明统一为中立 `WIKI.md` 架构

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写文档验证或 golden-check 用例
  - 检查 `README.md`、`README.en.md`、`README.ja.md`
  - 断言文档声明 `WIKI.md` 为 canonical runtime contract
  - 断言文档说明 `config-dir` 与 `wiki-root` 可分离
  - 断言文档声明 `skill/` 为唯一公开 skill 目录

- [x] **1.2** 运行该验证并确认它 FAILS
  - 预期失败原因：当前文档仍以 `CLAUDE.md` 和 `.claude/skills/` 为中心

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 最小修改文档与模板
  - 更新 README 系列中的架构、安装、初始化与技能说明
  - 更新 `wiki-init` 产物模板，使其生成 `WIKI.md` 而不是 `CLAUDE.md` / `AGENTS.md`

- [x] **2.2** 再次运行文档验证并确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 统一中英文日文文档中的术语和目录图
  - 避免中立术语与旧 agent 叙事混用

- [x] **3.2** 运行全部验证，确认文档与行为一致

---

## Verification

After completing all behaviors:

- [x] 运行完整测试集
- [x] 所有测试通过
- [x] 实现满足 `proposal.md` 与 `specs/standard-wiki-runtime/spec.md`
- [x] 运行时不再依赖 `CLAUDE.md`、`.claude/skills/`、`.agents/skills/`
- [x] `WIKI.md` 中始终记录绝对 `wiki_root`

## Test Quality Checklist

- [x] 测试描述行为，而不是实现细节
- [x] 测试仅通过公开入口验证
- [x] 内部重构后测试仍应稳定
- [x] 测试名称表达 WHAT，而不是 HOW
- [x] 每个测试聚焦一个清晰行为
- [x] 不 mock 内部协作者，只替换外部依赖
