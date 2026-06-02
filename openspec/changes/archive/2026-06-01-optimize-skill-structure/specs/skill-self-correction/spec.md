# Specification: skill-self-correction

## Overview

在 wiki-ingest 和 wiki-lint 的关键步骤后增加自我验证环节，遵循 [[ai-skill-development-testing-best-practices]] 原则 4（内置自我纠错能力：输出前验证自己的输出）。

## Requirements

### REQ-1: wiki-ingest 步骤 6 后存在验证写入步骤

**Behavior**: wiki-ingest 的 SKILL.md 中，步骤 6（写入页面文件）之后存在步骤 6.1（验证写入），包含以下检查项：
- 重新读取刚写入的页面文件
- 检查 frontmatter 是否包含所有必填字段（title、tags、sources、updated、scope_level、scope_code）
- 检查正文中的 [[交叉引用]] 是否指向存在的页面
- 若验证失败，报告错误并建议修复

**Test Verification**: 文本匹配检查。

```
Given: wiki-ingest 的 SKILL.md
When:  搜索步骤 6 之后的内容
Then:  存在步骤 6.1 或等效的验证步骤
       包含 "重读" 或 "重新读取" 关键词
       包含 "frontmatter" 关键词
       包含 "交叉引用" 或 "[[ ]]" 关键词
```

**Interfaces to Test Through**: 文本匹配

---

### REQ-2: wiki-lint 步骤 2 后存在验证输出完整性步骤

**Behavior**: wiki-lint 的 SKILL.md 中，步骤 2（运行所有检查）之后存在步骤 2.1（验证输出完整性），包含以下检查项：
- 检查是否所有页面都被扫描（页面数 = index.md 中列出的页面数）
- 检查 Red Errors 是否都有对应的修复建议
- 检查 Yellow Warnings 是否都有对应的说明

**Test Verification**: 文本匹配检查。

```
Given: wiki-lint 的 SKILL.md
When:  搜索步骤 2 之后的内容
Then:  存在步骤 2.1 或等效的验证步骤
       包含 "所有页面" 或 "页面数" 关键词
       包含 "修复建议" 关键词
```

**Interfaces to Test Through**: 文本匹配

---

### REQ-3: 验证步骤使用明确的条件分支

**Behavior**: 验证步骤使用明确的条件分支（"若...则..."），Agent 可以无歧义地执行。

**Test Verification**: 文本匹配检查。

```
Given: wiki-ingest 或 wiki-lint 的 SKILL.md 中的验证步骤
When:  搜索验证步骤内容
Then:  包含 "若" 或 "如果" 条件描述
       包含 "则" 或 "那么" 结果描述
```

**Interfaces to Test Through**: 文本匹配

---

## Test Structure

### 静态检查

```python
def test_wiki_ingest_has_verify_step():
    """wiki-ingest 步骤 6 后有验证步骤"""
    body = extract_body("skill/wiki-ingest/SKILL.md")
    assert "重读" in body or "重新读取" in body
    assert "frontmatter" in body.lower()
    assert "交叉引用" in body or "[[" in body

def test_wiki_lint_has_verify_step():
    """wiki-lint 步骤 2 后有验证步骤"""
    body = extract_body("skill/wiki-lint/SKILL.md")
    assert "所有页面" in body or "页面数" in body
    assert "修复建议" in body

def test_verify_steps_have_conditions():
    """验证步骤包含条件分支"""
    ingest_body = extract_body("skill/wiki-ingest/SKILL.md")
    lint_body = extract_body("skill/wiki-lint/SKILL.md")
    combined = ingest_body + lint_body
    assert "若" in combined or "如果" in combined
    assert "则" in combined or "那么" in combined
```

### Test Files to Create

| File | Purpose |
|------|---------|
| tests/test_self_correction.py | 验证步骤存在性 + 条件分支检查 |

## Edge Cases

- 验证步骤是否可能被 Agent 跳过（指令不够强制）
- 验证失败后的回滚策略是否明确
- 硬链接同步后 wiki-update 的验证步骤是否与源一致
