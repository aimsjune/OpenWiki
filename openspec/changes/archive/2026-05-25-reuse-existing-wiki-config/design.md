# Design: reuse-existing-wiki-config

## Overview

这个变更为 `wiki-init` 增加“已有配置复用”快速路径，但不改变它作为初始化技能的边界。核心设计是：当用户显式提供 `config-dir` 时，先尝试把该目录解析为现有 wiki 运行时入口；如果 `WIKI.md` 有效，则返回一个“已连接现有 wiki”的运行时摘要，并裁剪掉所有已知初始化问题；如果配置无效，则以非破坏方式快速失败，只有在用户显式选择 `reinitialize` 时才允许进入覆盖式初始化。

设计重点不是让 `wiki-init` 自动代理 `wiki-query`，而是让它成为“已有实例识别 + 初始化入口”的可预测前门，并把后续工作流继续委托给 `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update`。

## Architecture

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| 显式配置入口识别器 | 判断用户是否在 `wiki-init` 请求中显式提供了 `config-dir` | `detectExplicitConfigDir(input)` |
| 运行时契约加载器 | 读取并解析 `<config-dir>/WIKI.md`，返回标准化运行时数据 | `loadWikiContract(configDir)` |
| 现有 wiki 校验器 | 验证 `wiki_root` 是否绝对、可访问且具备最小布局 | `validateExistingWiki(runtime)` |
| 初始化提问规划器 | 根据“新建模式”或“复用模式”决定还需要问哪些问题 | `planInitQuestions(mode, runtime)` |
| 复用结果摘要器 | 生成“已连接现有 wiki”的用户可见摘要和后续 workflow 指引 | `buildReuseSummary(runtime)` |
| 重新初始化分支 | 仅在用户显式要求时写入新的 `WIKI.md` 并重建布局 | 现有 `wiki-init` 写入/脚手架流程 |

## Interface Design for Testability

### Public Interfaces

```typescript
type ExistingWikiReuseMode = 'reuse' | 'reinitialize' | 'new';

type WikiContract = {
  wikiRoot: string;
  domain?: string;
  sourceTypes?: string[];
  indexCategories?: string[];
};

type ExistingWikiValidationResult = {
  ok: boolean;
  error?: string;
};

type InitQuestionPlan = {
  mode: ExistingWikiReuseMode;
  skippedFields: string[];
  requiredQuestions: string[];
};

type ReuseSummary = {
  mode: 'reuse';
  configDir: string;
  wikiRoot: string;
  domain?: string;
  sourceTypes?: string[];
  indexCategories?: string[];
  nextSuggestedSkills: string[];
};

interface WikiContractLoader {
  load(configDir: string): Promise<WikiContract>;
}

interface ExistingWikiValidator {
  validate(configDir: string, contract: WikiContract): Promise<ExistingWikiValidationResult>;
}

interface InitQuestionPlanner {
  plan(mode: ExistingWikiReuseMode, contract?: WikiContract): InitQuestionPlan;
}

interface ReuseSummaryBuilder {
  build(configDir: string, contract: WikiContract): ReuseSummary;
}
```

### Testability Guidelines

1. **Accept dependencies, don't create them**
   ```typescript
   // Testable
   async function resolveExistingWiki(configDir, loader, validator) {}

   // Hard to test
   async function resolveExistingWiki(configDir) {
     const loader = new FileBackedWikiContractLoader();
     const validator = new DefaultExistingWikiValidator();
   }
   ```

2. **Return results, don't produce side effects**
   ```typescript
   // Testable
   function planInitQuestions(mode, contract): InitQuestionPlan {}

   // Hard to test
   function askQuestionsImmediately(mode, contract): void {}
   ```

3. **Small surface area**
   - 将“已有配置识别”收敛为一次 `load + validate + plan + summarize` 流程
   - 把“提问规划”与“实际提问”分离，便于单测和 smoke test 各自验证
   - 把“复用摘要”作为结构化结果返回，避免在多个分支里拼接提示文本

## Data Flow

### 1. 显式 `config-dir` 的已有配置复用路径

```text
User runs wiki-init
  │
  ├─ provides explicit config-dir
  ▼
Detect explicit config-dir
  │
  ▼
Read <config-dir>/WIKI.md
  │
  ├─ missing file ───────────────▶ fall back to normal new-init questioning
  │
  ▼
Parse wiki contract
  │
  ▼
Validate existing wiki
  │
  ├─ invalid contract/layout ───▶ fail fast with non-destructive error
  │
  ▼
Plan init questions in reuse mode
  │
  └─ skip wiki_root / domain / source_types / index_categories
  ▼
Build reuse summary
  │
  ▼
Return "connected to existing wiki"
  └─ suggest wiki-query / wiki-ingest / wiki-lint / wiki-update with same config-dir
```

可观察结果：
- 已有 `WIKI.md` 被读取而不是重写
- 已知字段不再重复询问
- 输出明确提示现有 wiki 已连接

### 2. 损坏配置的失败路径

```text
Read WIKI.md
  │
  ▼
Validate contract and layout
  │
  ├─ wiki_root missing
  ├─ wiki_root not absolute
  └─ required layout missing
        │
        ▼
Return explicit error
  ├─ do not rewrite WIKI.md
  ├─ do not scaffold replacement layout
  └─ tell user to fix config or explicitly choose reinitialize
```

可观察结果：
- 返回清晰错误文本
- 文件系统保持不变
- 默认路径不进入覆盖式重建

### 3. 明确 reinitialize 的覆盖路径

```text
Existing config detected
  │
  ▼
User explicitly chooses reinitialize
  │
  ▼
Run normal wiki-init scaffold flow
  ├─ ask required inputs
  ├─ rewrite WIKI.md
  └─ create/update wiki layout
```

可观察结果：
- 只有显式确认时才发生写操作
- 默认 continue/reuse 路径保持非破坏性

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 文件系统 | 使用临时目录构造 `config-dir`、`wiki_root` 以及不同版本的 `WIKI.md` 夹具 |
| 用户交互 | 使用脚本化 prompt 输入或现有 real-agent smoke 测试提示词，观察是否跳过已知问题 |
| 运行时契约解析 | 使用固定 `WIKI.md` 文本夹具进行 golden-style 断言 |
| wiki 布局存在性 | 在临时目录中分别构造完整布局和缺失 `wiki/index.md` / `wiki/log.md` 的损坏布局 |

## Implementation Notes

- 仅当用户“显式提供 `config-dir`”时启用本变更定义的快速路径；不改变现有“从 current working directory 向上搜索 `WIKI.md`”的发现规则。
- `WIKI.md` 是否“有效”至少应包含：
  - 可解析的 `wiki_root`
  - `wiki_root` 为绝对路径
  - `wiki_root` 下存在最小必需布局：`wiki/index.md`、`wiki/log.md`、`wiki/pages/`
- `domain`、`source_types`、`index_categories` 建议作为“可复用字段”参与摘要与提问裁剪；若缺少非关键字段，可在实现阶段决定是部分提问还是降级提示，但不得要求重输已经存在的信息。
- 成功复用后，最终提示应显式包含同一 `config-dir` 的后续用法，至少包含 `wiki-query`。
- 该设计不引入新的共享配置文件，也不改变 `WIKI.md` 作为唯一中立运行时契约的地位。
