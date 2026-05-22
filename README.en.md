# LLM Wiki — AI-Powered Personal Knowledge Base

**Language / 语言 / 言語：** [中文](README.md) ｜ English（default）｜ [日本語](README.ja.md)

---

## What is this?

LLM Wiki is a personal knowledge-base scaffold for `skill.io`-compatible agents. Raw material lives in `raw/`, structured knowledge lives in `wiki/`, and saved analyses live in `concepts/`. The repository exposes public skills through `skill/` and uses `WIKI.md` as the instance-level runtime contract.

**Core idea:**
- `WIKI.md` is the canonical runtime contract
- `skill/` is the canonical public wiki skill directory
- `config-dir` and `wiki-root` may be fully separated
- `raw/` stores immutable sources while `wiki/` is maintained by AI

---

## Runtime Model

```text
<config-dir>/
└── WIKI.md            # runtime contract with absolute wiki_root

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
2. Choose a `config-dir`, such as `~/wiki-config/personal-research`
3. Choose a `wiki-root`, such as `~/data/my-wiki`
4. Let `wiki-init` write `<config-dir>/WIKI.md` with an absolute `wiki_root`
5. Put source material into `<wiki-root>/raw/` and run `wiki-ingest`
6. Use `wiki-query`, `wiki-lint`, and `wiki-update` for ongoing work

Runtime discovery order:
- prefer an explicitly provided `config-dir`
- otherwise search upward from the current working directory for `WIKI.md`
- if still missing, ask for an absolute config-dir or run `wiki-init`

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
├── WIKI.md            # runtime contract for this repository instance
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
- `runtime` wiki objects remain `WIKI.md` plus `raw/`, `wiki/`, and `concepts/` under `wiki_root`
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
- writes `WIKI.md` into the configuration directory
- initializes `raw/`, `wiki/index.md`, `wiki/log.md`, `wiki/pages/`, and `concepts/` under `wiki-root`

### wiki-ingest

- reads new sources and discusses takeaways first
- resolves runtime paths through `WIKI.md`
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

- **Neutral runtime**: runtime behavior depends on `WIKI.md`, not agent-specific file names
- **Single public skill surface**: public skills are maintained only in `skill/`
- **Knowledge compounding**: new knowledge should connect to the existing graph
- **Traceable sources**: important claims should point to file paths or URLs

---

## License

MIT
