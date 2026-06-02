# Specification: skill-test-directory

## Overview

为 wiki-lint、wiki-ingest、wiki-distill 三个技能增加 `tests/` 目录，包含测试用例描述和 fixtures，遵循 [[ai-skill-development-testing-best-practices]] 的测试金字塔原则和 [[pi-agent-extension-design]] 原则 12（可测试性设计）。

## Requirements

### REQ-1: wiki-lint 存在 tests/ 目录及 fixtures

**Behavior**: `skill/wiki-lint/tests/` 目录存在，包含至少 3 个 fixtures 子目录（healthy-wiki、broken-links、missing-scope），每个 fixture 是一个完整的迷你 wiki 实例。

**Test Verification**: 检查目录结构和 fixture 完整性。

```
Given: wiki-lint 技能目录
When:  检查 tests/ 目录结构
Then:  tests/fixtures/healthy-wiki/ 存在，包含 WIKI.md、wiki/index.md、wiki/pages/*.md
       tests/fixtures/broken-links/ 存在，包含有断链的 wiki 实例
       tests/fixtures/missing-scope/ 存在，包含缺 scope 字段的 wiki 实例
```

**Interfaces to Test Through**: 目录结构检查、文件存在性检查

---

### REQ-2: wiki-lint 存在测试用例描述文件

**Behavior**: `skill/wiki-lint/tests/test_cases.md` 存在，描述每个 fixture 的测试场景和预期结果。

**Test Verification**: 检查文件存在且包含至少 3 个测试用例描述。

```
Given: wiki-lint 的 tests/ 目录
When:  读取 tests/test_cases.md
Then:  包含至少 3 个测试用例，每个用例描述 fixture、输入、预期输出
```

**Interfaces to Test Through**: 文件存在性检查、内容结构检查

---

### REQ-3: wiki-ingest 存在 tests/ 目录及 fixtures

**Behavior**: `skill/wiki-ingest/tests/` 目录存在，包含至少 2 个 fixtures（url-source、file-source），每个 fixture 包含输入源和预期输出。

**Test Verification**: 检查目录结构和 fixture 完整性。

```
Given: wiki-ingest 技能目录
When:  检查 tests/ 目录结构
Then:  tests/fixtures/url-source/ 存在，包含输入 URL 和预期页面
       tests/fixtures/file-source/ 存在，包含输入文件和预期页面
```

**Interfaces to Test Through**: 目录结构检查、文件存在性检查

---

### REQ-4: wiki-distill 存在 tests/ 目录及 fixtures

**Behavior**: `skill/wiki-distill/tests/` 目录存在，包含至少 2 个 fixtures（go-project、python-project），每个 fixture 是一个迷你项目。

**Test Verification**: 检查目录结构和 fixture 完整性。

```
Given: wiki-distill 技能目录
When:  检查 tests/ 目录结构
Then:  tests/fixtures/go-project/ 存在，包含迷你 Go 项目
       tests/fixtures/python-project/ 存在，包含迷你 Python 项目
```

**Interfaces to Test Through**: 目录结构检查、文件存在性检查

---

### REQ-5: fixtures 是自包含的迷你 wiki 实例

**Behavior**: 每个 fixture 是一个完整的、自包含的 wiki 实例，不依赖外部文件或网络。

**Test Verification**: 检查 fixture 目录包含 WIKI.md 和 wiki/ 子目录。

```
Given: 任意 fixture 目录
When:  检查目录内容
Then:  包含 WIKI.md（含 wiki_root 指向自身）
       包含 wiki/index.md
       包含 wiki/pages/ 目录
```

**Interfaces to Test Through**: 文件存在性检查、WIKI.md 内容解析

---

## Test Structure

### 静态检查

```python
def test_wiki_lint_tests_dir():
    """wiki-lint tests/ 目录结构完整"""
    assert os.path.isdir("skill/wiki-lint/tests")
    assert os.path.isdir("skill/wiki-lint/tests/fixtures/healthy-wiki")
    assert os.path.isdir("skill/wiki-lint/tests/fixtures/broken-links")
    assert os.path.isdir("skill/wiki-lint/tests/fixtures/missing-scope")
    assert os.path.exists("skill/wiki-lint/tests/test_cases.md")

def test_wiki_ingest_tests_dir():
    """wiki-ingest tests/ 目录结构完整"""
    assert os.path.isdir("skill/wiki-ingest/tests")
    assert os.path.isdir("skill/wiki-ingest/tests/fixtures/url-source")
    assert os.path.isdir("skill/wiki-ingest/tests/fixtures/file-source")

def test_wiki_distill_tests_dir():
    """wiki-distill tests/ 目录结构完整"""
    assert os.path.isdir("skill/wiki-distill/tests")
    assert os.path.isdir("skill/wiki-distill/tests/fixtures/go-project")
    assert os.path.isdir("skill/wiki-distill/tests/fixtures/python-project")

def test_fixtures_self_contained():
    """fixtures 是自包含的"""
    for fixture_dir in find_fixture_dirs():
        assert os.path.exists(os.path.join(fixture_dir, "WIKI.md"))
        assert os.path.exists(os.path.join(fixture_dir, "wiki/index.md"))
```

### Test Files to Create

| File | Purpose |
|------|---------|
| tests/test_skill_tests_dir.py | 目录结构 + fixture 完整性检查 |

## Edge Cases

- fixture 目录为空时如何处理
- fixture 中的 WIKI.md 的 wiki_root 指向自身（相对路径或绝对路径）
- 硬链接同步后 wiki-update 的 tests/ 是否与源文件一致
