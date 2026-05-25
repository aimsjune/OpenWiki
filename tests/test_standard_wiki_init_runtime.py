import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class StandardWikiInitRuntimeTest(unittest.TestCase):
    def test_repo_has_root_wiki_contract_with_absolute_wiki_root(self) -> None:
        wiki_md = REPO_ROOT / "WIKI.md"

        self.assertTrue(wiki_md.exists(), "expected root WIKI.md to exist")

        content = wiki_md.read_text(encoding="utf-8")
        self.assertIn(
            f"wiki_root: {REPO_ROOT}",
            content,
            "expected WIKI.md to record the repository root as an absolute wiki_root",
        )
        self.assertTrue((REPO_ROOT / "raw").is_dir(), "expected raw/ under wiki_root")
        self.assertTrue((REPO_ROOT / "wiki").is_dir(), "expected wiki/ under wiki_root")
        self.assertTrue(
            (REPO_ROOT / "wiki" / "pages").is_dir(),
            "expected wiki/pages/ under wiki_root",
        )
        self.assertTrue(
            (REPO_ROOT / "wiki" / "index.md").exists(),
            "expected wiki/index.md under wiki_root",
        )
        self.assertTrue(
            (REPO_ROOT / "wiki" / "log.md").exists(),
            "expected wiki/log.md under wiki_root",
        )
        self.assertTrue(
            (REPO_ROOT / "concepts").is_dir(),
            "expected concepts/ under wiki_root",
        )

    def test_wiki_init_skill_requires_separate_config_dir_and_wiki_root(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-init" / "SKILL.md"

        self.assertTrue(skill_path.exists(), "expected canonical wiki-init skill in skill/")

        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("configuration directory", content)
        self.assertIn("wiki root directory", content)
        self.assertIn("WIKI.md", content)
        self.assertIn("absolute `wiki_root`", content)
        self.assertIn("raw/", content)
        self.assertIn("wiki/index.md", content)
        self.assertIn("wiki/log.md", content)
        self.assertIn("concepts/", content)

    def test_wiki_init_skill_reuses_existing_explicit_config_dir(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-init" / "SKILL.md"

        self.assertTrue(skill_path.exists(), "expected canonical wiki-init skill in skill/")

        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("explicitly provides a `config-dir`", content)
        self.assertIn("reuse the existing `WIKI.md`", content)
        self.assertIn("continue with the existing wiki instance", content)
        self.assertIn("rather than reinitializing", content)
        self.assertIn("do not rewrite `WIKI.md`", content)

    def test_wiki_init_skill_skips_known_fields_from_existing_wiki_md(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-init" / "SKILL.md"

        self.assertTrue(skill_path.exists(), "expected canonical wiki-init skill in skill/")

        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("skip asking for `wiki_root`", content)
        self.assertIn("`domain`", content)
        self.assertIn("`source_types`", content)
        self.assertIn("`index_categories`", content)
        self.assertIn("only ask for fields that are still missing", content)

    def test_wiki_init_skill_fails_fast_for_invalid_existing_wiki_config(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-init" / "SKILL.md"

        self.assertTrue(skill_path.exists(), "expected canonical wiki-init skill in skill/")

        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("fail fast", content)
        self.assertIn("missing `wiki_root`", content)
        self.assertIn("`wiki_root` is not absolute", content)
        self.assertIn("required wiki layout is missing", content)
        self.assertIn("do not rewrite `WIKI.md`", content)
        self.assertIn("explicitly chooses `reinitialize`", content)

    def test_wiki_init_index_template_uses_category_placeholders(self) -> None:
        template_path = REPO_ROOT / "skill" / "wiki-init" / "templates" / "index.md"
        wiki_contract_template_path = (
            REPO_ROOT / "skill" / "wiki-init" / "templates" / "WIKI.md"
        )
        skill_path = REPO_ROOT / "skill" / "wiki-init" / "SKILL.md"

        self.assertTrue(template_path.exists(), "expected wiki-init index template")
        self.assertTrue(
            wiki_contract_template_path.exists(),
            "expected wiki-init WIKI contract template",
        )

        template_content = template_path.read_text(encoding="utf-8")
        wiki_contract_template_content = wiki_contract_template_path.read_text(
            encoding="utf-8"
        )
        skill_content = skill_path.read_text(encoding="utf-8")

        self.assertIn("<category_1>", template_content)
        self.assertIn("<category_2>", template_content)
        self.assertIn("<category_3>", template_content)
        self.assertIn("<category_4>", template_content)
        self.assertIn("<category_1>", wiki_contract_template_content)
        self.assertIn("<category_2>", wiki_contract_template_content)
        self.assertIn("<category_3>", wiki_contract_template_content)
        self.assertIn("<category_4>", wiki_contract_template_content)
        self.assertIn("user-selected categories", skill_content)


if __name__ == "__main__":
    unittest.main()
