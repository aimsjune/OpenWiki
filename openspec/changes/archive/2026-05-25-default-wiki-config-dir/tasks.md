# Tasks: default-wiki-config-dir

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

## Behavior 1: 四个 wiki workflow 的发现顺序包含默认配置目录

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_runtime_resolution.py` 中新增 `test_wiki_workflows_include_default_config_dir_in_discovery_order`
  - 对 `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update` 四个 skill 的 `SKILL.md` 进行静态文本断言
  - 断言每个文件的 Pre-condition 节包含 `~/wiki/.wiki-config`
  - 断言默认目录在"向上搜索工作目录"之前被描述
  - 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新 `skill/wiki-query/SKILL.md` Pre-condition 节，加入 `~/wiki/.wiki-config` 发现步骤
- [x] **2.2** 更新 `skill/wiki-ingest/SKILL.md` Pre-condition 节，加入 `~/wiki/.wiki-config` 发现步骤
- [x] **2.3** 更新 `skill/wiki-lint/SKILL.md` Pre-condition 节，加入 `~/wiki/.wiki-config` 发现步骤
- [x] **2.4** 更新 `skill/wiki-update/SKILL.md` Pre-condition 节，加入 `~/wiki/.wiki-config` 发现步骤
- [x] **2.5** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保四个 Pre-condition 节文本一致（除 skill 特定差异外）
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 2: 默认配置目录被命中时输出明确提示

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_runtime_resolution.py` 中新增 `test_default_config_dir_usage_is_communicated_to_user`
  - 对四个 workflow 的 `SKILL.md` 进行静态文本断言
  - 断言每个文件包含"使用默认配置时告知用户"的语义（如 "default wiki config" 或 `~/wiki/.wiki-config` 路径提示）
  - 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-query/SKILL.md` Pre-condition 节追加默认配置命中时的提示说明
- [x] **2.2** 在 `skill/wiki-ingest/SKILL.md` Pre-condition 节追加默认配置命中时的提示说明
- [x] **2.3** 在 `skill/wiki-lint/SKILL.md` Pre-condition 节追加默认配置命中时的提示说明
- [x] **2.4** 在 `skill/wiki-update/SKILL.md` Pre-condition 节追加默认配置命中时的提示说明
- [x] **2.5** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 统一四个文件的提示措辞
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 3: wiki-init 在无 config-dir 时推荐默认目录

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_runtime_resolution.py` 中新增 `test_wiki_init_recommends_default_config_dir`
  - 读取 `skill/wiki-init/SKILL.md`
  - 断言其中包含 `~/wiki/.wiki-config` 作为默认推荐的描述
  - 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新 `skill/wiki-init/SKILL.md` Process 节，在用户未指定 `config-dir` 时推荐 `~/wiki/.wiki-config` 作为默认路径
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保新增内容与现有 `wiki-init` 的复用路径逻辑不冲突
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 4: 文档说明默认配置目录

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_documentation_layout.py` 中新增 `test_readme_mentions_default_config_dir`
  - 对 `README.md`、`README.en.md`、`README.ja.md` 进行静态文本断言
  - 断言每个文件提及 `~/wiki/.wiki-config`
  - 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新 `README.md`，在 wiki workflow 使用说明中加入默认配置目录描述
- [x] **2.2** 更新 `README.en.md`，加入默认配置目录描述
- [x] **2.3** 更新 `README.ja.md`，加入默认配置目录描述
- [x] **2.4** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保三语言版本措辞一致
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 5: 真实 agent smoke E2E 覆盖默认目录命中与回退

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_agent_skill_smoke_e2e.py` 中新增 `test_wiki_query_uses_default_config_dir`
  - 在临时目录创建 fixture `~/wiki/.wiki-config/WIKI.md`（模拟），不传 `config-dir` 调用 `wiki-query`
  - 验证 agent 输出包含默认配置路径提示
  - 运行测试确认 FAILS（需要 `SKILL_AGENT_E2E=1`）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 此 behavior 的"实现"是前面四个 behavior 的 SKILL.md 更新，本阶段验证 agent 行为与文本一致
- [x] **2.2** 运行测试确认 PASSES（需要 `SKILL_AGENT_E2E=1`）

### Phase 3: REFACTOR - Improve

- [x] **3.1** 清理 fixture，确保不污染真实 `~/.wiki-config`
- [x] **3.2** 运行所有测试确认通过

---

## Verification

- [x] 运行完整测试套件：`python3 -m unittest tests.test_wiki_runtime_resolution tests.test_documentation_layout tests.test_agent_skill_smoke_e2e -v`
- [x] 所有测试通过
- [x] 实现与 acceptance criteria 匹配
- [x] 测试只通过公共接口（SKILL.md 文本、agent 行为输出）

## Test Quality Checklist

- [x] 测试描述行为而非实现
- [x] 测试仅使用公共接口
- [x] 测试能在内部重构后继续存活
- [x] 测试名称描述 WHAT 而非 HOW
- [x] 每个测试一个逻辑断言
- [x] 不 mock 内部协作者
