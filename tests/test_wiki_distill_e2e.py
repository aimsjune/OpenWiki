import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_DISTILL_SKILL = REPO_ROOT / "skill" / "wiki-distill" / "SKILL.md"


class WikiDistillE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = _DISTILL_SKILL.read_text(encoding="utf-8")

    def test_skill_describes_complete_end_to_end_flow(self) -> None:
        self.assertIn("Phase 1: ANALYZE", self.content)
        self.assertIn("Phase 2: COMPARE", self.content)
        self.assertIn("Phase 3: DECIDE & MERGE", self.content)

    def test_skill_flows_from_analyze_to_compare(self) -> None:
        analyze_pos = self.content.index("Phase 1: ANALYZE")
        compare_pos = self.content.index("Phase 2: COMPARE")
        self.assertLess(analyze_pos, compare_pos)

    def test_skill_flows_from_compare_to_decide_and_merge(self) -> None:
        compare_pos = self.content.index("Phase 2: COMPARE")
        merge_pos = self.content.index("Phase 3: DECIDE & MERGE")
        self.assertLess(compare_pos, merge_pos)

    def test_skill_includes_common_mistakes_section(self) -> None:
        self.assertIn("常见错误", self.content)

    def test_common_mistakes_mentions_depth_appropriateness(self) -> None:
        self.assertIn("分析深度不合适", self.content)

    def test_common_mistakes_mentions_sanitization_verification(self) -> None:
        self.assertIn("脱敏过滤遗漏", self.content)

    def test_common_mistakes_mentions_comparison_granularity(self) -> None:
        self.assertIn("比对粒度太粗", self.content)

    def test_common_mistakes_mentions_user_decision_required(self) -> None:
        self.assertIn("跳过用户决策", self.content)

    def test_common_mistakes_mentions_lint_not_forgotten(self) -> None:
        self.assertIn("忘记委托 wiki-lint", self.content)

    def test_common_mistakes_mentions_state_file_update(self) -> None:
        self.assertIn("状态丢失", self.content)


if __name__ == "__main__":
    unittest.main()
