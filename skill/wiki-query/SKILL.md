---
name: wiki-query
description: Use when asking a question against a personal wiki built with wiki-init and wiki-ingest. Do not answer from general knowledge — always read the wiki pages first.
---
# Wiki Query

Ask a question. Read the wiki. Synthesize with citations. Offer to file the answer back.

## Pre-condition

Use this discovery order for the configuration directory:

1. If the user explicitly provides a `config-dir`, use it.
2. Otherwise, check `~/.openwiki/openwiki.toml`. If it exists and is valid, use it as the default wiki config.
3. If the default config is not found or invalid, search upward from the current working directory for `openwiki.toml`.
4. If `openwiki.toml` is still not found, ask the user for an absolute config-dir or tell them to run `wiki-init` first.

If the default wiki config at `~/.openwiki` is used, tell the user you are using the default wiki config.

Read `openwiki.toml` to resolve the absolute `wiki_root` plus:

- `wiki/index.md`
- `wiki/log.md`
- `wiki/pages/`
- `entities/`
- `concepts/`

Do not depend on legacy agent-specific files or compatibility directories.

> **日期占位符说明：** 本文档中的 `<today>` 在执行时必须替换为实际当前日期，格式为 YYYY-MM-DD（如 `2026-05-26`）。

## Process

### 1. Read `wiki/index.md` first

Use the CLI to scan the full index:

```bash
openwiki page list --json
```

Identify which pages are likely relevant. Do not answer from general knowledge first.

同时扫描 category_3（适用范围）区域。当用户问题涉及特定代码仓库或领域时，优先检索该 `scope_code` 下的页面。

### 2. Read relevant pages

Use the CLI to read pages (supports cross-directory search across `wiki/pages/`, `entities/`, `concepts/`):

```bash
openwiki page get <slug> --json
```

Read the identified pages in full. Follow one level of `[[slug]]` links if they point to pages that seem relevant to the question.

### 3. Outside supplement (if needed)

**铁律：外部搜索必须并行执行。** 当本地 wiki 无法满足查询时，以下三个渠道的搜索必须在同一轮 tool call 中同时发起，禁止串行逐个执行。违反此规则属于 Common Mistake。

同时，Step 2 的 grep/页面读取与 Step 3 的外部搜索之间没有依赖关系——一旦 Step 1 确认 wiki 中无精确匹配，即可将 grep + 外部搜索全部并行发出。

**并行启动以下搜索（必须在同一轮 tool call 中完成）：**

| 渠道 | 工具 | 命令 / 用法 |
|------|------|-------------|
| Web 搜索 | `WebSearch` 工具 | 直接调用，使用用户原始查询中的核心术语。可同时发起多个不同关键词的搜索 |
| ByteTech 内部文章 | `RunCommand` | `python3 scripts/bytetech_api.py search "<关键词>"`（在 bytetech skill 目录下执行） |
| 飞书文档 | `RunCommand` | `lark-cli docs +search --as user --query "<关键词>"` |

三个搜索的关键词应保持一致，使用用户原始查询中的核心术语。

#### lark-cli 文档搜索详细用法

飞书文档搜索用于查找字节跳动内部知识库中的规范文档：

```bash
# 搜索飞书云文档（必须使用 --query flag，不支持位置参数）
lark-cli docs +search --as user --query "<关键词>"
```

搜索结果返回文档 token 和标题，可进一步用 `lark-cli docs +fetch --as user --doc "<token>"` 获取正文。

#### agent-browser（仅当需要抓取特定 URL 时使用）

当搜索结果返回了需要深入阅读的特定网页时，使用 `agent-browser` 抓取内容。优先使用权威站点：

- **General concepts**: en.wikipedia.org / zh.wikipedia.org
- **Tech/Programming**: docs.python.org, developer.mozilla.org, arxiv.org, github.com
- **AI/ML Papers**: arxiv.org, paperswithcode.com, huggingface.co
- **News/Current Events**: reuters.com, bbc.com, theguardian.com
- **Academic**: scholar.google.com, semanticscholar.org

### 4. Synthesize the answer

Write a response that:

- is grounded in the wiki pages you read
- cites inline using `[[slug]]` for local pages and URLs for web sources
- notes agreements and disagreements between pages
- flags gaps like "The wiki has no page on X"
- suggests follow-up sources to ingest or questions to investigate

### 5. Always offer to save

After answering, say:

> "Worth saving to `concepts/<suggested-slug>.md`?"

If yes:

- write the page with frontmatter: `tags: [query, analysis]`, `sources: <number>`, `updated: <today>`
- update `wiki/index.md` under **Concepts Pages**
- append a `query` record to `wiki/log.md`

If no:

- still append a `query` record to `wiki/log.md` noting the pages read and whether web verification was used

## Common Mistakes

- **Answering from memory** — always read the wiki pages first
- **Skipping the save offer** — always offer
- **No citations** — every factual claim should trace back to a `[[slug]]` or URL
- **串行执行外部搜索** — Step 3 的 Web 搜索、ByteTech 搜索、lark-cli 搜索必须在同一轮 tool call 中并行发起，禁止逐个串行调用
- **跳过 lark-cli 搜索** — 当查询涉及字节跳动内部规范/文档时，lark-cli 搜索是必选项，不可省略
