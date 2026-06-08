# LLM Wiki — AI-Powered Personal Knowledge Base

**Language / 语言 / 言語：** [中文](README.md) ｜ English（default）｜ [日本語](README.ja.md)

---

## What is this?

LLM Wiki is a personal knowledge-base scaffold for `skill.io`-compatible agents. Raw material lives in `raw/`, structured knowledge lives in `wiki/`, and saved analyses live in `concepts/`. The repository exposes public skills through `skill/` and uses `openwiki.toml` as the instance-level runtime contract.

**Core idea:**
- `openwiki.toml` is the canonical runtime contract
- `skill/` is the canonical public wiki skill directory
- `config-dir` and `wiki-root` may be fully separated
- `raw/` stores immutable sources while `wiki/` is maintained by AI

---

## Runtime Model

```text
<config-dir>/
└── openwiki.toml            # runtime contract with absolute wiki_root

<wiki-root>/
├── raw/               # source material
├── wiki/
│   ├── index.md       # global index
│   ├── log.md         # operation log
│   └── pages/         # topic pages
└── concepts/          # analyses, answers, reports
```

Public skills live in:

```text
skill/
├── wiki-init/
├── wiki-ingest/
├── wiki-query/
├── wiki-lint/
├── wiki-update/
└── agent-browser/
```

---

## Quick Start

### Prerequisites

- Any `skill.io`-compatible agent or tool
- (Optional) [agent-browser](https://github.com/mediar-ai/agent-browser) for web-augmented research
  ```bash
  brew install mediar-ai/agent-browser/agent-browser
  ```

### Installation

```bash
git clone https://github.com/crabin/llm-wiki.git my-wiki
cd my-wiki
```

Load the repository into your compatible agent and ensure it can read the public wiki skills in `skill/`.

### Usage

1. Run `wiki-init`
2. Choose a `config-dir`, such as `~/.openwiki`
3. Choose a `wiki-root`, such as `~/data/my-wiki`
4. Let `wiki-init` write `<config-dir>/openwiki.toml` with an absolute `wiki_root`
5. Put source material into `<wiki-root>/raw/` and run `wiki-ingest`
6. Use `wiki-query`, `wiki-lint`, and `wiki-update` for ongoing work

Because `openwiki.toml` contains a machine-specific absolute path, do not commit it to Git. The repository ignores the root config and provides a sanitized `openwiki.example.toml` instead.

Runtime discovery order:
- prefer an explicitly provided `config-dir`
- otherwise check the default config directory at `~/.openwiki/openwiki.toml`
- if the default config is not found or invalid, search upward from the current working directory for `openwiki.toml`
- if still missing, ask for an absolute config-dir or run `wiki-init`

If the explicitly provided `config-dir` already contains a valid `openwiki.toml`, `wiki-init` should say it is connected to the existing wiki, reuse that runtime contract, and suggest continuing with the same `config-dir` in `wiki-query`, `wiki-ingest`, `wiki-lint`, and `wiki-update`.

### E2E Testing

- Fast deterministic artifact E2E:
  ```bash
  python3 -m unittest tests.test_wiki_skill_workflow_e2e -v
  ```
- Full fast test suite:
  ```bash
  python3 -m unittest discover -s tests -p "test_*.py"
  ```
- Slow real-agent smoke E2E:
  ```bash
  SKILL_AGENT_E2E=1 SKILL_AGENT_RUNNER=/path/to/compatible-agent-wrapper python3 -m unittest tests.test_agent_skill_smoke_e2e -v
  ```

Notes:
- `tests.test_wiki_skill_workflow_e2e` uses only local fixtures and temporary directories, with no network dependency.
- `tests.test_agent_skill_smoke_e2e` skips the real runner scenario by default and only executes it when `SKILL_AGENT_E2E=1` is set.
- `SKILL_AGENT_RUNNER` must point to an executable compatible wrapper, using either an absolute path or a path relative to the repository root.
- Compatible wrapper contract: start with no extra arguments, read the prompt from `stdin`, and write results to `stdout`; by default it runs inside the `repository root`, but smoke tests may override the working directory to validate upward `openwiki.toml` discovery.

---

## Repository Layout

```text
llm-wiki/
├── skill/             # only public wiki skill directory
│   ├── wiki-init/
│   ├── wiki-ingest/
│   ├── wiki-query/
│   ├── wiki-lint/
│   ├── wiki-update/
│   └── agent-browser/
├── openwiki.example.toml    # sanitized, committable config example
├── openwiki.toml            # machine-local runtime contract (Git-ignored)
├── raw/
├── wiki/
│   ├── index.md
│   ├── log.md
│   └── pages/
├── concepts/
├── README.md
├── README.en.md
└── README.ja.md
```

---

## Skill Asset Boundary

- See `skill/ASSET-LAYOUT.md` for the public wiki skill boundary rules
- A `skill-private asset` must live inside the owning `skill/<name>/` directory tree
- `runtime` wiki objects remain `openwiki.toml` plus `raw/`, `wiki/`, and `concepts/` under `wiki_root`
- Approved skill-local directory names:
  - `templates/`
  - `examples/`
  - `fixtures/`
  - `assets/`
  - `scripts/`

---

## Skills

### wiki-init

- collects separate `config-dir` and `wiki-root`
- writes `openwiki.toml` into the configuration directory
- initializes `raw/`, `wiki/index.md`, `wiki/log.md`, `wiki/pages/`, and `concepts/` under `wiki-root`

### wiki-ingest

- reads new sources and discusses takeaways first
- resolves runtime paths through `openwiki.toml`
- updates pages, backlinks, index, and log

### wiki-query

- always reads `wiki/index.md` and relevant pages first
- uses `agent-browser` only when local wiki data is insufficient
- always offers to save valuable answers into `concepts/`

### wiki-lint

- detects broken links, orphan pages, contradictions, and stale content
- writes reports to `concepts/lint-<date>.md`
- shows diffs before fixes are applied

### wiki-update

- revises existing wiki pages
- confirms page-by-page
- checks downstream impact and logs every change

### agent-browser

- provides web retrieval and fact-checking
- prefers authoritative sources
- supplies URLs and page content that wiki workflows can cite

---

## Design Principles

- **Neutral runtime**: runtime behavior depends on `openwiki.toml`, not agent-specific file names
- **Single public skill surface**: public skills are maintained only in `skill/`
- **Knowledge compounding**: new knowledge should connect to the existing graph
- **Traceable sources**: important claims should point to file paths or URLs

---

## License

MIT
