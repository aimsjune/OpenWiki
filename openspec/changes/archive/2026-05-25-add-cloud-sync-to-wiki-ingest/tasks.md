# Tasks: add-cloud-sync-to-wiki-ingest

## TDD Workflow: RED → GREEN → REFACTOR

本变更是文档级变更（SKILL.md + WIKI.md + 模板），"实现"即修改这些文档内容。RED 阶段编写静态分析测试验证文档缺失/不正确的行为，GREEN 阶段修改文档使测试通过。

---

## Behavior 1: `WIKI.md` 模板包含 sync 字段默认值

### Phase 1: RED - Write Failing Test

- [x] **1.1** 新增测试 `tests/test_cloud_sync_static.py`，写入 `test_wiki_md_template_contains_sync_fields`
- [x] **1.2** 运行测试确认 FAILS（当前模板不含 sync 字段）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-init/templates/WIKI.md`，在 frontmatter 中新增 `remote_sync_path: wiki` 和 `auto_sync: false`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认模板 frontmatter 字段顺序合理
- [x] **3.2** 运行全部已有测试确认无回归

---

## Behavior 2: 运行时 `WIKI.md` 包含 sync 字段

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_cloud_sync_static.py` 中新增 `test_wiki_md_runtime_contains_sync_fields`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改运行时 `WIKI.md`，在 frontmatter 中新增 `remote_sync_path: wiki` 和 `auto_sync: false`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认与模板字段顺序一致
- [x] **3.2** 运行全部已有测试确认无回归

---

## Behavior 3: `wiki-ingest` pre-condition 声明 sync 字段解析

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_cloud_sync_static.py` 中新增 `test_wiki_ingest_precondition_declares_sync_fields`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-ingest/SKILL.md` 的 Pre-condition 节，新增 `remote_sync_path` 和 `auto_sync`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认字段声明格式与已有字段保持一致
- [x] **3.2** 运行全部已有测试确认无回归

---

## Behavior 4: `wiki-ingest` 包含步骤 12 "Cloud Sync"

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_cloud_sync_static.py` 中新增 `test_wiki_ingest_has_step_12_cloud_sync`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `skill/wiki-ingest/SKILL.md` 步骤 11 之后新增步骤 12 "Cloud Sync"
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查步骤 12 的语言风格与已有步骤 1-11 一致
- [x] **3.2** 运行全部已有测试确认无回归

---

## Behavior 5: `wiki-init` 复用已有配置时 sync 字段参与提问裁剪

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_cloud_sync_static.py` 中新增 `test_wiki_init_reuse_crops_sync_fields`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修改 `skill/wiki-init/SKILL.md`，在提问裁剪列表中新增 `remote_sync_path`、`auto_sync`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认提问裁剪描述与 REQ-7 的已有表述一致
- [x] **3.2** 运行全部已有测试确认无回归

---

## Behavior 6: `wiki-ingest` sync 步骤的非阻塞语义

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_cloud_sync_static.py` 中新增 `test_wiki_ingest_sync_non_blocking`
- [x] **1.2** 运行测试确认 FAILS（在 Behavior 4 写入步骤 12 之前）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** Behavior 4 中写入的步骤 12 已包含非阻塞声明
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认非阻塞声明覆盖：pcloud 未安装、pcloud 未配置、sync 执行失败三种场景
- [x] **3.2** 运行全部已有测试确认无回归

---

## 最终验证

- [x] 运行完整测试套件：`python3 -m unittest tests.test_cloud_sync_static tests.test_standard_wiki_init_runtime tests.test_wiki_runtime_resolution tests.test_wiki_skill_workflow_e2e tests.test_skill_layout -v` — 25 测试全部通过
- [x] 所有测试通过（包括新增的 cloud sync 静态测试和已有测试）
- [x] 实现与 acceptance criteria 全部匹配
- [x] 将 delta spec 同步到主 spec `openspec/specs/standard-wiki-runtime/spec.md`
- [x] 运行 `openspec status --change "add-cloud-sync-to-wiki-ingest"` 确认全部 artifacts 完成

## Test Quality Checklist

- [x] 测试描述 BEHAVIOR 而非实现细节
- [x] 测试通过公开接口（文件内容）验证
- [x] 测试名称描述 WHAT 而非 HOW
- [x] 每个测试一个逻辑断言
- [x] 无 mock 内部实现细节
