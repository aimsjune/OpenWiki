import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class SkillLayoutTest(unittest.TestCase):
    def test_public_wiki_skills_live_only_under_skill_directory(self) -> None:
        skill_root = REPO_ROOT / "skill"
        expected_skills = (
            "wiki-init",
            "wiki-ingest",
            "wiki-query",
            "wiki-lint",
            "wiki-update",
            "wiki-distill",
            "agent-browser",
        )

        for skill_name in expected_skills:
            with self.subTest(skill=skill_name):
                self.assertTrue(
                    (skill_root / skill_name / "SKILL.md").exists(),
                    f"expected {skill_name} under skill/",
                )
                self.assertFalse(
                    (REPO_ROOT / ".claude" / "skills" / skill_name / "SKILL.md").exists(),
                    f"did not expect legacy .claude/skills copy for {skill_name}",
                )
                self.assertFalse(
                    (REPO_ROOT / ".agents" / "skills" / skill_name / "SKILL.md").exists(),
                    f"did not expect legacy .agents/skills copy for {skill_name}",
                )


if __name__ == "__main__":
    unittest.main()
