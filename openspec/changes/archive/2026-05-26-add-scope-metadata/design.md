# Design: add-scope-metadata

## Overview

为 wiki 页面增加"适用范围"（scope）元数据，在 `wiki/pages/<slug>.md` 的 frontmatter 中新增 `scope_level` 和 `scope_code` 两个字段，并在 `wiki/index.md` 的 category_3 区域按 `scope_code` 聚合展示。这是一个纯声明式元数据增强，不引入新的目录结构或存储后端。

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Scope 元数据架构                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  数据源 (Source of Truth):                                           │
│  ┌──────────────────────────────────────────────────┐              │
│  │ wiki/pages/<slug>.md                             │              │
│  │                                                  │              │
│  │ ---                                             │              │
│  │ scope_level: repo                               │              │
│  │ scope_code: llm-wiki                            │              │
│  │ ---                                             │              │
│  └────────────────────┬─────────────────────────────┘              │
│                       │                                             │
│                       ▼                                             │
│  聚合视图 (Aggregated View):                                        │
│  ┌──────────────────────────────────────────────────┐              │
│  │ wiki/index.md → category_3                       │              │
│  │                                                  │              │
│  │ ## 适用范围                                       │              │
│  │                                                  │              │
│  │ ### llm-wiki                                     │              │
│  │ - [[di-patterns]] — 代码仓库                     │              │
│  │ - [[testing-strategy]] — 代码仓库                 │              │
│  │                                                  │              │
│  │ ### fintech                                      │              │
│  │ - [[account-design]] — 行业                      │              │
│  │                                                  │              │
│  │ ### wisdom                                       │              │
│  │ - [[solid-principles]] — 智慧                    │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                     │
│  消费者:                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │  ingest  │ │ distill  │ │   lint   │ │  query   │              │
│  │ 写入scope │ │ 推断scope │ │ 校验scope │ │ 过滤scope │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| Page Frontmatter | 存储 scope 元数据（单一事实来源） | `wiki/pages/<slug>.md` 的 YAML frontmatter |
| index.md category_3 | 按 scope_code 聚合展示所有页面 | `wiki/index.md` 的 category_3 区域 |
| wiki-ingest (步骤 3, 6, 9) | 摄入时确定 scope，写入页面和 index | SKILL.md 流程描述 |
| wiki-distill (Phase 1, 3) | 从项目路径推断 scope，委托 ingest | SKILL.md 流程描述 |
| wiki-lint (步骤 2) | 校验 scope 字段合法性 | SKILL.md 流程描述 |
| wiki-query (步骤 1) | 利用 scope 辅助检索 | SKILL.md 流程描述 |
| wiki-update (步骤 5) | scope 变更时同步 index | SKILL.md 流程描述 |

### Scope 枚举与映射

```
scope_level 枚举值        中文名        含义
─────────────────────────────────────────────────
repo          →          代码仓库      单个代码仓库级别
domain        →          领域          跨若干个代码仓库适用
company       →          公司          跨若干个领域适用
industry      →          行业          跨若干个公司适用
wisdom        →          智慧          高度抽象，跨多行业多场景适用
```

约束：`wisdom` 级别的 `scope_code` 固定为 `wisdom`（强制一致性校验）。

## Data Flow

### Flow 1: wiki-ingest 摄入新页面

```
用户提供源 (URL/文件/文本)
  │
  ▼
步骤 2: 读取源全文
  │
  ▼
步骤 3: AI 分析 → 建议 scope_level + scope_code
  │
  │  "建议适用范围: 代码仓库 (llm-wiki)"
  │
  ▼
用户确认 scope
  │
  ├── 同意 → 使用 AI 建议
  └── 修改 → 用户指定 scope_level 和 scope_code
  │
  ▼
步骤 6: 写入 wiki/pages/<slug>.md
  │  frontmatter: { scope_level, scope_code }
  │  正文: **适用范围：** 代码仓库（llm-wiki）
  │
  ▼
步骤 9: 更新 wiki/index.md
  │
  ├── category_1 (Wiki 页面): 新增 [[slug]] 行
  └── category_3 (适用范围):
       ├── scope_code 组已存在 → 追加 [[slug]] 到该组
       └── scope_code 组不存在 → 创建 ### scope_code 区块
```

### Flow 2: wiki-distill 推断 scope

```
Phase 1: 分析项目路径
  │
  │  项目路径: /Users/.../git/llm-wiki
  │  → 推断 scope_level: repo
  │  → 推断 scope_code: llm-wiki
  │
  ▼
Phase 3.1: NEW 条目逐条决策
  │
  │  展示: 🆕 NEW: <经验标题>
  │        适用范围: 代码仓库 (llm-wiki) ← AI 推断
  │
  ▼
用户确认或修改 scope
  │
  ▼
委托 wiki-ingest 写入
  │  传递: scope_level, scope_code
  │  ingest 的步骤 3 跳过 scope 询问（已由 distill 确认）
```

### Flow 3: wiki-lint 校验 scope

```
步骤 2: 遍历 wiki/pages/*.md
  │
  ├── 检查 frontmatter 是否有 scope_level + scope_code
  │   └── 缺失 → Yellow Warning: missing-scope-fields
  │
  ├── 检查 scope_level 是否在合法枚举中
  │   └── 非法 → Yellow Warning: invalid-scope-level
  │
  ├── 检查 scope_code 是否符合 slug 规则
  │   └── 非法 → Yellow Warning: invalid-scope-code-format
  │
  └── 检查 scope_level 与 scope_code 一致性
      └── wisdom 但 scope_code ≠ "wisdom" → Yellow Warning: scope-level-code-mismatch
```

### Flow 4: wiki-query 利用 scope

```
步骤 1: 扫描 wiki/index.md
  │
  ├── category_1 (Wiki 页面): 按标题/摘要/标签匹配
  └── category_3 (适用范围): 辅助过滤
       │
       │  用户问: "llm-wiki 项目中有哪些设计模式？"
       │  → 识别 scope_code: llm-wiki
       │  → 优先检索 category_3 → llm-wiki 组下的页面
       │
       ▼
  合并候选页面列表 → 进入步骤 2 全文读取
```

### Flow 5: wiki-update scope 变更

```
步骤 5: 更新 wiki/index.md
  │
  │  页面 scope 从 {repo, llm-wiki} 变更为 {industry, wiki-ecosystem}
  │
  ├── category_3 → llm-wiki 组: 移除 [[slug]]
  │   └── 若 llm-wiki 组变为空 → 删除该 ### 区块
  │
  └── category_3 → wiki-ecosystem 组: 新增 [[slug]]
      └── 若 wiki-ecosystem 组不存在 → 创建 ### wiki-ecosystem 区块
```

## Interface Design for Testability

### Testable Interfaces

由于 wiki 技能是 LLM Agent 驱动的声明式流程（SKILL.md），"接口"体现为：

1. **SKILL.md 文本**：每个步骤的描述文本 → 可通过静态正则/语义匹配验证
2. **模板文件**：`skill/wiki-init/templates/index.md`、页面模板 → 可通过静态内容验证
3. **运行时文件**：`wiki/index.md`、`wiki/pages/<slug>.md` → 可通过 smoke 测试验证

| 被测接口 | 验证方式 | 测试类型 |
|---------|---------|---------|
| ingest 步骤 6 frontmatter 模板 | 正则匹配 `scope_level:` 和 `scope_code:` | 静态 |
| ingest 步骤 3 scope 确认交互 | 语义匹配 "建议适用范围" | 静态 |
| ingest 步骤 9 category_3 维护 | 语义匹配 category_3 + scope_code 聚合 | 静态 |
| lint 步骤 2 scope 规则 | 语义匹配 4 条规则名 | 静态 |
| index.md 模板 category_3 列名 | 字符串精确匹配 | 静态 |
| distill Phase 3.1 scope 传递 | 语义匹配 "scope" + "委托" | 静态 |
| query 步骤 1 scope 辅助 | 语义匹配 "适用范围" 或 "category_3" | 静态 |
| update 步骤 5 scope 同步 | 语义匹配 scope + category_3 | 静态 |

### Testability Guidelines

1. **声明级验证**：所有行为通过 SKILL.md 文本描述，测试验证文本内容的存在性和正确性
2. **模板隔离**：模板文件与技能逻辑分离，可独立静态验证
3. **枚举集中定义**：scope_level 的 5 个合法值和中文映射在 SKILL.md 中集中描述，便于验证一致性

## Category_3 聚合格式设计

```markdown
## 适用范围

### llm-wiki
- [[di-patterns]] — 代码仓库 | 2026-05-26
- [[testing-strategy]] — 代码仓库 | 2026-05-25

### fintech
- [[account-design]] — 行业 | 2026-05-22

### wisdom
- [[solid-principles]] — 智慧 | 2026-05-20
```

格式说明：
- 按 `scope_code` 分组，使用 `### scope_code` 三级标题
- 每组内按最后更新日期倒序排列
- 列表项格式：`- [[slug]] — <scope_level 中文名> | <最后更新>`
- 空组自动删除

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 文件系统 (页面读取/写入) | 使用临时目录 fixture |
| 用户交互 (scope 确认) | 预设确认输入，验证输出文本 |
| wiki/index.md 解析 | 构造 fixture index.md，验证更新后的内容 |

## Implementation Notes

1. **scope 字段非强制**：所有旧页面可继续正常工作，wiki-lint 以 Yellow Warning 提示缺失
2. **category_3 区域不存在时自动创建**：wiki-ingest 步骤 9 检测到 index.md 无 category_3 区域时，自动追加
3. **scope_code 与 page slug 独立**：`scope_code` 不要求与 page slug 有关联，是完全独立的维度
4. **ingest 步骤 3 scope 建议优先级**：
   - 用户显式指定 → 直接使用
   - wiki-distill 委托传入 → 直接使用（跳过 ingest 步骤 3 的 scope 询问）
   - AI 从源内容分析推断 → 建议，用户确认
5. **scope 中文映射统一位置**：在 `wiki-ingest` SKILL.md 中定义映射表，其他技能引用
