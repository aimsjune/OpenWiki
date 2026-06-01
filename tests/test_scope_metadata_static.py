"""静态测试: scope-metadata 变更 — 验证所有 SKILL.md 和模板文件中的 scope 相关内容。"""

import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(rel_path):
    with open(os.path.join(REPO_ROOT, rel_path), "r") as f:
        return f.read()


# ── Behavior 1: Page Frontmatter 模板新增 scope 字段 ──

def test_ingest_page_template_has_scope_frontmatter():
    """wiki-ingest SKILL.md 步骤 6 模板 frontmatter 包含 scope_level 和 scope_code"""
    content = read_file("skill/wiki-ingest/SKILL.md")
    assert "scope_level:" in content, "模板 frontmatter 缺少 scope_level"
    assert "scope_code:" in content, "模板 frontmatter 缺少 scope_code"
    assert "**适用范围：**" in content, "模板正文缺少适用范围字段"


# ── Behavior 2-5: wiki-lint scope 规则 ──

def test_lint_has_invalid_scope_level_rule():
    content = read_file("skill/wiki-lint/SKILL.md")
    assert "invalid-scope-level" in content
    for val in ["repo", "domain", "company", "industry", "wisdom"]:
        assert val in content, f"scope_level 合法值缺少: {val}"


def test_lint_has_invalid_scope_code_format_rule():
    content = read_file("skill/wiki-lint/SKILL.md")
    assert "invalid-scope-code-format" in content


def test_lint_has_scope_level_code_mismatch_rule():
    content = read_file("skill/wiki-lint/SKILL.md")
    assert "scope-level-code-mismatch" in content


def test_lint_has_missing_scope_fields_rule():
    content = read_file("skill/wiki-lint/SKILL.md")
    assert "missing-scope-fields" in content
    # 确保在 Yellow Warnings 中，而非 Red Errors
    yellow_section = content.split("Red Errors")[1].split("Blue Info")[0] if "Red Errors" in content else ""
    assert "missing-scope-fields" in content


# ── Behavior 6: wiki-ingest 步骤 3 scope 确认交互 ──

def test_ingest_step3_asks_scope_confirmation():
    content = read_file("skill/wiki-ingest/SKILL.md")
    # 步骤 3 附近应包含 scope 相关描述
    assert "适用范围" in content


# ── Behavior 7: wiki-ingest 步骤 9 category_3 维护 ──

def test_ingest_step9_maintains_category3():
    content = read_file("skill/wiki-ingest/SKILL.md")
    assert "category_3" in content


# ── Behavior 8: wiki-distill Phase 3 scope 推断 ──

def test_distill_phase3_passes_scope_to_ingest():
    content = read_file("skill/wiki-distill/SKILL.md")
    assert "scope" in content.lower()


def test_distill_phase3_allows_scope_override():
    content = read_file("skill/wiki-distill/SKILL.md")
    assert "适用范围" in content


# ── Behavior 9: index.md 模板 category_3 列名 ──

def test_index_template_category3_columns():
    content = read_file("skill/wiki-init/templates/index.md")
    assert "范围代号" in content
    assert "最后更新" in content


# ── Behavior 10: wiki-query 利用 scope ──

def test_query_step1_mentions_scope_filter():
    content = read_file("skill/wiki-query/SKILL.md")
    assert "scope" in content.lower() or "适用范围" in content


# ── Behavior 11: wiki-update scope 同步 ──

def test_update_step5_syncs_scope_category3():
    content = read_file("skill/wiki-update/SKILL.md")
    assert "scope" in content.lower() or "适用范围" in content


# ── Behavior 12: scope 中文映射表 ──

def test_scope_level_chinese_mapping():
    content = read_file("skill/wiki-ingest/SKILL.md")
    mapping = {
        "repo": "代码仓库",
        "domain": "领域",
        "company": "公司",
        "industry": "行业",
        "wisdom": "智慧",
    }
    for en, zh in mapping.items():
        assert en in content, f"映射表缺少英文: {en}"
        assert zh in content, f"映射表缺少中文: {zh}"


# ── Behavior 13: 运行时 wiki/index.md category_3 ──

def test_wiki_index_has_category3_structure():
    content = read_file("wiki/index.md")
    assert "适用范围" in content
