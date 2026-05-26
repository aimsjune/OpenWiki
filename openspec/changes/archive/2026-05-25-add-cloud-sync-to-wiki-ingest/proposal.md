# Proposal: add-cloud-sync-to-wiki-ingest

## Why

`wiki-ingest` 每次摄入内容后都会修改本地 wiki 文件（`wiki/pages/`、`wiki/index.md`、`wiki/log.md`），但这些变更仅存在于本地。用户需要通过 `pcloud` CLI 手动执行 `pcloud sync` 才能将本地 wiki 同步到云端对象存储。这导致本地与云端容易产生不一致，且手动同步步骤容易被遗忘。

本变更为 `wiki-ingest` 增加自动云端同步能力，在每次摄入完成后自动（或经用户确认后）将整个 `wiki_root` 安全同步到云端，确保本地与云端始终一致。

## What Changes

1. **WIKI.md 契约扩展**：新增 `remote_sync_path` 和 `auto_sync` 字段
   - `remote_sync_path`：pcloud 远端逻辑路径，默认值 `"wiki"`，设为空则跳过同步
   - `auto_sync`：`true` 时跳过 dry-run 确认直接同步，默认 `false`

2. **wiki-ingest 流程增强**：在现有 11 步流程末尾新增第 12 步 "Cloud Sync"
   - 读取 `WIKI.md` 中的 `remote_sync_path` 和 `auto_sync`
   - `remote_sync_path` 为空时静默跳过
   - `pcloud` 未安装或未配置时发出警告但不阻塞
   - `auto_sync = false` 时先 dry-run 预览变更，询问用户确认后执行
   - `auto_sync = true` 时直接执行同步
   - 同步完成后追加记录到 `wiki/log.md`

3. **wiki-init 模板更新**：初始化模板中包含新的同步字段

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `wiki-init` 模板生成的 `WIKI.md` 包含 `remote_sync_path: wiki` 和 `auto_sync: false` | 运行 `wiki-init` 初始化新 wiki，验证生成的 `WIKI.md` frontmatter 包含这两个字段且默认值正确 |
| 2 | `wiki-ingest` 读取 `WIKI.md` 中的 `remote_sync_path` 和 `auto_sync` | 构造 fixture `WIKI.md` 含 sync 字段，验证 `wiki-ingest` SKILL.md 的 pre-condition 节声明了这些字段的读取 |
| 3 | `remote_sync_path` 为空时跳过同步，不影响 ingest 主流程 | 设置 `remote_sync_path: ""`，执行 ingest，验证无 sync 调用且 ingest 正常完成 |
| 4 | `pcloud` 未安装时发出警告但不阻塞 | 在无 `pcloud` 的环境中执行 ingest（`remote_sync_path` 非空），验证输出包含 warning 且 ingest 正常完成 |
| 5 | `auto_sync = false` 时先 dry-run 预览再询问确认 | 验证 `wiki-ingest` SKILL.md 流程中描述了 dry-run → 展示变更 → 询问确认 → 执行的交互序列 |
| 6 | `auto_sync = true` 时跳过确认直接执行同步 | 设置 `auto_sync: true`，验证 `wiki-ingest` SKILL.md 流程中描述了跳过 dry-run 确认直接执行 `pcloud sync` |
| 7 | 同步完成后追加 `sync` 记录到 `wiki/log.md` | 验证 `wiki-ingest` SKILL.md 中描述了 log 追加格式（操作类型 `sync`，上传/下载计数） |
| 8 | `WIKI.md` 中的 `remote_sync_path` 和 `auto_sync` 字段在 `wiki-init` 复用路径中不被重复询问 | 当 `wiki-init` 复用已有配置时，不询问 sync 相关字段（如果已存在），或询问但接受默认值跳过（提问裁剪） |

## Impact

- **受影响文件**：
  - `skill/wiki-ingest/SKILL.md` — 新增步骤 12 和 pre-condition 字段声明
  - `skill/wiki-init/templates/WIKI.md` — 模板新增 `remote_sync_path` 和 `auto_sync`
  - `WIKI.md` — 同步增加新字段
  - `openspec/specs/standard-wiki-runtime/spec.md` — 新增 sync 相关 REQ

- **受影响技能**：`wiki-ingest`、`wiki-init`
- **外部依赖**：`pcloud` CLI（可选，不存在时不阻塞）
- **不涉及**：`wiki-query`、`wiki-lint`、`wiki-update` 的流程变更

## Non-Goals

- 不在 `wiki-update` 或 `wiki-lint` 中自动触发同步
- 不创建独立的 `wiki-sync` 技能
- 不处理 `pcloud` 的安装或配置（由用户自行完成）
- 不支持增量同步或选择性目录同步（始终同步整个 `wiki_root`）
- 不处理并发同步冲突（`pcloud sync` 本身是安全并集）

## Test Considerations

- 测试框架：Python（`pytest`），与现有测试保持一致
- 关键测试接口：
  - `wiki-ingest` SKILL.md 静态分析（验证步骤 12 存在、pre-condition 声明新字段）
  - `wiki-init` 模板静态分析（验证 `WIKI.md` 模板包含 sync 字段）
  - `WIKI.md` 静态分析（验证 frontmatter 字段格式）
- 外部依赖 mock：`pcloud` CLI 不需要 mock（静态测试即可），若后续增加 E2E 测试则需要 `pcloud config init --provider stub`
