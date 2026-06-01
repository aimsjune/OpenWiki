"""简单测试运行器: scope-metadata 静态验证。"""
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

    # ── Behavior 1: Page Frontmatter 模板新增 scope 字段 ──
    print("\n=== Behavior 1: Page Frontmatter scope 字段 ===")
    content = read_file("skill/wiki-ingest/SKILL.md")
    check("scope_level in ingest template", "scope_level:" in content)
    check("scope_code in ingest template", "scope_code:" in content)
    check("适用范围 in ingest template body", "**适用范围：**" in content)

    # ── Behavior 2-5: wiki-lint scope 规则 ──
    print("\n=== Behavior 2-5: wiki-lint scope 规则 ===")
    lint = read_file("skill/wiki-lint/SKILL.md")
    check("invalid-scope-level rule", "invalid-scope-level" in lint)
    check("invalid-scope-code-format rule", "invalid-scope-code-format" in lint)
    check("scope-level-code-mismatch rule", "scope-level-code-mismatch" in lint)
    check("missing-scope-fields rule", "missing-scope-fields" in lint)

    # ── Behavior 6: wiki-ingest step3 scope 确认 ──
    print("\n=== Behavior 6: ingest step3 scope 确认 ===")
    check("适用范围 in ingest SKILL.md", "适用范围" in content)

    # ── Behavior 7: wiki-ingest step9 category_3 ──
    print("\n=== Behavior 7: ingest step9 category_3 ===")
    check("category_3 in ingest SKILL.md", "category_3" in content)

    # ── Behavior 8: wiki-distill Phase 3 scope ──
    print("\n=== Behavior 8: distill Phase 3 scope ===")
    distill = read_file("skill/wiki-distill/SKILL.md")
    check("scope in distill SKILL.md", "scope" in distill.lower())
    check("适用范围 in distill SKILL.md", "适用范围" in distill)

    # ── Behavior 9: index.md 模板 category_3 列名 ──
    print("\n=== Behavior 9: index.md 模板 category_3 ===")
    tmpl = read_file("skill/wiki-init/templates/index.md")
    check("范围代号 in index template", "范围代号" in tmpl)
    check("最后更新 in index template", "最后更新" in tmpl)

    # ── Behavior 10: wiki-query scope ──
    print("\n=== Behavior 10: wiki-query scope ===")
    query = read_file("skill/wiki-query/SKILL.md")
    check("scope/适用范围 in query SKILL.md", "scope" in query.lower() or "适用范围" in query)

    # ── Behavior 11: wiki-update scope ──
    print("\n=== Behavior 11: wiki-update scope ===")
    update = read_file("skill/wiki-update/SKILL.md")
    check("scope/适用范围 in update SKILL.md", "scope" in update.lower() or "适用范围" in update)

    # ── Behavior 12: scope 中文映射表 ──
    print("\n=== Behavior 12: scope 中文映射表 ===")
    mapping = {"repo": "代码仓库", "domain": "领域", "company": "公司", "industry": "行业", "wisdom": "智慧"}
    for en, zh in mapping.items():
        check(f"mapping {en}→{zh}", en in content and zh in content)

    # ── Behavior 13: 运行时 wiki/index.md ──
    print("\n=== Behavior 13: 运行时 wiki/index.md ===")
    idx = read_file("wiki/index.md")
    check("适用范围 in wiki/index.md", "适用范围" in idx)

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
