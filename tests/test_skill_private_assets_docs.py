import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

README_FILES = ("README.md", "README.en.md", "README.ja.md")
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


if __name__ == "__main__":
    unittest.main()
