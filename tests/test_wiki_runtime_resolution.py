import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

_DEFAULT_CONFIG_DIR = "~/.wiki-config"

_WORKFLOW_SKILLS = ("wiki-ingest", "wiki-query", "wiki-lint", "wiki-update", "wiki-distill")


def _workspace_phrase(skill_name: str) -> str:
    if skill_name == "wiki-distill":
        return "当前工作目录"
    return "current working directory"


def _absolute_config_phrase(skill_name: str) -> str:
    if skill_name == "wiki-distill":
        return "绝对 `config-dir`"
    return "absolute config-dir"


def _default_config_phrase(skill_name: str) -> str:
    if skill_name == "wiki-distill":
        return "wiki/.wiki-config"
    return _DEFAULT_CONFIG_DIR


def _default_communication_phrases(skill_name: str) -> tuple[str, str]:
    if skill_name == "wiki-distill":
        return ("默认 wiki 配置", "告知用户")
    return ("default wiki config", "tell the user")


class WikiRuntimeResolutionTest(unittest.TestCase):
    def test_wiki_workflow_skills_resolve_runtime_from_wiki_md(self) -> None:
        for skill_name in _WORKFLOW_SKILLS:
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
                self.assertIn(_workspace_phrase(skill_name), content)
                self.assertIn(_absolute_config_phrase(skill_name), content)

    def test_wiki_workflows_include_default_config_dir_in_discovery_order(self) -> None:
        for skill_name in _WORKFLOW_SKILLS:
            with self.subTest(skill=skill_name):
                skill_path = REPO_ROOT / "skill" / skill_name / "SKILL.md"
                content = skill_path.read_text(encoding="utf-8")
                config_phrase = _default_config_phrase(skill_name)
                self.assertIn(
                    config_phrase,
                    content,
                    f"{skill_name} SKILL.md should mention {config_phrase} "
                    "in discovery order",
                )

                default_pos = content.index(config_phrase)
                workspace_phrase = _workspace_phrase(skill_name)
                workspace_pos = content.index(workspace_phrase)
                self.assertLess(
                    default_pos,
                    workspace_pos,
                    f"{skill_name}: {config_phrase} should appear "
                    "before workspace discovery",
                )

    def test_default_config_dir_usage_is_communicated_to_user(self) -> None:
        for skill_name in _WORKFLOW_SKILLS:
            with self.subTest(skill=skill_name):
                skill_path = REPO_ROOT / "skill" / skill_name / "SKILL.md"
                content = skill_path.read_text(encoding="utf-8")
                default_phrase, tell_phrase = _default_communication_phrases(skill_name)
                self.assertIn(
                    default_phrase,
                    content.lower() if skill_name != "wiki-distill" else content,
                    f"{skill_name} SKILL.md should mention '{default_phrase}' "
                    "when the default config-dir is used",
                )
                self.assertIn(
                    tell_phrase,
                    content.lower() if skill_name != "wiki-distill" else content,
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
