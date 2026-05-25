# Specification: skill-private-assets-layout

## Overview

This specification defines the dependency boundary for public wiki skills in the repository. It distinguishes skill-private assets from wiki runtime contract and wiki instance data, and it defines which supporting files must live under the owning `skill/<name>/` directory.

## Requirements

### REQ-1: Runtime wiki references remain allowed

**Behavior**: Public wiki skills may reference the neutral runtime contract `WIKI.md` and wiki instance data paths under `wiki_root` without those references being treated as layout violations.

**Test Verification**: Verify that repository validation accepts runtime references such as `WIKI.md`, `raw/`, `wiki/`, `concepts/`, `wiki/index.md`, `wiki/log.md`, and `wiki/pages/` when they appear in public wiki skill documents.

```
Given: a public wiki skill document that references `WIKI.md` and wiki instance data paths
When:  repository layout validation scans `skill/*/SKILL.md`
Then:  those runtime references are accepted and do not fail the validation
```

**Interfaces to Test Through**: Public `skill/*/SKILL.md` files and repository validation tests.

---

### REQ-2: Skill-private assets stay with the owning skill

**Behavior**: If a public wiki skill directly references a skill-private asset that it owns, the referenced asset must live under that same `skill/<name>/` directory tree.

**Test Verification**: Verify that validation fails when a `skill/<name>/SKILL.md` references an owned template, example, fixture, script, or media file outside `skill/<name>/`.

```
Given: a public wiki skill document that references a skill-owned template or example file
When:  the referenced path is outside the same `skill/<name>/` directory tree
Then:  repository validation fails the skill layout check
```

**Interfaces to Test Through**: Public `skill/*/SKILL.md` files and repository validation tests.

---

### REQ-3: Repository-level loose assets are not direct skill dependencies

**Behavior**: Public wiki skills must not directly depend on loose repository-level assets or design-time artifacts such as root `README*`, root `assets/`, root helper scripts, or `openspec/` files.

**Test Verification**: Verify that validation fails when a public wiki skill directly references those disallowed repository-level files or directories.

```
Given: a public wiki skill document that directly references a root README, root assets path, root helper script, or `openspec/` artifact
When:  repository layout validation scans public wiki skills
Then:  validation reports the reference as a layout violation
```

**Interfaces to Test Through**: Public `skill/*/SKILL.md` files and repository validation tests.

---

### REQ-4: Public documentation explains the dependency boundary

**Behavior**: Repository documentation must describe that public wiki skills may depend on runtime wiki objects, but any skill-private assets must live under the owning skill directory.

**Test Verification**: Verify that repository documentation contains the allowed dependency boundary and does not describe runtime wiki data as skill-private assets.

```
Given: the repository README and skill-layout guidance
When:  documentation checks inspect the published rules
Then:  the docs explain the distinction between runtime wiki objects and skill-private assets
```

**Interfaces to Test Through**: Repository README files and any published skill layout guidance.

---

### REQ-5: Skill-local asset directories use standardized names

**Behavior**: When a public wiki skill includes local supporting materials, those materials must use standardized subdirectory names so the layout remains predictable across skills.

**Test Verification**: Verify that any local asset directories introduced under `skill/<name>/` use the approved vocabulary and that unknown directory categories are rejected by validation.

```
Given: a public wiki skill directory that contains supporting asset folders
When:  repository layout validation inspects those subdirectories
Then:  only approved names such as `templates/`, `examples/`, `fixtures/`, `assets/`, and `scripts/` are accepted
```

**Interfaces to Test Through**: Public `skill/*/` directories and repository validation tests.

---

## Test Structure

### Integration Tests

```python
import unittest


class SkillPrivateAssetsLayoutTest(unittest.TestCase):
    def test_public_wiki_skills_follow_dependency_boundary(self) -> None:
        # Given
        skill_documents = load_public_skill_documents()

        # When
        violations = scan_skill_dependency_boundary(skill_documents)

        # Then
        self.assertEqual([], violations)
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_skill_private_assets_boundary.py` | 验证公共 wiki skill 的允许/禁止依赖边界 |
| `tests/test_skill_private_assets_docs.py` | 验证文档是否正确描述 skill 私有资产与 runtime 数据的区分 |

## Edge Cases

- A skill references `WIKI.md` and `wiki_root` data paths in prose but owns no local assets.
- A skill introduces `templates/` and `examples/` locally and both should be accepted.
- A skill references another skill's local asset path; this should be treated as a violation.
- A skill references a root-level screenshot or helper script for convenience; this should be treated as a violation.
- A repository-level README may mention skill names, but skills must not depend on README as a private asset source.
