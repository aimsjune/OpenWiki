# Design: standard-wiki

## Overview

This change redefines the repository around a neutral `skill.io`-style runtime contract:

- `skill/` becomes the only canonical public skill directory.
- `WIKI.md` becomes the only canonical runtime contract file for a wiki instance.
- `config-dir` and `wiki-root` become explicit, independent locations.
- All wiki workflows resolve runtime state from `WIKI.md` instead of agent-specific files or directory conventions.

The design intentionally separates repository-level capability definitions from instance-level configuration and data storage. This keeps the runtime portable across compatible agents while preserving the existing wiki knowledge architecture under `wiki_root`.

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| `skill/` public skills | Expose canonical workflow definitions for `wiki-init`, `wiki-ingest`, `wiki-query`, `wiki-lint`, `wiki-update`, and `agent-browser` | Skill entrypoints under `skill/<name>/SKILL.md` |
| `WIKI.md` runtime contract | Store instance-scoped configuration, including absolute `wiki_root` and wiki conventions | `WIKI.md` file read by wiki workflow preconditions |
| `wiki-init` scaffold flow | Collect user inputs, validate paths, write `WIKI.md`, and create wiki data layout under `wiki_root` | Interactive `wiki-init` workflow |
| runtime resolution layer | Resolve configuration directory, parse `WIKI.md`, validate `wiki_root`, and return a normalized runtime context | Shared precondition behavior used by all wiki workflows |
| wiki data layout | Hold persistent knowledge data under `wiki_root` | Filesystem structure under `raw/`, `wiki/`, and `concepts/` |
| repository documentation | Teach users the neutral contract and canonical layout | `README.md`, `README.en.md`, `README.ja.md`, and generated initialization guidance |

## Interface Design for Testability

### Public Interfaces

```typescript
type WikiInitInput = {
  configDir: string;
  wikiRoot: string;
  domain: string;
  sourceTypes: string[];
  indexCategories: string[];
};

type WikiRuntimeConfig = {
  wikiRoot: string; // absolute path
  domain: string;
  sourceTypes: string[];
  indexCategories: string[];
};

type WikiInitResult = {
  configFilePath: string;
  wikiRoot: string;
  createdPaths: string[];
};

type WikiRuntimeContext = {
  configDir: string;
  configFilePath: string;
  wikiRoot: string;
  rawDir: string;
  wikiDir: string;
  pagesDir: string;
  indexFile: string;
  logFile: string;
  conceptsDir: string;
};

interface WikiConfigStore {
  load(configDir: string): Promise<WikiRuntimeConfig>;
  save(configDir: string, config: WikiRuntimeConfig): Promise<string>;
}

interface WikiLayoutPlanner {
  plan(wikiRoot: string): WikiRuntimeContext;
}

interface WikiScaffolder {
  scaffold(input: WikiInitInput): Promise<WikiInitResult>;
}

interface WikiRuntimeResolver {
  resolve(configDir: string): Promise<WikiRuntimeContext>;
}
```

### Testability Guidelines

1. **Accept dependencies, don't create them**
   ```typescript
   // Testable
   async function resolveWikiRuntime(configDir, configStore, layoutPlanner) {}

   // Hard to test
   async function resolveWikiRuntime(configDir) {
     const configStore = new FileBackedWikiConfigStore();
     const layoutPlanner = new DefaultWikiLayoutPlanner();
   }
   ```

2. **Return results, don't produce side effects**
   ```typescript
   // Testable
   function planWikiLayout(wikiRoot): WikiRuntimeContext {}

   // Hard to test
   function setGlobalWikiLayout(wikiRoot): void {
     global.runtimeContext = buildContext(wikiRoot);
   }
   ```

3. **Small surface area**
   - Keep wiki runtime resolution centered on a single `resolve(configDir)` style interface
   - Keep initialization centered on a single `scaffold(input)` style interface
   - Reuse one normalized runtime context so every workflow reads the same resolved paths

## Data Flow

### 1. Initialization flow

```text
User input
  ├─ configDir
  ├─ wikiRoot
  ├─ domain
  ├─ sourceTypes
  └─ indexCategories
        │
        ▼
Path validation
  ├─ configDir must be writable
  ├─ wikiRoot must be absolute
  └─ wikiRoot target must be writable/creatable
        │
        ▼
WIKI.md generation
  └─ write runtime contract to <configDir>/WIKI.md
        │
        ▼
Layout planning
  └─ derive raw/, wiki/, wiki/pages/, wiki/index.md, wiki/log.md, concepts/
        │
        ▼
Filesystem scaffold
  └─ create planned directories and starter files under wikiRoot
        │
        ▼
Result summary
```

Observable outcomes:
- `WIKI.md` exists in `config-dir`
- `wiki_root` is absolute in `WIKI.md`
- wiki data files exist under `wiki-root`

### 2. Runtime resolution flow for wiki skills

```text
Skill starts
   │
   ▼
Receive configDir or locate configured working context
   │
   ▼
Read <configDir>/WIKI.md
   │
   ▼
Parse and validate wiki_root
   ├─ must exist as absolute path
   ├─ must point to expected wiki layout
   └─ return explicit error if invalid
   │
   ▼
Build normalized runtime context
   │
   ▼
Workflow proceeds using resolved paths only
```

Observable outcomes:
- precondition failures are tied to `WIKI.md` issues, not missing legacy files
- all wiki workflows operate on the same resolved path set

### 3. Repository skill layout flow

```text
Repository skill discovery
   │
   ▼
Enumerate skill/*
   │
   ├─ wiki-init
   ├─ wiki-ingest
   ├─ wiki-query
   ├─ wiki-lint
   ├─ wiki-update
   └─ agent-browser
```

Observable outcomes:
- public skills are discoverable in one canonical location
- no compatibility-layer indirection is needed

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| File System | Use temp directories for `config-dir` and `wiki-root`, plus fixture files for `WIKI.md` |
| Interactive user input | Use scripted prompt answers or a prompt adapter that can be stubbed in tests |
| Markdown/frontmatter parsing | Use fixed fixture content and golden-file assertions |
| Skill execution environment | Test public precondition behavior through a thin harness that simulates skill startup inputs |

## Implementation Notes

- `WIKI.md` must contain an explicit absolute `wiki_root`; relative path expansion is not part of the canonical contract.
- `config-dir` and `wiki-root` are independent by design; initialization must not silently collapse them into one path.
- `skill/` is the only supported public skill location. Migration must remove `.claude/skills/` and `.agents/skills/` from canonical docs and runtime assumptions.
- `agent-browser` remains part of the public workflow surface and moves into `skill/` with the other wiki skills.
- Existing wiki knowledge architecture remains intact under `wiki_root`:
  - `raw/` for source materials
  - `wiki/` for structured pages plus `index.md` and `log.md`
  - `concepts/` for generated analyses
- Runtime resolution should fail fast with clear errors when:
  - `WIKI.md` is missing
  - `wiki_root` is not absolute
  - `wiki_root` points to an invalid or inaccessible layout
