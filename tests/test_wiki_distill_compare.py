import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_DISTILL_SKILL = REPO_ROOT / "skill" / "wiki-distill" / "SKILL.md"


class WikiDistillCompareTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = _DISTILL_SKILL.read_text(encoding="utf-8")

    def test_compare_phase_loads_wiki_content(self) -> None:
        self.assertIn("wiki/index.md", self.content)
        self.assertIn("wiki/pages/", self.content)
        self.assertIn("加载 wiki", self.content)

    def test_compare_phase_describes_statement_level_matching(self) -> None:
        self.assertIn("声明", self.content)
        self.assertIn("语义比对", self.content)

    def test_compare_phase_defines_new_category(self) -> None:
        self.assertIn("NEW", self.content)
        self.assertIn("无对应页面", self.content)

    def test_compare_phase_defines_conflict_category(self) -> None:
        self.assertIn("CONFLICT", self.content)
        self.assertIn("矛盾", self.content)

    def test_compare_phase_defines_exists_category(self) -> None:
        self.assertIn("EXISTS", self.content)
        self.assertIn("完全一致", self.content)

    def test_compare_phase_shows_new_format(self) -> None:
        self.assertIn("NEW: <经验标题>", self.content)
        self.assertIn("Wiki 状态: 无对应内容", self.content)

    def test_compare_phase_shows_conflict_format(self) -> None:
        self.assertIn("CONFLICT: <经验标题>", self.content)
        self.assertIn("当前 wiki", self.content)
        self.assertIn("建议", self.content)

    def test_compare_phase_shows_exists_format(self) -> None:
        self.assertIn("EXISTS: <经验标题>", self.content)
        self.assertIn("已覆盖于", self.content)


if __name__ == "__main__":
    unittest.main()
