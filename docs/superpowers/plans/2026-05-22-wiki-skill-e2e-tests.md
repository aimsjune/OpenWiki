# Wiki Skill E2E Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build deterministic end-to-end coverage for `wiki-init -> wiki-ingest -> wiki-query -> wiki-update`, plus one optional real-agent smoke path that proves the public skills are executable in practice.

**Architecture:** Add a small Python test harness under `tests/e2e/` that creates isolated temporary wiki instances, loads fixed fixtures, and drives deterministic artifact-level state transitions without requiring network or real LLM reasoning. Add a separate smoke harness that invokes a user-provided compatible agent runner through environment variables and validates the same minimal workflow against real skill consumption.

**Tech Stack:** Python 3, `unittest`, `pathlib`, `tempfile`, `json`, `shutil`, `subprocess`, existing `skill/` templates and repository README docs

---

## File Structure

### New Files

- `tests/e2e/harness.py`
  - deterministic helper functions for temporary wiki setup, fixture loading, and artifact workflow execution
- `tests/e2e/agent_harness.py`
  - wrapper for invoking a user-provided real agent runner
- `tests/e2e/fixtures/source.md`
  - fixed ingest source for the minimal scenario
- `tests/e2e/fixtures/query.txt`
  - fixed query for the minimal scenario
- `tests/e2e/fixtures/update.md`
  - fixed update input for the minimal scenario
- `tests/e2e/fixtures/expected/created-page-slug.txt`
  - expected primary page slug
- `tests/e2e/fixtures/expected/key-facts.json`
  - semantic checkpoints for assertions
- `tests/test_wiki_skill_workflow_e2e.py`
  - deterministic artifact E2E for init/ingest/query/update
- `tests/test_agent_skill_smoke_e2e.py`
  - optional real-agent smoke E2E for the same workflow

### Existing Files To Modify

- `README.md`
  - add E2E testing commands and explain fast vs slow layers
- `README.en.md`
  - same as above in English
- `README.ja.md`
  - same as above in Japanese

### Existing Files To Read Before Editing

- `skill/wiki-init/SKILL.md`
- `skill/wiki-ingest/SKILL.md`
- `skill/wiki-query/SKILL.md`
- `skill/wiki-update/SKILL.md`
- `skill/wiki-init/templates/WIKI.md`
- `skill/wiki-init/templates/index.md`
- `skill/wiki-init/templates/log.md`
- `WIKI.md`
- `docs/superpowers/specs/2026-05-22-wiki-skill-e2e-tests-design.md`

---

### Task 1: Deterministic Artifact E2E For wiki-init

**Files:**
- Create: `tests/e2e/harness.py`
- Create: `tests/test_wiki_skill_workflow_e2e.py`
- Test: `tests/test_wiki_skill_workflow_e2e.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest
from pathlib import Path

from tests.e2e.harness import build_temp_instance, run_init_reference


class WikiSkillWorkflowE2ETest(unittest.TestCase):
    def test_wiki_init_creates_separated_config_and_wiki_roots(self) -> None:
        instance = build_temp_instance()

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

        self.assertTrue((instance.config_dir / "WIKI.md").exists())
        self.assertTrue((instance.wiki_root / "raw").is_dir())
        self.assertTrue((instance.wiki_root / "wiki" / "index.md").exists())
        self.assertTrue((instance.wiki_root / "wiki" / "log.md").exists())
        self.assertTrue((instance.wiki_root / "wiki" / "pages").is_dir())
        self.assertTrue((instance.wiki_root / "concepts").is_dir())

        contract = (instance.config_dir / "WIKI.md").read_text(encoding="utf-8")
        index_md = (instance.wiki_root / "wiki" / "index.md").read_text(encoding="utf-8")
        log_md = (instance.wiki_root / "wiki" / "log.md").read_text(encoding="utf-8")

        self.assertIn(str(instance.wiki_root), contract)
        self.assertIn("Wiki Pages", index_md)
        self.assertIn("Quick Navigation", index_md)
        self.assertIn("init | E2E testing knowledge base", log_md)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_wiki_skill_workflow_e2e.WikiSkillWorkflowE2ETest.test_wiki_init_creates_separated_config_and_wiki_roots -v`
Expected: FAIL with `ModuleNotFoundError` or missing `build_temp_instance` / `run_init_reference`

- [ ] **Step 3: Write minimal implementation**

Create `tests/e2e/harness.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / "skill" / "wiki-init" / "templates"


@dataclass
class TempWikiInstance:
    temp_dir: TemporaryDirectory[str]
    temp_root: Path
    config_dir: Path
    wiki_root: Path


def build_temp_instance() -> TempWikiInstance:
    temp_dir = TemporaryDirectory()
    temp_root = Path(temp_dir.name)
    config_dir = temp_root / "config"
    wiki_root = temp_root / "wiki-data"
    config_dir.mkdir(parents=True, exist_ok=True)
    wiki_root.mkdir(parents=True, exist_ok=True)
    return TempWikiInstance(
        temp_dir=temp_dir,
        temp_root=temp_root,
        config_dir=config_dir,
        wiki_root=wiki_root,
    )


def _load_template(name: str) -> str:
    return (SKILL_ROOT / name).read_text(encoding="utf-8")


def run_init_reference(
    *,
    instance: TempWikiInstance,
    domain: str,
    source_types: list[str],
    index_categories: list[str],
) -> None:
    contract = _load_template("WIKI.md")
    contract = contract.replace("/absolute/path/to/wiki-root", str(instance.wiki_root))
    contract = contract.replace("<user domain description>", domain)
    contract = contract.replace("- papers", f"- {source_types[0]}")
    contract = contract.replace("- urls", f"- {source_types[1]}")
    for i, category in enumerate(index_categories, start=1):
        contract = contract.replace(f"<category_{i}>", category)

    wiki_dir = instance.wiki_root / "wiki"
    pages_dir = wiki_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    (instance.wiki_root / "raw").mkdir(parents=True, exist_ok=True)
    (instance.wiki_root / "concepts").mkdir(parents=True, exist_ok=True)

    index_md = _load_template("index.md")
    for i, category in enumerate(index_categories, start=1):
        index_md = index_md.replace(f"<category_{i}>", category)

    log_md = _load_template("log.md").replace("<today>", "2026-05-22").replace(
        "<domain>", domain
    )

    (instance.config_dir / "WIKI.md").write_text(contract, encoding="utf-8")
    (wiki_dir / "index.md").write_text(index_md, encoding="utf-8")
    (wiki_dir / "log.md").write_text(log_md, encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_wiki_skill_workflow_e2e.WikiSkillWorkflowE2ETest.test_wiki_init_creates_separated_config_and_wiki_roots -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/e2e/harness.py tests/test_wiki_skill_workflow_e2e.py
git commit -m "test: add artifact e2e init workflow"
```

---

### Task 2: Deterministic Artifact E2E For ingest -> query -> update

**Files:**
- Create: `tests/e2e/fixtures/source.md`
- Create: `tests/e2e/fixtures/query.txt`
- Create: `tests/e2e/fixtures/update.md`
- Create: `tests/e2e/fixtures/expected/created-page-slug.txt`
- Create: `tests/e2e/fixtures/expected/key-facts.json`
- Modify: `tests/e2e/harness.py`
- Modify: `tests/test_wiki_skill_workflow_e2e.py`
- Test: `tests/test_wiki_skill_workflow_e2e.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_wiki_skill_workflow_e2e.py`:

```python
from tests.e2e.harness import (
    fixture_path,
    run_ingest_reference,
    run_query_reference,
    run_update_reference,
)


    def test_artifact_workflow_ingest_query_update(self) -> None:
        instance = build_temp_instance()
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

        slug = run_ingest_reference(instance=instance, fixture_root=fixture_path())
        answer = run_query_reference(instance=instance, fixture_root=fixture_path())
        run_update_reference(instance=instance, fixture_root=fixture_path(), slug=slug)

        page_md = (instance.wiki_root / "wiki" / "pages" / f"{slug}.md").read_text(
            encoding="utf-8"
        )
        index_md = (instance.wiki_root / "wiki" / "index.md").read_text(encoding="utf-8")
        log_md = (instance.wiki_root / "wiki" / "log.md").read_text(encoding="utf-8")

        self.assertEqual("local-first-wiki-testing", slug)
        self.assertIn("[[local-first-wiki-testing]]", index_md)
        self.assertIn("Artifact E2E runs without network access.", page_md)
        self.assertIn("Agent Smoke E2E validates a real compatible agent.", answer)
        self.assertIn("The update now covers wiki-lint in a later phase.", page_md)
        self.assertIn("ingest | Local-First Wiki Testing", log_md)
        self.assertIn("query | local-first-wiki-testing", log_md)
        self.assertIn("update | local-first-wiki-testing", log_md)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_wiki_skill_workflow_e2e.WikiSkillWorkflowE2ETest.test_artifact_workflow_ingest_query_update -v`
Expected: FAIL with missing fixture files or undefined `run_ingest_reference` / `run_query_reference` / `run_update_reference`

- [ ] **Step 3: Write minimal implementation**

Create fixtures:

`tests/e2e/fixtures/source.md`

```md
# Local-First Wiki Testing

- Artifact E2E runs without network access.
- Agent Smoke E2E validates a real compatible agent.
- The first version excludes wiki-lint.
```

`tests/e2e/fixtures/query.txt`

```text
What are the two main testing layers in this wiki skill workflow?
```

`tests/e2e/fixtures/update.md`

```md
Update the prior plan: the update now covers wiki-lint in a later phase.
```

`tests/e2e/fixtures/expected/created-page-slug.txt`

```text
local-first-wiki-testing
```

`tests/e2e/fixtures/expected/key-facts.json`

```json
{
  "title": "Local-First Wiki Testing",
  "slug": "local-first-wiki-testing",
  "facts": [
    "Artifact E2E runs without network access.",
    "Agent Smoke E2E validates a real compatible agent."
  ],
  "updated_fact": {
    "old": "The first version excludes wiki-lint.",
    "new": "The update now covers wiki-lint in a later phase."
  }
}
```

Extend `tests/e2e/harness.py`:

```python
import json


def fixture_path() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _expected_data(fixture_root: Path) -> dict:
    return json.loads(
        (fixture_root / "expected" / "key-facts.json").read_text(encoding="utf-8")
    )


def run_ingest_reference(*, instance: TempWikiInstance, fixture_root: Path) -> str:
    expected = _expected_data(fixture_root)
    slug = (fixture_root / "expected" / "created-page-slug.txt").read_text(
        encoding="utf-8"
    ).strip()
    page_md = f\"\"\"---
title: {expected['title']}
tags: [testing, e2e]
sources: 1
updated: 2026-05-22
---

# {expected['title']}

## Key Takeaways

- {expected['facts'][0]}
- {expected['facts'][1]}
- {expected['updated_fact']['old']}
\"\"\"
    page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
    page_path.write_text(page_md, encoding="utf-8")

    index_path = instance.wiki_root / "wiki" / "index.md"
    index_md = index_path.read_text(encoding="utf-8")
    index_md += f\"\\n| [[{slug}]] | Local-first workflow notes | testing, e2e | 2026-05-22 |\\n\"
    index_path.write_text(index_md, encoding="utf-8")

    log_path = instance.wiki_root / "wiki" / "log.md"
    log_md = log_path.read_text(encoding="utf-8")
    log_md += (
        \"\\n## [2026-05-22] ingest | Local-First Wiki Testing\\n\"
        \"- Created/Updated pages: local-first-wiki-testing\\n\"
    )
    log_path.write_text(log_md, encoding="utf-8")
    return slug


def run_query_reference(*, instance: TempWikiInstance, fixture_root: Path) -> str:
    expected = _expected_data(fixture_root)
    answer = (
        f\"[[{expected['slug']}]] says {expected['facts'][0]} \"
        f\"and {expected['facts'][1]}\"
    )
    log_path = instance.wiki_root / "wiki" / "log.md"
    log_md = log_path.read_text(encoding="utf-8")
    log_md += (
        f\"\\n## [2026-05-22] query | {expected['slug']}\\n\"
        \"- Pages read: local-first-wiki-testing\\n\"
    )
    log_path.write_text(log_md, encoding="utf-8")
    return answer


def run_update_reference(*, instance: TempWikiInstance, fixture_root: Path, slug: str) -> None:
    expected = _expected_data(fixture_root)
    page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
    page_md = page_path.read_text(encoding="utf-8")
    page_md = page_md.replace(
        expected["updated_fact"]["old"],
        expected["updated_fact"]["new"],
    ).replace("updated: 2026-05-22", "updated: 2026-05-23")
    page_path.write_text(page_md, encoding="utf-8")

    index_path = instance.wiki_root / "wiki" / "index.md"
    index_md = index_path.read_text(encoding="utf-8").replace("2026-05-22", "2026-05-23")
    index_path.write_text(index_md, encoding="utf-8")

    log_path = instance.wiki_root / "wiki" / "log.md"
    log_md = log_path.read_text(encoding="utf-8")
    log_md += (
        f\"\\n## [2026-05-23] update | {slug}\\n\"
        f\"- Replaced fact: {expected['updated_fact']['new']}\\n\"
    )
    log_path.write_text(log_md, encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_wiki_skill_workflow_e2e.WikiSkillWorkflowE2ETest.test_artifact_workflow_ingest_query_update -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/e2e/fixtures tests/e2e/harness.py tests/test_wiki_skill_workflow_e2e.py
git commit -m "test: add artifact e2e workflow coverage"
```

---

### Task 3: Optional Real-Agent Smoke E2E

**Files:**
- Create: `tests/e2e/agent_harness.py`
- Create: `tests/test_agent_skill_smoke_e2e.py`
- Test: `tests/test_agent_skill_smoke_e2e.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_agent_skill_smoke_e2e.py`:

```python
import os
import unittest

from tests.e2e.agent_harness import run_agent_prompt
from tests.e2e.harness import build_temp_instance, fixture_path


class AgentSkillSmokeE2ETest(unittest.TestCase):
    def test_real_agent_runs_minimal_skill_workflow(self) -> None:
        if os.environ.get("SKILL_AGENT_E2E") != "1":
            self.skipTest("set SKILL_AGENT_E2E=1 to enable slow real-agent smoke test")

        instance = build_temp_instance()
        fixture_root = fixture_path()

        init_result = run_agent_prompt(
            f\"Use skill wiki-init. Create config-dir {instance.config_dir} and wiki-root {instance.wiki_root}. \"
            \"Domain: E2E testing knowledge base. Source types: notes, articles. "
            "\"Categories: Wiki Pages, Concepts Pages, Topic Relations, Quick Navigation.\""
        )
        self.assertEqual(0, init_result.returncode)
        self.assertTrue((instance.config_dir / "WIKI.md").exists())

        source_path = fixture_root / "source.md"
        ingest_result = run_agent_prompt(
            f\"Use skill wiki-ingest. Ingest local file {source_path} into the current wiki instance.\"
        )
        self.assertEqual(0, ingest_result.returncode)

        query_prompt = (fixture_root / "query.txt").read_text(encoding="utf-8").strip()
        query_result = run_agent_prompt(f\"Use skill wiki-query. {query_prompt}\")
        self.assertEqual(0, query_result.returncode)
        self.assertIn("local-first-wiki-testing", query_result.stdout.lower())

        update_path = fixture_root / "update.md"
        update_result = run_agent_prompt(
            f\"Use skill wiki-update. Apply update from file {update_path}.\"
        )
        self.assertEqual(0, update_result.returncode)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `SKILL_AGENT_E2E=1 SKILL_AGENT_RUNNER=/bin/false python3 -m unittest tests.test_agent_skill_smoke_e2e.AgentSkillSmokeE2ETest.test_real_agent_runs_minimal_skill_workflow -v`
Expected: FAIL because `run_agent_prompt()` does not exist yet or the fake runner returns non-zero

- [ ] **Step 3: Write minimal implementation**

Create `tests/e2e/agent_harness.py`:

```python
from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_agent_prompt(prompt: str) -> subprocess.CompletedProcess[str]:
    runner = os.environ["SKILL_AGENT_RUNNER"]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    return subprocess.run(
        [runner],
        input=prompt,
        text=True,
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        check=False,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `SKILL_AGENT_E2E=1 SKILL_AGENT_RUNNER=/path/to/compatible-agent-wrapper python3 -m unittest tests.test_agent_skill_smoke_e2e.AgentSkillSmokeE2ETest.test_real_agent_runs_minimal_skill_workflow -v`
Expected: PASS with a real wrapper that accepts prompt text on stdin and runs inside the repository root

- [ ] **Step 5: Commit**

```bash
git add tests/e2e/agent_harness.py tests/test_agent_skill_smoke_e2e.py
git commit -m "test: add real agent smoke e2e workflow"
```

---

### Task 4: Document Fast vs Slow E2E Execution

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `README.ja.md`
- Test: `tests/test_skill_private_assets_docs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_skill_private_assets_docs.py`:

```python
    def test_readmes_document_fast_and_slow_e2e_commands(self) -> None:
        for readme_name in README_FILES:
            with self.subTest(readme=readme_name):
                content = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
                self.assertIn("tests.test_wiki_skill_workflow_e2e", content)
                self.assertIn("tests.test_agent_skill_smoke_e2e", content)
                self.assertIn("SKILL_AGENT_E2E=1", content)
                self.assertIn("SKILL_AGENT_RUNNER", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_skill_private_assets_docs.SkillPrivateAssetsDocsTest.test_readmes_document_fast_and_slow_e2e_commands -v`
Expected: FAIL because README files do not yet describe the new commands

- [ ] **Step 3: Write minimal implementation**

Add a short E2E testing section to `README.md`:

```md
## E2E Testing

- Fast deterministic workflow:
  - `python3 -m unittest tests.test_wiki_skill_workflow_e2e`
- Full fast suite:
  - `python3 -m unittest discover -s tests -p "test_*.py"`
- Slow real-agent smoke workflow:
  - `SKILL_AGENT_E2E=1 SKILL_AGENT_RUNNER=/path/to/compatible-agent-wrapper python3 -m unittest tests.test_agent_skill_smoke_e2e`
```

Mirror the same commands in `README.en.md` and `README.ja.md`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_skill_private_assets_docs.SkillPrivateAssetsDocsTest.test_readmes_document_fast_and_slow_e2e_commands -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md README.en.md README.ja.md tests/test_skill_private_assets_docs.py
git commit -m "docs: add wiki skill e2e test commands"
```

---

## Verification

- [ ] Run targeted artifact E2E: `python3 -m unittest tests.test_wiki_skill_workflow_e2e -v`
- [ ] Run full fast suite: `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] Run optional smoke suite with a real wrapper:
  - `SKILL_AGENT_E2E=1 SKILL_AGENT_RUNNER=/path/to/compatible-agent-wrapper python3 -m unittest tests.test_agent_skill_smoke_e2e -v`
- [ ] Confirm artifact E2E covers `wiki-init -> wiki-ingest -> wiki-query -> wiki-update`
- [ ] Confirm fast and slow layers can run independently
- [ ] Confirm no test depends on network access

## Test Quality Checklist

- [ ] Tests describe workflow behavior, not implementation trivia
- [ ] Assertions focus on file state, logs, semantic checkpoints, and slugs
- [ ] No exact-prose golden assertions for generated wiki pages
- [ ] Fast artifact E2E is deterministic and local-only
- [ ] Slow smoke E2E is optional and gated by environment variables
- [ ] Temporary wiki instances use separated `config-dir` and `wiki-root`

## Spec Coverage Self-Review

- `Overview / Goals`: Covered by Tasks 1-4
- `Fixture Design`: Covered by Task 2 fixture files
- `Temporary Wiki Instance Model`: Covered by Task 1 harness
- `wiki-init Assertions`: Covered by Task 1 test
- `wiki-ingest / wiki-query / wiki-update Assertions`: Covered by Task 2 test
- `Agent Smoke E2E`: Covered by Task 3
- `Execution Strategy / CI Strategy`: Covered by Task 4 documentation
- `Failure Isolation`: Supported by separate fast and slow test entrypoints

No uncovered design sections remain in the first-version scope.
