# Design: add-cloud-sync-to-wiki-ingest

## Overview

本变更为 `wiki-ingest` 技能增加云端同步步骤，通过 `pcloud sync` 将本地 `wiki_root` 安全同步到远端对象存储。变更主要涉及技能文档（SKILL.md）、运行时契约（WIKI.md）和初始化模板的修改，不涉及新的可执行代码。

## Architecture

### 组件关系

```
┌──────────────────────────────────────────────────────────────┐
│                      WIKI.md (运行时契约)                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ wiki_root: /path/to/wiki                                │ │
│  │ remote_sync_path: "wiki"   ← 新增                      │ │
│  │ auto_sync: false            ← 新增                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │ 解析
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ wiki-init  │  │ wiki-ingest│  │ 其他       │
   │ (模板写入) │  │ (读取+同步)│  │ workflow   │
   └─────┬──────┘  └─────┬──────┘  └────────────┘
         │                │
         │  写入默认值     │  步骤 12: 执行 pcloud sync
         ▼                ▼
   ┌────────────┐  ┌────────────────────────────┐
   │ templates/ │  │        pcloud CLI           │
   │ WIKI.md    │  │  sync <root> <path>         │
   └────────────┘  │  --dry-run / --checksum     │
                   └────────────┬───────────────┘
                                │
                                ▼
                   ┌────────────────────────────┐
                   │   云端对象存储 (TOS/S3)     │
                   │   <root-prefix>/<path>/    │
                   └────────────────────────────┘
```

### 组件职责

| 组件 | 职责 | 公共接口 |
|------|------|----------|
| `WIKI.md` | 存储 `remote_sync_path` 和 `auto_sync` 字段，作为运行时契约的一部分 | 文件读取（frontmatter 解析） |
| `skill/wiki-init/templates/WIKI.md` | 新 wiki 初始化时写入 sync 字段默认值 | 文件内容（模板输出） |
| `skill/wiki-ingest/SKILL.md` | 声明 sync 字段解析，定义步骤 12 的同步流程和交互逻辑 | SKILL.md 文档（AI 执行指令） |
| `skill/wiki-init/SKILL.md` | 复用已有配置时对 sync 字段应用提问裁剪 | SKILL.md 文档（AI 执行指令） |
| `pcloud CLI` | 执行实际的本地↔云端文件同步 | `pcloud sync <local> <remote> [--dry-run] [--json]` |

## Interface Design for Testability

本变更的"接口"是技能文档（SKILL.md）和配置文件（WIKI.md）的静态内容。测试通过读取这些文件并验证关键内容来确保行为正确。

### 关键测试接口

```
测试层                        被测接口
═══════════════════════════════════════════════════════
静态分析测试
├── test_wiki_md_template     skill/wiki-init/templates/WIKI.md
├── test_wiki_md_runtime      WIKI.md
├── test_wiki_ingest_skill    skill/wiki-ingest/SKILL.md
│   ├── pre-condition 字段
│   ├── 步骤 12 存在
│   ├── dry-run 逻辑
│   ├── auto_sync 逻辑
│   ├── 非阻塞语义
│   └── log.md 追加格式
└── test_wiki_init_skill      skill/wiki-init/SKILL.md
    └── 提问裁剪覆盖 sync 字段

E2E Smoke 测试
└── test_wiki_init_reuse      wiki-init 复用路径
    └── sync 字段不重复询问
```

### 可测试性设计原则

1. **依赖外部化**：`pcloud` 作为外部 CLI 调用，不在技能内部创建。测试时通过 stub provider（`pcloud config init --provider stub`）模拟。
2. **结果可观测**：sync 结果通过 `wiki/log.md` 追加记录和终端输出来验证，不依赖云端状态。
3. **小接口面**：仅在 `wiki-ingest` 一个 workflow 中增加 sync，其他 workflow 不受影响。

## Data Flow

```
wiki-init (新初始化)
═══════════════════
用户输入 → templates/WIKI.md (含 sync 默认值) → WIKI.md 写入
                                                      │
wiki-init (复用已有)                                  │
═══════════════════                                   │
WIKI.md 读取 → 解析现有字段 → 提问裁剪(sync 已有则跳过) → 摘要输出


wiki-ingest (摄入流程)
═════════════════════
步骤 1-11 (现有流程不变)
       │
       ▼
步骤 12 Cloud Sync:
       │
       ├─ WIKI.md.remote_sync_path == "" → 跳过
       │
       ├─ pcloud 不可用 → 警告 → 跳过
       │
       ├─ auto_sync == true
       │   └─ pcloud sync <wiki_root> <remote_sync_path> → log.md
       │
       └─ auto_sync == false (默认)
           ├─ pcloud sync --dry-run → 展示变更摘要
           ├─ 询问用户确认
           ├─ [Y] pcloud sync → log.md
           └─ [n] 跳过 → 报告 "sync skipped"
```

## pcloud sync 语义

`pcloud sync` 是**安全并集同步**（Safe Union），关键属性：

| 属性 | 说明 |
|------|------|
| 非破坏性 | 不删除任何文件，只做新增和更新 |
| 双向 | 本地新文件上传，远端新文件下载 |
| 幂等 | 多次执行结果一致 |
| 可预览 | `--dry-run` 展示同步计划 |
| 可校验 | `--checksum` 基于内容哈希比较 |
| 结构化输出 | `--json` 输出机器可解析的 JSON |

这些属性天然符合 `wiki-ingest` 的 Safe-union 原则。

## 向后兼容

- 旧 `WIKI.md`（不含 `remote_sync_path`）：视为空字符串，静默跳过同步
- `wiki-init` 复用旧配置：补问 sync 字段，默认值 `"wiki"` / `false`
- `wiki-ingest` 在 `remote_sync_path` 为空时：现有流程完全不变

## Implementation Notes

1. **变更类型**：纯文档级变更，不涉及可执行代码
2. **修改顺序**：
   - 先修改 `skill/wiki-init/templates/WIKI.md`（模板）
   - 同步修改运行时 `WIKI.md`（添加新字段）
   - 修改 `skill/wiki-ingest/SKILL.md`（新增步骤 12 和 pre-condition 字段）
   - 修改 `skill/wiki-init/SKILL.md`（提问裁剪覆盖 sync 字段）
   - 更新主 spec `openspec/specs/standard-wiki-runtime/spec.md`（合并 delta）
3. **测试顺序**：先写静态测试（验证文档内容），再写 E2E smoke 测试（验证交互行为）
4. **pcloud 配置**：`pcloud` 的凭证配置（`~/.config/pcloud/config.toml`）由用户自行管理，不在本变更范围内
