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
                self.assertIn("openwiki.toml", content)
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

    def test_readmes_and_wiki_init_explain_existing_config_reuse(self) -> None:
        readme_expectations = {
            "README.md": "已连接现有 wiki",
            "README.en.md": "connected to the existing wiki",
            "README.ja.md": "既存の wiki に接続",
        }

        for readme_name, expected_phrase in readme_expectations.items():
            with self.subTest(readme=readme_name):
                content = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
                self.assertIn(expected_phrase, content)
                self.assertIn("config-dir", content)
                self.assertIn("wiki-query", content)

        skill_content = (REPO_ROOT / "skill" / "wiki-init" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("connected to the existing wiki", skill_content)
        self.assertIn("same `config-dir`", skill_content)
        self.assertIn("`wiki-query`", skill_content)

    def test_readmes_mention_default_config_dir(self) -> None:
        for readme_name in ("README.md", "README.en.md", "README.ja.md"):
            with self.subTest(readme=readme_name):
                content = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
                self.assertIn(
                    "~/.openwiki",
                    content,
                    f"{readme_name} should mention ~/.openwiki "
                    "as the default config directory",
                )


if __name__ == "__main__":
    unittest.main()
