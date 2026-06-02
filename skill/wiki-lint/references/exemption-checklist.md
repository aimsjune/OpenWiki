# 豁免清单

本文档列出 wiki-lint 语言规则检查中应被豁免的英文内容。这些场景中的英文内容不触发语言相关规则（content-not-chinese-primary、missing-chinese-title、missing-term-glossary）。

---

## 1. 代码块

```
```...```
```

三反引号包裹的代码块，无论内容是什么语言，均不参与中文占比计算。

**示例**:
```go
func main() {
    fmt.Println("Hello, World")
}
```

---

## 2. 行内代码

`` `code` ``

单反引号包裹的行内代码，通常为函数名、变量名、命令等。

**示例**: 使用 `fmt.Println` 输出内容。

---

## 3. URL 链接

`https://...` 或 `http://...`

完整的 URL 链接，通常出现在来源引用或外部链接中。

**示例**: 来源：https://example.com/doc

---

## 4. YAML Frontmatter

`---...---`

页面顶部的 YAML 元数据块，包含 `title`、`tags`、`sources`、`updated`、`scope_level`、`scope_code` 等字段。

**示例**:
```yaml
---
title: 示例页面
tags: [go, design-pattern]
sources: 1
updated: 2026-05-26
scope_level: repo
scope_code: example
---
```

---

## 5. 术语首次标注

`中文术语（English Term）` 或 `English Term（中文术语）`

技术术语首次出现时附带的中英文对照标注。括号内的英文/中文部分不触发语言规则。

**示例**:
- 依赖注入（Dependency Injection）是一种设计模式。
- Dependency Injection（依赖注入）is a design pattern.
