# Design: optimize-skill-structure

## Overview

本变更对 llm-wiki 项目的 6 个技能进行结构优化，使其符合 [[agent-skills-specification]] 和 [[progressive-disclosure]] 的最佳实践。核心思路是「内容分层」：将 SKILL.md 正文保持简洁（Level 2 指令层），将详细参考资料移至 `references/`（Level 3 资源层），并增加 `tests/` 和 `scripts/` 目录。

## Architecture

### 变更前后对比

```
变更前:                              变更后:
skill/wiki-lint/                     skill/wiki-lint/
├── SKILL.md (~80 行，含规则定义)      ├── SKILL.md (~60 行，仅流程)
│                                     ├── references/
│                                     │   ├── rules-catalog.md
│                                     │   └── exemption-checklist.md
│                                     ├── tests/
│                                     │   ├── test_cases.md
│                                     │   └── fixtures/
│                                     │       ├── healthy-wiki/
│                                     │       ├── broken-links/
│                                     │       └── missing-scope/
│                                     └── scripts/
│                                         └── validate_wiki.py

skill/wiki-ingest/                   skill/wiki-ingest/
├── SKILL.md (~120 行，含模板规范)     ├── SKILL.md (~80 行，仅流程)
│                                     ├── references/
│                                     │   ├── page-template.md
│                                     │   └── slug-rules.md
│                                     └── tests/
│                                         └── fixtures/
│                                             ├── url-source/
│                                             └── file-source/

skill/wiki-distill/                  skill/wiki-distill/
├── SKILL.md (~150 行)               ├── SKILL.md (~150 行，+ composes)
│                                     └── tests/
│                                         └── fixtures/
│                                             ├── go-project/
│                                             └── python-project/

skill/wiki-update/                   skill/wiki-update/
├── SKILL.md                         ├── SKILL.md (+ composes)
│                                     └── (硬链接自动同步)
```

### Components

| Component | Responsibility | Public Interface |
|-----------|---------------|------------------|
| SKILL.md 正文 | 核心流程指令（Level 2） | Markdown 正文，Agent 直接读取 |
| references/ | 详细规则/模板/清单（Level 3） | Markdown 文件，Agent 按需加载 |
| tests/fixtures/ | 测试用迷你 wiki 实例 | 静态目录结构，测试脚本读取 |
| tests/test_cases.md | 测试用例描述 | Markdown 文件，Agent 可执行 |
| scripts/validate_wiki.py | wiki 结构验证 | CLI：`python validate_wiki.py <wiki_root>`，输出 JSON |

## Interface Design for Testability

### 测试接口

所有测试通过以下公共接口进行，不依赖 Agent 运行时：

| 接口 | 类型 | 用途 |
|------|------|------|
| 文件存在性 | `os.path.exists()` | 检查 references/、tests/、scripts/ 目录结构 |
| YAML 解析 | `yaml.safe_load()` | 检查 frontmatter 的 composes 字段 |
| 行数统计 | `len(body.split("\n"))` | 检查 SKILL.md 正文行数 |
| 文本匹配 | `"pattern" in content` | 检查关键指令是否存在 |
| 脚本执行 | `subprocess.run()` | 检查 validate_wiki.py 的 JSON 输出和退出码 |
| 硬链接检查 | `os.stat().st_ino` | 检查 wiki-update 的硬链接一致性 |

### Testability Guidelines

1. **Accept dependencies, don't create them**
   - `validate_wiki.py` 接受 `wiki_root` 参数，不假设当前目录
   - fixtures 是自包含的，不依赖外部文件或网络

2. **Return results, don't produce side effects**
   - `validate_wiki.py` 输出 JSON 到 stdout，不修改文件
   - 测试仅检查文件系统状态，不产生副作用

3. **Small surface area**
   - 每个 spec 对应一个测试文件，职责单一
   - fixtures 最小化：仅包含触发特定检查所需的最少文件

## Data Flow

### 正文拆分流程

```
SKILL.md 正文 (当前)
     │
     ├── 识别可提取内容:
     │   ├── lint 规则定义 → references/rules-catalog.md
     │   ├── 豁免清单 → references/exemption-checklist.md
     │   ├── 页面模板规范 → references/page-template.md
     │   └── slug 规则 → references/slug-rules.md
     │
     ├── 替换为引用:
     │   "详见 references/rules-catalog.md"
     │
     └── 验证:
          ├── 正文行数 ≤ 阈值
          ├── references/ 文件存在
          └── 正文包含 references/ 引用
```

### composes 声明流程

```
SKILL.md frontmatter
     │
     ├── wiki-distill:
     │   composes: [wiki-ingest, wiki-lint]
     │   (distill 委托 ingest 写入页面，委托 lint 验证)
     │
     └── wiki-update:
         composes: [wiki-ingest, wiki-lint, wiki-init]
         (update 委托 ingest 写入，委托 lint 检查，委托 init 模板)
```

### 自我纠错流程

```
wiki-ingest 步骤 6: 写入页面
     │
     ▼
步骤 6.1: 验证写入
     │
     ├── 重读刚写入的文件
     ├── 检查 frontmatter 必填字段
     ├── 检查 [[交叉引用]] 可达性
     │
     ├── 全部通过 → 继续步骤 7
     └── 验证失败 → 报告错误 + 建议修复
```

### validate_wiki.py 数据流

```
python validate_wiki.py <wiki_root>
     │
     ├── 读取 WIKI.md → 检查必填字段
     ├── 读取 wiki/index.md → 检查表格格式
     ├── 扫描 wiki/pages/*.md → 提取 [[交叉引用]]
     ├── 验证交叉引用 → 检查目标文件存在
     │
     └── 输出 JSON:
         {
           "wiki_root": "...",
           "checks": [
             {"name": "WIKI.md 必填字段", "status": "pass", "message": "..."},
             {"name": "index.md 表格格式", "status": "fail", "message": "..."},
             {"name": "交叉引用可达性", "status": "pass", "message": "..."}
           ],
           "summary": {"pass": 2, "fail": 1}
         }
```

## Test Mocking Strategy

| External Dependency | How to Mock |
|--------------------|-------------|
| 文件系统 | fixtures 目录提供静态 wiki 实例 |
| WIKI.md 配置 | 每个 fixture 包含自指向的 WIKI.md |
| wiki/pages/ | fixtures 中包含预制的页面文件 |
| 硬链接 | 使用 `os.stat().st_ino` 检查 inode 一致性 |

## Implementation Notes

### 硬链接同步策略

wiki-update 通过硬链接共享 wiki-init、wiki-ingest、wiki-lint 的文件。新增的 `references/`、`tests/`、`scripts/` 目录需要在创建后手动建立硬链接，或依赖现有的硬链接目录结构自动同步。

```
skill/wiki-update/
├── wiki-init/    → 硬链接到 skill/wiki-init/
├── wiki-ingest/  → 硬链接到 skill/wiki-ingest/
└── wiki-lint/    → 硬链接到 skill/wiki-lint/
```

新增文件后，需要确认硬链接是否自动传播。如果不自动传播，需要在 wiki-update 下创建对应的硬链接。

### 正文行数阈值

| 技能 | 当前行数（估） | 目标行数 | 提取内容 |
|------|-------------|---------|---------|
| wiki-lint | ~80 | ≤80 | 规则定义、豁免清单 |
| wiki-ingest | ~120 | ≤100 | 页面模板、slug 规则 |
| wiki-distill | ~150 | ~150 | 无需拆分（三段式流程是核心） |

### validate_wiki.py 实现要点

- 使用 `argparse` 解析命令行参数
- 使用 `pathlib` 处理路径
- 使用 `json.dumps()` 输出结果
- 所有检查通过 → `sys.exit(0)`
- 任一检查失败 → `sys.exit(1)`
- 不使用 `yaml` 库（避免外部依赖），手动解析 WIKI.md 的简单 YAML frontmatter
