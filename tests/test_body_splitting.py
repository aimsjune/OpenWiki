"""测试正文拆分：wiki-lint 和 wiki-ingest 的 SKILL.md 正文精简 + references/ 文件存在性"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_body(filepath):
    """提取 SKILL.md 中 frontmatter 之后的行"""
    with open(filepath) as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return ""


def run_tests():
    failures = []
    passed = 0

    # Test 1: wiki-lint references exist
    base = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "references")
    try:
        assert os.path.exists(os.path.join(base, "rules-catalog.md")), \
            "skill/wiki-lint/references/rules-catalog.md 不存在"
        assert os.path.exists(os.path.join(base, "exemption-checklist.md")), \
            "skill/wiki-lint/references/exemption-checklist.md 不存在"
        passed += 1
        print("✓ test_wiki_lint_references_exist")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_lint_references_exist: {e}")

    # Test 2: wiki-lint body lines <= 80
    try:
        body = extract_body(os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "SKILL.md"))
        lines = [l for l in body.split("\n") if l.strip()]
        assert len(lines) <= 80, f"wiki-lint 正文 {len(lines)} 行，超过 80 行上限"
        passed += 1
        print("✓ test_wiki_lint_body_lines")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_lint_body_lines: {e}")

    # Test 3: wiki-ingest references exist
    base = os.path.join(PROJECT_ROOT, "skill", "wiki-ingest", "references")
    try:
        assert os.path.exists(os.path.join(base, "page-template.md")), \
            "skill/wiki-ingest/references/page-template.md 不存在"
        assert os.path.exists(os.path.join(base, "slug-rules.md")), \
            "skill/wiki-ingest/references/slug-rules.md 不存在"
        passed += 1
        print("✓ test_wiki_ingest_references_exist")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_ingest_references_exist: {e}")

    # Test 4: wiki-ingest body lines <= 100
    try:
        body = extract_body(os.path.join(PROJECT_ROOT, "skill", "wiki-ingest", "SKILL.md"))
        lines = [l for l in body.split("\n") if l.strip()]
        assert len(lines) <= 100, f"wiki-ingest 正文 {len(lines)} 行，超过 100 行上限"
        passed += 1
        print("✓ test_wiki_ingest_body_lines")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_ingest_body_lines: {e}")

    # Test 5: body contains references/ reference
    for skill in ["wiki-lint", "wiki-ingest"]:
        try:
            body = extract_body(os.path.join(PROJECT_ROOT, "skill", skill, "SKILL.md"))
            assert "references/" in body, f"{skill}/SKILL.md 正文未包含 references/ 引用"
            passed += 1
            print(f"✓ test_{skill}_body_references")
        except AssertionError as e:
            failures.append(f"✗ test_{skill}_body_references: {e}")

    print(f"\n{passed} passed, {len(failures)} failed")
    if failures:
        for f in failures:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
