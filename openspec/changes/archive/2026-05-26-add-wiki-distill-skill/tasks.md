# Tasks: add-wiki-distill-skill

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

## Behavior 1: SKILL.md 资产合规性与 Pre-condition 一致性 (REQ-1, REQ-2)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_static.py` 中编写测试：验证 `skill/wiki-distill/SKILL.md` 存在
- [x] **1.2** 编写测试：验证 SKILL.md 不引用 `openspec/`、根目录 `README.md`、`assets/` 等禁止路径
- [x] **1.3** 编写测试：提取 SKILL.md 的 Pre-condition 节，与 `wiki-ingest` 的 Pre-condition 节逐句比对，验证发现顺序一致
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 创建 `skill/wiki-distill/SKILL.md`（含 frontmatter、Pre-condition、三步流程描述）
- [x] **2.2** Pre-condition 节严格遵循：显式 config-dir → `~/wiki/.wiki-config` → 工作目录向上搜索 → 报错
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保 SKILL.md 不包含冗余或与 spec 不一致的描述
- [x] **3.2** 运行所有静态测试确认通过

---

## Behavior 2: 分析阶段生成结构化经验报告 (REQ-3, REQ-13)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_analyze.py` 中编写测试：提供 fixture 代码库，执行分析 → 断言 `raw/distill-<project>.md` 存在
- [x] **1.2** 编写测试：验证 frontmatter 包含 `project`、`distilled_at`、`depth`、`categories`、`mode`、`dynamic_categories` 字段
- [x] **1.3** 编写测试：验证报告按默认分类组织（设计原则、代码模式、错误处理、测试策略、架构决策、安全实践）
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 1 (ANALYZE) 中详细描述分析流程：扫描文件 → 识别模式 → 提取经验 → 生成报告
- [x] **2.2** 定义经验报告的 YAML frontmatter 结构和 Markdown 分类格式
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保报告模板清晰、可解析
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 3: 脱敏过滤强制执行 (REQ-4)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_analyze.py` 中编写测试：构造含姓名、邮箱、手机号、token、内网 IP、加密算法的 fixture 代码库
- [x] **1.2** 编写测试：验证生成的报告中不包含上述敏感字段
- [x] **1.3** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 1 (ANALYZE) 中添加脱敏过滤规则：明确列出必须过滤的敏感信息类别和正则模式
- [x] **2.2** 明确说明脱敏策略：匹配内容替换为 `<redacted>` 标注
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认脱敏规则覆盖所有 spec 中定义的敏感类别
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 4: 比对阶段三分类 (REQ-5)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_compare.py` 中编写测试：提供经验报告 fixture + wiki fixture（含预设计的 NEW/CONFLICT/EXISTS 模式）
- [x] **1.2** 编写测试：验证比对输出中每条经验被正确归类为 NEW、CONFLICT 或 EXISTS
- [x] **1.3** 编写测试：验证匹配粒度为声明级（具体观点的语义比对）
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 2 (COMPARE) 中描述比对流程：逐条经验 → 读取 wiki index → 搜索相关页面 → 声明级比对 → 三分类
- [x] **2.2** 定义三分类的判定标准：
  - NEW: wiki 中无对应页面或对应页面不涉及该声明
  - CONFLICT: wiki 中有对应声明但内容矛盾
  - EXISTS: wiki 中有完全一致的声明
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保比对流程的描述足够精确，使 Agent 能一致地执行分类
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 5: NEW 条目委托 wiki-ingest (REQ-6)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_merge.py` 中编写测试：提供 NEW 条目 fixture，模拟用户确认
- [x] **1.2** 编写测试：验证 `wiki/pages/<slug>.md` 被创建（一条经验 → 一个 wiki page）
- [x] **1.3** 编写测试：验证 `wiki/index.md` 和 `wiki/log.md` 被更新
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 3 (DECIDE & MERGE) 中描述 NEW 条目处理流程：逐条展示 → 用户确认 → 委托 wiki-ingest
- [x] **2.2** 明确 slug 生成规则：经验标题的 slugify（小写、连字符、无特殊字符）
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保流程描述清晰，与 wiki-ingest 的接口约定明确
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 6: CONFLICT 条目委托 wiki-update 合并 (REQ-7)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_merge.py` 中编写测试：提供 CONFLICT 条目 fixture（当前 wiki 内容 vs 经验内容）
- [x] **1.2** 编写测试：验证用户可见输出包含 diff 展示（当前 vs 经验）
- [x] **1.3** 编写测试：验证合并后页面融合了经验和 wiki 内容，并标注来源
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 3 (DECIDE & MERGE) 中描述 CONFLICT 条目处理流程：展示 diff → 给出合并建议（策略C）→ 用户确认 → 委托 wiki-update
- [x] **2.2** 定义策略C的具体行为：融合两者内容，标注"经验来源"和"wiki 来源"
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保合并建议的展示格式清晰可读
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 7: EXISTS 条目记录日志不写页面 (REQ-8)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_merge.py` 中编写测试：提供 EXISTS 条目 fixture
- [x] **1.2** 编写测试：验证无新 wiki 页面创建，无现有页面修改
- [x] **1.3** 编写测试：验证 `wiki/log.md` 中包含 `distill` 类型日志条目，记录了 EXISTS 条目信息
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 3 (DECIDE & MERGE) 中描述 EXISTS 条目处理流程：告知用户已覆盖 → 追加 log.md distill 记录
- [x] **2.2** 定义 distill 日志格式：`## [<today>] distill | <project> | EXISTS: <条目数>`
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保日志格式与 wiki-ingest 和 wiki-update 的日志格式一致
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 8: 合并完成后委托 wiki-lint (REQ-9)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_e2e.py` 中编写测试：提供合并完成的 wiki fixture
- [x] **1.2** 编写测试：验证调用了 wiki-lint 流程
- [x] **1.3** 编写测试：验证 `concepts/lint-<today>.md` 存在
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 3 (DECIDE & MERGE) 末尾添加收尾步骤：委托 wiki-lint 执行健康检查
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认 wiki-lint 的调用方式与 spec 中描述一致
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 9: 增量蒸馏支持 (REQ-10)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_analyze.py` 中编写测试：首次蒸馏 → 修改部分文件 → 再次蒸馏（无 --full）
- [x] **1.2** 编写测试：验证第二次蒸馏仅分析变更文件
- [x] **1.3** 编写测试：验证报告 frontmatter 中 `mode` 为 `incremental`
- [x] **1.4** 编写测试：使用 `--full` 参数，验证全量分析，`mode` 为 `full`
- [x] **1.5** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 1 (ANALYZE) 中描述增量蒸馏逻辑：读取上次状态 → git diff 检测变更 → 仅分析变更文件
- [x] **2.2** 定义状态文件 `raw/.distill-<project>-state` 的格式（记录上次 HEAD commit）
- [x] **2.3** 描述 `--full` 参数行为：忽略状态文件，全量分析
- [x] **2.4** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 处理无 git 仓库或首次提交的边界情况
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 10: 深度控制和路径指定 (REQ-11)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_analyze.py` 中编写测试：指定 `--depth shallow`，验证仅分析 README、配置文件、顶层结构
- [x] **1.2** 编写测试：指定 `--depth medium`（默认），验证分析关键模块的代码组织和接口
- [x] **1.3** 编写测试：指定 `--depth deep`，验证分析具体实现细节
- [x] **1.4** 编写测试：指定 `--project /path/to/other/repo`，验证分析指定路径
- [x] **1.5** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 1 (ANALYZE) 中定义三种深度的分析范围：
  - shallow: README、配置文件、顶层目录结构
  - medium: 关键模块代码组织、接口设计
  - deep: 具体实现细节、算法选择
- [x] **2.2** 描述 `--project` 参数：接受绝对路径，默认当前仓库
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 处理指定路径不存在或无权限的边界情况
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 11: AI 动态分类发现 (REQ-12)

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_analyze.py` 中编写测试：提供包含独特模式（如国际化策略、特定日志规范）的 fixture
- [x] **1.2** 编写测试：验证报告包含 AI 动态添加的分类
- [x] **1.3** 编写测试：验证动态分类在 frontmatter 的 `dynamic_categories` 中标注
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 SKILL.md 的 Phase 1 (ANALYZE) 中描述：在默认 6 个分类之外，AI 可在分析过程中动态发现新分类
- [x] **2.2** 要求动态分类在报告中标注来源为 `dynamic`
- [x] **2.3** 处理动态分类与默认分类名称冲突的情况：合并为同一分类
- [x] **2.4** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保动态分类的描述足够灵活，不限制 AI 的发现能力
- [x] **3.2** 运行所有测试确认通过

---

## Behavior 12: Agent Smoke E2E 端到端验证

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_wiki_distill_e2e.py` 中编写真实 Agent 交互测试：完整蒸馏流程（分析 → 比对 → 合并 → lint）
- [x] **1.2** 编写测试：验证 NEW 条目最终写入 wiki
- [x] **1.3** 编写测试：验证 CONFLICT 条目最终合并到 wiki
- [x] **1.4** 编写测试：验证 `wiki/log.md` 包含完整的 distill 操作记录
- [x] **1.5** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 确保 SKILL.md 流程描述完整、可被 Agent 正确执行
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 审查 SKILL.md 的措辞是否与 Agent 的实际行为一致
- [x] **3.2** 运行所有测试确认通过

---

## Verification

完成所有 behavior 后：

- [x] 运行完整测试套件：`python3 -m unittest discover tests/ -v`
- [x] 所有测试通过（wiki-distill 相关 76 tests，预存问题 1 test 除外）
- [x] 实现与 acceptance criteria 匹配（proposal.md 中 12 条 AC）
- [x] SKILL.md 内容与 spec.md 中 13 条 REQ 一致

## Test Quality Checklist

- [x] 测试描述 BEHAVIOR（行为），而非 implementation（实现）
- [x] 测试通过 PUBLIC interfaces（SKILL.md 描述的流程、文件系统输出）
- [x] 测试可在内部重构后仍然存活
- [x] 测试命名描述 WHAT（什么），而非 HOW（怎么实现）
- [x] 每个测试聚焦一个逻辑断言
- [x] 不 mock 内部协作者（wiki-ingest/wiki-update 在 E2E 中真实调用）
