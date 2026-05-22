# Wiki Skill E2E Tests Design

Date: 2026-05-22
Topic: wiki-skill-e2e-tests

## Overview

This design adds end-to-end validation for the public wiki skills under `skill/`.
The first version focuses on the core workflow:

- `wiki-init`
- `wiki-ingest`
- `wiki-query`
- `wiki-update`

`wiki-lint` is intentionally excluded from the first version to keep scope focused on the primary knowledge-base construction loop.

The design uses two complementary test layers:

1. **Artifact E2E**
   - Verifies that the skill workflow produces the correct wiki instance state.
   - Stable, deterministic, and suitable for default CI.
2. **Agent Smoke E2E**
   - Verifies that a `skill.io`-compatible agent can actually consume the skill definitions and complete the minimal happy path.
   - Slower and more fragile, so it runs separately from the default fast test layer.

## Goals

- Prove that the skills under `skill/` can collaboratively build a usable wiki instance.
- Prove that the first-version skill workflow can initialize, ingest, query, and update a knowledge base.
- Keep the default validation layer deterministic and local-only.
- Add a separate smoke layer that validates real agent execution.

## Non-Goals

- Including `wiki-lint` in the first-version end-to-end workflow
- Verifying exact LLM wording or full-page markdown golden files
- Requiring network access for first-version E2E
- Building a multi-agent compatibility matrix in the first version
- Covering every source type or every query branch in the first version

## Layered Test Architecture

### Layer 1: Artifact E2E

Artifact E2E validates the knowledge-base state transitions caused by the skill workflow.
It does not require real LLM reasoning. Instead, it verifies the observable outputs that a correct workflow must leave behind in a temporary wiki instance.

This layer is the primary correctness signal.

### Layer 2: Agent Smoke E2E

Agent Smoke E2E validates that a real `skill.io`-compatible agent can read the public skills and run the same minimum workflow against a temporary wiki instance.

This layer is intentionally narrow:

- one scenario
- one happy path
- no network dependency
- minimal assertions on success and critical outputs

This layer is the primary compatibility signal.

## Test Scope

First-version end-to-end scope:

```text
wiki-init
  -> wiki-ingest
  -> wiki-query
  -> wiki-update
```

The workflow is complete when:

- a new wiki instance is created
- a source is ingested into the wiki
- a query can be answered from the created wiki state
- an update can revise the previously ingested knowledge

## Fixture Design

The first version uses a single fixed scenario.
The goal is stability, not breadth.

### Proposed Layout

```text
tests/e2e/
├── fixtures/
│   ├── source.md
│   ├── query.txt
│   ├── update.md
│   └── expected/
│       ├── created-page-slug.txt
│       └── key-facts.json
├── test_wiki_skill_workflow_e2e.py
└── test_agent_skill_smoke_e2e.py
```

### Fixture Roles

- `source.md`
  - the initial source material
  - contains one main concept, several key facts, and one fact that will later be updated
- `query.txt`
  - a stable question that should be answerable from the ingested wiki state
- `update.md`
  - a simple revision that changes one prior fact
- `expected/created-page-slug.txt`
  - the expected primary page slug
- `expected/key-facts.json`
  - semantic checkpoints for assertions

### Fixture Constraints

- Content should be short and deterministic.
- Content should avoid external dependencies.
- The updated fact should be explicit and easy to detect.
- The source title should produce a predictable slug.

## Temporary Wiki Instance Model

Each test run creates an isolated temporary instance with separated configuration and data roots.

```text
<tmp-root>/
├── config/
│   └── WIKI.md
└── wiki-data/
    ├── raw/
    ├── wiki/
    │   ├── index.md
    │   ├── log.md
    │   └── pages/
    └── concepts/
```

This intentionally validates the existing runtime rule that `config-dir` and `wiki-root` may be fully separated.

## End-to-End Assertions

### 1. wiki-init

Inputs:

- `config-dir`
- `wiki-root`
- domain
- source types
- four index categories

Assertions:

- `<config-dir>/WIKI.md` exists
- `WIKI.md` contains an absolute `wiki_root`
- `wiki_root` contains `raw/`, `wiki/index.md`, `wiki/log.md`, `wiki/pages/`, and `concepts/`
- `wiki/index.md` uses the selected category values rather than raw placeholders
- `wiki/log.md` contains an initialization record

### 2. wiki-ingest

Input:

- `source.md`

Assertions:

- `wiki/pages/<slug>.md` exists
- the page contains required frontmatter fields
- the page contains the semantic facts listed in `expected/key-facts.json`
- `wiki/index.md` contains an entry for the created page
- `wiki/log.md` contains an ingest record

### 3. wiki-query

Input:

- `query.txt`

Assertions:

- the answer references the local wiki page slug or the corresponding local knowledge entry
- the answer covers the expected key conclusions
- the answer is grounded in ingested wiki state rather than empty summary text
- if the scenario chooses "save answer", the corresponding `concepts/` file, index row, and log entry exist
- if the first version skips the save branch, at minimum the query log record exists

### 4. wiki-update

Input:

- `update.md`

Assertions:

- the original page still exists
- the targeted fact changes from old value to new value
- the page `updated` metadata changes
- `wiki/index.md` reflects the update
- `wiki/log.md` contains an update record

## Assertion Philosophy

Assertions should target structure and semantic checkpoints, not exact prose.

### Good Assertions

- file exists
- frontmatter field exists
- slug is correct
- log contains the expected operation entry
- key fact appears or is replaced
- index contains the expected row

### Bad Assertions

- full markdown page must match a golden file exactly
- answer text must match exact wording
- tags must appear in one exact order
- generated summaries must use one exact sentence

## Agent Smoke E2E Design

This layer validates that a compatible agent can actually consume the skills and execute the minimal workflow.

### Happy Path

```text
create temp wiki instance
  -> run wiki-init
  -> run wiki-ingest with fixed source
  -> run wiki-query with fixed question
  -> run wiki-update with fixed update
```

### Smoke Assertions

- the agent can locate `skill/`
- the agent can locate `WIKI.md`
- the workflow completes without blocking failures
- key output files exist after each step
- query output is non-empty and mentions the target topic
- update output changes the expected fact

### Smoke Constraints

- no network requirement in the first version
- one minimal fixture set only
- no multi-agent matrix in the first version

## Execution Strategy

### Default Validation Layer

Runs the deterministic Artifact E2E tests as part of normal repository testing.

Suggested command:

```bash
python3 -m unittest tests.test_wiki_skill_workflow_e2e
```

### Full Fast Repository Validation

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### Slow Agent Smoke Layer

Runs separately from the default fast suite.

Suggested command:

```bash
python3 -m unittest tests.test_agent_skill_smoke_e2e
```

## CI Strategy

### CI Level 1

- repository structure tests
- runtime contract tests
- skill boundary tests
- Artifact E2E

This is the default CI layer.

### CI Level 2

- Agent Smoke E2E

This runs manually, on schedule, or before release.

## Failure Isolation

```text
Artifact E2E fails
  -> skill contract problem
  -> template/layout problem
  -> workflow state transition problem
  -> fixture mismatch

Agent Smoke E2E fails
  -> agent execution problem
  -> environment/setup problem
  -> skill consumption compatibility problem
```

This separation is intentional and necessary.

## Implementation Notes

- The first implementation should reuse the repository's existing Python `unittest` approach.
- The fixture scenario should stay as small as possible.
- The first version should avoid introducing network dependencies.
- The first version should avoid exact-prose golden testing.
- Documentation should explain the difference between deterministic Artifact E2E and slow Agent Smoke E2E.

## Success Criteria

The first version is successful when:

- the repository has a deterministic E2E test for `wiki-init -> wiki-ingest -> wiki-query -> wiki-update`
- the E2E test validates the resulting wiki instance state rather than exact wording
- the repository provides one real-agent smoke path that proves the public skills are executable in practice
- the fast and slow layers can run independently
