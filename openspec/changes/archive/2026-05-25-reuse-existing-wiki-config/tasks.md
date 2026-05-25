# Tasks: reuse-existing-wiki-config

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

## Behavior 1: 显式已有 config-dir 进入复用路径

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_standard_wiki_init_runtime.py` 中新增失败用例
  - 行为描述：用户在 `wiki-init` 中显式提供一个已有且有效的 `config-dir` 时，流程会复用现有 `WIKI.md`
  - 仅通过公共 skill 入口和可观察文件系统结果断言
  - 位置：`tests/test_standard_wiki_init_runtime.py`

- [x] **1.2** 运行该测试并确认它先失败
  - 预期：当前实现未定义 continue 快速路径或未完整暴露该行为
  - 不期望：测试直接通过

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-init/SKILL.md` 中补全“显式已有 `config-dir`”的 continue/复用语义
  - 仅添加使当前测试通过所需的最小行为说明
  - 明确读取现有 `WIKI.md`，而不是默认重写

- [x] **2.2** 重新运行目标测试并确认通过
  - 预期：测试通过，且 `WIKI.md` 未被覆盖

### Phase 3: REFACTOR - Improve

- [x] **3.1** 清理与现有 pre-flight / process 描述重复或冲突的文案
  - 合并“已有实例 continue”与“新建初始化”两条路径的说明
  - 保持 `wiki-init` 的职责边界清晰

- [x] **3.2** 运行相关测试确保无回归
  - 至少运行 `tests/test_standard_wiki_init_runtime.py`

---

## Behavior 2: 复用路径跳过已知初始化问题

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_agent_skill_smoke_e2e.py` 或可替代的交互测试中新增失败用例
  - 行为描述：复用路径不会再次要求输入 `wiki_root`、`domain`、`source_types`、`index_categories`
  - 优先验证用户可见提示与交互轨迹，而不是内部条件分支
  - 位置：`tests/test_agent_skill_smoke_e2e.py`

- [x] **1.2** 运行目标测试并确认失败
  - 预期：当前文案或交互仍会重复采集已知字段

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-init/SKILL.md` 中增加“提问裁剪”规则
  - 明确复用模式下应跳过哪些字段
  - 若非关键字段缺失，仅补问缺失字段，不重复采集已存在字段

- [x] **2.2** 重新运行目标测试并确认通过
  - 预期：交互中不再重复要求输入已存在信息

### Phase 3: REFACTOR - Improve

- [x] **3.1** 对 `wiki-init` 的问题收集段落做结构化整理
  - 把“新建模式问题列表”和“复用模式跳过规则”拆清楚
  - 避免多个段落分别描述同一字段

- [x] **3.2** 运行相关测试确保无回归
  - 至少运行 `tests/test_standard_wiki_init_runtime.py` 与目标 smoke test

---

## Behavior 3: 复用成功后提供后续 workflow 指引

### Phase 1: RED - Write Failing Test

- [x] **1.1** 为成功复用场景新增失败用例
  - 行为描述：`wiki-init` 在复用成功后提示“已连接现有 wiki”，并建议使用同一 `config-dir` 继续运行 `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update`
  - 位置：`tests/test_standard_wiki_init_runtime.py` 或 `tests/test_documentation_layout.py`

- [x] **1.2** 运行目标测试并确认失败
  - 预期：当前确认文案没有完整覆盖后续 workflow 指引

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新 `skill/wiki-init/SKILL.md` 以及必要的 README 指南
  - 增加“已连接现有 wiki”的确认语义
  - 明确说明同一 `config-dir` 可直接用于 `wiki-query` 等 workflow

- [x] **2.2** 重新运行目标测试并确认通过
  - 预期：成功输出包含至少 `wiki-query` 的继续使用指引

### Phase 3: REFACTOR - Improve

- [x] **3.1** 对中英日 README 的相关说明保持语义一致
  - 保证“已有配置复用”与“后续 workflow 指引”在多语言文档中对齐

- [x] **3.2** 运行相关测试确保无回归
  - 至少运行 `tests/test_documentation_layout.py` 和受影响的 skill/runtime 测试

---

## Behavior 4: 损坏配置 fail-fast 且保持非破坏性

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_standard_wiki_init_runtime.py` 中新增损坏配置失败用例
  - 行为描述：当 `WIKI.md` 缺失 `wiki_root`、`wiki_root` 非绝对路径、或布局不完整时，`wiki-init` 报错并停止
  - 断言不改写原有 `WIKI.md`、不创建替代布局
  - 位置：`tests/test_standard_wiki_init_runtime.py`

- [x] **1.2** 运行目标测试并确认失败
  - 预期：当前规范未明确 fail-fast 与非破坏性要求

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-init/SKILL.md` 中补充损坏配置的错误分支说明
  - 明确列出 fail-fast 条件
  - 明确只有用户显式选择 `reinitialize` 才能进入覆盖式初始化

- [x] **2.2** 重新运行目标测试并确认通过
  - 预期：错误输出清晰，且文件系统保持不变

### Phase 3: REFACTOR - Improve

- [x] **3.1** 将 fail-fast 条件与现有运行时契约说明对齐
  - 保证与 `standard-wiki-runtime` 的 `WIKI.md` 约束不冲突
  - 收敛错误语义，减少模糊表述

- [x] **3.2** 运行相关测试确保无回归
  - 至少运行 `tests/test_standard_wiki_init_runtime.py`、`tests/test_wiki_runtime_resolution.py`

---

## Verification

After completing all behaviors:

- [x] 运行受影响测试集，例如：
  - `python3 -m unittest tests.test_standard_wiki_init_runtime -v`
  - `python3 -m unittest tests.test_documentation_layout -v`
  - 如启用真实 agent smoke，再运行 `python3 -m unittest tests.test_agent_skill_smoke_e2e -v`
- [x] 确认所有测试通过
- [x] 确认实现符合 proposal 和 spec 中的 acceptance criteria
- [x] 确认测试仍通过公共入口和可观察行为验证，而非绑定内部实现

## Test Quality Checklist

- [x] 测试描述的是行为，而不是实现细节
- [x] 测试仅通过公共 skill 入口、文档输出或文件系统结果断言
- [x] 即使后续内部重构，测试仍应稳定成立
- [x] 测试名称描述 WHAT，而不是 HOW
- [x] 每个测试聚焦一个清晰行为
- [x] 不 mock 内部协作者，只在边界上使用夹具和临时目录
