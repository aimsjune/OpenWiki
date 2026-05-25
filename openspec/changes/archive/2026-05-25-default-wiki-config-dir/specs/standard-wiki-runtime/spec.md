# Specification: standard-wiki-runtime (delta)

## Overview

为 `standard-wiki-runtime` 能力新增“默认用户级配置目录”运行时发现规则。所有 wiki workflow 在没有显式 `config-dir` 时，统一优先检查 `~/wiki/.wiki-config`，再回退到工作目录向上搜索。

## ADDED Requirements

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

### Test Files to Update

| File | Purpose |
|------|---------|
| `tests/test_wiki_runtime_resolution.py` | 新增静态测试：验证四个 workflow SKILL.md 中的发现顺序一致性 |
| `tests/test_documentation_layout.py` | 新增静态测试：验证 README 多语言版本提及 `~/wiki/.wiki-config` |
| `tests/test_agent_skill_smoke_e2e.py` | 新增真实 agent smoke 测试：默认目录命中与回退行为 |

## Edge Cases

- `~/wiki/.wiki-config/WIKI.md` 存在但 `wiki_root` 不是绝对路径：视为无效，回退到工作目录搜索
- `~/wiki/.wiki-config/WIKI.md` 存在但指向不存在的 `wiki_root`：视为无效，回退到工作目录搜索
- `~/wiki/.wiki-config` 目录本身不存在：视为默认目录未初始化，回退到工作目录搜索
- 用户同时有默认目录和工作目录 `WIKI.md`：默认目录优先（除非用户显式提供 `config-dir`）
- 显式 `config-dir` 仍为最高优先级，不受此变更影响
