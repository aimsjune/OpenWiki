import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_DISTILL_SKILL = REPO_ROOT / "skill" / "wiki-distill" / "SKILL.md"


class WikiDistillMergeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = _DISTILL_SKILL.read_text(encoding="utf-8")

    def test_new_delegates_to_wiki_ingest(self) -> None:
        self.assertIn("wiki-ingest", self.content)

    def test_new_one_experience_per_page(self) -> None:
        self.assertIn("每条 NEW 经验", self.content)
        self.assertIn("wiki page", self.content.lower())

    def test_new_describes_slug_generation(self) -> None:
        self.assertIn("slugify", self.content.lower())

    def test_new_describes_full_ingest_flow(self) -> None:
        self.assertIn("Phase 3: DECIDE & MERGE", self.content)

    def test_new_asks_user_for_confirmation(self) -> None:
        self.assertIn("是否将这条经验新增到 wiki", self.content)
        self.assertIn("[Y/n/修改适用范围]", self.content)

    def test_conflict_delegates_to_wiki_update(self) -> None:
        self.assertIn("openwiki page update", self.content)

    def test_conflict_shows_diff(self) -> None:
        self.assertIn("diff", self.content.lower())

    def test_conflict_uses_strategy_c(self) -> None:
        self.assertIn("策略C", self.content)

    def test_conflict_merges_and_annotates_sources(self) -> None:
        self.assertIn("经验来源", self.content)
        self.assertIn("wiki 来源", self.content)

    def test_conflict_describes_update_flow(self) -> None:
        self.assertIn("确认", self.content)
        self.assertIn("收尾：委托 wiki-lint", self.content)

    def test_conflict_asks_user_for_confirmation(self) -> None:
        self.assertIn("是否按建议合并", self.content)

    def test_exists_tells_user_covered(self) -> None:
        self.assertIn("已被 wiki 覆盖", self.content)
        self.assertIn("无需操作", self.content)

    def test_exists_logs_to_wiki_log(self) -> None:
        self.assertIn("wiki/log.md", self.content)

    def test_exists_does_not_create_pages(self) -> None:
        self.assertIn("无需操作", self.content)

    def test_post_merge_delegates_to_wiki_lint(self) -> None:
        self.assertIn("wiki-lint", self.content)

    def test_post_merge_lint_checks_consistency(self) -> None:
        self.assertIn("交叉引用", self.content)
        self.assertIn("孤立页面", self.content)
        self.assertIn("无新增矛盾", self.content)

    def test_post_merge_writes_full_log(self) -> None:
        self.assertIn("完整日志", self.content)
        self.assertIn("distill |", self.content)

    def test_post_merge_updates_incremental_state(self) -> None:
        self.assertIn("更新增量状态", self.content)
        self.assertIn("HEAD commit", self.content)


if __name__ == "__main__":
    unittest.main()
