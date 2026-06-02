"""测试运行器: fix-date-placeholders — 验证日期列名一致性和 <today> 替换规则。"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(rel_path):
    with open(os.path.join(REPO_ROOT, rel_path), "r") as f:
        return f.read()


def run_tests():
    passed = 0
    failed = 0
    errors = []

    def check(name, condition, msg=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  PASS {name}")
        else:
            failed += 1
            print(f"  FAIL {name}: {msg}")
            errors.append((name, msg))

    # ── Behavior 1: wiki/index.md category_2 列名 ──
    print("\n=== Behavior 1: wiki/index.md category_2 列名 ===")
    idx = read_file("wiki/index.md")
    check("category_2 列名为 '最后更新'", "| 页面 | 类型 | 最后更新 |" in idx)

    # ── Behavior 2: 模板 index.md category_2 列名 ──
    print("\n=== Behavior 2: 模板 index.md category_2 列名 ===")
    tmpl = read_file("skill/wiki-init/templates/index.md")
    check("模板 category_2 列名为 '最后更新'", "| 页面 | 类型 | 最后更新 |" in tmpl)

    # ── Behavior 3: wiki-ingest <today> 替换规则 ──
    print("\n=== Behavior 3: wiki-ingest <today> 替换规则 ===")
    ingest = read_file("skill/wiki-ingest/SKILL.md")
    check("ingest 包含 YYYY-MM-DD", "YYYY-MM-DD" in ingest)

    # ── Behavior 4: wiki-distill <today> 替换规则 ──
    print("\n=== Behavior 4: wiki-distill <today> 替换规则 ===")
    distill = read_file("skill/wiki-distill/SKILL.md")
    check("distill 包含 YYYY-MM-DD", "YYYY-MM-DD" in distill)

    # ── Behavior 5: wiki-query <today> 替换规则 ──
    print("\n=== Behavior 5: wiki-query <today> 替换规则 ===")
    query = read_file("skill/wiki-query/SKILL.md")
    check("query 包含 YYYY-MM-DD", "YYYY-MM-DD" in query)

    # ── Behavior 6: wiki-lint <today> 替换规则 + hardcoded 规则 ──
    print("\n=== Behavior 6: wiki-lint <today> 替换规则 + hardcoded 规则 ===")
    lint = read_file("skill/wiki-lint/SKILL.md")
    check("lint 包含 YYYY-MM-DD", "YYYY-MM-DD" in lint)
    check("lint 包含 hardcoded-or-literal-today", "hardcoded-or-literal-today" in lint)

    # ── Behavior 7: log.md 模板 <today> 替换规则 ──
    print("\n=== Behavior 7: log.md 模板 <today> 替换规则 ===")
    log = read_file("skill/wiki-init/templates/log.md")
    check("log 模板包含 YYYY-MM-DD", "YYYY-MM-DD" in log)

    print(f"\n{'='*50}")
    print(f"结果: {passed} passed, {failed} failed, {passed+failed} total")
    if errors:
        print("\n失败详情:")
        for name, msg in errors:
            print(f"  - {name}: {msg}")
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
