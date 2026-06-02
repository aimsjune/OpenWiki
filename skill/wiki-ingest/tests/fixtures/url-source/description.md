# URL Source Fixture

## 输入描述

一个模拟的 URL 源，用于测试 wiki-ingest 从 URL 获取内容并创建 wiki 页面的流程。

## 源内容

**URL**: https://example.com/test-article

**标题**: 测试文章标题

**正文**:

这是一篇测试文章，介绍了测试驱动开发（TDD）的基本概念。

TDD 的核心循环是 RED → GREEN → REFACTOR：
1. RED: 先写一个失败的测试
2. GREEN: 写最少的代码让测试通过
3. REFACTOR: 重构代码，保持测试通过

## 预期输出

- 创建页面: `wiki/pages/test-driven-development.md`
- 页面包含 frontmatter: title, tags, updated, scope_level, scope_code
- index.md 中新增条目
- log.md 中追加记录
