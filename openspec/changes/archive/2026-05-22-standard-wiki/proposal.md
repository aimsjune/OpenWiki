# Proposal: standard-wiki

## Why

The repository currently organizes its runtime contract and skill definitions around specific agent ecosystems, especially Claude-oriented files and directory names. That makes the project harder to run in other `skill.io`-compatible agents because the canonical entrypoints, skill locations, and initialization flow are not agent-neutral.

This change standardizes the wiki runtime around a single neutral contract file and a single neutral skill directory so that any compatible agent can execute the workflow without relying on compatibility shims or agent-specific conventions.

## What Changes

- Replace agent-specific runtime entrypoints with a neutral configuration contract stored in `WIKI.md`.
- Require `WIKI.md` to record the absolute `wiki_root` path explicitly.
- Allow `config-dir` and `wiki-root` to be fully separated locations.
- Move all wiki-related skills, including `agent-browser`, into a single canonical `skill/` directory.
- Remove `.claude/skills/`, `.agents/skills/`, and related compatibility-layer assumptions from initialization flow and documentation.
- Update wiki skills so they resolve wiki state through `WIKI.md` instead of agent-specific files or directory guesses.

## Acceptance Criteria (Testable)

For each criterion, specify WHAT behavior should be testable:

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `wiki-init` asks for both a configuration directory and a wiki root directory, writes `WIKI.md` into the configuration directory, and records an absolute `wiki_root` path in that file. | An integration test runs the initialization flow, then asserts that `<config-dir>/WIKI.md` exists and contains an absolute `wiki_root` value that points to the requested wiki root. |
| 2 | After initialization, the wiki data directories are created under the configured wiki root, even when the configuration directory and wiki root are different paths. | An integration test initializes with two different absolute paths and verifies that `raw/`, `wiki/`, `wiki/index.md`, `wiki/log.md`, and `concepts/` are created under `wiki_root`, not under `config-dir`. |
| 3 | Wiki skills resolve runtime configuration from `WIKI.md` and no longer require `CLAUDE.md`, `.claude/skills/`, or `.agents/skills/` to exist. | Skill-focused tests or scripted verification invoke the wiki skill preconditions in a repo containing only `skill/` and `WIKI.md`, and assert the workflows proceed without checking for legacy agent-specific paths. |
| 4 | All public skill definitions needed by the wiki workflow are maintained only under `skill/`, including `agent-browser`, with no compatibility copies retained elsewhere. | A repository structure test verifies that the required skill names exist under `skill/` and that `.claude/skills/` and `.agents/skills/` are absent from the supported runtime layout and documentation. |
| 5 | Project documentation describes the neutral `skill/` plus `WIKI.md` architecture and no longer presents Claude-specific files as the canonical runtime contract. | Documentation tests or review checks assert that README and initialization guidance reference `WIKI.md` and `skill/` as canonical, and do not instruct users to rely on `CLAUDE.md` or compatibility skill directories. |

## Impact

- Affects repository layout and initialization behavior
- Affects all wiki workflow skill definitions
- Affects README, setup guidance, and architecture documentation
- Removes legacy agent-specific directory conventions from the canonical runtime model

## Non-Goals

- Redesigning wiki content format, page schema, or ingest semantics
- Changing the `raw/`, `wiki/`, and `concepts/` knowledge architecture itself
- Replacing `agent-browser` with a different web research capability
- Implementing multi-wiki orchestration beyond a single `WIKI.md` pointing to one `wiki_root`

## Test Considerations

- Use the existing project test approach plus focused integration tests for initialization and skill preconditions
- Test through observable filesystem outputs and skill entry behavior rather than internal implementation details
- Mock user input where needed for initialization prompts
- Use temporary directories to validate fully separated `config-dir` and `wiki-root` paths
