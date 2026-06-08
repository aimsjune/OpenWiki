import json
import os
import re
import sys


def parse_frontmatter(filepath):
    with open(filepath) as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_text = parts[1].strip()
    result = {}
    current_key = None
    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key:
            val = stripped[2:].strip()
            if not isinstance(result.get(current_key), list):
                result[current_key] = []
            result[current_key].append(val.strip('"').strip("'"))
        elif ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                result[key] = [v.strip() for v in val[1:-1].split(",")]
                current_key = None
            elif not val:
                result[key] = []
                current_key = key
            else:
                result[key] = val.strip('"').strip("'")
                current_key = None
    return result


def parse_toml(filepath):
    result = {}
    current_section = result
    with open(filepath) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                section_name = stripped[1:-1].strip()
                section_path = section_name.split(".")
                current_section = result
                for part in section_path:
                    if part not in current_section:
                        current_section[part] = {}
                    current_section = current_section[part]
                continue
            if "=" in stripped:
                key, _, val = stripped.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                current_section[key] = val
    return result


def check_wiki_config(wiki_root):
    config_path = os.path.join(wiki_root, "openwiki.toml")
    if not os.path.exists(config_path):
        return {"name": "wiki-config-exists", "status": "fail", "message": f"openwiki.toml 不存在于 {wiki_root}"}

    cfg = parse_toml(config_path)
    missing = []
    if "wiki_root" not in cfg:
        missing.append("wiki_root")
    wiki_section = cfg.get("wiki", {})
    if "primary_language" not in wiki_section:
        missing.append("wiki.primary_language")

    if missing:
        return {"name": "wiki-config-fields", "status": "fail", "message": f"openwiki.toml 缺少必填字段: {', '.join(missing)}"}

    return {"name": "wiki-config-fields", "status": "pass", "message": "openwiki.toml 必填字段完整"}


def check_index_table(wiki_root):
    index_path = os.path.join(wiki_root, "wiki", "index.md")
    if not os.path.exists(index_path):
        return {"name": "index-table-format", "status": "fail", "message": f"wiki/index.md 不存在于 {wiki_root}"}

    with open(index_path) as f:
        content = f.read()

    legacy_format = "## Wiki 页面" in content and "| 页面 |" in content and "摘要" in content
    current_sections = all(section in content for section in ("## 资料页", "## 实体页", "## 概念页"))
    current_format = current_sections and content.count("| Slug | 标题 | 类型 | 标签 | 适用范围 | 最后更新 |") >= 3
    if not legacy_format and not current_format:
        return {"name": "index-table-format", "status": "fail", "message": "index.md 不符合旧版或当前多类型索引格式"}

    return {"name": "index-table-format", "status": "pass", "message": "index.md 表格格式正确"}


def wiki_page_paths(wiki_root):
    paths = []
    for relative_dir in ("wiki/pages", "entities", "concepts"):
        page_dir = os.path.join(wiki_root, relative_dir)
        if not os.path.isdir(page_dir):
            continue
        paths.extend(
            os.path.join(page_dir, fname)
            for fname in os.listdir(page_dir)
            if fname.endswith(".md")
        )
    return paths


def check_cross_references(wiki_root):
    pages_dir = os.path.join(wiki_root, "wiki", "pages")
    if not os.path.isdir(pages_dir):
        return {"name": "cross-references", "status": "fail", "message": f"wiki/pages/ 目录不存在于 {wiki_root}"}

    page_paths = wiki_page_paths(wiki_root)
    existing_slugs = {os.path.basename(path)[:-3] for path in page_paths}
    broken_links = []
    ref_pattern = re.compile(r"\[\[([^\]]+)\]\]")

    for page_path in page_paths:
        with open(page_path) as f:
            content = f.read()
        for match in ref_pattern.finditer(content):
            target = match.group(1)
            if target not in existing_slugs:
                broken_links.append(f"{os.path.basename(page_path)[:-3]} -> [[{target}]]")

    if broken_links:
        return {"name": "cross-references", "status": "fail", "message": f"发现 {len(broken_links)} 个断链: {', '.join(broken_links[:5])}"}

    return {"name": "cross-references", "status": "pass", "message": "所有交叉引用可达"}


def check_page_frontmatter(wiki_root):
    pages_dir = os.path.join(wiki_root, "wiki", "pages")
    if not os.path.isdir(pages_dir):
        return {"name": "page-frontmatter", "status": "fail", "message": f"wiki/pages/ 目录不存在于 {wiki_root}"}

    required_fields = ["title", "updated", "scope_level", "scope_code"]
    valid_scope_levels = {"repo", "domain", "company", "industry", "wisdom"}
    missing_pages = []

    for page_path in wiki_page_paths(wiki_root):
        fm = parse_frontmatter(page_path)
        slug = os.path.basename(page_path)[:-3]

        missing = [f for f in required_fields if f not in fm]
        if missing:
            missing_pages.append(f"{slug}: 缺少 {', '.join(missing)}")
            continue

        if fm.get("scope_level") not in valid_scope_levels:
            missing_pages.append(f"{slug}: scope_level 值 '{fm['scope_level']}' 无效")

        if fm.get("scope_level") == "wisdom" and fm.get("scope_code") != "wisdom":
            missing_pages.append(f"{slug}: wisdom 级别的 scope_code 必须为 'wisdom'")

    if missing_pages:
        return {"name": "page-frontmatter", "status": "fail", "message": f"frontmatter 问题: {'; '.join(missing_pages[:5])}"}

    return {"name": "page-frontmatter", "status": "pass", "message": "所有页面 frontmatter 字段完整"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"checks": [{"name": "usage", "status": "fail", "message": "用法: validate_wiki.py <wiki_root>"}]}, ensure_ascii=False, indent=2))
        sys.exit(1)

    wiki_root = sys.argv[1]
    if not os.path.isdir(wiki_root):
        print(json.dumps({"checks": [{"name": "wiki-root", "status": "fail", "message": f"wiki_root 不存在: {wiki_root}"}]}, ensure_ascii=False, indent=2))
        sys.exit(1)

    checks = [
        check_wiki_config(wiki_root),
        check_index_table(wiki_root),
        check_cross_references(wiki_root),
        check_page_frontmatter(wiki_root),
    ]

    print(json.dumps({"checks": checks}, ensure_ascii=False, indent=2))

    has_failure = any(c["status"] == "fail" for c in checks)
    sys.exit(1 if has_failure else 0)


if __name__ == "__main__":
    main()
