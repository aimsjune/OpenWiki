import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

_DEFAULT_CONFIG_DIR = "~/.wiki-config"


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

    def test_wiki_workflows_include_default_config_dir_in_discovery_order(self) -> None:
        for skill_name in ("wiki-ingest", "wiki-query", "wiki-lint", "wiki-update"):
            with self.subTest(skill=skill_name):
                skill_path = REPO_ROOT / "skill" / skill_name / "SKILL.md"
                content = skill_path.read_text(encoding="utf-8")
                self.assertIn(
                    _DEFAULT_CONFIG_DIR,
                    content,
                    f"{skill_name} SKILL.md should mention {_DEFAULT_CONFIG_DIR} "
                    "in discovery order",
                )

                default_pos = content.index(_DEFAULT_CONFIG_DIR)
                workspace_pos = content.index("current working directory")
                self.assertLess(
                    default_pos,
                    workspace_pos,
                    f"{skill_name}: {_DEFAULT_CONFIG_DIR} should appear "
                    "before workspace discovery",
                )

    def test_default_config_dir_usage_is_communicated_to_user(self) -> None:
        for skill_name in ("wiki-ingest", "wiki-query", "wiki-lint", "wiki-update"):
            with self.subTest(skill=skill_name):
                skill_path = REPO_ROOT / "skill" / skill_name / "SKILL.md"
                content = skill_path.read_text(encoding="utf-8")
                self.assertIn(
                    "default wiki config",
                    content.lower(),
                    f"{skill_name} SKILL.md should mention 'default wiki config' "
                    "when the default config-dir is used",
                )
                self.assertIn(
                    "tell the user",
                    content.lower(),
                    f"{skill_name} SKILL.md should instruct the agent to "
                    "tell the user when default config is being used",
                )

    def test_wiki_init_recommends_default_config_dir(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-init" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        self.assertIn(
            _DEFAULT_CONFIG_DIR,
            content,
            f"wiki-init SKILL.md should recommend {_DEFAULT_CONFIG_DIR} "
            "as the default config-dir",
        )


if __name__ == "__main__":
    unittest.main()
