import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATORS = (
    REPO_ROOT / "skill" / "wiki-lint" / "scripts" / "validate_wiki.py",
    REPO_ROOT / "skill" / "wiki-update" / "scripts" / "validate_wiki.py",
)


class ValidateWikiCurrentRuntimeTest(unittest.TestCase):
    def test_validators_accept_current_index_and_cross_directory_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_runtime(root, target="concept-page")

            for validator in VALIDATORS:
                with self.subTest(validator=validator):
                    result = subprocess.run(
                        ["python3", str(validator), str(root)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    checks = json.loads(result.stdout)["checks"]
                    self.assertTrue(all(check["status"] == "pass" for check in checks))

    def test_validators_detect_broken_cross_directory_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_runtime(root, target="missing-concept")

            for validator in VALIDATORS:
                with self.subTest(validator=validator):
                    result = subprocess.run(
                        ["python3", str(validator), str(root)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(1, result.returncode)
                    checks = json.loads(result.stdout)["checks"]
                    link_check = next(check for check in checks if check["name"] == "cross-references")
                    self.assertEqual("fail", link_check["status"])

    def _write_runtime(self, root: Path, target: str) -> None:
        (root / "wiki" / "pages").mkdir(parents=True)
        (root / "concepts").mkdir()
        (root / "entities").mkdir()
        (root / "openwiki.toml").write_text(
            f'wiki_root = "{root}"\n\n[wiki]\nprimary_language = "zh"\n',
            encoding="utf-8",
        )
        (root / "wiki" / "index.md").write_text(
            """# Wiki 索引

## 资料页

| Slug | 标题 | 类型 | 标签 | 适用范围 | 最后更新 |
|------|------|------|------|----------|----------|
| source-page | 来源页 | page | test | domain/root-cause-analysis | 2026-06-08 |

## 实体页

| Slug | 标题 | 类型 | 标签 | 适用范围 | 最后更新 |
|------|------|------|------|----------|----------|

## 概念页

| Slug | 标题 | 类型 | 标签 | 适用范围 | 最后更新 |
|------|------|------|------|----------|----------|
| concept-page | 概念页 | concept | test | domain/root-cause-analysis | 2026-06-08 |
""",
            encoding="utf-8",
        )
        (root / "wiki" / "pages" / "source-page.md").write_text(
            f"""---
title: 来源页
tags:
  - 测试
  - test
updated: 2026-06-08
scope_level: domain
scope_code: root-cause-analysis
---

# 来源页

关联 [[{target}]]。
""",
            encoding="utf-8",
        )
        (root / "concepts" / "concept-page.md").write_text(
            """---
title: 概念页
tags:
  - 测试
updated: 2026-06-08
scope_level: domain
scope_code: root-cause-analysis
---

# 概念页
""",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
