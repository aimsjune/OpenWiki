from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = REPO_ROOT / "skill" / "wiki-init" / "templates"
CATEGORY_PLACEHOLDERS = tuple(f"<category_{i}>" for i in range(1, 5))
EXPECTED_INDEX_CATEGORY_COUNT = len(CATEGORY_PLACEHOLDERS)


@dataclass
class TempWikiInstance:
    temp_dir: TemporaryDirectory
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
    return (TEMPLATE_ROOT / name).read_text(encoding="utf-8")


def fixture_path() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _require_exact_entries(name: str, values: list[str], expected_count: int) -> None:
    if len(values) != expected_count:
        raise ValueError(f"{name} must contain exactly {expected_count} entries")


def _require_non_empty_entries(name: str, values: list[str]) -> None:
    if not values:
        raise ValueError(f"{name} must contain at least 1 entry")


def _assert_no_placeholders(name: str, content: str, placeholders: tuple[str, ...]) -> None:
    remaining = [placeholder for placeholder in placeholders if placeholder in content]
    if remaining:
        joined = ", ".join(remaining)
        raise ValueError(f"{name} still contains unreplaced placeholders: {joined}")


def _expected_data(fixture_root: Path) -> dict[str, object]:
    return json.loads(
        (fixture_root / "expected" / "key-facts.json").read_text(encoding="utf-8")
    )


def _read_fixture(fixture_root: Path, name: str) -> str:
    return (fixture_root / name).read_text(encoding="utf-8").strip()


def _replace_section_block(
    content: str,
    *,
    start_marker: str,
    end_marker: str,
    replacement: str,
) -> str:
    start_index = content.find(start_marker)
    end_index = content.find(end_marker)
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        raise ValueError(
            f"template section {start_marker!r} to {end_marker!r} was not found"
        )
    return content[:start_index] + replacement + content[end_index:]


def _extract_section_lines(page_md: str, marker: str) -> list[str]:
    if marker not in page_md:
        raise ValueError("query requires an ingested wiki page with key takeaways")

    section_lines: list[str] = []
    in_section = False
    for line in page_md.splitlines():
        stripped = line.strip()
        if stripped == marker:
            in_section = True
            continue
        if in_section and stripped.startswith("#"):
            break
        if in_section:
            section_lines.append(line)
    return section_lines


def _extract_key_takeaways(page_md: str) -> list[str]:
    takeaways: list[str] = []
    for line in _extract_section_lines(page_md, "## Key Takeaways"):
        stripped = line.strip()
        if stripped.startswith("- "):
            takeaways.append(stripped[2:])
    return takeaways


def _replace_key_takeaway_line(page_md: str, *, target_line: str, replacement_line: str) -> str:
    lines = page_md.splitlines()
    in_takeaways = False
    matched_indexes: list[int] = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## Key Takeaways":
            in_takeaways = True
            continue
        if in_takeaways and stripped.startswith("#"):
            break
        if in_takeaways and stripped == f"- {target_line}":
            matched_indexes.append(index)

    if len(matched_indexes) != 1:
        raise ValueError(
            "update requires the target takeaway line to exist exactly once in Key Takeaways"
        )

    lines[matched_indexes[0]] = f"- {replacement_line}"
    return "\n".join(lines) + ("\n" if page_md.endswith("\n") else "")


def _update_index_row_for_slug(index_md: str, *, slug: str, updated_date: str) -> str:
    lines = index_md.splitlines()
    matched_indexes = [
        index for index, line in enumerate(lines) if line.strip().startswith(f"| [[{slug}]] |")
    ]
    if len(matched_indexes) != 1:
        raise ValueError(f"update requires exactly one index row for slug {slug}")

    row = lines[matched_indexes[0]]
    columns = [column.strip() for column in row.split("|")]
    if len(columns) != 6:
        raise ValueError(f"index row for slug {slug} must be a 4-column markdown table row")

    lines[matched_indexes[0]] = (
        f"| {columns[1]} | {columns[2]} | {columns[3]} | {updated_date} |"
    )
    return "\n".join(lines) + ("\n" if index_md.endswith("\n") else "")


def run_init_reference(
    *,
    instance: TempWikiInstance,
    domain: str,
    source_types: list[str],
    index_categories: list[str],
) -> None:
    _require_non_empty_entries("source_types", source_types)
    _require_exact_entries(
        "index_categories", index_categories, EXPECTED_INDEX_CATEGORY_COUNT
    )
    if not instance.wiki_root.is_absolute():
        raise ValueError("wiki_root must be an absolute path")

    contract = _load_template("WIKI.md")
    contract = contract.replace("/absolute/path/to/wiki-root", str(instance.wiki_root))
    contract = contract.replace("<user domain description>", domain)
    contract = _replace_section_block(
        contract,
        start_marker="source_types:\n",
        end_marker="index_categories:\n",
        replacement=(
            "source_types:\n"
            + "\n".join(f"  - {source_type}" for source_type in source_types)
            + "\n"
        ),
    )
    for placeholder, category in zip(CATEGORY_PLACEHOLDERS, index_categories):
        contract = contract.replace(placeholder, category)
    _assert_no_placeholders("WIKI.md", contract, CATEGORY_PLACEHOLDERS)

    wiki_dir = instance.wiki_root / "wiki"
    pages_dir = wiki_dir / "pages"
    raw_dir = instance.wiki_root / "raw"
    concepts_dir = instance.wiki_root / "concepts"

    pages_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    concepts_dir.mkdir(parents=True, exist_ok=True)

    index_md = _load_template("index.md")
    for placeholder, category in zip(CATEGORY_PLACEHOLDERS, index_categories):
        index_md = index_md.replace(placeholder, category)
    _assert_no_placeholders("index.md", index_md, CATEGORY_PLACEHOLDERS)

    log_md = _load_template("log.md")
    log_md = log_md.replace("<today>", "2026-05-22")
    log_md = log_md.replace("<domain>", domain)

    (instance.config_dir / "WIKI.md").write_text(contract, encoding="utf-8")
    (wiki_dir / "index.md").write_text(index_md, encoding="utf-8")
    (wiki_dir / "log.md").write_text(log_md, encoding="utf-8")


def run_ingest_reference(*, instance: TempWikiInstance, fixture_root: Path) -> str:
    expected = _expected_data(fixture_root)
    source_md = (fixture_root / "source.md").read_text(encoding="utf-8")
    slug = _read_fixture(fixture_root, "expected/created-page-slug.txt")
    facts = expected["facts"]
    updated_fact = expected["updated_fact"]
    raw_source_relative_path = f"raw/{slug}-source.md"

    if not source_md.startswith(f"# {expected['title']}"):
        raise ValueError("source fixture title does not match expected title")

    raw_source_path = instance.wiki_root / raw_source_relative_path
    raw_source_path.write_text(source_md, encoding="utf-8")

    page_md = f"""---
title: {expected["title"]}
tags: [testing, e2e]
sources: 1
updated: 2026-05-22
---

# {expected["title"]}

**Source:** {raw_source_relative_path}
**Date ingested:** 2026-05-22
**Type:** article

## Key Takeaways

- {facts[0]}
- {facts[1]}
- {updated_fact["old"]}
"""
    page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
    page_path.write_text(page_md, encoding="utf-8")

    index_path = instance.wiki_root / "wiki" / "index.md"
    index_md = index_path.read_text(encoding="utf-8")
    index_md += (
        f"\n| [[{slug}]] | Local-first workflow notes | testing, e2e | 2026-05-22 |\n"
    )
    index_path.write_text(index_md, encoding="utf-8")

    log_path = instance.wiki_root / "wiki" / "log.md"
    log_md = log_path.read_text(encoding="utf-8")
    log_md += (
        "\n## [2026-05-22] ingest | Local-First Wiki Testing\n"
        "- Created/Updated pages: local-first-wiki-testing\n"
    )
    log_path.write_text(log_md, encoding="utf-8")
    return slug


def run_query_reference(*, instance: TempWikiInstance, fixture_root: Path) -> str:
    expected = _expected_data(fixture_root)
    query_text = _read_fixture(fixture_root, "query.txt")
    if "testing layers" not in query_text.lower():
        raise ValueError("query fixture no longer matches the expected scenario")

    slug = str(expected["slug"])
    index_md = (instance.wiki_root / "wiki" / "index.md").read_text(encoding="utf-8")
    page_link = f"[[{slug}]]"
    page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
    if page_link not in index_md or not page_path.exists():
        raise ValueError(
            "query requires an ingested wiki page registered in the current wiki state"
        )

    page_md = page_path.read_text(encoding="utf-8")
    takeaways = _extract_key_takeaways(page_md)
    if len(takeaways) < 2:
        raise ValueError("query requires at least two key takeaways in the wiki page")

    answer = (
        f"{page_link} says {takeaways[0]} "
        f"and {takeaways[1]}"
    )
    log_path = instance.wiki_root / "wiki" / "log.md"
    log_md = log_path.read_text(encoding="utf-8")
    log_md += (
        f"\n## [2026-05-22] query | {slug}\n"
        f"- Pages read: {slug}\n"
    )
    log_path.write_text(log_md, encoding="utf-8")
    return answer


def run_update_reference(*, instance: TempWikiInstance, fixture_root: Path, slug: str) -> None:
    expected = _expected_data(fixture_root)
    update_text = _read_fixture(fixture_root, "update.md")
    target_line = str(expected["updated_fact"]["old"])
    replacement_line = str(expected["updated_fact"]["new"])
    if f"Target line: {target_line}" not in update_text:
        raise ValueError("update fixture does not include the expected target line")
    if f"Replacement line: {replacement_line}" not in update_text:
        raise ValueError("update fixture does not include the expected replacement line")

    page_path = instance.wiki_root / "wiki" / "pages" / f"{slug}.md"
    page_md = page_path.read_text(encoding="utf-8")
    updated_page_md = _replace_key_takeaway_line(
        page_md,
        target_line=target_line,
        replacement_line=replacement_line,
    ).replace("updated: 2026-05-22", "updated: 2026-05-23")

    index_path = instance.wiki_root / "wiki" / "index.md"
    index_md = index_path.read_text(encoding="utf-8")
    updated_index_md = _update_index_row_for_slug(
        index_md,
        slug=slug,
        updated_date="2026-05-23",
    )

    page_path.write_text(updated_page_md, encoding="utf-8")
    index_path.write_text(updated_index_md, encoding="utf-8")

    log_path = instance.wiki_root / "wiki" / "log.md"
    log_md = log_path.read_text(encoding="utf-8")
    log_md += (
        f"\n## [2026-05-23] update | {slug}\n"
        f"- Replaced fact: {expected['updated_fact']['new']}\n"
    )
    log_path.write_text(log_md, encoding="utf-8")
