import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_DISTILL_SKILL = REPO_ROOT / "skill" / "wiki-distill" / "SKILL.md"


class WikiDistillAnalyzeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = _DISTILL_SKILL.read_text(encoding="utf-8")

    def test_analyze_phase_describes_report_output_path(self) -> None:
        self.assertIn("raw/distill-", self.content)
        self.assertIn(".md", self.content)

    def test_analyze_phase_describes_frontmatter_fields(self) -> None:
        self.assertIn("project:", self.content)
        self.assertIn("distilled_at:", self.content)
        self.assertIn("depth:", self.content)
        self.assertIn("mode:", self.content)
        self.assertIn("categories:", self.content)
        self.assertIn("dynamic_categories:", self.content)

    def test_analyze_phase_describes_default_categories(self) -> None:
        for category in ("设计原则", "代码模式", "错误处理", "测试策略", "架构决策", "安全实践"):
            with self.subTest(category=category):
                self.assertIn(category, self.content)

    def test_analyze_phase_describes_project_path_parameter(self) -> None:
        self.assertIn("--project", self.content)
        self.assertIn("当前仓库", self.content)

    def test_analyze_phase_describes_depth_parameter(self) -> None:
        self.assertIn("--depth", self.content)

    def test_analyze_phase_describes_full_parameter(self) -> None:
        self.assertIn("--full", self.content)

    def test_analyze_phase_describes_three_depth_levels(self) -> None:
        content_lower = self.content.lower()
        self.assertIn("shallow", content_lower)
        self.assertIn("medium", content_lower)
        self.assertIn("deep", content_lower)

    def test_analyze_phase_describes_shallow_depth_scope(self) -> None:
        self.assertIn("README", self.content)
        self.assertIn("配置文件", self.content)
        self.assertIn("顶层目录结构", self.content)

    def test_analyze_phase_describes_medium_depth_scope(self) -> None:
        self.assertIn("关键模块", self.content)
        self.assertIn("接口设计", self.content)

    def test_analyze_phase_describes_deep_depth_scope(self) -> None:
        self.assertIn("实现细节", self.content)
        self.assertIn("算法选择", self.content)

    def test_sanitization_describes_personal_info_filtering(self) -> None:
        self.assertIn("姓名", self.content)
        self.assertIn("邮箱", self.content)
        self.assertIn("手机号码", self.content)

    def test_sanitization_describes_credential_filtering(self) -> None:
        self.assertIn("api keys", self.content.lower())
        self.assertIn("tokens", self.content.lower())
        self.assertIn("passwords", self.content.lower())

    def test_sanitization_describes_network_filtering(self) -> None:
        self.assertIn("内网 IP", self.content)
        self.assertIn("内部域名", self.content)

    def test_sanitization_describes_crypto_filtering(self) -> None:
        self.assertIn("加密算法", self.content)

    def test_sanitization_uses_redacted_marker(self) -> None:
        self.assertIn("redacted", self.content.lower())

    def test_sanitization_describes_filtered_entry_handling(self) -> None:
        self.assertIn("filtered", self.content.lower())

    def test_analyze_phase_describes_report_summary_to_user(self) -> None:
        self.assertIn("报告路径", self.content)
        self.assertIn("脱敏过滤统计", self.content)

    def test_analyze_phase_asks_user_to_continue(self) -> None:
        self.assertIn("继续进入比对阶段", self.content)

    def test_incremental_mode_describes_state_file(self) -> None:
        self.assertIn(".distill-", self.content)
        self.assertIn("-state", self.content)

    def test_incremental_mode_describes_git_diff(self) -> None:
        self.assertIn("git diff", self.content.lower())

    def test_incremental_mode_describes_full_fallback(self) -> None:
        self.assertIn("无 git 仓库", self.content)

    def test_dynamic_categories_described(self) -> None:
        self.assertIn("动态", self.content)
        self.assertIn("dynamic", self.content.lower())

    def test_dynamic_categories_conflict_handling(self) -> None:
        self.assertIn("合并为同一分类", self.content)


if __name__ == "__main__":
    unittest.main()
