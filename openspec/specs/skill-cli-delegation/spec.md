# Specification: skill-cli-delegation

## Overview

将 6 个 Skill（wiki-init、wiki-ingest、wiki-lint、wiki-query、wiki-update、wiki-distill）中的文件操作委托给 openwiki CLI，减少 Skill 中的重复文件操作逻辑。

## Requirements

### REQ-1: wiki-init 委托 init

**Behavior**: wiki-init Skill 通过 `openwiki init` 创建 wiki 实例，而非直接创建目录和文件。

**Test Verification**: 检查 SKILL.md 中初始化步骤引用 CLI 命令。

```
Given: wiki-init SKILL.md
When:  检查初始化步骤
Then:  步骤含 openwiki init <wiki-root> --non-interactive --json 调用
      不再含直接 mkdir 或写文件指令
```

**Interfaces to Test Through**: SKILL.md 文本内容检查

---

### REQ-2: wiki-ingest 委托 page 操作

**Behavior**: wiki-ingest Skill 通过 `openwiki page` 命令进行页面 CRUD，而非直接读写文件。

**Test Verification**: 检查 SKILL.md 中各步骤引用 CLI 命令。

```
Given: wiki-ingest SKILL.md
When:  检查页面创建步骤
Then:  步骤含 openwiki page create <slug> --file /tmp/content.md --json
      不再含直接写 wiki/pages/<slug>.md 指令

Given: wiki-ingest SKILL.md
When:  检查已有页面检查步骤
Then:  步骤含 openwiki page list --json
      不再含直接读取 wiki/index.md 指令

Given: wiki-ingest SKILL.md
When:  检查回链审计步骤
Then:  步骤含 openwiki page get <slug> --json（利用 cross_references 字段）
      不再含手动 grep [[ref]] 指令
```

**Interfaces to Test Through**: SKILL.md 文本内容检查

---

### REQ-3: wiki-lint 委托 page 操作

**Behavior**: wiki-lint Skill 通过 `openwiki page list` 和 `openwiki page get` 获取页面数据，而非直接遍历文件系统。

**Test Verification**: 检查 SKILL.md 中各步骤引用 CLI 命令。

```
Given: wiki-lint SKILL.md
When:  检查页面清单构建步骤
Then:  步骤含 openwiki page list --json
      不再含直接读取 wiki/index.md 和遍历 wiki/pages/ 指令

Given: wiki-lint SKILL.md
When:  检查页面内容读取步骤
Then:  步骤含 openwiki page get <slug1> <slug2> ... --json（批量获取）
      不再含逐个读取 wiki/pages/*.md 指令
```

**Interfaces to Test Through**: SKILL.md 文本内容检查

---

### REQ-4: wiki-query 委托 page 操作

**Behavior**: wiki-query Skill 通过 `openwiki page list` 和 `openwiki page get` 进行检索。

**Test Verification**: 检查 SKILL.md 中各步骤引用 CLI 命令。

```
Given: wiki-query SKILL.md
When:  检查索引扫描步骤
Then:  步骤含 openwiki page list --json
      不再含直接读取 wiki/index.md 指令

Given: wiki-query SKILL.md
When:  检查页面读取步骤
Then:  步骤含 openwiki page get <slug> --json
      不再含直接读取 wiki/pages/<slug>.md 指令

Given: wiki-query SKILL.md
When:  检查链接跟踪步骤
Then:  步骤利用 page get 返回的 cross_references 字段
      不再含手动解析 [[ref]] 指令
```

**Interfaces to Test Through**: SKILL.md 文本内容检查

---

### REQ-5: wiki-update 委托 page 和 log 操作

**Behavior**: wiki-update Skill 通过 `openwiki page` 和 `openwiki log` 进行页面更新和日志追加。

**Test Verification**: 检查 SKILL.md 中各步骤引用 CLI 命令。

```
Given: wiki-update SKILL.md
When:  检查页面读取步骤
Then:  步骤含 openwiki page get <slug> --json

Given: wiki-update SKILL.md
When:  检查页面写入步骤
Then:  步骤含 openwiki page update <slug> --file /tmp/updated.md --json

Given: wiki-update SKILL.md
When:  检查日志追加步骤
Then:  步骤含 openwiki log append "update | <slug>" --json
```

**Interfaces to Test Through**: SKILL.md 文本内容检查

---

### REQ-6: wiki-distill 委托 page 操作

**Behavior**: wiki-distill Skill 通过 `openwiki page create` 创建蒸馏产物页面。

**Test Verification**: 检查 SKILL.md 中各步骤引用 CLI 命令。

```
Given: wiki-distill SKILL.md
When:  检查页面创建步骤
Then:  步骤含 openwiki page create <slug> --file /tmp/distilled.md --json
```

**Interfaces to Test Through**: SKILL.md 文本内容检查

---

### REQ-7: 配置路径统一更新

**Behavior**: 所有 Skill 的配置读取路径从 WIKI.md 更新为 openwiki.toml。

**Test Verification**: 检查所有 SKILL.md 中不再引用 WIKI.md 作为配置来源。

```
Given: 任意 Skill 的 SKILL.md
When:  检查配置发现逻辑
Then:  不再含 "Read WIKI.md" 或 "~/.wiki-config/WIKI.md"
      改为引用 openwiki config 命令或 openwiki.toml 路径
```

**Interfaces to Test Through**: 所有 SKILL.md 文本内容检查

---

## Test Structure

### SKILL.md 内容验证测试

```python
def test_wiki_lint_uses_cli_for_page_list():
    """验证 wiki-lint SKILL.md 使用 openwiki page list 而非直接读文件"""
    with open("skill/wiki-lint/SKILL.md") as f:
        content = f.read()

    assert "openwiki page list --json" in content
    assert "openwiki page get" in content
    # 不应再含直接文件操作指令
    assert "Read `wiki/index.md`" not in content
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_skill_cli_delegation.py` | 验证所有 Skill 的 CLI 委托 |

## Edge Cases

- Skill 中某些操作无法完全委托给 CLI（如 concepts/ 报告写入）时保留直接文件操作
- `page get` 批量模式在 Skill 中的使用方式（分批获取 vs 全量获取）
- Skill 的自我纠错步骤（步骤 2.1/6.1）是否也需要委托给 CLI
