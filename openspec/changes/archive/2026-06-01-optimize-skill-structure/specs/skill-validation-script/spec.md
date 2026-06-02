# Specification: skill-validation-script

## Overview

为 wiki-lint 增加 `scripts/validate_wiki.py`，自动检查 wiki 结构完整性，输出 JSON 格式结果，遵循 [[agent-skills-specification]] 的验证工具建议。

## Requirements

### REQ-1: 脚本存在于 wiki-lint 目录下

**Behavior**: `skill/wiki-lint/scripts/validate_wiki.py` 文件存在且可执行。

**Test Verification**: 文件存在性 + 可执行权限检查。

```
Given: wiki-lint 技能目录
When:  检查 scripts/validate_wiki.py
Then:  文件存在，且有可执行权限（或可通过 python 解释器运行）
```

**Interfaces to Test Through**: 文件存在性检查、权限检查

---

### REQ-2: 脚本接受 wiki_root 参数

**Behavior**: 脚本接受一个位置参数或命名参数，指定要检查的 wiki 根目录路径。

**Test Verification**: 执行 `python validate_wiki.py --help` 或检查脚本源码。

```
Given: validate_wiki.py
When:  执行 python validate_wiki.py --help
Then:  显示用法说明，包含 wiki_root 参数
```

**Interfaces to Test Through**: 命令行接口

---

### REQ-3: 脚本输出 JSON 格式结果

**Behavior**: 脚本输出 JSON 格式的结构化结果，包含检查项列表和通过/失败状态。

**Test Verification**: 对 fixture 执行脚本，解析输出 JSON。

```
Given: 一个健康的 wiki fixture
When:  执行 python validate_wiki.py <fixture_path>
Then:  输出合法 JSON
       JSON 包含 "checks" 数组
       每个 check 包含 "name"、"status"（pass/fail）、"message" 字段
```

**Interfaces to Test Through**: JSON 解析

---

### REQ-4: 脚本检查 WIKI.md 必填字段

**Behavior**: 脚本检查 WIKI.md 是否包含 `wiki_root`、`primary_language`、`secondary_language` 等必填字段。

**Test Verification**: 对缺少字段的 fixture 执行脚本，检查输出。

```
Given: 一个缺少 primary_language 的 wiki fixture
When:  执行 python validate_wiki.py <fixture_path>
Then:  JSON 输出中包含 status: "fail" 的 check，message 提示缺少 primary_language
```

**Interfaces to Test Through**: JSON 解析 + 字段值验证

---

### REQ-5: 脚本检查 index.md 表格格式

**Behavior**: 脚本检查 index.md 中的表格格式是否完整（表头、分隔行、数据行）。

**Test Verification**: 对格式错误的 fixture 执行脚本，检查输出。

```
Given: 一个 index.md 表格格式错误的 wiki fixture
When:  执行 python validate_wiki.py <fixture_path>
Then:  JSON 输出中包含 status: "fail" 的 check，message 提示表格格式错误
```

**Interfaces to Test Through**: JSON 解析 + 字段值验证

---

### REQ-6: 脚本检查交叉引用可达性

**Behavior**: 脚本检查所有 `[[slug]]` 交叉引用是否指向存在的页面文件。

**Test Verification**: 对含断链的 fixture 执行脚本，检查输出。

```
Given: 一个包含 [[nonexistent]] 断链的 wiki fixture
When:  执行 python validate_wiki.py <fixture_path>
Then:  JSON 输出中包含 status: "fail" 的 check，message 提示断链
```

**Interfaces to Test Through**: JSON 解析 + 字段值验证

---

### REQ-7: 脚本使用 Python 标准库，无外部依赖

**Behavior**: 脚本仅使用 Python 标准库（os、json、sys、argparse、re、pathlib），不依赖第三方包。

**Test Verification**: 检查脚本的 import 语句。

```
Given: validate_wiki.py 源码
When:  检查所有 import 语句
Then:  所有 import 来自 Python 标准库
```

**Interfaces to Test Through**: 源码文本匹配

---

### REQ-8: 脚本返回标准退出码

**Behavior**: 所有检查通过时返回 0，有失败时返回 1。

**Test Verification**: 对健康/不健康的 fixture 执行脚本，检查退出码。

```
Given: 一个健康的 wiki fixture
When:  执行 python validate_wiki.py <fixture_path>
Then:  退出码为 0

Given: 一个不健康的 wiki fixture
When:  执行 python validate_wiki.py <fixture_path>
Then:  退出码为 1
```

**Interfaces to Test Through**: 进程退出码

---

## Test Structure

### 集成测试

```python
def test_validate_healthy_wiki():
    """健康 wiki 全部通过"""
    result = subprocess.run(
        ["python", "skill/wiki-lint/scripts/validate_wiki.py",
         "skill/wiki-lint/tests/fixtures/healthy-wiki"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    for check in data["checks"]:
        assert check["status"] == "pass"

def test_validate_broken_links():
    """断链 wiki 检测到错误"""
    result = subprocess.run(
        ["python", "skill/wiki-lint/scripts/validate_wiki.py",
         "skill/wiki-lint/tests/fixtures/broken-links"],
        capture_output=True, text=True
    )
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert any(c["status"] == "fail" for c in data["checks"])

def test_validate_missing_scope():
    """缺 scope wiki 检测到错误"""
    result = subprocess.run(
        ["python", "skill/wiki-lint/scripts/validate_wiki.py",
         "skill/wiki-lint/tests/fixtures/missing-scope"],
        capture_output=True, text=True
    )
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert any(c["status"] == "fail" for c in data["checks"])

def test_no_external_deps():
    """脚本无外部依赖"""
    with open("skill/wiki-lint/scripts/validate_wiki.py") as f:
        source = f.read()
    stdlib_modules = {"os", "json", "sys", "argparse", "re", "pathlib", "yaml"}
    # 检查所有 import 是否来自标准库
    ...

def test_exit_codes():
    """标准退出码"""
    # 健康 wiki → 0
    # 不健康 wiki → 1
    ...
```

### Test Files to Create

| File | Purpose |
|------|---------|
| tests/test_validate_wiki_script.py | 脚本执行 + JSON 输出 + 退出码检查 |

## Edge Cases

- wiki_root 路径不存在
- wiki_root 下没有 WIKI.md
- wiki/pages/ 目录为空
- index.md 不存在
- 硬链接同步后 wiki-update 的 scripts/ 是否与源一致
