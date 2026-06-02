"""测试 composes 依赖声明：wiki-distill 和 wiki-update 应在 frontmatter 中声明依赖"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_frontmatter(filepath):
    """简单解析 YAML frontmatter，仅支持单层键值对和列表"""
    with open(filepath) as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_text = parts[1].strip()
    result = {}
    current_key = None
    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key:
            val = stripped[2:].strip()
            if val.startswith("[") and val.endswith("]"):
                result[current_key] = [v.strip() for v in val[1:-1].split(",")]
            else:
                result.setdefault(current_key, []).append(val)
        elif ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                result[key] = [v.strip() for v in val[1:-1].split(",")]
            else:
                result[key] = val
                current_key = key
    return result


def run_tests():
    failures = []
    passed = 0

    # Test 1: wiki-distill has composes field
    try:
        fm = parse_frontmatter(os.path.join(PROJECT_ROOT, "skill", "wiki-distill", "SKILL.md"))
        assert "composes" in fm, "wiki-distill/SKILL.md frontmatter 缺少 composes 字段"
        composes = fm["composes"]
        assert isinstance(composes, list), "wiki-distill composes 应为列表"
        for skill in ["wiki-ingest", "wiki-lint"]:
            assert skill in composes, f"wiki-distill composes 应包含 {skill}"
        passed += 1
        print("✓ test_wiki_distill_composes")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_distill_composes: {e}")

    # Test 2: wiki-update has composes field
    try:
        fm = parse_frontmatter(os.path.join(PROJECT_ROOT, "skill", "wiki-update", "SKILL.md"))
        assert "composes" in fm, "wiki-update/SKILL.md frontmatter 缺少 composes 字段"
        composes = fm["composes"]
        assert isinstance(composes, list), "wiki-update composes 应为列表"
        for skill in ["wiki-ingest", "wiki-lint", "wiki-init"]:
            assert skill in composes, f"wiki-update composes 应包含 {skill}"
        passed += 1
        print("✓ test_wiki_update_composes")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_update_composes: {e}")

    # Test 3: Independent skills do NOT have composes
    for skill in ["wiki-init", "wiki-ingest", "wiki-lint", "wiki-query"]:
        try:
            fm = parse_frontmatter(os.path.join(PROJECT_ROOT, "skill", skill, "SKILL.md"))
            composes = fm.get("composes", [])
            assert composes == [], f"{skill}/SKILL.md 不应有 composes 字段（独立技能）"
            passed += 1
            print(f"✓ test_{skill}_no_composes")
        except AssertionError as e:
            failures.append(f"✗ test_{skill}_no_composes: {e}")

    print(f"\n{passed} passed, {len(failures)} failed")
    if failures:
        for f in failures:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
