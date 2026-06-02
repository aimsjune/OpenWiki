# Specification: skill-composes-declaration

## Overview

在 wiki-distill 和 wiki-update 的 SKILL.md frontmatter 中增加 `composes` 字段，显式声明技能间的依赖关系，遵循 [[pi-agent-extension-design]] 原则 8（技能与实现分离）。

## Requirements

### REQ-1: wiki-distill 声明 composes 依赖

**Behavior**: `skill/wiki-distill/SKILL.md` 的 frontmatter 包含 `composes: [wiki-ingest, wiki-lint]`。

**Test Verification**: 解析 YAML frontmatter，检查 composes 字段。

```
Given: wiki-distill 的 SKILL.md
When:  解析 frontmatter
Then:  composes 字段存在，值为 ["wiki-ingest", "wiki-lint"]
```

**Interfaces to Test Through**: YAML 解析 + 字段值验证

---

### REQ-2: wiki-update 声明 composes 依赖

**Behavior**: `skill/wiki-update/SKILL.md` 的 frontmatter 包含 `composes: [wiki-ingest, wiki-lint, wiki-init]`。

**Test Verification**: 解析 YAML frontmatter，检查 composes 字段。

```
Given: wiki-update 的 SKILL.md
When:  解析 frontmatter
Then:  composes 字段存在，值为 ["wiki-ingest", "wiki-lint", "wiki-init"]
```

**Interfaces to Test Through**: YAML 解析 + 字段值验证

---

### REQ-3: composes 值仅包含本项目的技能名

**Behavior**: composes 数组中的每个值必须是 llm-wiki 项目中存在的技能目录名。

**Test Verification**: 遍历 composes 数组，检查每个值对应的 `skill/<name>/` 目录是否存在。

```
Given: 任意 SKILL.md 的 composes 字段
When:  遍历 composes 数组
Then:  每个值对应的 skill/<name>/ 目录存在
```

**Interfaces to Test Through**: 目录存在性检查

---

### REQ-4: 独立技能不声明 composes

**Behavior**: wiki-init、wiki-ingest、wiki-lint、wiki-query 不声明 composes（它们不依赖其他技能）。

**Test Verification**: 解析这些技能的 frontmatter，确认 composes 字段不存在或为空。

```
Given: wiki-init、wiki-ingest、wiki-lint、wiki-query 的 SKILL.md
When:  解析 frontmatter
Then:  composes 字段不存在或为空数组
```

**Interfaces to Test Through**: YAML 解析 + 字段值验证

---

## Test Structure

### 静态检查

```python
def test_wiki_distill_composes():
    """wiki-distill 声明 composes 依赖"""
    fm = parse_frontmatter("skill/wiki-distill/SKILL.md")
    assert fm["composes"] == ["wiki-ingest", "wiki-lint"]

def test_wiki_update_composes():
    """wiki-update 声明 composes 依赖"""
    fm = parse_frontmatter("skill/wiki-update/SKILL.md")
    assert fm["composes"] == ["wiki-ingest", "wiki-lint", "wiki-init"]

def test_composes_values_valid():
    """composes 值对应存在的技能目录"""
    for skill_name in ["wiki-distill", "wiki-update"]:
        fm = parse_frontmatter(f"skill/{skill_name}/SKILL.md")
        for dep in fm.get("composes", []):
            assert os.path.isdir(f"skill/{dep}")

def test_independent_skills_no_composes():
    """独立技能不声明 composes"""
    for skill_name in ["wiki-init", "wiki-ingest", "wiki-lint", "wiki-query"]:
        fm = parse_frontmatter(f"skill/{skill_name}/SKILL.md")
        assert "composes" not in fm or fm["composes"] == []
```

### Test Files to Create

| File | Purpose |
|------|---------|
| tests/test_composes_declaration.py | composes 字段解析 + 有效性验证 |

## Edge Cases

- composes 数组为空 `[]` vs 字段不存在
- composes 值包含不存在的技能名
- composes 值重复
- 硬链接同步后 wiki-update 的 composes 是否与源一致
