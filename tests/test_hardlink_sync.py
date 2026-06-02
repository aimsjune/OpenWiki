"""测试硬链接同步：wiki-update 应与 wiki-lint 共享 references/、tests/、scripts/ 目录"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_hardlink_or_same(src, dst):
    """检查两个路径是否指向同一 inode（硬链接或同一文件）"""
    try:
        return os.stat(src).st_ino == os.stat(dst).st_ino
    except FileNotFoundError:
        return False


def run_tests():
    failures = []
    passed = 0

    lint_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-lint")
    update_dir = os.path.join(PROJECT_ROOT, "skill", "wiki-update")

    # Test 1: wiki-update references/ synced with wiki-lint
    try:
        lint_ref = os.path.join(lint_dir, "references")
        update_ref = os.path.join(update_dir, "references")
        assert os.path.isdir(update_ref), "skill/wiki-update/references/ 目录不存在"
        for fname in os.listdir(lint_ref):
            src = os.path.join(lint_ref, fname)
            dst = os.path.join(update_ref, fname)
            assert os.path.exists(dst), f"skill/wiki-update/references/{fname} 不存在"
            assert is_hardlink_or_same(src, dst), f"skill/wiki-update/references/{fname} 不是硬链接"
        passed += 1
        print("✓ test_wiki_update_references_synced")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_update_references_synced: {e}")

    # Test 2: wiki-update tests/ synced with wiki-lint
    try:
        lint_tests = os.path.join(lint_dir, "tests")
        update_tests = os.path.join(update_dir, "tests")
        assert os.path.isdir(update_tests), "skill/wiki-update/tests/ 目录不存在"

        def check_tree_synced(src_root, dst_root, rel=""):
            for name in os.listdir(src_root):
                src_path = os.path.join(src_root, name)
                dst_path = os.path.join(dst_root, name)
                if os.path.isdir(src_path):
                    assert os.path.isdir(dst_path), f"skill/wiki-update/tests/{rel}{name}/ 目录不存在"
                    check_tree_synced(src_path, dst_path, f"{rel}{name}/")
                else:
                    assert os.path.exists(dst_path), f"skill/wiki-update/tests/{rel}{name} 不存在"
                    assert is_hardlink_or_same(src_path, dst_path), f"skill/wiki-update/tests/{rel}{name} 不是硬链接"

        check_tree_synced(lint_tests, update_tests)
        passed += 1
        print("✓ test_wiki_update_tests_synced")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_update_tests_synced: {e}")

    # Test 3: wiki-update scripts/ synced with wiki-lint
    try:
        lint_scripts = os.path.join(lint_dir, "scripts")
        update_scripts = os.path.join(update_dir, "scripts")
        assert os.path.isdir(update_scripts), "skill/wiki-update/scripts/ 目录不存在"
        for fname in os.listdir(lint_scripts):
            src = os.path.join(lint_scripts, fname)
            dst = os.path.join(update_scripts, fname)
            assert os.path.exists(dst), f"skill/wiki-update/scripts/{fname} 不存在"
            assert is_hardlink_or_same(src, dst), f"skill/wiki-update/scripts/{fname} 不是硬链接"
        passed += 1
        print("✓ test_wiki_update_scripts_synced")
    except AssertionError as e:
        failures.append(f"✗ test_wiki_update_scripts_synced: {e}")

    print(f"\n{passed} passed, {len(failures)} failed")
    if failures:
        for f in failures:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
