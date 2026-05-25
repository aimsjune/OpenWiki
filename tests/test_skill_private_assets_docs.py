import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

README_FILES = ("README.md", "README.en.md", "README.ja.md")
EXPECTED_CWD_PHRASE = {
    "README.md": "仓库根目录",
    "README.en.md": "repository root",
    "README.ja.md": "リポジトリルート",
}
APPROVED_SKILL_LOCAL_DIRS = (
    "templates/",
    "examples/",
    "fixtures/",
    "assets/",
    "scripts/",
)


class SkillPrivateAssetsDocsTest(unittest.TestCase):
    def test_readmes_document_skill_private_asset_boundary(self) -> None:
        for readme_name in README_FILES:
            with self.subTest(readme=readme_name):
                content = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
                self.assertIn("skill/ASSET-LAYOUT.md", content)
                self.assertIn("skill-private", content)
                self.assertIn("runtime", content)
                for directory_name in APPROVED_SKILL_LOCAL_DIRS:
                    self.assertIn(directory_name, content)

    def test_readmes_document_fast_and_slow_e2e_commands(self) -> None:
        for readme_name in README_FILES:
            with self.subTest(readme=readme_name):
                content = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
                self.assertIn("tests.test_wiki_skill_workflow_e2e", content)
                self.assertIn("tests.test_agent_skill_smoke_e2e", content)
                self.assertIn("SKILL_AGENT_E2E=1", content)
                self.assertIn("SKILL_AGENT_RUNNER", content)
                self.assertIn("stdin", content)
                self.assertIn("stdout", content)
                self.assertIn(EXPECTED_CWD_PHRASE[readme_name], content)


if __name__ == "__main__":
    unittest.main()
