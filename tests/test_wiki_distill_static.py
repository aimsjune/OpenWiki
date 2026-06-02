import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "skill"
_DISTILL_SKILL = SKILL_ROOT / "wiki-distill" / "SKILL.md"

DISALLOWED_REPOSITORY_REFERENCES = (
    "openspec/",
    "README.md",
    "README.en.md",
    "README.ja.md",
    "assets/",
)


class WikiDistillStaticTest(unittest.TestCase):
    def test_distill_skill_md_exists(self) -> None:
        self.assertTrue(
            _DISTILL_SKILL.exists(),
            "expected skill/wiki-distill/SKILL.md to exist",
        )

    def test_distill_skill_does_not_reference_disallowed_assets(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        for disallowed in DISALLOWED_REPOSITORY_REFERENCES:
            with self.subTest(disallowed=disallowed):
                self.assertNotIn(
                    disallowed,
                    content,
                    f"wiki-distill SKILL.md should not reference {disallowed}",
                )

    def test_distill_skill_has_valid_frontmatter(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertTrue(
            content.startswith("---"),
            "expected SKILL.md to start with YAML frontmatter",
        )
        self.assertIn("name: wiki-distill", content)
        self.assertIn("description:", content)

    def test_distill_precondition_matches_discovery_order(self) -> None:
        distill_content = _DISTILL_SKILL.read_text(encoding="utf-8")
        ingest_content = (
            SKILL_ROOT / "wiki-ingest" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("显式提供了 `config-dir`", distill_content)
        self.assertIn("explicitly provides a `config-dir`", ingest_content)

        self.assertIn("~/.openwiki", distill_content)
        self.assertIn("~/.openwiki", ingest_content)

        self.assertIn("当前工作目录", distill_content)
        self.assertIn("current working directory", ingest_content)

        self.assertIn("wiki-init", distill_content)
        self.assertIn("wiki-init` first", ingest_content)

    def test_distill_precondition_default_config_appears_before_workspace(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")

        default_pos = content.index("~/.openwiki")
        workspace_pos = content.index("当前工作目录")
        self.assertLess(
            default_pos,
            workspace_pos,
            "~/.openwiki should appear before workspace discovery in distill",
        )

    def test_distill_precondition_mentions_default_config_communication(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "默认 wiki 配置",
            content,
            "distill SKILL.md should mention '默认 wiki 配置'",
        )
        self.assertIn(
            "告知用户",
            content,
            "distill SKILL.md should instruct the agent to tell the user",
        )

    def test_distill_skill_resolves_wiki_md_fields(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("openwiki.toml", content)
        self.assertIn("wiki_root", content)
        self.assertIn("wiki/index.md", content)
        self.assertIn("wiki/log.md", content)
        self.assertIn("wiki/pages/", content)
        self.assertIn("raw/", content)
        self.assertIn("concepts/", content)
        self.assertNotIn("CLAUDE.md", content)
        self.assertNotIn(".claude/skills/", content)
        self.assertNotIn(".agents/skills/", content)

    def test_distill_skill_describes_three_phases(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("Phase 1: ANALYZE", content)
        self.assertIn("Phase 2: COMPARE", content)
        self.assertIn("Phase 3: DECIDE & MERGE", content)

    def test_distill_skill_describes_sanitization(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("脱敏", content)
        self.assertIn("redacted", content.lower())

    def test_distill_skill_describes_delegation_to_wiki_ingest(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("wiki-ingest", content)

    def test_distill_skill_describes_delegation_to_wiki_update(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("openwiki page update", content)

    def test_distill_skill_describes_delegation_to_wiki_lint(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("wiki-lint", content)

    def test_distill_skill_describes_incremental_mode(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("incremental", content.lower())
        self.assertIn("git diff", content.lower())

    def test_distill_skill_describes_depth_control(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("shallow", content.lower())
        self.assertIn("medium", content.lower())
        self.assertIn("deep", content.lower())

    def test_distill_skill_describes_dynamic_categories(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("动态", content)
        self.assertIn("dynamic", content.lower())

    def test_distill_skill_describes_conflict_strategy_c(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("策略C", content)
        self.assertIn("融合", content)

    def test_distill_skill_describes_new_one_experience_per_page(self) -> None:
        content = _DISTILL_SKILL.read_text(encoding="utf-8")
        self.assertIn("每条 NEW 经验", content)


if __name__ == "__main__":
    unittest.main()
