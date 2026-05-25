# Design: standardize-skill-private-assets

## Overview

This change introduces a repository-wide packaging rule for public wiki skills. The core design separates three classes of paths:

1. **skill-private assets**: files owned by a skill and required by that skill
2. **wiki runtime objects**: `WIKI.md` and data under `wiki_root`
3. **repository-level documents and tooling**: top-level docs, images, helper scripts, and OpenSpec artifacts

Only the first class is required to live inside `skill/<name>/`. The second class stays outside skills because it belongs to a wiki instance, not a skill package. The third class must not become a direct dependency of public wiki skills.

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| `skill/<name>/SKILL.md` | Defines the public behavior and declared references for one public wiki skill | Referenced directly as the public skill entrypoint |
| `skill/<name>/` local asset tree | Stores templates, examples, fixtures, media, and scripts owned by the skill | Referenced only through local paths beneath the owning skill |
| `WIKI.md` and `wiki_root` data paths | Provide runtime contract and wiki instance data used by wiki workflows | Referenced in skill instructions as runtime objects |
| Repository layout validator | Scans skill documents and directories for allowed/disallowed references | Tested through repository test files |
| Repository documentation | Explains the boundary so future contributors follow the same rules | Tested through README and guidance checks |

## Interface Design for Testability

### Public Interfaces

```python
ALLOWED_RUNTIME_REFERENCES = {
    "WIKI.md",
    "raw/",
    "wiki/",
    "concepts/",
    "wiki/index.md",
    "wiki/log.md",
    "wiki/pages/",
}

APPROVED_SKILL_ASSET_DIRS = {
    "templates",
    "examples",
    "fixtures",
    "assets",
    "scripts",
}

DISALLOWED_REPOSITORY_REFERENCES = {
    "README.md",
    "README.en.md",
    "README.ja.md",
    "assets/",
    "openspec/",
}
```

The observable outcome is not an internal parser implementation; it is a repository validation result over public `skill/*/SKILL.md` files and public `skill/*/` directory names.

### Testability Guidelines

1. **Accept dependencies as input sets**

   The validator should work from explicit allowlists and denylists for path categories. This keeps tests focused on observed reference classification rather than hidden heuristics.

2. **Return violations rather than only printing**

   Validation should produce a structured list of violations so tests can assert exact outcomes without scraping command output.

3. **Validate through public surfaces**

   Tests should scan `skill/*/SKILL.md`, public `skill/*/` subdirectories, and repository docs. They should not depend on implementation-specific helper functions.

## Data Flow

```text
skill/*/SKILL.md
      │
      ├── classify references
      │     ├── allowed runtime references
      │     ├── local skill-owned references
      │     └── disallowed repository-level references
      │
      └── inspect local skill subdirectories
            ├── approved names
            └── unknown names => violation

README / guidance docs
      │
      └── verify documented boundary matches repository rules
```

The important design choice is classification before enforcement:

- if a reference points to `WIKI.md` or `wiki_root` data, it is allowed as runtime usage
- if a reference points to an owned template/example/fixture/script/media file, it must remain under the same `skill/<name>/`
- if a reference points to a loose repository-level asset, it is rejected

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| File system layout | Use the real repository tree or a temporary test directory snapshot |
| Path classification inputs | Use small in-test sample path lists |
| Documentation content | Read repository markdown files directly |

No network, browser, or external API dependencies are required for this change.

## Implementation Notes

- The repository should publish one clear glossary for path categories so contributors do not conflate runtime wiki objects with skill-private assets.
- `skill/<name>/` should be treated as the ownership boundary for any optional templates, examples, fixtures, media, or helper scripts used by that skill.
- Cross-skill private asset references should be treated the same as root-level loose asset references: not allowed.
- This design intentionally does not move runtime wiki data under `skill/`, because that would break the separation established by `standard-wiki`.
- If `wiki-init` later externalizes inline starter content into files, those files should become `skill/wiki-init/templates/...` rather than root-level templates.
