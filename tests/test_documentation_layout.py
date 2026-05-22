import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class DocumentationLayoutTest(unittest.TestCase):
    def test_readmes_teach_neutral_wiki_contract(self) -> None:
        disallowed_phrases = {
            "README.md": "运行时契约示例",
            "README.en.md": "example runtime contract",
            "README.ja.md": "ランタイム契約例",
        }

        for readme_name in ("README.md", "README.en.md", "README.ja.md"):
            with self.subTest(readme=readme_name):
                content = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
                self.assertIn("WIKI.md", content)
                self.assertIn("skill/", content)
                self.assertIn("config-dir", content)
                self.assertIn("wiki-root", content)
                self.assertNotIn("CLAUDE.md", content)
                self.assertNotIn(".claude/skills/", content)
                self.assertNotIn(".agents/skills/", content)
                self.assertNotIn(disallowed_phrases[readme_name], content)

    def test_legacy_runtime_entrypoint_files_are_removed(self) -> None:
        self.assertFalse((REPO_ROOT / "CLAUDE.md").exists())
        self.assertFalse((REPO_ROOT / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
