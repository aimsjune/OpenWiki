# Specification: standard-wiki-runtime

## Purpose

Define the observable runtime behavior for a neutral wiki setup that follows `skill.io` conventions. This spec covers initialization inputs, reuse of an existing runtime contract, the `WIKI.md` runtime contract, separation between configuration and data locations, and the canonical skill layout used by wiki workflows.

## Requirements

### REQ-1: Initialization writes a neutral runtime contract

**Behavior**: `wiki-init` must collect a configuration directory and a wiki root directory as separate inputs, create `WIKI.md` in the configuration directory, and record the absolute `wiki_root` path in that file.

**Test Verification**: Run the initialization workflow through its public entrypoint with two explicit absolute paths. Assert that `WIKI.md` is created only in the configuration directory and that its frontmatter or configuration block contains the exact absolute wiki root path provided during initialization.

```
Given: an empty configuration directory and an empty wiki root directory at different absolute paths
When:  the user completes the `wiki-init` workflow with those two paths
Then:  `<config-dir>/WIKI.md` exists and records `wiki_root: <absolute wiki-root path>`
```

**Interfaces to Test Through**: `wiki-init` skill entry workflow and generated filesystem outputs

---

### REQ-2: Wiki data lives under wiki_root, not config-dir

**Behavior**: After initialization, the wiki data layout must be created under the configured `wiki_root`, including `raw/`, `wiki/`, `wiki/index.md`, `wiki/log.md`, `wiki/pages/`, and `concepts/`, regardless of where the configuration directory lives.

**Test Verification**: Run initialization with fully separated directories and inspect the filesystem. Verify that the required data directories and files are present under `wiki_root`, and that `config-dir` contains `WIKI.md` rather than duplicated wiki data directories.

```
Given: a configuration directory and a distinct wiki root directory
When:  initialization completes successfully
Then:  the wiki data tree exists under `wiki_root`, and `config-dir` only contains the runtime contract plus any config-scoped files defined by the workflow
```

**Interfaces to Test Through**: `wiki-init` skill entry workflow and generated filesystem outputs

---

### REQ-3: Wiki workflows resolve runtime state from WIKI.md

**Behavior**: `wiki-ingest`, `wiki-query`, `wiki-lint`, and `wiki-update` must resolve wiki location and runtime conventions from `WIKI.md` instead of requiring `CLAUDE.md`, `.claude/skills/`, `.agents/skills/`, or inferred working-directory-relative paths.

**Test Verification**: Prepare a fixture repository that contains only the neutral `skill/` directory and a configuration directory with `WIKI.md`. Invoke each wiki workflow through its public entrypoint and verify that precondition checks succeed without looking for legacy agent-specific files.

```
Given: a repository with `skill/` and a valid `WIKI.md`, but no `CLAUDE.md`, `.claude/skills/`, or `.agents/skills/`
When:  a wiki workflow is started
Then:  the workflow resolves its wiki paths through `WIKI.md` and proceeds past precondition checks
```

**Interfaces to Test Through**: public wiki skill entry workflows and precondition checks

---

### REQ-4: Public skills exist only in the neutral skill directory

**Behavior**: The repository must expose the public wiki workflow skills only under `skill/`, including `wiki-init`, `wiki-ingest`, `wiki-query`, `wiki-lint`, `wiki-update`, and `agent-browser`. The supported runtime layout must not depend on compatibility copies under agent-specific directories.

**Test Verification**: Validate the repository structure after migration. Assert that each required public skill exists under `skill/` and that runtime documentation does not declare `.claude/skills/` or `.agents/skills/` as required canonical locations.

```
Given: the migrated repository layout
When:  the public skill directories are enumerated
Then:  the required skills are found under `skill/`, and agent-specific skill directories are not part of the supported runtime contract
```

**Interfaces to Test Through**: repository filesystem structure and published documentation

---

### REQ-5: Documentation teaches the neutral contract

**Behavior**: Project documentation must describe `WIKI.md` as the canonical runtime contract and `skill/` as the canonical public skill directory, and it must explain that `config-dir` and `wiki-root` may be separate paths.

**Test Verification**: Review the user-facing documentation and initialization guidance. Assert that setup instructions explain the two-path model and do not instruct users to rely on `CLAUDE.md` or compatibility layers for normal operation.

```
Given: the updated README and setup guidance
When:  a new user follows the documented setup flow
Then:  they are instructed to use `WIKI.md`, choose both `config-dir` and `wiki-root`, and rely on `skill/` as the canonical skill location
```

**Interfaces to Test Through**: README files, setup guidance, and generated initialization artifacts

---

### REQ-6: `wiki-init` reuses an explicitly provided existing config-dir

**Behavior**: When a user explicitly provides an absolute `config-dir` to `wiki-init` and that directory contains a valid `WIKI.md`, the workflow must treat it as the entrypoint to an existing wiki instance and reuse that runtime contract instead of defaulting to a fresh initialization.

**Test Verification**: Invoke the `wiki-init` public entrypoint with a fixture `config-dir` that already contains a valid `WIKI.md`. Verify that the workflow reads the file, enters the continue or reuse path, and does not overwrite `WIKI.md` or recreate an existing wiki data tree by default.

```
Given: an absolute config-dir that already contains a valid WIKI.md pointing at an accessible wiki_root
When:  the user explicitly provides that config-dir to `wiki-init`
Then:  the workflow reuses the existing WIKI.md as the runtime entrypoint instead of performing a fresh initialization write
```

**Interfaces to Test Through**: `wiki-init` skill public entrypoint, `<config-dir>/WIKI.md`, and existing `<wiki-root>/` filesystem outputs

---

### REQ-7: `wiki-init` skips known initialization prompts when WIKI.md already provides them

**Behavior**: Once `wiki-init` enters the existing-config reuse path, it must skip re-asking for initialization fields that can already be parsed from `WIKI.md`, including `wiki_root`, `domain`, `source_types`, and `index_categories`.

**Test Verification**: Provide a `WIKI.md` fixture with all relevant fields populated and run the reuse path through `wiki-init`. Verify that the interaction log no longer asks the user to provide those fields again, and that the final runtime summary matches the values already recorded in `WIKI.md`.

```
Given: a complete WIKI.md containing wiki_root, domain, source_types, and index_categories
When:  `wiki-init` recognizes the config-dir as an existing wiki instance
Then:  the workflow skips collecting those fields again and uses the parsed values to build the runtime summary
```

**Interfaces to Test Through**: `wiki-init` skill public entrypoint, interaction prompt history, and final user-visible summary output

---

### REQ-8: Successful reuse returns an existing-wiki summary and next-step workflow guidance

**Behavior**: After `wiki-init` successfully reuses an existing config, it must clearly tell the user that they are now connected to an existing wiki and explain that the same `config-dir` can be used to continue with `wiki-query`, `wiki-ingest`, `wiki-lint`, and `wiki-update`.

**Test Verification**: Run `wiki-init` against a reusable existing config. Verify that the final confirmation includes an "existing wiki connected" semantic and follow-up guidance for reusing the same `config-dir`, including at least `wiki-query`.

```
Given: an existing config-dir that can be reused successfully
When:  `wiki-init` completes existing-config recognition
Then:  the user receives a runtime summary for the existing wiki and guidance to continue using the same config-dir with `wiki-query` and other workflows
```

**Interfaces to Test Through**: `wiki-init` skill public entrypoint and final confirmation message text

---

### REQ-9: Invalid existing configs fail fast and remain non-destructive by default

**Behavior**: If the user explicitly provides a `config-dir` whose `WIKI.md` is invalid, such as missing `wiki_root`, using a non-absolute `wiki_root`, or pointing to a missing required wiki layout, `wiki-init` must return a clear error and stop. It must not silently guess, auto-repair, or overwrite the existing config unless the user explicitly chooses `reinitialize`.

**Test Verification**: Construct fixtures for each invalid-config shape and pass them to `wiki-init` through an explicit `config-dir`. Verify that the workflow returns a clear failure, does not rewrite `WIKI.md`, and does not create substitute wiki data layouts.

```
Given: a config-dir whose WIKI.md is missing required fields or points at an invalid wiki_root
When:  the user explicitly provides that config-dir to `wiki-init`
Then:  the workflow returns a clear error, stops immediately, and preserves the existing config and filesystem state
```

**Interfaces to Test Through**: `wiki-init` skill public entrypoint, original `<config-dir>/WIKI.md` contents, `<wiki-root>/` filesystem state, and emitted error output

---

### REQ-10: Wiki workflows use a default user-level config-dir before workspace discovery

**Behavior**: 当用户没有显式提供 `config-dir` 时，`wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update` 必须统一按以下顺序发现配置：

1. 检查 `~/wiki/.wiki-config/WIKI.md` 是否存在且有效
2. 如果默认目录未初始化或无效，回退到从当前工作目录向上搜索 `WIKI.md`
3. 仍找不到时，提示用户提供 `config-dir` 或先运行 `wiki-init`

**Test Verification**: 对每个 wiki workflow 创建 fixture `~/wiki/.wiki-config/WIKI.md`（指向有效 `wiki_root`），不传 `config-dir` 调用 workflow。验证 workflow 使用该默认配置而非当前目录下的配置。再测试默认目录无效时回退到工作目录搜索。

```
Given: `~/wiki/.wiki-config/WIKI.md` 存在且指向有效 `wiki_root`，当前工作目录不包含 `WIKI.md`
When:  用户在不传 `config-dir` 的情况下调用 `wiki-query`、`wiki-ingest`、`wiki-lint` 或 `wiki-update`
Then:  每个 workflow 都从 `~/wiki/.wiki-config/WIKI.md` 解析运行时状态
```

```
Given: `~/wiki/.wiki-config/WIKI.md` 不存在或无效，当前工作目录或其父目录包含有效 `WIKI.md`
When:  用户在不传 `config-dir` 的情况下调用 wiki workflow
Then:  workflow 回退到工作目录向上搜索并命中项目内 `WIKI.md`
```

**Interfaces to Test Through**: 各 wiki skill 的 `SKILL.md` 文档中描述的 Pre-condition 发现顺序，以及真实 agent smoke 测试中的行为输出

---

### REQ-11: Default config-dir usage is explicitly communicated to the user

**Behavior**: 当 wiki workflow 通过默认目录 `~/wiki/.wiki-config` 发现配置时，必须明确告知用户当前使用的是默认配置位置，以避免用户误以为在使用项目内 wiki。

**Test Verification**: 在 fixture 中设置 `~/wiki/.wiki-config/WIKI.md`，调用 wiki workflow，验证输出中包含 "default wiki config" 或 `~/wiki/.wiki-config` 路径提示。

```
Given: `~/wiki/.wiki-config/WIKI.md` 存在且有效，用户未提供显式 `config-dir`
When:  任意 wiki workflow 通过默认目录发现配置并继续执行
Then:  输出中包含明确提示，告知用户当前使用 `~/wiki/.wiki-config` 作为配置来源
```

**Interfaces to Test Through**: wiki workflow 的用户可见输出文本

---

### REQ-12: `wiki-init` recommends the default config-dir when none is provided

**Behavior**: 当用户调用 `wiki-init` 且未显式指定 `config-dir` 时，`wiki-init` 应将 `~/wiki/.wiki-config` 作为默认推荐路径展示给用户。

**Test Verification**: 调用 `wiki-init` 不传 `config-dir`，验证交互或输出中包含 `~/wiki/.wiki-config` 作为建议路径。

```
Given: 用户启动 `wiki-init` 且未提供 `config-dir`
When:  初始化进入配置收集阶段
Then:  输出中将 `~/wiki/.wiki-config` 作为推荐的默认配置目录
```

**Interfaces to Test Through**: `wiki-init` skill 的 SKILL.md 文档和用户交互输出

---

### REQ-13: Discovery order is consistent across all wiki workflows

**Behavior**: `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update` 四个 workflow 的 Pre-condition 节必须描述完全一致的配置发现顺序（显式 `config-dir` → 默认 `~/wiki/.wiki-config` → 工作目录向上搜索 → 报错）。

**Test Verification**: 静态读取四个 workflow 的 `SKILL.md`，断言它们的 Pre-condition 节中的发现步骤文本一致。

```
Given: 四个 wiki workflow 的 `SKILL.md` 文件
When:  读取它们的 Pre-condition 配置发现描述
Then:  每个文件的发现顺序描述一致，且都包含 `~/wiki/.wiki-config` 作为第二步
```

**Interfaces to Test Through**: `skill/wiki-query/SKILL.md`, `skill/wiki-ingest/SKILL.md`, `skill/wiki-lint/SKILL.md`, `skill/wiki-update/SKILL.md`

---

## Test Structure

### Integration Tests

```typescript
describe('standard-wiki-runtime', () => {
  it('writes WIKI.md with an absolute wiki_root and initializes data under wiki_root', async () => {
    // Given
    const configDir = makeTempDir('config');
    const wikiRoot = makeTempDir('wiki-root');

    // When
    await runWikiInit({
      configDir,
      wikiRoot,
      domain: 'Test Wiki',
      sourceTypes: ['notes'],
      indexCategories: ['Wiki Pages', 'Concepts Pages'],
    });

    // Then
    expect(readFile(`${configDir}/WIKI.md`)).toContain(`wiki_root: ${wikiRoot}`);
    expect(pathExists(`${wikiRoot}/raw`)).toBe(true);
    expect(pathExists(`${wikiRoot}/wiki/index.md`)).toBe(true);
    expect(pathExists(`${wikiRoot}/wiki/log.md`)).toBe(true);
    expect(pathExists(`${wikiRoot}/concepts`)).toBe(true);
  });

  it('reuses an explicitly provided existing config-dir instead of reinitializing', async () => {
    // Given
    const configDir = makeExistingConfigDir();
    const wikiRoot = makeExistingWikiRoot();

    // When
    const result = await runWikiInit({
      configDir,
    });

    // Then
    expect(result.output).toContain('existing wiki');
    expect(result.output).toContain('wiki-query');
    expect(readFile(`${configDir}/WIKI.md`)).toEqual(originalWikiContract);
  });
});
```

```python
def test_default_config_dir_used_when_no_explicit_config_dir(self):
    # Given: fixture `~/wiki/.wiki-config/WIKI.md` exists, no `WIKI.md` in cwd
    # When: workflow called without explicit config-dir
    # Then: workflow resolves from default config-dir
    pass

def test_fallback_to_workspace_when_default_invalid(self):
    # Given: `~/wiki/.wiki-config/WIKI.md` is corrupt, cwd ancestor has valid WIKI.md
    # When: workflow called without explicit config-dir
    # Then: workflow falls back to workspace discovery
    pass

def test_wiki_init_recommends_default_config_dir(self):
    # Given: wiki-init called without explicit config-dir
    # When: configuration gathering phase
    # Then: output mentions ~/wiki/.wiki-config as default recommendation
    pass
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/wiki-init/standard-wiki-runtime.test.*` | 验证 `config-dir` 与 `wiki-root` 分离时的初始化产物 |
| `tests/wiki-skills/wiki-runtime-resolution.test.*` | 验证各 wiki skill 通过 `WIKI.md` 完成前置解析 |
| `tests/repo-layout/skill-layout.test.*` | 验证 `skill/` 是唯一公开 skill 目录以及文档不再声明旧布局 |
| `tests/test_standard_wiki_init_runtime.py` | 扩展 `wiki-init` 运行时契约测试，覆盖已有 `config-dir` 复用与损坏配置 fail-fast |
| `tests/test_agent_skill_smoke_e2e.py` | 扩展真实 agent smoke 测试，覆盖显式已有 `config-dir` 下的提问裁剪与后续 workflow 指引 |
| `tests/test_documentation_layout.py` | 验证文档已说明已有配置可复用，并说明同一 `config-dir` 的后续 workflow 用法 |
| `tests/test_wiki_runtime_resolution.py` | 新增静态测试：验证四个 workflow SKILL.md 中的发现顺序一致性 |
| `tests/test_documentation_layout.py` | 新增静态测试：验证 README 多语言版本提及 `~/wiki/.wiki-config` |
| `tests/test_agent_skill_smoke_e2e.py` | 新增真实 agent smoke 测试：默认目录命中与回退行为 |
| `tests/test_cloud_sync_static.py` | 新增静态测试：验证 WIKI.md 模板、SKILL.md、运行时 WIKI.md 中的 sync 字段和步骤 12 流程 |

---

### REQ-14: `WIKI.md` 包含 `remote_sync_path` 和 `auto_sync` 字段

**Behavior**: `WIKI.md` frontmatter 必须支持 `remote_sync_path`（pcloud 远端逻辑路径，默认 `"wiki"`，空字符串表示跳过同步）和 `auto_sync`（布尔值，默认 `false`）两个可选字段。wiki workflow 在读取 `WIKI.md` 时应正确解析这些字段。若 `WIKI.md` 不包含这些字段（旧格式），workflow 仍能正常运行（向后兼容，视为跳过同步）。

**Test Verification**: 构造包含 sync 字段的 `WIKI.md` fixture，通过 `wiki-ingest` SKILL.md 的 pre-condition 声明验证字段被识别。同时验证旧格式 `WIKI.md`（不含这些字段）不会导致 workflow 报错。

```
Given: WIKI.md frontmatter 包含 remote_sync_path: "wiki" 和 auto_sync: false
When:  wiki-ingest 读取 WIKI.md 解析运行时状态
Then:  识别 remote_sync_path 为 "wiki"，auto_sync 为 false
```

```
Given: WIKI.md frontmatter 不包含 remote_sync_path 或 auto_sync（旧格式）
When:  wiki-ingest 读取 WIKI.md 解析运行时状态
Then:  remote_sync_path 视为空字符串，auto_sync 视为 false（向后兼容，跳过同步）
```

**Interfaces to Test Through**: `WIKI.md` 静态分析、`skill/wiki-ingest/SKILL.md` 中 pre-condition 字段声明

---

### REQ-15: `wiki-init` 模板写入 sync 字段默认值

**Behavior**: `wiki-init` 初始化新 wiki 时，生成的 `WIKI.md` 模板必须包含 `remote_sync_path: wiki` 和 `auto_sync: false` 作为默认值。

**Test Verification**: 读取 `skill/wiki-init/templates/WIKI.md`，验证 frontmatter 中包含这两个字段且默认值正确。

```
Given: wiki-init 模板文件 skill/wiki-init/templates/WIKI.md
When:  读取模板内容
Then:  frontmatter 包含 remote_sync_path: wiki 和 auto_sync: false
```

**Interfaces to Test Through**: `skill/wiki-init/templates/WIKI.md` 静态分析

---

### REQ-16: `wiki-ingest` pre-condition 声明 sync 字段解析

**Behavior**: `wiki-ingest` SKILL.md 的 Pre-condition 节必须声明从 `WIKI.md` 解析 `remote_sync_path` 和 `auto_sync`，与已有的 `wiki_root` 等字段并列。

**Test Verification**: 静态读取 `skill/wiki-ingest/SKILL.md`，验证 Pre-condition 节中在 "Read WIKI.md to resolve" 列表中包含 `remote_sync_path` 和 `auto_sync`。

```
Given: skill/wiki-ingest/SKILL.md
When:  读取 Pre-condition 节的字段解析列表
Then:  列表包含 remote_sync_path 和 auto_sync
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-17: `wiki-ingest` 在摄入完成后执行云端同步

**Behavior**: `wiki-ingest` 在完成现有 11 步摄入流程后，新增第 12 步 "Cloud Sync"。该步骤按以下逻辑执行：

1. 若 `remote_sync_path` 为空字符串，静默跳过同步
2. 若 `pcloud` CLI 不可用（未安装或未配置），发出警告但不阻塞 ingest 主流程
3. 若 `auto_sync = true`，直接执行 `pcloud sync <wiki_root> <remote_sync_path>`
4. 若 `auto_sync = false`（默认），先执行 `pcloud sync <wiki_root> <remote_sync_path> --dry-run` 展示同步计划（上传/下载文件列表），询问用户确认后执行实际同步
5. 同步完成后追加 `sync` 记录到 `wiki/log.md`，包含上传和下载文件计数

**Test Verification**: 静态读取 `skill/wiki-ingest/SKILL.md`，验证步骤 12 存在且描述了上述完整逻辑。

```
Given: skill/wiki-ingest/SKILL.md
When:  读取流程步骤
Then:  步骤 12 存在，标题为 "Cloud Sync" 或类似，包含:
       - remote_sync_path 为空时跳过的逻辑
       - pcloud 不可用时的警告逻辑
       - auto_sync = true 时的直接同步逻辑
       - auto_sync = false 时的 dry-run → 确认 → 执行交互序列
       - sync 完成后追加 log.md 的记录格式
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-18: 云端同步失败不阻塞 ingest 主流程

**Behavior**: 若云端同步步骤执行失败（如网络错误、pcloud 返回非零退出码），`wiki-ingest` 应报告错误但不回滚已完成的摄入操作。ingest 的页面写入、index 更新和 log 记录不受 sync 失败影响。

**Test Verification**: 静态验证 `skill/wiki-ingest/SKILL.md` 步骤 12 中明确声明 sync 失败不影响 ingest 主流程。

```
Given: skill/wiki-ingest/SKILL.md 步骤 12
When:  读取错误处理描述
Then:  明确声明 sync 失败不阻塞、不回滚 ingest 结果
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-19: `wiki-init` 复用已有配置时同步字段参与提问裁剪

**Behavior**: 当 `wiki-init` 进入已有配置复用路径时，若 `WIKI.md` 已包含 `remote_sync_path` 和 `auto_sync`，不应重复询问这些字段。若缺失（旧格式 `WIKI.md`），应补问并接受默认值。

**Test Verification**: 提供包含完整 sync 字段的 `WIKI.md` fixture，验证复用路径不询问 sync 字段。提供缺失 sync 字段的旧格式 `WIKI.md`，验证补问时展示默认值 `"wiki"` / `false`。

```
Given: 已有 WIKI.md 包含 remote_sync_path: "wiki" 和 auto_sync: false
When:  wiki-init 识别为已有配置并进入复用路径
Then:  不询问 remote_sync_path 和 auto_sync（提问裁剪）
```

```
Given: 已有 WIKI.md 不包含 remote_sync_path 和 auto_sync（旧格式）
When:  wiki-init 识别为已有配置并进入复用路径
Then:  补问 sync 字段，默认值分别为 "wiki" 和 false
```

**Interfaces to Test Through**: `wiki-init` 技能交互输出、`skill/wiki-init/SKILL.md` 中的提问裁剪逻辑

---

## Edge Cases

- `WIKI.md` 中的 `wiki_root` 不是绝对路径时，初始化后续流程或运行时前置检查应失败并给出明确提示
- `config-dir` 可写但 `wiki-root` 不可写时，初始化应失败且不误报成功
- `WIKI.md` 存在但指向缺失的 `wiki_root` 时，wiki skill 应返回清晰错误
- 用户把 `config-dir` 与 `wiki-root` 设为同一路径时，流程仍应工作，不应强制分离
- `WIKI.md` 存在且只包含 `wiki_root`，缺少 `domain` 或 `index_categories` 等非关键字段时，流程应只补问缺失字段，不重复收集已知字段
- `config-dir` 有效但 `wiki_root` 缺少 `wiki/index.md` 或 `wiki/log.md` 时，应视为损坏布局并快速失败
- 用户显式要求 `reinitialize` 时，允许进入覆盖式初始化；默认路径不得隐式切换到该分支
- 显式 `config-dir` 为最高优先级，不受默认目录发现变更影响
- `~/wiki/.wiki-config/WIKI.md` 存在但 `wiki_root` 不是绝对路径：视为无效，回退到工作目录搜索
- `~/wiki/.wiki-config/WIKI.md` 存在但指向不存在的 `wiki_root`：视为无效，回退到工作目录搜索
- `~/wiki/.wiki-config` 目录本身不存在：视为默认目录未初始化，回退到工作目录搜索
- 用户同时有默认目录和工作目录 `WIKI.md`：默认目录优先（除非用户显式提供 `config-dir`）
- `remote_sync_path` 为空字符串时，`wiki-ingest` 静默跳过同步，不调用 `pcloud`
- `pcloud` CLI 未安装或未配置时，发出警告但不阻塞 ingest
- `pcloud sync --dry-run` 显示 0 变更时，告知用户 "云端已是最新"
- `pcloud sync` 执行中途失败，报告错误但不回滚已完成的摄入操作
- `WIKI.md` 不存在 `remote_sync_path` 字段（旧格式），视为空字符串，向后兼容跳过同步
- 用户在 dry-run 预览后选择跳过，不执行同步但 ingest 已成功完成
