# Tasks: add-openwiki-cli

## TDD Workflow: RED → GREEN → REFACTOR

**CRITICAL: This workflow uses VERTICAL SLICES (tracer bullets)**

```
WRONG (horizontal slicing - DO NOT USE):
  RED:   test1, test2, test3
  GREEN: impl1, impl2, impl3

RIGHT (vertical slices - USE THIS):
  RED→GREEN→REFACTOR: test1→impl1
  RED→GREEN→REFACTOR: test2→impl2
  RED→GREEN→REFACTOR: test3→impl3
```

**Rules:**
1. Write ONE failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed, ensure tests pass
4. Only then move to next behavior

---

## Behavior 1: Go 项目骨架 + config TOML 解析

### Phase 1: RED - Write Failing Test

- [x] **1.1** 创建 Go 项目骨架：`go mod init`，目录结构 `cmd/openwiki/`、`internal/config/`、`internal/wiki/`、`internal/cli/`、`internal/output/`
- [x] **1.2** 在 `internal/config/config_test.go` 编写 TOML 解析测试
  - 测试：解析有效 openwiki.toml，验证所有字段正确映射
  - 测试：解析缺少必填字段的 TOML 返回错误
  - 测试：解析语法错误的 TOML 返回解析错误
- [x] **1.3** 运行 `go test ./internal/config/` 确认测试 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/config/config.go` 定义 `Config` 结构体和 `Load(path)` 函数
- [x] **2.2** 添加 `github.com/BurntSushi/toml` 依赖
- [x] **2.3** 运行 `go test ./internal/config/` 确认测试 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 TOML tag 映射，确保字段名一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 2: 配置发现优先级链

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/config/discovery_test.go` 编写配置发现测试
  - 测试：`--config` 显式指定 → source="explicit"
  - 测试：`OPENWIKI_CONFIG` 环境变量 → source="env"
  - 测试：`~/.openwiki/openwiki.toml` 存在 → source="global"
  - 测试：CWD 向上搜索找到 openwiki.toml → source="local"
  - 测试：所有来源都找不到 → 返回 ErrConfigNotFound
- [x] **1.2** 运行 `go test ./internal/config/ -run TestDiscover` 确认测试 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/config/discovery.go` 实现 `Discoverer` 接口和 `DefaultDiscoverer`
- [x] **2.2** 实现 4 级优先级链逻辑
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 `expandPath` 处理 `~` 展开
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 3: 配置校验

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/config/validate_test.go` 编写校验测试
  - 测试：缺少 wiki_root → CONFIG_MISSING_FIELD
  - 测试：primary_language 无效值 → CONFIG_INVALID_FIELD
  - 测试：wiki_root 路径不存在 → CONFIG_INVALID_PATH
  - 测试：有效配置 → 无错误
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/config/validate.go` 实现 `Validate(cfg)` 函数
- [x] **2.2** 定义允许的语言值列表 `["zh", "en"]`
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取错误消息模板
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 4: 配置读写（set/get）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/config/config_test.go` 编写配置读写测试
  - 测试：`Set(path, "wiki.primary_language", "en")` 修改嵌套字段
  - 测试：`Set(path, "wiki_root", "/new/path")` 修改顶层字段
  - 测试：`Set` 不存在的字段返回错误
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/config/config.go` 实现 `Set(path, key, value)` 函数
- [x] **2.2** 支持点号分隔的嵌套键路径（如 `wiki.primary_language`）
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保 Set 后文件格式保持整洁（保留注释和空行）
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 5: wiki FS 抽象 + Init

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/fs_test.go` 编写 MemFS 测试
  - 测试：ReadFile/WriteFile/MkdirAll/Remove/Stat/ReadDir/Glob
- [x] **1.2** 在 `internal/wiki/init_test.go` 编写 Init 测试
  - 测试：Init 创建完整目录结构（wiki/pages/, raw/, concepts/）
  - 测试：Init 创建 openwiki.toml 含正确 wiki_root
  - 测试：Init 创建 wiki/index.md 和 wiki/log.md
  - 测试：目标已存在时返回 WIKI_ALREADY_EXISTS
  - 测试：--force 覆盖已有实例
- [x] **1.3** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/fs.go` 定义 `FS` 接口、`OsFS`、`MemFS`
- [x] **2.2** 在 `internal/wiki/init.go` 实现 `Init(fs, root, cfg)` 函数
- [x] **2.3** 创建 wiki-init 模板（index.md, log.md）
- [x] **2.4** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取模板常量为独立文件或变量
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 6: wiki page CRUD（list/get/create）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 编写页面操作测试
  - 测试：`ListPages` 解析 index.md 返回页面元信息列表
  - 测试：`GetPage` 返回单个页面（frontmatter + body + cross_references）
  - 测试：`GetPage` 批量返回多个页面
  - 测试：`GetPage` 不存在的 slug 返回 PAGE_NOT_FOUND
  - 测试：`CreatePage` 创建页面文件 + 更新 index.md + 追加 log.md
  - 测试：`CreatePage` 已存在的 slug 返回 PAGE_ALREADY_EXISTS
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 实现 `ListPages`, `GetPage`, `CreatePage`
- [x] **2.2** 在 `internal/wiki/index.go` 实现 index.md 解析与更新
- [x] **2.3** 在 `internal/wiki/log.go` 实现 log.md 追加
- [x] **2.4** 实现 frontmatter 解析（YAML）和 cross_references 提取（`[[ref]]` 正则）
- [x] **2.5** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 frontmatter 解析为独立函数
- [x] **3.2** 提取 index.md 表格解析为独立函数
- [x] **3.3** 运行全部测试确认通过

---

## Behavior 7: wiki page CRUD（update/delete）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/page_test.go` 编写更新和删除测试
  - 测试：`UpdatePage` 更新页面内容 + 更新 index.md 日期 + 追加 log.md
  - 测试：`UpdatePage` 不存在的 slug 返回 PAGE_NOT_FOUND
  - 测试：`DeletePage` 删除页面文件 + 从 index.md 移除 + 追加 log.md
  - 测试：`DeletePage` 不存在的 slug 返回 PAGE_NOT_FOUND
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/page.go` 实现 `UpdatePage`, `DeletePage`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 index.md 行操作（增/删/改）为独立函数
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 8: wiki log 操作

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/wiki/log_test.go` 编写日志测试
  - 测试：`ShowLog` 返回所有日志条目
  - 测试：`ShowLog` 带 limit 参数限制返回数量
  - 测试：`AppendLog` 追加条目到 log.md
  - 测试：空日志时 `ShowLog` 返回空数组
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/wiki/log.go` 实现 `ShowLog`, `AppendLog`
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保日志条目格式一致（时间戳 + 操作类型 + 详情）
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 9: output 格式化（JSON + Text）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/output/json_test.go` 编写 JSON 输出测试
  - 测试：成功响应含 `success: true`, `data`, `timestamp`
  - 测试：错误响应含 `success: false`, `error.code`, `error.message`, `error.details`
  - 测试：timestamp 为 ISO 8601 格式
- [x] **1.2** 在 `internal/output/text_test.go` 编写文本输出测试
  - 测试：status 文本输出含配置来源
  - 测试：status --verbose 文本输出含每页详情
- [x] **1.3** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/output/json.go` 实现 `JSON(w, success, data, err)` 函数
- [x] **2.2** 在 `internal/output/text.go` 实现 `Text(w, result)` 函数
- [x] **2.3** 定义 `Response`, `ErrorInfo` 结构体
- [x] **2.4** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取错误码常量到 `internal/output/errors.go`
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 10: CLI 根命令 + 全局选项

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/root_test.go` 编写根命令测试
  - 测试：`--help` 输出帮助信息
  - 测试：`--version` 输出版本号（非空）
  - 测试：`--config` 指定配置文件路径
  - 测试：`--json` 启用 JSON 输出模式
  - 测试：`--quiet` 抑制非错误输出
  - 测试：`--no-color` 禁用颜色输出
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `cmd/openwiki/main.go` 创建入口（ldflags 注入点）
- [x] **2.2** 在 `internal/cli/root.go` 实现根命令 + 全局选项解析 + 配置发现
- [x] **2.3** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取全局选项解析为独立函数
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 11: CLI init 命令

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/init_test.go` 编写 init 命令测试
  - 测试：`init ./test-wiki --non-interactive --json` 创建目录并返回 JSON
  - 测试：`init` 缺少 wiki-root 参数返回错误
  - 测试：`init` 目标已存在返回 WIKI_ALREADY_EXISTS
  - 测试：`init --force` 覆盖已有实例
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/init.go` 实现 `runInit` 和 init 命令注册
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取参数验证逻辑
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 12: CLI config 命令组

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/config_test.go` 编写 config 命令测试
  - 测试：`config show --json` 返回完整配置
  - 测试：`config get wiki_root --json` 返回单个值
  - 测试：`config set wiki.primary_language en --json` 修改并返回旧/新值
  - 测试：`config validate --json` 有效配置返回 success
  - 测试：`config validate --json` 无效配置返回错误
  - 测试：`config path --json` 返回路径和来源
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/config.go` 实现 config 子命令组
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取配置键路径解析为独立函数
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 13: CLI status 命令

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/status_test.go` 编写 status 命令测试
  - 测试：`status --json` 返回页面统计和配置来源
  - 测试：`status --verbose` 输出含每页详情
  - 测试：status 输出含孤立页面和过期页面信息
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/status.go` 实现 `runStatus` 和 status 命令注册
- [x] **2.2** 实现孤立页面检测（index.md 中无其他页面引用）
- [x] **2.3** 实现过期页面检测（updated 超过 90 天）
- [x] **2.4** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取健康检查逻辑为独立函数
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 14: CLI page 命令组

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/page_test.go` 编写 page 命令测试
  - 测试：`page list --json` 返回页面列表
  - 测试：`page list --scope repo --json` 按 scope 过滤
  - 测试：`page get <slug> --json` 返回页面内容
  - 测试：`page get <slug1> <slug2> --json` 批量返回
  - 测试：`page create <slug> --file /tmp/content.md --json` 创建页面
  - 测试：`page update <slug> --file /tmp/updated.md --json` 更新页面
  - 测试：`page delete <slug> --force --json` 删除页面
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/page.go` 实现 page 子命令组
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 `--file` 参数读取为独立函数
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 15: CLI log 命令组

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/log_test.go` 编写 log 命令测试
  - 测试：`log show --json` 返回日志列表
  - 测试：`log show --limit 5 --json` 限制返回数量
  - 测试：`log append "test entry" --json` 追加日志
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/log.go` 实现 log 子命令组
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保日志格式一致
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 16: CLI sync 命令

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `internal/cli/sync_test.go` 编写 sync 命令测试
  - 测试：`sync --dry-run --json` 预览变更
  - 测试：sync 未配置 remote 时返回错误
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `internal/cli/sync.go` 实现 sync 命令（使用 Syncer 接口，测试用 stub）
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 Syncer 接口定义
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 17: E2E Test Harness

### Phase 1: RED - Write Failing Test

- [x] **1.1** 创建 `tests/e2e/harness/harness.go`
  - Harness 负责：构建二进制、创建临时 wiki、执行命令、捕获输出
- [x] **1.2** 在 `tests/e2e/harness/harness_test.go` 编写 Harness 自身测试
  - 测试：Harness 能成功构建二进制
  - 测试：Harness 能执行命令并捕获输出
- [x] **1.3** 运行测试确认 FAILS（二进制尚未构建）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 实现 Harness 的 `New`, `Run`, `Cleanup`, `TempWikiRoot` 方法
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 添加 Harness 超时控制
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 18: E2E 测试（init → page → status 完整流程）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/e2e/init_test.go` 编写 init E2E 测试
  - 测试：完整 init 流程，验证所有目录和文件创建
- [x] **1.2** 在 `tests/e2e/page_test.go` 编写 page E2E 测试
  - 测试：create → get → update → delete 完整生命周期
  - 测试：验证 index.md 和 log.md 自动更新
- [x] **1.3** 在 `tests/e2e/status_test.go` 编写 status E2E 测试
  - 测试：status 正确反映页面变更
- [x] **1.4** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 修复 E2E 测试中发现的问题
- [x] **2.2** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 提取 E2E 测试公共 fixture 创建逻辑
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 19: 构建系统（Makefile + ldflags）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 创建 `Makefile` 含 build/test/test-e2e 目标
- [x] **1.2** 在 `internal/cli/root_test.go` 编写版本注入测试
  - 测试：`--version` 输出非空且非 "dev"（构建时注入）
- [x] **1.3** 运行 `make build && ./bin/openwiki --version` 确认输出版本

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 在 `cmd/openwiki/main.go` 添加 `Version` 和 `BuildTime` 变量
- [x] **2.2** 在 Makefile 添加 ldflags 注入
- [x] **2.3** 运行 `make test` 确认全部测试通过

### Phase 3: REFACTOR - Improve

- [x] **3.1** 添加 `make clean` 目标
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 20: 配置格式迁移（WIKI.md → openwiki.toml）

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_config_migration.py` 编写迁移验证测试
  - 测试：所有 Skill SKILL.md 不再引用 `WIKI.md` 作为配置来源
  - 测试：所有 Skill SKILL.md 引用 `openwiki.toml` 或 `openwiki config` 命令
  - 测试：wiki-init 模板目录含 `openwiki.toml` 而非 `WIKI.md`
  - 测试：validate_wiki.py 检查对象为 `openwiki.toml`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新 `skill/wiki-init/templates/`：WIKI.md → openwiki.toml
- [x] **2.2** 更新 `skill/wiki-init/SKILL.md`：配置路径变更
- [x] **2.3** 更新 `skill/wiki-ingest/SKILL.md`：配置路径变更
- [x] **2.4** 更新 `skill/wiki-lint/SKILL.md`：配置路径变更
- [x] **2.5** 更新 `skill/wiki-query/SKILL.md`：配置路径变更
- [x] **2.6** 更新 `skill/wiki-update/SKILL.md`：配置路径变更
- [x] **2.7** 更新 `skill/wiki-distill/SKILL.md`：配置路径变更
- [x] **2.8** 更新 `skill/wiki-lint/scripts/validate_wiki.py`：检查对象变更
- [x] **2.9** 更新所有测试 fixtures：WIKI.md → openwiki.toml
- [x] **2.10** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查是否有遗漏的 WIKI.md 引用
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 21: Skill → CLI 委托

### Phase 1: RED - Write Failing Test

- [x] **1.1** 在 `tests/test_skill_cli_delegation.py` 编写委托验证测试
  - 测试：wiki-lint 步骤含 `openwiki page list --json` 和 `openwiki page get`
  - 测试：wiki-ingest 步骤含 `openwiki page create` 和 `openwiki page list`
  - 测试：wiki-query 步骤含 `openwiki page list` 和 `openwiki page get`
  - 测试：wiki-update 步骤含 `openwiki page get`、`openwiki page update`、`openwiki log append`
  - 测试：wiki-distill 步骤含 `openwiki page create`
  - 测试：wiki-init 步骤含 `openwiki init`
- [x] **1.2** 运行测试确认 FAILS

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 更新 `skill/wiki-lint/SKILL.md`：页面清单构建 → `openwiki page list --json`，内容读取 → `openwiki page get <slugs> --json`
- [x] **2.2** 更新 `skill/wiki-ingest/SKILL.md`：页面创建 → `openwiki page create`，已有页面检查 → `openwiki page list --json`，回链审计 → `openwiki page get --json`
- [x] **2.3** 更新 `skill/wiki-query/SKILL.md`：索引扫描 → `openwiki page list --json`，页面读取 → `openwiki page get --json`
- [x] **2.4** 更新 `skill/wiki-update/SKILL.md`：页面读写 → `openwiki page get/update`，日志 → `openwiki log append`
- [x] **2.5** 更新 `skill/wiki-distill/SKILL.md`：页面创建 → `openwiki page create`
- [x] **2.6** 更新 `skill/wiki-init/SKILL.md`：初始化 → `openwiki init`
- [x] **2.7** 运行测试确认 PASSES

### Phase 3: REFACTOR - Improve

- [x] **3.1** 检查 Skill 中是否还有残留的直接文件操作指令
- [x] **3.2** 运行全部测试确认通过

---

## Verification

完成所有 Behavior 后：

- [x] 运行 `make test` 确认全部 Go 单元测试通过
- [x] 运行 `make test-e2e` 确认全部 E2E 测试通过
- [x] 运行 `python3 -m unittest discover -s tests -p "test_*.py" -v` 确认全部 Python 测试通过
- [x] 验证 25 条 acceptance criteria 全部满足
- [x] 手动执行 `./bin/openwiki init ./test-wiki --non-interactive --json` 验证
- [x] 手动执行 `./bin/openwiki status --json` 验证
- [x] 手动执行 `./bin/openwiki page create test --file /tmp/test.md --json` 验证

## Test Quality Checklist

- [x] 测试描述 BEHAVIOR，而非实现细节
- [x] 测试使用 PUBLIC 接口（CLI 命令或公开函数）
- [x] 测试在内部重构后仍然有效
- [x] 测试名称描述 WHAT，而非 HOW
- [x] 每个测试一个逻辑断言
- [x] 不 mock 内部协作者（使用 MemFS 替代 mock）
