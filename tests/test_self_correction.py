"""测试自我纠错步骤：wiki-ingest 和 wiki-lint 应在执行后验证输出"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_body(filepath):
    with open(filepath) as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return ""


def run_tests():
    failures = []
    passed = 0

    # Test 1: wiki-ingest has verify step (re-read after write)
    try:
        body = extract_body(os.path.join(PROJECT_ROOT, "skill", "wiki-ingest", "SKILL.md"))
        has_verify = ("重读" in body or "重新读取" in body)
        assert has_verify, "wiki-ingest/SKILL.md 正文缺少自我纠错步骤（应包含'重读'或'重新读取'）"
        passed += 1
        print("✓ test_wiki_ingest_has_verify_step")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_ingest_has_verify_step: {e}")

    # Test 2: wiki-lint has verify step (check all pages scanned)
    try:
        body = extract_body(os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "SKILL.md"))
        has_verify = ("所有页面" in body or "页面数" in body)
        assert has_verify, "wiki-lint/SKILL.md 正文缺少自我纠错步骤（应包含'所有页面'或'页面数'）"
        passed += 1
        print("✓ test_wiki_lint_has_verify_step")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_lint_has_verify_step: {e}")

    print(f"\n{passed} passed, {len(failures)} failed")
    if failures:
        for f in failures:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
