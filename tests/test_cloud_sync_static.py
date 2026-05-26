import pathlib
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class CloudSyncStaticTest(unittest.TestCase):
    def test_wiki_md_template_contains_sync_fields(self) -> None:
        template_path = REPO_ROOT / "skill" / "wiki-init" / "templates" / "WIKI.md"
        content = template_path.read_text(encoding="utf-8")
        self.assertIn("remote_sync_path", content)
        self.assertIn("auto_sync", content)

    def test_wiki_md_runtime_contains_sync_fields(self) -> None:
        wiki_md_path = REPO_ROOT / "WIKI.md"
        content = wiki_md_path.read_text(encoding="utf-8")
        self.assertIn("remote_sync_path", content)
        self.assertIn("auto_sync", content)

    def test_wiki_ingest_precondition_declares_sync_fields(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-ingest" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("remote_sync_path", content)
        self.assertIn("auto_sync", content)

    def test_wiki_ingest_has_step_12_cloud_sync(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-ingest" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("pcloud sync", content)
        self.assertIn("--dry-run", content)

    def test_wiki_init_reuse_crops_sync_fields(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-init" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("remote_sync_path", content)
        self.assertIn("auto_sync", content)

    def test_wiki_ingest_sync_non_blocking(self) -> None:
        skill_path = REPO_ROOT / "skill" / "wiki-ingest" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("do not", content.lower())
        self.assertIn("roll back", content.lower())


if __name__ == "__main__":
    unittest.main()
