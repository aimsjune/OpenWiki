# Proposal: add-openwiki-cli

## Why

当前 llm-wiki 是一个纯 Skill 驱动的 wiki 生态系统——所有操作（初始化、配置管理、页面 CRUD、健康检查、云同步）均由 AI Agent 通过加载 SKILL.md 上下文来执行文件操作。这导致以下问题：

1. **无统一执行入口**：每个 Skill 各自实现配置发现、页面读写、日志追加，逻辑重复且不一致
2. **无结构化输出**：Skill 直接操作文件，Agent 无法获取机器可解析的结构化状态（JSON）
3. **人类使用门槛高**：没有 CLI，人类用户无法直接操作 wiki（如 `openwiki status` 查看状态）
4. **配置格式混乱**：WIKI.md 使用 Markdown + YAML frontmatter 混合格式，不适合程序化读写
5. **Agent 效率低**：每次操作需加载完整 Skill 上下文（数百行 SKILL.md），而非轻量 CLI 调用

## What Changes

### Part A: 配置格式迁移

- **WIKI.md → openwiki.toml**：将 Markdown + YAML frontmatter 格式替换为纯 TOML 格式
- **配置路径变更**：
  - 全局默认配置：`~/.openwiki/openwiki.toml`（原 `~/.wiki-config/WIKI.md`）
  - 实例配置：`<wiki_root>/openwiki.toml`（从 CWD 向上逐层搜索）
- **更新所有受影响文件**：6 个 Skill 的 SKILL.md、wiki-init 模板、validate_wiki.py、所有测试 fixtures

### Part B: openwiki CLI 实现

使用 Go 语言实现 `openwiki` CLI，提供 6 组命令：

| 命令组 | 用途 | 面向 |
|--------|------|------|
| `init` | 初始化 wiki 实例（创建目录结构 + openwiki.toml） | Human + Agent |
| `config` | 配置读写验证（show/get/set/path/validate） | Human + Agent |
| `status` | wiki 健康状态快照（含配置来源展示） | Human + Agent |
| `page` | 页面 CRUD（list/get/create/update/delete） | Agent（通过 Skill 委托） |
| `log` | 操作日志（show/append） | Agent（通过 Skill 委托） |
| `sync` | 云同步 | Human + Agent |

### Part C: Skill → CLI 委托

将 6 个 Skill 中的文件操作逐步委托给 CLI：

- **wiki-ingest**：页面创建、回链审计、index 更新委托给 `page create` / `page list` / `page get`
- **wiki-lint**：页面清单构建、内容读取委托给 `page list` / `page get`（支持批量）
- **wiki-query**：索引扫描、页面读取委托给 `page list` / `page get`
- **wiki-update**：页面读写、日志追加委托给 `page get` / `page update` / `log append`
- **wiki-distill**：页面创建委托给 `page create`
- **wiki-init**：初始化委托给 `openwiki init`

## Acceptance Criteria (Testable)

| # | Criterion | Test Verification |
|---|-----------|-------------------|
| 1 | `openwiki init ./test-wiki --non-interactive --json` 创建完整目录结构并返回 JSON | E2E 测试：执行 init 后检查目录存在 + JSON 输出含 `success: true` |
| 2 | `openwiki config show --json` 返回完整 TOML 配置的 JSON 表示 | 单元测试：给定已知 openwiki.toml，验证 JSON 输出字段完整 |
| 3 | `openwiki config get wiki_root --json` 返回单个配置项 | 单元测试：验证 `data.value` 等于预期值 |
| 4 | `openwiki config set primary_language en --json` 修改配置并返回旧/新值 | 单元测试：修改后再次 get 验证新值生效 |
| 5 | `openwiki config validate --json` 对无效配置返回错误码和详情 | 单元测试：给定无效 TOML，验证 `success: false` + `error.code` |
| 6 | `openwiki config path --json` 输出当前使用的配置路径和来源 | 单元测试：验证 `data.source` 为 `global`/`local`/`explicit` |
| 7 | `openwiki status --json` 返回页面统计、健康状态、配置来源 | 集成测试：给定已知 wiki，验证 `data.pages.total` 和 `data.config.source` |
| 8 | `openwiki status --verbose` 显示每页详情（含孤立页面和过期页面） | 集成测试：验证输出含具体 slug 名称 |
| 9 | `openwiki page list --json` 返回所有页面元信息（slug/title/tags/scope/updated） | 集成测试：给定已知 wiki，验证返回的页面数量正确 |
| 10 | `openwiki page list --scope repo --json` 按 scope_code 过滤 | 集成测试：验证返回的页面 scope_code 全部为指定值 |
| 11 | `openwiki page get <slug> --json` 返回页面完整内容（frontmatter + body + cross_references） | 集成测试：验证 `data.frontmatter.title` 和 `data.cross_references` 非空 |
| 12 | `openwiki page get <slug1> <slug2> --json` 批量返回多个页面 | 集成测试：验证 `data.pages` 数组长度为 2 |
| 13 | `openwiki page create <slug> --file /tmp/content.md --json` 创建页面并自动更新 index.md + log.md | E2E 测试：创建后检查 index.md 含新条目 + log.md 含 create 记录 |
| 14 | `openwiki page update <slug> --file /tmp/updated.md --json` 更新页面并自动更新 index.md + log.md | E2E 测试：更新后检查页面内容变更 + index.md 日期更新 |
| 15 | `openwiki page delete <slug> --force --json` 删除页面并自动更新 index.md + log.md | E2E 测试：删除后检查 index.md 无该条目 + log.md 含 delete 记录 |
| 16 | `openwiki log show --limit 5 --json` 返回最近 5 条日志 | 集成测试：验证返回数组长度 ≤ 5 |
| 17 | `openwiki log append "ingest | test-page" --json` 追加日志条目 | 集成测试：追加后 log show 验证新条目存在 |
| 18 | `openwiki sync --dry-run --json` 预览云同步变更 | 集成测试：验证 JSON 输出含 `data.changes` 数组 |
| 19 | 配置发现优先级链正确：`--config` > `OPENWIKI_CONFIG` > `~/.openwiki/openwiki.toml` > CWD 向上搜索 | 单元测试：4 种场景分别验证 |
| 20 | 所有命令在 `--json` 模式下输出含 `success`/`data`/`error`/`timestamp` 字段 | 单元测试：验证 JSON schema |
| 21 | 错误输出含唯一错误码 + 三要素（发生什么/为什么/如何解决） | 单元测试：验证 error 对象含 `code`/`message`/`details` |
| 22 | 非交互模式下不等待用户输入 | E2E 测试：`init --non-interactive` 不阻塞 |
| 23 | wiki-lint 通过 `page list` + `page get` 获取页面数据（不再直接读文件） | 验证 SKILL.md 步骤含 `openwiki page` 调用 |
| 24 | wiki-ingest 通过 `page create` 创建页面（不再直接写文件） | 验证 SKILL.md 步骤含 `openwiki page create` 调用 |
| 25 | 构建时通过 ldflags 注入版本信息，`--version` 输出版本号 | 单元测试：验证 `--version` 输出非空 |

## Impact

### 受影响文件

**新增（Go 项目）：**
- `cmd/openwiki/main.go`
- `internal/cli/`（root.go, init.go, config.go, status.go, page.go, log.go, sync.go）
- `internal/config/`（config.go, discovery.go, validate.go）
- `internal/wiki/`（init.go, page.go, index.go, log.go）
- `internal/output/`（json.go, text.go）
- `tests/e2e/harness/`（harness.go, fixtures.go）
- `tests/fixtures/`（healthy-wiki/, empty-wiki/）
- `Makefile`, `go.mod`, `go.sum`

**修改（配置迁移）：**
- `skill/wiki-init/templates/` — WIKI.md 模板 → openwiki.toml 模板
- `skill/wiki-init/SKILL.md` — 配置路径更新
- `skill/wiki-ingest/SKILL.md` — 配置路径 + CLI 委托
- `skill/wiki-lint/SKILL.md` — 配置路径 + CLI 委托
- `skill/wiki-query/SKILL.md` — 配置路径 + CLI 委托
- `skill/wiki-update/SKILL.md` — 配置路径 + CLI 委托
- `skill/wiki-distill/SKILL.md` — 配置路径 + CLI 委托
- `skill/wiki-lint/scripts/validate_wiki.py` — 检查对象变更
- `tests/` — 所有 fixture 的 WIKI.md → openwiki.toml

### 外部依赖

- Go 标准库（`flag`, `os`, `encoding/json`, `testing` 等）
- `github.com/BurntSushi/toml`（TOML 解析，唯一外部依赖）

## Non-Goals

- **不实现 ingest/lint/query/update/distill 的 CLI 命令**：这些操作需要 AI 语义理解，保留在 Skill 层
- **不向后兼容旧的 WIKI.md 格式**：不考虑自动迁移
- **不实现交互式 TUI**：CLI 保持简单，非交互模式优先
- **不实现远程 API 服务**：CLI 仅本地文件操作

## Test Considerations

- **测试框架**：Go 标准库 `testing` + `go test`
- **测试金字塔**：
  - 单元测试（70%）：config 解析、discovery 优先级、output 格式化、page/index 逻辑
  - Stub E2E（20%）：使用测试 fixtures 的集成测试，通过 Harness 构建并执行二进制
  - 真实 E2E（10%）：完整 init → page create → status → lint 流程
- **Mock 策略**：文件系统操作用 `t.TempDir()` 隔离，云同步用 stub
- **关键接口**：`internal/config/discovery.go` 的 `Discover()` 函数，`internal/wiki/page.go` 的 CRUD 函数
