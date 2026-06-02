"""测试各 skill 的 tests/ 目录和 fixtures 结构"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    failures = []
    passed = 0

    # Test 1: wiki-lint tests/ directory exists
    try:
        tests_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "tests")
        assert os.path.isdir(tests_dir), "skill/wiki-lint/tests/ 目录不存在"
        passed += 1
        print("✓ test_wiki_lint_tests_dir")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_lint_tests_dir: {e}")

    # Test 2: wiki-lint fixtures exist
    try:
        fixtures_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "tests", "fixtures")
        assert os.path.isdir(fixtures_dir), "skill/wiki-lint/tests/fixtures/ 目录不存在"
        for name in ["healthy-wiki", "broken-links", "missing-scope"]:
            d = os.path.join(fixtures_dir, name)
            assert os.path.isdir(d), f"skill/wiki-lint/tests/fixtures/{name}/ 目录不存在"
        passed += 1
        print("✓ test_wiki_lint_fixtures")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_lint_fixtures: {e}")

    # Test 3: wiki-lint test_cases.md exists
    try:
        tc = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "tests", "test_cases.md")
        assert os.path.exists(tc), "skill/wiki-lint/tests/test_cases.md 不存在"
        passed += 1
        print("✓ test_wiki_lint_test_cases")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_lint_test_cases: {e}")

    # Test 4: wiki-ingest tests/ directory exists
    try:
        tests_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-ingest", "tests")
        assert os.path.isdir(tests_dir), "skill/wiki-ingest/tests/ 目录不存在"
        passed += 1
        print("✓ test_wiki_ingest_tests_dir")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_ingest_tests_dir: {e}")

    # Test 5: wiki-ingest fixtures exist
    try:
        fixtures_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-ingest", "tests", "fixtures")
        assert os.path.isdir(fixtures_dir), "skill/wiki-ingest/tests/fixtures/ 目录不存在"
        for name in ["url-source", "file-source"]:
            d = os.path.join(fixtures_dir, name)
            assert os.path.isdir(d), f"skill/wiki-ingest/tests/fixtures/{name}/ 目录不存在"
        passed += 1
        print("✓ test_wiki_ingest_fixtures")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_ingest_fixtures: {e}")

    # Test 6: wiki-distill tests/ directory exists
    try:
        tests_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-distill", "tests")
        assert os.path.isdir(tests_dir), "skill/wiki-distill/tests/ 目录不存在"
        passed += 1
        print("✓ test_wiki_distill_tests_dir")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_distill_tests_dir: {e}")

    # Test 7: wiki-distill fixtures exist
    try:
        fixtures_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-distill", "tests", "fixtures")
        assert os.path.isdir(fixtures_dir), "skill/wiki-distill/tests/fixtures/ 目录不存在"
        for name in ["go-project", "python-project"]:
            d = os.path.join(fixtures_dir, name)
            assert os.path.isdir(d), f"skill/wiki-distill/tests/fixtures/{name}/ 目录不存在"
        passed += 1
        print("✓ test_wiki_distill_fixtures")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_distill_fixtures: {e}")

    print(f"\n{passed} passed, {len(failures)} failed")
    if failures:
        for f in failures:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
