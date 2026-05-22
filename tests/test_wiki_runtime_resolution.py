import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class WikiRuntimeResolutionTest(unittest.TestCase):
    def test_wiki_workflow_skills_resolve_runtime_from_wiki_md(self) -> None:
        for skill_name in ("wiki-ingest", "wiki-query", "wiki-lint", "wiki-update"):
            with self.subTest(skill=skill_name):
                skill_path = REPO_ROOT / "skill" / skill_name / "SKILL.md"
                self.assertTrue(
                    skill_path.exists(),
                    f"expected canonical {skill_name} skill in skill/",
                )

                content = skill_path.read_text(encoding="utf-8")
                self.assertIn("WIKI.md", content)
                self.assertIn("wiki_root", content)
                self.assertNotIn("CLAUDE.md", content)
                self.assertNotIn(".claude/skills/", content)
                self.assertNotIn(".agents/skills/", content)
                self.assertIn("wiki/index.md", content)
                self.assertIn("wiki/log.md", content)
                self.assertIn("current working directory", content)
                self.assertIn("absolute config-dir", content)


if __name__ == "__main__":
    unittest.main()
