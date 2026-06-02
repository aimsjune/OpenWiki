# Slug 生成规则

本文档定义 wiki-ingest 的 slug 生成规则。Slug 是 `wiki/pages/<slug>.md` 中的页面标识符。

---

## 基本规则

- **全小写**: 所有字母转为小写
- **连字符分隔**: 空格替换为连字符 `-`
- **无特殊字符**: 移除所有非字母数字和连字符的字符
- **无连续连字符**: 不出现 `--`
- **无首尾连字符**: 不以 `-` 开头或结尾

---

## 英文源标题

直接应用基本规则。

**示例**:

| 源标题 | Slug |
|--------|------|
| `Attention Is All You Need` | `attention-is-all-you-need` |
| `Go Error Handling Best Practices` | `go-error-handling-best-practices` |
| `CLI Design for AI Agents` | `cli-design-for-ai-agents` |

---

## 中文源标题

**先翻译为英文，再应用基本规则。明确排除拼音。**

**示例**:

| 源标题 | 翻译 | Slug |
|--------|------|------|
| 依赖注入模式 | Dependency Injection Pattern | `dependency-injection-pattern` |
| 分布式系统设计 | Distributed System Design | `distributed-system-design` |
| 金融核心轧差模式 | Financial Core Netting Pattern | `financial-core-netting-pattern` |

**反例（不使用）**:

| 源标题 | 拼音 Slug（不使用） |
|--------|---------------------|
| 依赖注入模式 | ~~`yi-lai-zhu-ru-mo-shi`~~ |
| 分布式系统设计 | ~~`fen-bu-shi-xi-tong-she-ji`~~ |

---

## 特殊处理

- **数字**: 保留，如 `3d-rendering-pipeline`
- **缩写**: 保持大写转小写，如 `CLI` → `cli`
- **版本号**: 保留点号或转为连字符，如 `python-3-12` 或 `python-3.12`
- **特殊符号**: 移除，如 `C++` → `c`
