---
name: agent-browser
description: "Browser automation via the agent-browser CLI. Use when you need to browse the web for research or fact-checking, extract real-time information from URLs, verify claims against live web pages, scrape structured content from websites, or interact with web apps."
---

# agent-browser

Fast native Rust CLI for browser automation. Uses a persistent background daemon so browser state persists across commands in the same session.

## Core Workflow

```bash
# 1. Navigate
agent-browser open <url>

# 2. Get interactive elements with refs
agent-browser snapshot -i --json

# 3. Interact using refs
agent-browser click @e2
agent-browser fill @e3 "search term"
agent-browser press Enter

# 4. Re-snapshot after page changes
agent-browser snapshot -i --json

# 5. Get page text
agent-browser get text "body"

# 6. Close when done
agent-browser close
```

## Research Workflow

When supplementing local wiki knowledge with live web data:

```bash
agent-browser open "https://example.com/article"
agent-browser wait --load networkidle
agent-browser get text "article" 2>/dev/null || agent-browser get text "main" 2>/dev/null || agent-browser get text "body"
```

## Search Workflow

```bash
agent-browser open "https://www.google.com/search?q=your+query"
agent-browser snapshot -i --json
agent-browser click @e5
```

## Key Notes

- Use `--json` for machine-readable output when possible
- Prefer authoritative sources for wiki enrichment
- Keep captured URLs so downstream wiki skills can cite them

See `agent-browser --help` for the full command reference.
