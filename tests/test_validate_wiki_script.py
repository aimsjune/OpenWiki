"""测试 validate_wiki.py 验证脚本"""

import os
import sys
import subprocess
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "scripts", "validate_wiki.py")


def run_tests():
    failures = []
    passed = 0

    # Test 1: script exists
    try:
        assert os.path.exists(SCRIPT_PATH), "skill/wiki-lint/scripts/validate_wiki.py 不存在"
        passed += 1
        print("✓ test_script_exists")
    except AssertionError as e:
        failures.append(f"✗ test_script_exists: {e}")
        print(f"\n{passed} passed, {len(failures)} failed")
        for f in failures:
            print(f)
        sys.exit(1)

    # Test 2: script uses only stdlib (no external imports)
    try:
        with open(SCRIPT_PATH) as f:
            content = f.read()
        banned = ["import requests", "import yaml", "import toml", "import click", "import typer"]
        for b in banned:
            assert b not in content, f"validate_wiki.py 使用了外部依赖: {b}"
        passed += 1
        print("✓ test_script_no_external_deps")
    except AssertionError as e:
        failures.append(f"✗ test_script_no_external_deps: {e}")

    # Test 3: healthy-wiki fixture passes all checks
    try:
        fixture = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "tests", "fixtures", "healthy-wiki")
        result = subprocess.run(
            ["python3", SCRIPT_PATH, fixture],
            capture_output=True, text=True, timeout=10
        )
        output = json.loads(result.stdout)
        assert result.returncode == 0, f"healthy-wiki 应 exit 0，实际 exit {result.returncode}"
        for check in output.get("checks", []):
            assert check["status"] == "pass", f"healthy-wiki 检查 {check['name']} 应为 pass，实际 {check['status']}"
        passed += 1
        print("✓ test_healthy_wiki_passes")
    except (AssertionError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        failures.append(f"✗ test_healthy_wiki_passes: {e}")

    # Test 4: broken-links fixture detects broken links
    try:
        fixture = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "tests", "fixtures", "broken-links")
        result = subprocess.run(
            ["python3", SCRIPT_PATH, fixture],
            capture_output=True, text=True, timeout=10
        )
        output = json.loads(result.stdout)
        assert result.returncode == 1, f"broken-links 应 exit 1，实际 exit {result.returncode}"
        broken_check = [c for c in output.get("checks", []) if "broken" in c.get("name", "").lower() or "link" in c.get("name", "").lower()]
        if broken_check:
            assert broken_check[0]["status"] == "fail", f"broken-links 检查应为 fail"
        passed += 1
        print("✓ test_broken_links_detected")
    except (AssertionError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        failures.append(f"✗ test_broken_links_detected: {e}")

    # Test 5: missing-scope fixture detects missing scope
    try:
        fixture = os.path.join(PROJECT_ROOT, "skill", "wiki-lint", "tests", "fixtures", "missing-scope")
        result = subprocess.run(
            ["python3", SCRIPT_PATH, fixture],
            capture_output=True, text=True, timeout=10
        )
        output = json.loads(result.stdout)
        assert result.returncode == 1, f"missing-scope 应 exit 1，实际 exit {result.returncode}"
        scope_check = [c for c in output.get("checks", []) if "scope" in c.get("name", "").lower()]
        if scope_check:
            assert scope_check[0]["status"] == "fail", f"missing-scope 检查应为 fail"
        passed += 1
        print("✓ test_missing_scope_detected")
    except (AssertionError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        failures.append(f"✗ test_missing_scope_detected: {e}")

    print(f"\n{passed} passed, {len(failures)} failed")
    if failures:
        for f in failures:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
