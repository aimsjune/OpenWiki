# Skill Asset Layout

This document defines the dependency boundary for public wiki skills under `skill/`.

## Allowed Runtime References

Public wiki skills may refer to runtime wiki objects that belong to a wiki instance rather than to the skill package itself:

- `openwiki.toml`
- `raw/`
- `wiki/`
- `concepts/`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`

These references are allowed because they describe the runtime contract and the data layout under `wiki_root`.

## Disallowed Repository-Level Dependencies

Public wiki skills must not directly depend on loose repository-level assets or design artifacts such as:

- `README.md`
- `README.en.md`
- `README.ja.md`
- `assets/`
- `openspec/`

Repository-level docs may describe skills, but they are not skill-private asset sources.

## Ownership Rule

If a public wiki skill needs a skill-private template, example, fixture, media file, or helper script, that asset must live under the same `skill/<name>/` directory tree as the owning skill.

Approved skill-local directory names:

- `templates/`
- `examples/`
- `fixtures/`
- `assets/`
- `scripts/`
- `references/`
- `tests/`
