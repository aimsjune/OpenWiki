import pathlib
import re
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "skill"

PUBLIC_WIKI_SKILLS = (
    "wiki-init",
    "wiki-ingest",
    "wiki-query",
    "wiki-lint",
    "wiki-update",
    "wiki-distill",
)

ALLOWED_RUNTIME_REFERENCES = (
    "WIKI.md",
    "raw/",
    "wiki/",
    "concepts/",
    "wiki/index.md",
    "wiki/log.md",
    "wiki/pages/",
)

DISALLOWED_REPOSITORY_REFERENCES = (
    "README.md",
    "README.en.md",
    "README.ja.md",
    "assets/",
    "openspec/",
)

APPROVED_SKILL_LOCAL_DIRS = (
    "templates",
    "examples",
    "fixtures",
    "assets",
    "scripts",
)


def read_public_skill_contents() -> dict[str, str]:
    return {
        skill_name: (SKILL_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")
        for skill_name in PUBLIC_WIKI_SKILLS
    }


def is_disallowed_repository_reference(reference: str) -> bool:
    normalized = reference.lstrip("./")
    path = pathlib.PurePosixPath(normalized)
    parts = path.parts
    if not parts:
        return False

    if parts[0] == "openspec":
        return True
    if parts[0] == "assets":
        return True
    if normalized in {"README.md", "README.en.md", "README.ja.md"}:
        return True
    return False


def extract_path_like_references(content: str) -> list[str]:
    return re.findall(r"`([^`]+)`", content)


class SkillPrivateAssetsBoundaryTest(unittest.TestCase):
    def test_public_wiki_skills_allow_runtime_refs_and_forbid_repo_loose_assets(
        self,
    ) -> None:
        layout_guide = SKILL_ROOT / "ASSET-LAYOUT.md"
        self.assertTrue(
            layout_guide.exists(),
            "expected repository skill asset layout guidance at skill/ASSET-LAYOUT.md",
        )

        guide_content = layout_guide.read_text(encoding="utf-8")
        for allowed in ALLOWED_RUNTIME_REFERENCES:
            with self.subTest(allowed=allowed):
                self.assertIn(allowed, guide_content)

        for disallowed in DISALLOWED_REPOSITORY_REFERENCES:
            with self.subTest(disallowed=disallowed):
                self.assertIn(disallowed, guide_content)

        for skill_name, content in read_public_skill_contents().items():
            with self.subTest(skill=skill_name):
                self.assertTrue(
                    any(ref in content for ref in ALLOWED_RUNTIME_REFERENCES),
                    f"expected {skill_name} to reference runtime wiki objects",
                )
                extracted_refs = extract_path_like_references(content)
                violations = [
                    ref for ref in extracted_refs if is_disallowed_repository_reference(ref)
                ]
                self.assertEqual(
                    [],
                    violations,
                    f"did not expect {skill_name} to depend on repository-level assets",
                )

    def test_wiki_init_owned_templates_live_under_own_skill_directory(self) -> None:
        wiki_init_skill = SKILL_ROOT / "wiki-init" / "SKILL.md"
        wiki_init_content = wiki_init_skill.read_text(encoding="utf-8")

        expected_templates = (
            "skill/wiki-init/templates/WIKI.md",
            "skill/wiki-init/templates/index.md",
            "skill/wiki-init/templates/log.md",
        )

        for template_path in expected_templates:
            with self.subTest(template=template_path):
                self.assertIn(
                    template_path,
                    wiki_init_content,
                    "expected wiki-init to reference its own local template asset",
                )
                self.assertTrue(
                    (REPO_ROOT / template_path).exists(),
                    "expected referenced wiki-init template to exist under the owning skill directory",
                )

        for skill_name, content in read_public_skill_contents().items():
            if skill_name == "wiki-init":
                continue

            with self.subTest(other_skill=skill_name):
                self.assertNotIn("skill/wiki-init/templates/", content)

    def test_skill_local_assets_are_not_misclassified_as_root_assets(self) -> None:
        owned_asset_ref = "skill/wiki-init/assets/example.png"

        self.assertFalse(
            is_disallowed_repository_reference(owned_asset_ref),
            "expected skill-local assets to remain allowed even when their path contains 'assets/'",
        )
        self.assertTrue(is_disallowed_repository_reference("assets/example.png"))

    def test_skill_layout_guide_and_real_skill_dirs_use_approved_names(self) -> None:
        layout_guide = (SKILL_ROOT / "ASSET-LAYOUT.md").read_text(encoding="utf-8")
        for directory_name in APPROVED_SKILL_LOCAL_DIRS:
            with self.subTest(directory=directory_name):
                self.assertIn(f"`{directory_name}/`", layout_guide)

        for skill_dir in SKILL_ROOT.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name.startswith("."):
                continue

            for child in skill_dir.iterdir():
                if child.name == "SKILL.md":
                    continue
                if child.is_dir():
                    self.assertIn(
                        child.name,
                        APPROVED_SKILL_LOCAL_DIRS,
                        f"unexpected skill-local directory name: {child}",
                    )


if __name__ == "__main__":
    unittest.main()
