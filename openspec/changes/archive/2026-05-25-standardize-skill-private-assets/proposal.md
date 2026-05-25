# Proposal: standardize-skill-private-assets

## Why

The repository has already standardized public wiki skills under `skill/`, but it still lacks an explicit rule for where skill-private assets must live. Without that boundary, future skills may begin depending directly on repository-level files such as root `assets/`, ad hoc templates, loose example files, or design-time documents under `openspec/`.

This creates three risks:

- skill portability degrades because a skill can no longer be copied or reused with its own assets intact
- repository structure drifts because supporting files are scattered outside the owning skill
- runtime wiki data such as `WIKI.md`, `raw/`, `wiki/`, and `concepts/` can be confused with skill package assets

We need a clear, testable convention that separates:

- skill-private assets that must live under `skill/<name>/`
- wiki runtime contract and instance data that remain outside skill directories
- repository-level documentation that must not become direct skill dependencies

## What Changes

- Define a standard boundary for skill-private assets in this repository.
- Require any asset directly referenced by a `skill/<name>/SKILL.md` and owned by that skill to live under the same `skill/<name>/` directory tree.
- Explicitly preserve `WIKI.md` and `wiki_root` data directories as runtime objects, not skill-private assets.
- Forbid public wiki skills from directly depending on repository-level loose assets such as root `assets/`, root `README*`, root helper scripts, or `openspec/` artifacts.
- Establish a standard internal layout for optional skill-private materials such as `templates/`, `examples/`, `fixtures/`, `assets/`, and `scripts/`.
- Add validation that distinguishes allowed runtime references from disallowed external asset dependencies.

## Acceptance Criteria (Testable)

For each criterion, specify WHAT behavior should be testable:

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | Public wiki skills may reference `WIKI.md` and `wiki_root` runtime data paths without being flagged as layout violations. | A repository-level test scans `skill/*/SKILL.md` and accepts references to `WIKI.md`, `raw/`, `wiki/`, `concepts/`, `wiki/index.md`, `wiki/log.md`, and `wiki/pages/`. |
| 2 | Any skill-private asset referenced by a public wiki skill must live under that same skill directory. | A test fails if `skill/<name>/SKILL.md` references templates, examples, fixtures, scripts, or media outside `skill/<name>/`. |
| 3 | Public wiki skills do not directly depend on repository-level loose assets or design artifacts. | A test fails if `skill/*/SKILL.md` directly references root `README*`, root `assets/`, root helper scripts, or `openspec/` paths. |
| 4 | The repository documents the allowed dependency boundary for public wiki skills. | Documentation checks confirm README and/or skill layout guidance describe the distinction between skill-private assets and runtime wiki data. |
| 5 | Skill-local asset directories use a standardized vocabulary when present. | Tests or golden checks confirm that supported subdirectories, when introduced, use approved names such as `templates/`, `examples/`, `fixtures/`, `assets/`, or `scripts/`. |

## Impact

- Affects `skill/` layout rules for all public wiki skills
- Affects repository documentation describing skill packaging rules
- Adds validation for allowed and disallowed skill references
- May require migrating future skill-private templates or examples into owning skill directories

## Non-Goals

- Moving `WIKI.md`, `raw/`, `wiki/`, or `concepts/` into `skill/`
- Redesigning wiki runtime semantics introduced by `standard-wiki`
- Implementing agent-specific compatibility layers
- Rewriting skill behavior unrelated to asset ownership boundaries

## Test Considerations

- Use Python `unittest`, matching the repository's current lightweight validation approach
- Test through public `skill/*/SKILL.md` files and repository documentation
- No external services are needed; checks operate on repository files only
