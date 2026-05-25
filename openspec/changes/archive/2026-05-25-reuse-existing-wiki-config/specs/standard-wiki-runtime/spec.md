# Specification: standard-wiki-runtime

## Overview

本规格为 `standard-wiki-runtime` 增加“已有配置复用”行为，定义当用户在 `wiki-init` 中显式提供一个已经存在的 `config-dir` 时，系统如何通过该目录下的 `WIKI.md` 识别现有 wiki、跳过已知初始化问题、返回运行时摘要，并在配置损坏时以非破坏方式快速失败。

## Requirements

### REQ-1: `wiki-init` 复用显式提供的已有 config-dir

**Behavior**: 当用户在 `wiki-init` 中显式提供一个绝对 `config-dir`，且该目录下存在有效 `WIKI.md` 时，流程必须将其视为现有 wiki 实例入口，复用该运行时契约，而不是默认重新初始化。

**Test Verification**: 通过 `wiki-init` 公共入口传入一个包含有效 `WIKI.md` 的 `config-dir` 夹具。验证流程读取该文件并进入 continue/复用路径，且不会默认覆盖 `WIKI.md` 或重复创建现有 wiki 数据树。

```
Given: 一个绝对 config-dir，目录下存在有效的 WIKI.md，并指向一个可访问的 wiki_root
When:  用户通过 wiki-init 显式提供该 config-dir
Then:  流程复用现有 WIKI.md 作为运行时入口，而不是默认执行新的初始化写入
```

**Interfaces to Test Through**: `wiki-init` skill 公共入口、`<config-dir>/WIKI.md`、`<wiki-root>/` 现有文件系统产物

---

### REQ-2: `wiki-init` 跳过可从 WIKI.md 解析的已知初始化信息

**Behavior**: 一旦 `wiki-init` 进入已有配置复用路径，凡是能够从 `WIKI.md` 解析得到的已知初始化信息，包括 `wiki_root`、`domain`、`source_types`、`index_categories`，都必须跳过重复提问。

**Test Verification**: 准备带完整字段的 `WIKI.md` 夹具，通过 `wiki-init` 启动复用路径。验证交互记录中不再要求用户重复输入这些字段，并且最终输出的运行时摘要与 `WIKI.md` 中的记录一致。

```
Given: 一个字段完整的 WIKI.md，包含 wiki_root、domain、source_types、index_categories
When:  wiki-init 识别该 config-dir 为现有 wiki 实例
Then:  流程跳过上述字段的重新采集，并直接使用解析结果生成摘要
```

**Interfaces to Test Through**: `wiki-init` skill 公共入口、交互提示记录、最终用户可见摘要输出

---

### REQ-3: 复用成功后返回现有 wiki 摘要与后续 workflow 指引

**Behavior**: 当 `wiki-init` 成功复用已有配置后，必须明确告知用户当前已连接到现有 wiki，并提示可继续使用同一 `config-dir` 运行 `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update`。

**Test Verification**: 通过已有配置运行 `wiki-init`。验证最终提示包含“已连接现有 wiki”的确认语义，以及复用同一 `config-dir` 调用后续 wiki workflow 的指引，至少覆盖 `wiki-query`。

```
Given: 一个可成功复用的既有 config-dir
When:  wiki-init 完成已有配置识别
Then:  用户收到现有 wiki 摘要，并被提示可继续使用同一 config-dir 调用 wiki-query 等 workflow
```

**Interfaces to Test Through**: `wiki-init` skill 公共入口、最终确认消息文本

---

### REQ-4: 损坏的已有配置必须快速失败且保持非破坏性

**Behavior**: 如果用户显式提供的 `config-dir` 中存在无效 `WIKI.md`，例如缺失 `wiki_root`、`wiki_root` 不是绝对路径、或 `wiki_root` 指向的布局缺失，`wiki-init` 必须报错并停止，不得静默猜测、自动修复或直接覆盖，除非用户显式选择 `reinitialize`。

**Test Verification**: 分别构造多种损坏配置夹具，通过 `wiki-init` 显式传入 `config-dir`。验证流程返回清晰错误，不改写 `WIKI.md`，也不新建替代布局。

```
Given: 一个 config-dir，其中 WIKI.md 缺失关键字段或指向无效 wiki_root
When:  用户通过 wiki-init 显式提供该 config-dir
Then:  流程返回明确错误并停止，且保持配置和数据的非破坏性
```

**Interfaces to Test Through**: `wiki-init` skill 公共入口、`<config-dir>/WIKI.md` 原始内容、`<wiki-root>/` 文件系统状态、错误输出

---

## Test Structure

### Integration Tests

```typescript
describe('reuse-existing-wiki-config', () => {
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

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_standard_wiki_init_runtime.py` | 扩展 `wiki-init` 的运行时契约测试，覆盖已有 config-dir 复用与损坏配置 fail-fast |
| `tests/test_agent_skill_smoke_e2e.py` | 扩展真实 agent smoke 测试，覆盖显式已有 `config-dir` 下的交互跳过与后续 workflow 指引 |
| `tests/test_documentation_layout.py` | 验证文档已说明已有配置可复用，并指向同一 `config-dir` 的后续 workflow 用法 |

## Edge Cases

- `WIKI.md` 存在，但只包含 `wiki_root`，缺少 `domain` 或 `index_categories` 等非关键字段时，是否允许部分复用，需要给出一致的用户提示策略
- `config-dir` 有效，但 `wiki_root` 中缺少 `wiki/index.md` 或 `wiki/log.md` 时，应视为损坏布局而失败
- 用户显式要求 `reinitialize` 时，允许覆盖已有配置，但默认路径不能隐式进入该分支
- 用户未显式提供 `config-dir` 时，不改变现有“向上搜索 `WIKI.md`”的运行时发现顺序
