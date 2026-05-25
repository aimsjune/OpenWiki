import unittest

from tests.e2e.harness import (
    CATEGORY_PLACEHOLDERS,
    build_temp_instance,
    fixture_path,
    run_ingest_reference,
    run_init_reference,
    run_query_reference,
    run_update_reference,
)


class WikiSkillWorkflowE2ETest(unittest.TestCase):
    def test_wiki_init_materializes_runtime_contract_and_wiki_layout(self) -> None:
        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        run_init_reference(
            instance=instance,
            domain="E2E testing knowledge base",
            source_types=["notes", "articles", "transcripts"],
            index_categories=[
                "Wiki Pages",
                "Concepts Pages",
                "Topic Relations",
                "Quick Navigation",
            ],
        )

        self.assertTrue((instance.config_dir / "WIKI.md").exists())
        self.assertTrue((instance.wiki_root / "raw").is_dir())
        self.assertTrue((instance.wiki_root / "wiki" / "index.md").exists())
        self.assertTrue((instance.wiki_root / "wiki" / "log.md").exists())
        self.assertTrue((instance.wiki_root / "wiki" / "pages").is_dir())
        self.assertTrue((instance.wiki_root / "concepts").is_dir())

        contract = (instance.config_dir / "WIKI.md").read_text(encoding="utf-8")
        index_md = (instance.wiki_root / "wiki" / "index.md").read_text(encoding="utf-8")
        log_md = (instance.wiki_root / "wiki" / "log.md").read_text(encoding="utf-8")
        expected_categories = [
            "Wiki Pages",
            "Concepts Pages",
            "Topic Relations",
            "Quick Navigation",
        ]

        self.assertIn(f"wiki_root: {instance.wiki_root}", contract)
        self.assertIn("domain: E2E testing knowledge base", contract)
        self.assertIn(
            "source_types:\n  - notes\n  - articles\n  - transcripts",
            contract,
        )
        self.assertIn(
            "index_categories:\n"
            "  - Wiki Pages\n"
            "  - Concepts Pages\n"
            "  - Topic Relations\n"
            "  - Quick Navigation",
            contract,
        )
        self.assertNotIn("<user domain description>", contract)
        for category in expected_categories:
            self.assertIn(category, index_md)
        for placeholder in CATEGORY_PLACEHOLDERS:
            self.assertNotIn(placeholder, contract)
            self.assertNotIn(placeholder, index_md)
        self.assertIn("init | E2E testing knowledge base", log_md)

    def test_wiki_init_rejects_empty_source_types_and_wrong_category_cardinality(
        self,
    ) -> None:
        invalid_cases = [
            (
                "empty source types",
                [],
                ["Wiki Pages", "Concepts Pages", "Topic Relations", "Quick Navigation"],
                "source_types must contain at least 1 entry",
            ),
            (
                "index categories",
                ["notes"],
                ["Wiki Pages", "Concepts Pages", "Topic Relations"],
                "index_categories must contain exactly 4 entries",
            ),
        ]

        for case_name, source_types, index_categories, message in invalid_cases:
            with self.subTest(case=case_name):
                instance = build_temp_instance()
                self.addCleanup(instance.temp_dir.cleanup)

                with self.assertRaisesRegex(ValueError, message):
                    run_init_reference(
                        instance=instance,
                        domain="E2E testing knowledge base",
                        source_types=source_types,
                        index_categories=index_categories,
                    )

                self.assertFalse((instance.config_dir / "WIKI.md").exists())
                self.assertFalse((instance.wiki_root / "wiki" / "index.md").exists())
                self.assertFalse((instance.wiki_root / "wiki" / "log.md").exists())

    def test_artifact_workflow_ingest_query_update(self) -> None:
        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        run_init_reference(
            instance=instance,
            domain="E2E testing knowledge base",
            source_types=["notes", "articles"],
            index_categories=[
                "Wiki Pages",
                "Concepts Pages",
                "Topic Relations",
                "Quick Navigation",
            ],
        )

        fixture_root = fixture_path()
        slug = run_ingest_reference(instance=instance, fixture_root=fixture_root)
        answer = run_query_reference(instance=instance, fixture_root=fixture_root)
        run_update_reference(instance=instance, fixture_root=fixture_root, slug=slug)

        page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
        raw_source_path = instance.wiki_root / "raw" / f"{slug}-source.md"
        source_md = (fixture_root / "source.md").read_text(encoding="utf-8")
        page_md = page_path.read_text(encoding="utf-8")
        index_md = (instance.wiki_root / "wiki" / "index.md").read_text(encoding="utf-8")
        log_md = (instance.wiki_root / "wiki" / "log.md").read_text(encoding="utf-8")

        self.assertEqual("local-first-wiki-testing", slug)
        self.assertTrue(page_path.exists())
        self.assertTrue(raw_source_path.exists())
        self.assertEqual(source_md, raw_source_path.read_text(encoding="utf-8"))
        self.assertIn("title: Local-First Wiki Testing", page_md)
        self.assertIn("tags: [testing, e2e]", page_md)
        self.assertIn("sources: 1", page_md)
        self.assertIn("updated: 2026-05-23", page_md)
        self.assertIn("**Source:** raw/local-first-wiki-testing-source.md", page_md)
        self.assertIn("**Date ingested:** 2026-05-22", page_md)
        self.assertIn("**Type:** article", page_md)
        self.assertIn("[[local-first-wiki-testing]]", index_md)
        self.assertIn("| [[local-first-wiki-testing]] |", index_md)
        self.assertIn("2026-05-23", index_md)
        self.assertIn("Artifact E2E runs without network access.", page_md)
        self.assertIn("Agent Smoke E2E validates a real compatible agent.", page_md)
        self.assertIn("[[local-first-wiki-testing]]", answer)
        self.assertIn("Artifact E2E runs without network access.", answer)
        self.assertIn("Agent Smoke E2E validates a real compatible agent.", answer)
        self.assertIn("Worth saving to `concepts/local-first-wiki-testing.md`?", answer)
        self.assertIn("The update now covers wiki-lint in a later phase.", page_md)
        self.assertNotIn("The first version excludes wiki-lint.", page_md)
        self.assertIn("ingest | Local-First Wiki Testing", log_md)
        self.assertIn("query | local-first-wiki-testing", log_md)
        self.assertIn("Pages read: local-first-wiki-testing", log_md)
        self.assertIn("update | local-first-wiki-testing", log_md)
        self.assertIn("Reason: fixture-driven update", log_md)
        self.assertIn("Source: raw/local-first-wiki-testing-source.md", log_md)

    def test_query_requires_existing_wiki_state(self) -> None:
        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        run_init_reference(
            instance=instance,
            domain="E2E testing knowledge base",
            source_types=["notes", "articles"],
            index_categories=[
                "Wiki Pages",
                "Concepts Pages",
                "Topic Relations",
                "Quick Navigation",
            ],
        )

        fixture_root = fixture_path()
        slug = run_ingest_reference(instance=instance, fixture_root=fixture_root)
        page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
        page_path.unlink()

        with self.assertRaisesRegex(
            ValueError,
            "query requires an ingested wiki page registered in the current wiki state",
        ):
            run_query_reference(instance=instance, fixture_root=fixture_root)

    def test_query_reads_only_key_takeaways_section(self) -> None:
        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        run_init_reference(
            instance=instance,
            domain="E2E testing knowledge base",
            source_types=["notes"],
            index_categories=[
                "Wiki Pages",
                "Concepts Pages",
                "Topic Relations",
                "Quick Navigation",
            ],
        )

        fixture_root = fixture_path()
        slug = run_ingest_reference(instance=instance, fixture_root=fixture_root)
        page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
        page_md = page_path.read_text(encoding="utf-8")
        page_md = page_md.replace(
            "## Key Takeaways",
            "## Scratchpad\n\n"
            "- Distractor note that must not appear in query output.\n"
            "- Another distractor line.\n\n"
            "## Key Takeaways",
        )
        page_path.write_text(page_md, encoding="utf-8")

        answer = run_query_reference(instance=instance, fixture_root=fixture_root)

        self.assertIn("Artifact E2E runs without network access.", answer)
        self.assertIn("Agent Smoke E2E validates a real compatible agent.", answer)
        self.assertNotIn("Distractor note that must not appear in query output.", answer)
        self.assertNotIn("Another distractor line.", answer)

    def test_update_replaces_only_target_takeaway_line(self) -> None:
        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        run_init_reference(
            instance=instance,
            domain="E2E testing knowledge base",
            source_types=["notes"],
            index_categories=[
                "Wiki Pages",
                "Concepts Pages",
                "Topic Relations",
                "Quick Navigation",
            ],
        )

        fixture_root = fixture_path()
        slug = run_ingest_reference(instance=instance, fixture_root=fixture_root)
        page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
        page_md = page_path.read_text(encoding="utf-8")
        page_md += (
            "\n## Notes\n\n"
            "- The first version excludes wiki-lint.\n"
        )
        page_path.write_text(page_md, encoding="utf-8")

        run_update_reference(instance=instance, fixture_root=fixture_root, slug=slug)

        updated_page_md = page_path.read_text(encoding="utf-8")
        self.assertIn("- The update now covers wiki-lint in a later phase.", updated_page_md)
        self.assertIn("## Notes\n\n- The first version excludes wiki-lint.", updated_page_md)
        self.assertEqual(
            1,
            updated_page_md.count("The first version excludes wiki-lint."),
        )

    def test_update_updates_only_matching_index_row_for_slug(self) -> None:
        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        run_init_reference(
            instance=instance,
            domain="E2E testing knowledge base",
            source_types=["notes"],
            index_categories=[
                "Wiki Pages",
                "Concepts Pages",
                "Topic Relations",
                "Quick Navigation",
            ],
        )

        fixture_root = fixture_path()
        slug = run_ingest_reference(instance=instance, fixture_root=fixture_root)
        index_path = instance.wiki_root / "wiki" / "index.md"
        index_md = index_path.read_text(encoding="utf-8")
        index_md += (
            "| [[other-testing-page]] | Another testing page | testing | 2026-05-22 |\n"
        )
        index_path.write_text(index_md, encoding="utf-8")

        run_update_reference(instance=instance, fixture_root=fixture_root, slug=slug)

        updated_index_md = index_path.read_text(encoding="utf-8")
        self.assertIn(
            "| [[local-first-wiki-testing]] | Local-first workflow notes | testing, e2e | 2026-05-23 |",
            updated_index_md,
        )
        self.assertIn(
            "| [[other-testing-page]] | Another testing page | testing | 2026-05-22 |",
            updated_index_md,
        )

    def test_update_rejects_duplicate_target_takeaway_lines(self) -> None:
        instance = build_temp_instance()
        self.addCleanup(instance.temp_dir.cleanup)

        run_init_reference(
            instance=instance,
            domain="E2E testing knowledge base",
            source_types=["notes"],
            index_categories=[
                "Wiki Pages",
                "Concepts Pages",
                "Topic Relations",
                "Quick Navigation",
            ],
        )

        fixture_root = fixture_path()
        slug = run_ingest_reference(instance=instance, fixture_root=fixture_root)
        page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
        original_page_md = page_path.read_text(encoding="utf-8")
        duplicated_page_md = original_page_md.replace(
            "- The first version excludes wiki-lint.\n",
            "- The first version excludes wiki-lint.\n"
            "- The first version excludes wiki-lint.\n",
        )
        page_path.write_text(duplicated_page_md, encoding="utf-8")
        index_path = instance.wiki_root / "wiki" / "index.md"
        original_index_md = index_path.read_text(encoding="utf-8")

        with self.assertRaisesRegex(
            ValueError,
            "update requires the target takeaway line to exist exactly once in Key Takeaways",
        ):
            run_update_reference(instance=instance, fixture_root=fixture_root, slug=slug)

        self.assertEqual(duplicated_page_md, page_path.read_text(encoding="utf-8"))
        self.assertEqual(original_index_md, index_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
