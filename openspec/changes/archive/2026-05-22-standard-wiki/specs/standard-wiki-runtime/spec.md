# Specification: standard-wiki-runtime

## Overview

This specification defines the observable runtime behavior for a neutral wiki setup that follows `skill.io` conventions. It covers initialization inputs, the `WIKI.md` runtime contract, separation between configuration and data locations, and the canonical skill layout used by wiki workflows.

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
});
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/wiki-init/standard-wiki-runtime.test.*` | 验证 `config-dir` 与 `wiki-root` 分离时的初始化产物 |
| `tests/wiki-skills/wiki-runtime-resolution.test.*` | 验证各 wiki skill 通过 `WIKI.md` 完成前置解析 |
| `tests/repo-layout/skill-layout.test.*` | 验证 `skill/` 是唯一公开 skill 目录以及文档不再声明旧布局 |

## Edge Cases

- `WIKI.md` 中的 `wiki_root` 不是绝对路径时，初始化后续流程或运行时前置检查应失败并给出明确提示
- `config-dir` 可写但 `wiki-root` 不可写时，初始化应失败且不误报成功
- `WIKI.md` 存在但指向缺失的 `wiki_root` 时，wiki skill 应返回清晰错误
- 用户把 `config-dir` 与 `wiki-root` 设为同一路径时，流程仍应工作，不应强制分离
